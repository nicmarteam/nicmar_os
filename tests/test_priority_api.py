"""
Teste RED — Priority API (Decizia 39), HTTP real + PostgreSQL real.

Sursa: 39-priority-api-contract.md, sectiunea 7.

Inchide explicit golul de testare identificat la auditul contractului 19
(PriorityEngine): test_priority_engine.py contine doar teste unitare cu
mock-uri, fara izolare owner reala si fara integrare PostgreSQL. Aici
adaugam exact ce lipsea, la nivel de API, urmand fluxul HTTP real
(register -> login -> create contact -> create conversation -> create
followup / create mission), acelasi tipar deja folosit in
test_followup_api.py, test_partners_api.py, test_mission_api.py,
test_conversation_objection_linkage.py.
"""

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-doar-pentru-teste-minim-32-bytes-lungime")

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="Necesita DATABASE_URL (PostgreSQL real) — sarit fara DB configurat.",
)


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from src.api.main import app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module", autouse=True)
def ensure_kpis_seeded():
    from src.data.db import get_connection

    kpis = [
        ("DIS", "Daily Impact Score"), ("CRH", "Customer Relationship Health"),
        ("PDI", "Partner Development Index"), ("PIP", "Partner Integration Progress"),
        ("OAS", "Onboarding Activation Success"), ("ERI", "Experience Reuse Index"),
        ("LRI", "Leadership Readiness Index"), ("MEI", "Mentoring Effectiveness Index"),
        ("TDI", "Team Development Index"), ("AMS", "Autonomy Maturity Score"),
        ("PES", "Presentation Effectiveness Score"), ("ORE", "Objection Resolution Effectiveness"),
        ("OPI", "Overall Performance Index"),
    ]
    with get_connection() as conn:
        with conn.cursor() as cur:
            for code, name in kpis:
                cur.execute(
                    "INSERT INTO kpis (metric_code, name, status) VALUES (%s, %s, 'PROPOSED') "
                    "ON CONFLICT (metric_code) DO NOTHING",
                    (code, name),
                )


@pytest.fixture(autouse=True)
def reset_login_rate_limiter():
    from src.auth.rate_limit import login_rate_limiter
    login_rate_limiter.reset()
    yield
    login_rate_limiter.reset()


# ----------------------------------------------------------------------
# Helpere HTTP reale — acelasi tipar ca test_conversation_objection_linkage.py
# ----------------------------------------------------------------------


def _register_and_login(client, prefix: str) -> dict:
    email = f"{prefix}-{uuid4()}@nicmar.local"
    password = "parola123"
    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": prefix},
    )
    assert r.status_code == 201, r.text
    owner_id = r.json()["id"]

    r_login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r_login.status_code == 200, r_login.text
    token = r_login.json()["access_token"]

    return {"owner_id": owner_id, "headers": {"Authorization": f"Bearer {token}"}}


