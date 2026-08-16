"""
Teste pentru Mission API — folosind FastAPI TestClient.

Sarite (skip) daca DATABASE_URL nu e setat — la fel ca
test_real_postgres.py, API-ul foloseste engines/agents reale, care au
nevoie de PostgreSQL real (nu are sens sa mock-uim DB-ul la nivel de
API, ar testa doar routing-ul, nu integrarea reala).
"""

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.data.db import get_connection

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="Necesita DATABASE_URL (PostgreSQL real) — sarit fara DB configurat.",
)


@pytest.fixture(scope="module")
def client():
    from src.api.main import app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module", autouse=True)
def ensure_kpis_seeded():
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


def _create_user(prefix: str) -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, full_name, role) VALUES (%s, %s, 'LEADER') RETURNING id",
                (f"{prefix}-{uuid4()}@nicmar.local", f"API Test {prefix}"),
            )
            return str(cur.fetchone()[0])


def test_health_check(client):
    """/health raspunde 200, fara sa atinga DB."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_mission_success(client):
    """POST /api/v1/missions creeaza o misiune, status 201, GENERATED."""
    owner_id = _create_user("create")
    response = client.post("/api/v1/missions", json={"owner_id": owner_id, "title": "Test API"})
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "GENERATED"
    assert body["title"] == "Test API"


def test_create_mission_duplicate_returns_409(client):
    """A doua misiune, acelasi owner, aceeasi zi -> 409 ALREADY_EXISTS."""
    owner_id = _create_user("duplicate")
    client.post("/api/v1/missions", json={"owner_id": owner_id, "title": "Prima"})

    response = client.post("/api/v1/missions", json={"owner_id": owner_id, "title": "A doua"})
    assert response.status_code == 409
    assert response.json()["error_code"] == "ALREADY_EXISTS"


def test_present_mission(client):
    """GET /present include titlul misiunii in text."""
    owner_id = _create_user("present")
    create_resp = client.post("/api/v1/missions", json={"owner_id": owner_id, "title": "Sună clientul"})
    mission_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/missions/{mission_id}/present", params={"owner_id": owner_id})
    assert response.status_code == 200
    assert "Sună clientul" in response.json()["text"]


def test_start_without_assign_returns_400(client):
    """
    Pornirea directa (fara assign) da 400 INVALID_TRANSITION.

    Descoperire de la testarea manuala: endpoint-ul /assign nu exista
    inca in contract (v. 14-api-contract.md, sectiunea 6) — GENERATED
    nu poate sari direct in IN_PROGRESS.
    """
    owner_id = _create_user("start-fail")
    create_resp = client.post("/api/v1/missions", json={"owner_id": owner_id, "title": "Test"})
    mission_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/missions/{mission_id}/start",
        json={"owner_id": owner_id, "confirmed": True},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "INVALID_TRANSITION"


def test_access_denied_wrong_owner(client):
    """owner_id gresit -> 403 ACCESS_DENIED, nu 404 (nu dezvaluie existenta)."""
    owner_id = _create_user("access-a")
    create_resp = client.post("/api/v1/missions", json={"owner_id": owner_id, "title": "Confidential"})
    mission_id = create_resp.json()["id"]

    wrong_owner_id = str(uuid4())
    response = client.post(
        f"/api/v1/missions/{mission_id}/complete",
        json={"owner_id": wrong_owner_id},
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"


def test_dis_score_endpoint_readonly(client):
    """GET /dis-score raspunde 200, chiar daca nu exista inca niciun scor (None)."""
    owner_id = _create_user("dis-score")
    response = client.get("/api/v1/missions/dis-score", params={"owner_id": owner_id})
    assert response.status_code == 200
    assert response.json()["dis_score"] is None


def test_assign_mission_success(client):
    """POST /assign: GENERATED -> ASSIGNED, cu owner corect."""
    owner_id = _create_user("assign-ok")
    create_resp = client.post("/api/v1/missions", json={"owner_id": owner_id, "title": "Test assign"})
    mission_id = create_resp.json()["id"]

    response = client.post(f"/api/v1/missions/{mission_id}/assign", json={"owner_id": owner_id})
    assert response.status_code == 200
    assert response.json()["status"] == "ASSIGNED"


def test_assign_mission_wrong_owner_returns_403(client):
    """POST /assign, alt owner -> 403 ACCESS_DENIED."""
    owner_id = _create_user("assign-owner")
    other_owner_id = str(uuid4())
    create_resp = client.post("/api/v1/missions", json={"owner_id": owner_id, "title": "Confidential"})
    mission_id = create_resp.json()["id"]

    response = client.post(f"/api/v1/missions/{mission_id}/assign", json={"owner_id": other_owner_id})
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"


def test_assign_mission_nonexistent_id_returns_403(client):
    """
    POST /assign, ID inexistent -> 403 ACCESS_DENIED (nu 404).

    Comportament contractual confirmat: MissionAccessDeniedError
    foloseste acelasi mesaj/cod pentru "nu exista" si "nu e al tau" —
    previne enumerarea de ID-uri (v. docstring MissionAccessDeniedError).
    """
    owner_id = _create_user("assign-nonexistent")
    fake_mission_id = uuid4()

    response = client.post(f"/api/v1/missions/{fake_mission_id}/assign", json={"owner_id": owner_id})
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"


def test_assign_mission_invalid_transition_returns_400(client):
    """POST /assign de doua ori pe rand -> a doua oara, ASSIGNED->ASSIGNED e invalid."""
    owner_id = _create_user("assign-twice")
    create_resp = client.post("/api/v1/missions", json={"owner_id": owner_id, "title": "Test"})
    mission_id = create_resp.json()["id"]

    first = client.post(f"/api/v1/missions/{mission_id}/assign", json={"owner_id": owner_id})
    assert first.status_code == 200

    second = client.post(f"/api/v1/missions/{mission_id}/assign", json={"owner_id": owner_id})
    assert second.status_code == 400
    assert second.json()["error_code"] == "INVALID_TRANSITION"


def test_full_http_flow_generate_to_complete(client):
    """
    Fluxul HTTP complet: generate -> assign -> present -> start -> complete -> DIS.

    Acesta e testul decisiv — dovedeste ca Mission API e complet
    functional cap-coada, nu doar endpoint cu endpoint izolat.
    """
    owner_id = _create_user("full-flow")

    r1 = client.post("/api/v1/missions", json={"owner_id": owner_id, "title": "Sună clientul"})
    assert r1.status_code == 201
    mission_id = r1.json()["id"]
    assert r1.json()["status"] == "GENERATED"

    r2 = client.post(f"/api/v1/missions/{mission_id}/assign", json={"owner_id": owner_id})
    assert r2.status_code == 200
    assert r2.json()["status"] == "ASSIGNED"

    r3 = client.get(f"/api/v1/missions/{mission_id}/present", params={"owner_id": owner_id})
    assert r3.status_code == 200
    assert "Sună clientul" in r3.json()["text"]

    r4 = client.post(
        f"/api/v1/missions/{mission_id}/start",
        json={"owner_id": owner_id, "confirmed": True},
    )
    assert r4.status_code == 200
    assert r4.json()["status"] == "IN_PROGRESS"

    r5 = client.post(f"/api/v1/missions/{mission_id}/complete", json={"owner_id": owner_id})
    assert r5.status_code == 200
    assert r5.json()["status"] == "COMPLETED"

    r6 = client.get("/api/v1/missions/dis-score", params={"owner_id": owner_id})
    assert r6.status_code == 200
    assert r6.json()["dis_score"] == 1.0


class TestInvalidMissionIdReturns422:
    """
    Aliniere de comportament (12 august 2026): toate cele 4 endpoint-uri
    cu mission_id in path folosesc acum UUID direct ca tip — FastAPI
    valideaza automat si returneaza 422, nu mai crapa cu 500 pentru
    un ID malformat.
    """

    INVALID_ID = "nu-e-un-uuid-valid"

    def test_assign_invalid_id_returns_422(self, client):
        owner_id = _create_user("invalid-assign")
        response = client.post(
            f"/api/v1/missions/{self.INVALID_ID}/assign", json={"owner_id": owner_id}
        )
        assert response.status_code == 422

    def test_present_invalid_id_returns_422(self, client):
        owner_id = _create_user("invalid-present")
        response = client.get(
            f"/api/v1/missions/{self.INVALID_ID}/present", params={"owner_id": owner_id}
        )
        assert response.status_code == 422

    def test_start_invalid_id_returns_422(self, client):
        owner_id = _create_user("invalid-start")
        response = client.post(
            f"/api/v1/missions/{self.INVALID_ID}/start",
            json={"owner_id": owner_id, "confirmed": True},
        )
        assert response.status_code == 422

    def test_complete_invalid_id_returns_422(self, client):
        owner_id = _create_user("invalid-complete")
        response = client.post(
            f"/api/v1/missions/{self.INVALID_ID}/complete", json={"owner_id": owner_id}
        )
        assert response.status_code == 422
