"""
Teste FollowUp API + integrare Auth.

Regulă de securitate verificată explicit:
owner_id este derivat exclusiv din JWT. Orice owner_id trimis
suplimentar de client este ignorat.
"""

import os
from uuid import uuid4

import bcrypt
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


def _create_user(prefix: str) -> tuple[str, str, str]:
    email = f"{prefix}-{uuid4()}@nicmar.local"
    password = "TestPassword!123"
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, full_name, role, password_hash) "
                "VALUES (%s, %s, 'LEADER', %s) RETURNING id",
                (email, f"API Test {prefix}", password_hash),
            )
            return str(cur.fetchone()[0]), email, password


def _headers(client, email: str, password: str) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_contact_and_conversation(owner_id: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO contacts (owner_id, full_name, status) "
                "VALUES (%s, %s, 'ACTIVE') RETURNING id",
                (owner_id, "Contact API Test"),
            )
            contact_id = str(cur.fetchone()[0])
            cur.execute(
                "INSERT INTO conversations (owner_id, contact_id, channel, status) "
                "VALUES (%s, %s, 'WHATSAPP', 'FOLLOWUP_NEEDED') RETURNING id",
                (owner_id, contact_id),
            )
            conversation_id = str(cur.fetchone()[0])
    return contact_id, conversation_id


def _create_followup(client, headers, contact_id, conversation_id, extra=None):
    payload = {"contact_id": contact_id, "conversation_id": conversation_id}
    if extra:
        payload.update(extra)
    return client.post("/api/v1/followups", json=payload, headers=headers)


def test_create_followup_success(client):
    owner_id, email, password = _create_user("create")
    headers = _headers(client, email, password)
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)

    response = _create_followup(client, headers, contact_id, conversation_id)
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"
    assert response.json()["owner_id"] == owner_id


def test_create_followup_owner_id_from_body_is_ignored(client):
    owner_id, email, password = _create_user("create-owner-a")
    other_id, _, _ = _create_user("create-owner-b")
    headers = _headers(client, email, password)
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)

    response = _create_followup(
        client, headers, contact_id, conversation_id, extra={"owner_id": other_id}
    )
    assert response.status_code == 201
    assert response.json()["owner_id"] == owner_id


def test_create_followup_duplicate_returns_409(client):
    owner_id, email, password = _create_user("duplicate")
    headers = _headers(client, email, password)
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)

    assert _create_followup(client, headers, contact_id, conversation_id).status_code == 201
    response = _create_followup(client, headers, contact_id, conversation_id)
    assert response.status_code == 409
    assert response.json()["error_code"] == "ALREADY_EXISTS"


def test_list_followups_owner_isolated(client):
    owner_a, email_a, password_a = _create_user("list-a")
    owner_b, email_b, password_b = _create_user("list-b")
    headers_a = _headers(client, email_a, password_a)
    headers_b = _headers(client, email_b, password_b)

    contact_a, conv_a = _create_contact_and_conversation(owner_a)
    contact_b, conv_b = _create_contact_and_conversation(owner_b)
    assert _create_followup(client, headers_a, contact_a, conv_a).status_code == 201
    assert _create_followup(client, headers_b, contact_b, conv_b).status_code == 201

    response = client.get("/api/v1/followups", headers=headers_a)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["owner_id"] == owner_a


def test_list_followups_ignores_owner_id_query(client):
    owner_a, email_a, password_a = _create_user("list-query-a")
    owner_b, _, _ = _create_user("list-query-b")
    headers_a = _headers(client, email_a, password_a)
    contact_a, conv_a = _create_contact_and_conversation(owner_a)
    assert _create_followup(client, headers_a, contact_a, conv_a).status_code == 201

    response = client.get(
        "/api/v1/followups", params={"owner_id": owner_b}, headers=headers_a
    )
    assert response.status_code == 200
    assert all(item["owner_id"] == owner_a for item in response.json())


