"""
Teste pentru FollowUp API — folosind FastAPI TestClient.

Sarite (skip) daca DATABASE_URL nu e setat — la fel ca test_mission_api.py.
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


# ------------------------------------------------------------------
# create
# ------------------------------------------------------------------

def test_create_followup_success(client):
    owner_id = _create_user("create")
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)

    response = client.post(
        "/api/v1/followups",
        json={"owner_id": owner_id, "contact_id": contact_id, "conversation_id": conversation_id},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["owner_id"] == owner_id


def test_create_followup_duplicate_returns_409(client):
    owner_id = _create_user("duplicate")
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)

    payload = {"owner_id": owner_id, "contact_id": contact_id, "conversation_id": conversation_id}
    client.post("/api/v1/followups", json=payload)

    response = client.post("/api/v1/followups", json=payload)
    assert response.status_code == 409
    assert response.json()["error_code"] == "ALREADY_EXISTS"


# ------------------------------------------------------------------
# list
# ------------------------------------------------------------------

def test_list_followups_owner_izolat(client):
    """Owner A vede doar ale lui, chiar daca Owner B are follow-up-uri."""
    owner_a = _create_user("list-a")
    owner_b = _create_user("list-b")

    contact_a, conv_a = _create_contact_and_conversation(owner_a)
    contact_b, conv_b = _create_contact_and_conversation(owner_b)

    client.post("/api/v1/followups", json={"owner_id": owner_a, "contact_id": contact_a, "conversation_id": conv_a})
    client.post("/api/v1/followups", json={"owner_id": owner_b, "contact_id": contact_b, "conversation_id": conv_b})

    response = client.get("/api/v1/followups", params={"owner_id": owner_a})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["owner_id"] == owner_a


def test_list_followups_owner_fara_followup_returneaza_gol(client):
    owner_id = _create_user("list-empty")
    response = client.get("/api/v1/followups", params={"owner_id": owner_id})
    assert response.status_code == 200
    assert response.json() == []


# ------------------------------------------------------------------
# complete
# ------------------------------------------------------------------

def test_complete_followup_success(client):
    owner_id = _create_user("complete-ok")
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)
    create_resp = client.post(
        "/api/v1/followups",
        json={"owner_id": owner_id, "contact_id": contact_id, "conversation_id": conversation_id},
    )
    followup_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/followups/{followup_id}/complete",
        json={"owner_id": owner_id, "confirmed": True},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_complete_followup_without_confirmation_returns_400(client):
    owner_id = _create_user("complete-noconfirm")
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)
    create_resp = client.post(
        "/api/v1/followups",
        json={"owner_id": owner_id, "contact_id": contact_id, "conversation_id": conversation_id},
    )
    followup_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/followups/{followup_id}/complete",
        json={"owner_id": owner_id, "confirmed": False},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "CONFIRMATION_REQUIRED"


def test_complete_followup_wrong_owner_returns_403(client):
    owner_id = _create_user("complete-owner")
    other_owner_id = str(uuid4())
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)
    create_resp = client.post(
        "/api/v1/followups",
        json={"owner_id": owner_id, "contact_id": contact_id, "conversation_id": conversation_id},
    )
    followup_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/followups/{followup_id}/complete",
        json={"owner_id": other_owner_id, "confirmed": True},
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"


# ------------------------------------------------------------------
# postpone / reschedule
# ------------------------------------------------------------------

def test_postpone_followup_success(client):
    owner_id = _create_user("postpone-ok")
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)
    create_resp = client.post(
        "/api/v1/followups",
        json={"owner_id": owner_id, "contact_id": contact_id, "conversation_id": conversation_id},
    )
    followup_id = create_resp.json()["id"]

    response = client.post(f"/api/v1/followups/{followup_id}/postpone", json={"owner_id": owner_id})
    assert response.status_code == 200
    assert response.json()["status"] == "POSTPONED"


def test_reschedule_followup_success(client):
    owner_id = _create_user("reschedule-ok")
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)
    create_resp = client.post(
        "/api/v1/followups",
        json={"owner_id": owner_id, "contact_id": contact_id, "conversation_id": conversation_id},
    )
    followup_id = create_resp.json()["id"]

    response = client.post(f"/api/v1/followups/{followup_id}/reschedule", json={"owner_id": owner_id})
    assert response.status_code == 200
    assert response.json()["status"] == "RESCHEDULED"


# ------------------------------------------------------------------
# dis-score
# ------------------------------------------------------------------

def test_dis_score_no_followups_yet(client):
    owner_id = _create_user("dis-score-empty")
    response = client.get("/api/v1/followups/dis-score", params={"owner_id": owner_id})
    assert response.status_code == 200
    assert response.json()["dis_score"] is None


def test_dis_score_after_create(client):
    """DIS persistat la CREARE (nu la finalizare) — verificat prin API."""
    owner_id = _create_user("dis-score-after")
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)
    client.post(
        "/api/v1/followups",
        json={"owner_id": owner_id, "contact_id": contact_id, "conversation_id": conversation_id},
    )

    response = client.get("/api/v1/followups/dis-score", params={"owner_id": owner_id})
    assert response.status_code == 200
    assert response.json()["dis_score"] == 1.0


# ------------------------------------------------------------------
# UUID invalid -> 422, pe toate endpoint-urile cu followup_id
# ------------------------------------------------------------------

class TestInvalidFollowUpIdReturns422:

    INVALID_ID = "nu-e-un-uuid-valid"

    def test_complete_invalid_id_returns_422(self, client):
        owner_id = _create_user("invalid-complete")
        response = client.post(
            f"/api/v1/followups/{self.INVALID_ID}/complete",
            json={"owner_id": owner_id, "confirmed": True},
        )
        assert response.status_code == 422

    def test_postpone_invalid_id_returns_422(self, client):
        owner_id = _create_user("invalid-postpone")
        response = client.post(
            f"/api/v1/followups/{self.INVALID_ID}/postpone", json={"owner_id": owner_id}
        )
        assert response.status_code == 422

    def test_reschedule_invalid_id_returns_422(self, client):
        owner_id = _create_user("invalid-reschedule")
        response = client.post(
            f"/api/v1/followups/{self.INVALID_ID}/reschedule", json={"owner_id": owner_id}
        )
        assert response.status_code == 422


# ------------------------------------------------------------------
# Flux HTTP complet
# ------------------------------------------------------------------

def test_full_http_flow_create_to_complete(client):
    """create -> list (il contine) -> complete -> list (nu-l mai contine) -> DIS."""
    owner_id = _create_user("full-flow")
    contact_id, conversation_id = _create_contact_and_conversation(owner_id)

    r1 = client.post(
        "/api/v1/followups",
        json={"owner_id": owner_id, "contact_id": contact_id, "conversation_id": conversation_id},
    )
    assert r1.status_code == 201
    followup_id = r1.json()["id"]

    r2 = client.get("/api/v1/followups", params={"owner_id": owner_id})
    assert any(f["id"] == followup_id for f in r2.json())

    r3 = client.post(
        f"/api/v1/followups/{followup_id}/complete",
        json={"owner_id": owner_id, "confirmed": True},
    )
    assert r3.status_code == 200
    assert r3.json()["status"] == "COMPLETED"

    r4 = client.get("/api/v1/followups", params={"owner_id": owner_id})
    assert not any(f["id"] == followup_id for f in r4.json()), (
        "Follow-up-ul COMPLETED nu trebuie sa mai apara in lista PENDING"
    )

    r5 = client.get("/api/v1/followups/dis-score", params={"owner_id": owner_id})
    assert r5.json()["dis_score"] == 1.0
