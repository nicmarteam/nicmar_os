"""
Teste pentru Partner API — folosind FastAPI TestClient.

Sarite (skip) daca DATABASE_URL nu e setat.
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


def _create_partner(owner_id: str) -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO contacts (owner_id, full_name, status) "
                "VALUES (%s, %s, 'CONVERTED') RETURNING id",
                (owner_id, "Contact Partner Test"),
            )
            contact_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO partners (owner_id, contact_id, status) "
                "VALUES (%s, %s, 'ACTIVATED') RETURNING id",
                (owner_id, contact_id),
            )
            return str(cur.fetchone()[0])


# ------------------------------------------------------------------
# 1. owner corect
# ------------------------------------------------------------------

def test_diagnostic_correct_owner_success(client):
    owner_id = _create_user("diag-owner-ok")
    partner_id = _create_partner(owner_id)

    response = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"owner_id": owner_id, "diagnostic_type": "ENCOURAGEMENT"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["diagnostic_type"] == "ENCOURAGEMENT"
    assert "[STUB]" in body["message"]


# ------------------------------------------------------------------
# 2. owner greșit -> refuz
# ------------------------------------------------------------------

def test_diagnostic_wrong_owner_returns_403(client):
    """
    Testul decisiv cerut explicit: Lider B incearca diagnostic pe
    partenerul lui Lider A, prin HTTP real, pe PostgreSQL real —
    exact bug-ul #4 gasit azi (impersonare partiala), verificat acum
    si la nivel HTTP, nu doar Engine direct.
    """
    owner_a = _create_user("diag-owner-a")
    owner_b = _create_user("diag-owner-b")
    partner_id = _create_partner(owner_a)

    response = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"owner_id": owner_b, "diagnostic_type": "CLARITY"},
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"


def test_send_wrong_owner_returns_403(client):
    """Aceeasi verificare, dar pe endpoint-ul /send."""
    owner_a = _create_user("send-owner-a")
    owner_b = _create_user("send-owner-b")
    partner_id = _create_partner(owner_a)

    response = client.post(
        f"/api/v1/partners/{partner_id}/send",
        json={"owner_id": owner_b, "confirmed": True},
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"


# ------------------------------------------------------------------
# 3. partner_id inexistent
# ------------------------------------------------------------------

def test_diagnostic_nonexistent_partner_returns_403(client):
    """
    partner_id inexistent -> 403 (nu 404) — acelasi mesaj ca 'nu-i al
    tau', previne enumerarea de ID-uri (verificat in cod, PartnerAccessDeniedError).
    """
    owner_id = _create_user("diag-nonexistent")
    fake_partner_id = str(uuid4())

    response = client.post(
        f"/api/v1/partners/{fake_partner_id}/diagnostic",
        json={"owner_id": owner_id, "diagnostic_type": "NEXT_STEP"},
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"


# ------------------------------------------------------------------
# 4. UUID invalid -> 422
# ------------------------------------------------------------------

class TestInvalidPartnerIdReturns422:

    INVALID_ID = "nu-e-un-uuid-valid"

    def test_diagnostic_invalid_id_returns_422(self, client):
        owner_id = _create_user("invalid-diag")
        response = client.post(
            f"/api/v1/partners/{self.INVALID_ID}/diagnostic",
            json={"owner_id": owner_id, "diagnostic_type": "ENCOURAGEMENT"},
        )
        assert response.status_code == 422

    def test_send_invalid_id_returns_422(self, client):
        owner_id = _create_user("invalid-send")
        response = client.post(
            f"/api/v1/partners/{self.INVALID_ID}/send",
            json={"owner_id": owner_id, "confirmed": True},
        )
        assert response.status_code == 422


# ------------------------------------------------------------------
# 5. flux complet + 6. raspunsul contine scorurile actualizate
# ------------------------------------------------------------------

def test_full_http_flow_diagnostic_to_send_returns_scores(client):
    """
    Flux complet: diagnostic -> send -> raspunsul /send contine PDI+PIP
    actualizate -> GET /scores confirma aceleasi valori separat.
    """
    owner_id = _create_user("full-flow-partner")
    partner_id = _create_partner(owner_id)

    r1 = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"owner_id": owner_id, "diagnostic_type": "APPRECIATION"},
    )
    assert r1.status_code == 201

    r2 = client.post(
        f"/api/v1/partners/{partner_id}/send",
        json={"owner_id": owner_id, "confirmed": True},
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body["pdi"] == 1.0
    assert body["pip"] == 1.0

    r3 = client.get("/api/v1/partners/scores", params={"owner_id": owner_id})
    assert r3.status_code == 200
    assert r3.json()["pdi"] == 1.0
    assert r3.json()["pip"] == 1.0


def test_send_without_confirmation_returns_400(client):
    owner_id = _create_user("send-noconfirm")
    partner_id = _create_partner(owner_id)
    client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"owner_id": owner_id, "diagnostic_type": "NEXT_STEP"},
    )

    response = client.post(
        f"/api/v1/partners/{partner_id}/send",
        json={"owner_id": owner_id, "confirmed": False},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "CONFIRMATION_REQUIRED"


def test_second_diagnostic_same_day_returns_409(client):
    owner_id = _create_user("diag-duplicate")
    partner_id = _create_partner(owner_id)
    client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"owner_id": owner_id, "diagnostic_type": "ENCOURAGEMENT"},
    )

    response = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"owner_id": owner_id, "diagnostic_type": "CLARITY"},
    )
    assert response.status_code == 409
    assert response.json()["error_code"] == "ALREADY_EXISTS"