def _create_contact(client, session, full_name: str = "Contact Priority Test") -> str:
    r = client.post(
        "/api/v1/contacts", json={"full_name": full_name}, headers=session["headers"],
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _create_conversation(client, session, contact_id: str) -> str:
    r = client.post(
        "/api/v1/conversations", json={"contact_id": contact_id}, headers=session["headers"],
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _create_followup(client, session, contact_id: str, conversation_id: str,
                      scheduled_at: str | None = None) -> str:
    payload = {"contact_id": contact_id, "conversation_id": conversation_id}
    if scheduled_at is not None:
        payload["scheduled_at"] = scheduled_at
    r = client.post("/api/v1/followups", json=payload, headers=session["headers"])
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _create_pending_followup(client, session, scheduled_at: str | None = None) -> str:
    """Creeaza contact + conversatie + followup, fiecare cu date proprii — un follow-up PENDING complet nou."""
    contact_id = _create_contact(client, session)
    conversation_id = _create_conversation(client, session, contact_id)
    return _create_followup(client, session, contact_id, conversation_id, scheduled_at)


def _create_mission(client, session, title: str = "Mission Priority Test") -> dict:
    r = client.post("/api/v1/missions", json={"title": title}, headers=session["headers"])
    assert r.status_code == 201, r.text
    return r.json()


def _complete_mission_fully(client, session, mission_id: str) -> None:
    """Parcurge fluxul complet GENERATED -> ASSIGNED -> IN_PROGRESS -> COMPLETED, prin HTTP real."""
    r1 = client.post(f"/api/v1/missions/{mission_id}/assign", headers=session["headers"])
    assert r1.status_code == 200, r1.text
    r2 = client.post(
        f"/api/v1/missions/{mission_id}/start", json={"confirmed": True}, headers=session["headers"],
    )
    assert r2.status_code == 200, r2.text
    r3 = client.post(f"/api/v1/missions/{mission_id}/complete", headers=session["headers"])
    assert r3.status_code == 200, r3.text


def _far_future_iso() -> str:
    """Scheduled_at suficient de departe incat urgenta FollowUp sa fie FAR (>=3 zile)."""
    return (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()


# ----------------------------------------------------------------------
# DECIZIA 39 (RED, 19 august 2026) — cele 8 criterii din contract,
# sectiunea 7.
# ----------------------------------------------------------------------


def test_get_priority_requires_authentication(client):
    """Criteriul 1: fara token -> 401."""
    r = client.get("/api/v1/priority")
    assert r.status_code == 401


def test_get_priority_returns_empty_list_when_no_activities(client):
    """Criteriul 2: owner nou, fara mission/followup activ -> lista goala."""
    session = _register_and_login(client, "priority-empty")

    r = client.get("/api/v1/priority", headers=session["headers"])

    assert r.status_code == 200
    assert r.json() == []


def test_get_priority_returns_max_five_activities(client):
    """
    Criteriul 3: owner cu 6 follow-up-uri PENDING eligibile (fiecare pe
    contact+conversatie proprii, ca sa nu loveasca regula de duplicat
    per-conversatie) -> raspunsul are exact 5 elemente, nu 6.
    """
    session = _register_and_login(client, "priority-max5")
    for _ in range(6):
        _create_pending_followup(client, session)

    r = client.get("/api/v1/priority", headers=session["headers"])

    assert r.status_code == 200
    assert len(r.json()) == 5


def test_get_priority_excludes_completed_activities(client):
    """
    Criteriul 4: o misiune dusa complet pana la COMPLETED (prin fluxul
    HTTP real assign->start->complete) nu apare in raspuns; un follow-up
    PENDING separat, al aceluiasi owner, apare.
    """
    session = _register_and_login(client, "priority-excl-completed")
    mission = _create_mission(client, session)
    _complete_mission_fully(client, session, mission["id"])
    followup_id = _create_pending_followup(client, session)

    r = client.get("/api/v1/priority", headers=session["headers"])

    assert r.status_code == 200
    body = r.json()
    entity_ids = [item["entity_id"] for item in body]
    assert mission["id"] not in entity_ids
    assert followup_id in entity_ids


def test_get_priority_orders_by_impact_domination(client):
    """
    Criteriul 5: invarianta 1 din contract 19 — Impact domina, verificat
    prin HTTP real. Mission are Impact 1.0 fix. Un FollowUp pe un contact
    proaspat creat (status implicit 'NEW' — nu exista endpoint HTTP care
    sa schimbe statusul contactului, verificat la audit) are Impact 1.5
    (1.0 + bonus 0.5), programat departe in viitor (Urgenta FAR, cea mai
    mica posibila) — trebuie sa apara totusi INAINTEA misiunii in lista,
    pentru ca Impact-ul mai mare decide primul in priority_key, indiferent
    de Urgenta.
    """
    session = _register_and_login(client, "priority-impact")
    mission = _create_mission(client, session)
    followup_id = _create_pending_followup(client, session, scheduled_at=_far_future_iso())

    r = client.get("/api/v1/priority", headers=session["headers"])

    assert r.status_code == 200
    entity_ids = [item["entity_id"] for item in r.json()]
    assert followup_id in entity_ids
    assert mission["id"] in entity_ids
    assert entity_ids.index(followup_id) < entity_ids.index(mission["id"]), (
        "FollowUp cu Impact 1.5 trebuie sa apara inaintea Mission cu Impact 1.0, "
        "indiferent de Urgenta (invarianta 1, contract 19)."
    )


def test_owner_a_vede_exclusiv_activitatile_proprii(client):
    """
    Criteriul 6 — PostgreSQL real, izolare: liderul A creeaza mission +
    followup; liderul B (autentificat separat) apeleaza GET /priority;
    activitatile lui A nu apar in raspunsul lui B.
    """
    session_a = _register_and_login(client, "priority-owner-a-1")
    session_b = _register_and_login(client, "priority-owner-b-1")

    mission_a = _create_mission(client, session_a)
    followup_a = _create_pending_followup(client, session_a)

    r_b = client.get("/api/v1/priority", headers=session_b["headers"])

    assert r_b.status_code == 200
    entity_ids_b = [item["entity_id"] for item in r_b.json()]
    assert mission_a["id"] not in entity_ids_b
    assert followup_a not in entity_ids_b


def test_owner_b_vede_exclusiv_activitatile_proprii(client):
    """
    Criteriul 7 — companion invers al testului anterior: liderul B
    creeaza activitati, liderul A nu le vede. Impreuna, cele doua teste
    inchid golul de izolare cerut explicit de contractul 19, sectiunea 11.
    """
    session_a = _register_and_login(client, "priority-owner-a-2")
    session_b = _register_and_login(client, "priority-owner-b-2")

    mission_b = _create_mission(client, session_b)
    followup_b = _create_pending_followup(client, session_b)

    r_a = client.get("/api/v1/priority", headers=session_a["headers"])

    assert r_a.status_code == 200
    entity_ids_a = [item["entity_id"] for item in r_a.json()]
    assert mission_b["id"] not in entity_ids_a
    assert followup_b not in entity_ids_a


def test_get_priority_response_fara_priority_key(client):
    """
    Criteriul 8: raspunsul JSON nu contine niciun camp priority_key —
    confirma decizia de serializare din contract 39, sectiunea 4
    (priority_key e derivabil din impact/urgency/vechime_seconds, deja
    expuse, si nu se duplica in response).
    """
    session = _register_and_login(client, "priority-no-key")
    _create_pending_followup(client, session)

    r = client.get("/api/v1/priority", headers=session["headers"])

    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert "priority_key" not in body[0]
    assert set(body[0].keys()) == {
        "entity_type", "entity_id", "title", "impact", "urgency", "vechime_seconds",
    }