def test_list_followups_owner_without_followup_returns_empty(client):
    _, email, password = _create_user("list-empty")
    headers = _headers(client, email, password)
    response = client.get("/api/v1/followups", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_complete_followup_success(client):
    owner_id, email, password = _create_user("complete-ok")
    headers = _headers(client, email, password)
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)
    followup_id = _create_followup(client, headers, contact_id, conversation_id).json()["id"]

    response = client.post(
        f"/api/v1/followups/{followup_id}/complete",
        json={"confirmed": True}, headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_complete_followup_without_confirmation_returns_400(client):
    owner_id, email, password = _create_user("complete-noconfirm")
    headers = _headers(client, email, password)
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)
    followup_id = _create_followup(client, headers, contact_id, conversation_id).json()["id"]

    response = client.post(
        f"/api/v1/followups/{followup_id}/complete",
        json={"confirmed": False}, headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "CONFIRMATION_REQUIRED"


def test_complete_followup_wrong_owner_returns_403(client):
    owner_a, email_a, password_a = _create_user("complete-owner-a")
    _, email_b, password_b = _create_user("complete-owner-b")
    headers_a = _headers(client, email_a, password_a)
    headers_b = _headers(client, email_b, password_b)
    contact_id, conversation_id = _create_contact_and_conversation(owner_a)
    followup_id = _create_followup(client, headers_a, contact_id, conversation_id).json()["id"]

    response = client.post(
        f"/api/v1/followups/{followup_id}/complete",
        json={"confirmed": True, "owner_id": owner_a}, headers=headers_b,
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"


def test_postpone_followup_success(client):
    owner_id, email, password = _create_user("postpone-ok")
    headers = _headers(client, email, password)
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)
    followup_id = _create_followup(client, headers, contact_id, conversation_id).json()["id"]

    response = client.post(
        f"/api/v1/followups/{followup_id}/postpone", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "POSTPONED"


def test_reschedule_followup_success(client):
    owner_id, email, password = _create_user("reschedule-ok")
    headers = _headers(client, email, password)
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)
    followup_id = _create_followup(client, headers, contact_id, conversation_id).json()["id"]

    response = client.post(
        f"/api/v1/followups/{followup_id}/reschedule", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "RESCHEDULED"


def test_dis_score_no_followups_yet(client):
    _, email, password = _create_user("dis-score-empty")
    headers = _headers(client, email, password)
    response = client.get(
        "/api/v1/followups/dis-score",
        params={"owner_id": str(uuid4())}, headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["dis_score"] is None


def test_dis_score_after_create(client):
    owner_id, email, password = _create_user("dis-score-after")
    headers = _headers(client, email, password)
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)
    _create_followup(client, headers, contact_id, conversation_id)

    response = client.get("/api/v1/followups/dis-score", headers=headers)
    assert response.status_code == 200
    assert response.json()["dis_score"] == 1.0


# ----------------------------------------------------------------------
# DECIZIA 45 (RED, 19 august 2026) — izolare owner pentru DIS FollowUp.
# Sursa: 45-followup-dis-workbench-contract.md, sectiunea 5, criteriile 4-5.
#
# Gol identificat la audit: izolarea era garantata doar de filtrul SQL
# (f.owner_id = %s), fara test HTTP dedicat cu doi lideri reali — spre
# deosebire de toate celelalte endpoint-uri mutante din proiect.
# ----------------------------------------------------------------------


def test_owner_a_vede_exclusiv_dis_score_propriu(client):
    """
    Contract 45, criteriul 4: liderul A creeaza un follow-up (DIS scris
    real), liderul B (autentificat separat) apeleaza GET /followups/dis-score
    si NU primeste DIS-ul lui A.
    """
    owner_a, email_a, password_a = _create_user("dis-isolation-owner-a")
    owner_b, email_b, password_b = _create_user("dis-isolation-owner-b")
    headers_a = _headers(client, email_a, password_a)
    headers_b = _headers(client, email_b, password_b)

    contact_id, conversation_id = _create_contact_and_conversation(owner_a)
    _create_followup(client, headers_a, contact_id, conversation_id)

    response_b = client.get("/api/v1/followups/dis-score", headers=headers_b)
    assert response_b.status_code == 200
    assert response_b.json()["dis_score"] is None


def test_owner_b_vede_exclusiv_dis_score_propriu(client):
    """
    Contract 45, criteriul 5: companion invers al testului anterior —
    liderul B creeaza follow-up-ul, liderul A nu-i vede DIS-ul. Impreuna,
    cele doua teste inchid golul de izolare identificat la audit.
    """
    owner_a, email_a, password_a = _create_user("dis-isolation-owner-a2")
    owner_b, email_b, password_b = _create_user("dis-isolation-owner-b2")
    headers_a = _headers(client, email_a, password_a)
    headers_b = _headers(client, email_b, password_b)

    contact_id, conversation_id = _create_contact_and_conversation(owner_b)
    _create_followup(client, headers_b, contact_id, conversation_id)

    response_a = client.get("/api/v1/followups/dis-score", headers=headers_a)
    assert response_a.status_code == 200
    assert response_a.json()["dis_score"] is None


class TestInvalidFollowUpIdReturns422:
    INVALID_ID = "nu-e-un-uuid-valid"

    def test_complete_invalid_id_returns_422(self, client):
        _, email, password = _create_user("invalid-complete")
        headers = _headers(client, email, password)
        response = client.post(
            f"/api/v1/followups/{self.INVALID_ID}/complete",
            json={"confirmed": True}, headers=headers,
        )
        assert response.status_code == 422

    def test_postpone_invalid_id_returns_422(self, client):
        _, email, password = _create_user("invalid-postpone")
        headers = _headers(client, email, password)
        response = client.post(
            f"/api/v1/followups/{self.INVALID_ID}/postpone", headers=headers
        )
        assert response.status_code == 422

    def test_reschedule_invalid_id_returns_422(self, client):
        _, email, password = _create_user("invalid-reschedule")
        headers = _headers(client, email, password)
        response = client.post(
            f"/api/v1/followups/{self.INVALID_ID}/reschedule", headers=headers
        )
        assert response.status_code == 422


def test_full_http_flow_create_to_complete(client):
    owner_id, email, password = _create_user("full-flow")
    headers = _headers(client, email, password)
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)

    r1 = _create_followup(client, headers, contact_id, conversation_id)
    assert r1.status_code == 201
    followup_id = r1.json()["id"]

    r2 = client.get("/api/v1/followups", headers=headers)
    assert any(f["id"] == followup_id for f in r2.json())

    r3 = client.post(
        f"/api/v1/followups/{followup_id}/complete",
        json={"confirmed": True}, headers=headers,
    )
    assert r3.status_code == 200
    assert r3.json()["status"] == "COMPLETED"

    r4 = client.get("/api/v1/followups", headers=headers)
    assert not any(f["id"] == followup_id for f in r4.json())

    r5 = client.get("/api/v1/followups/dis-score", headers=headers)
    assert r5.json()["dis_score"] == 1.0
