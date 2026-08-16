"""
Teste Partner API + integrare Auth.

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


def test_diagnostic_correct_owner_success(client):
    owner_id, email, password = _create_user("diag-owner-ok")
    headers = _headers(client, email, password)
    partner_id = _create_partner(owner_id)

    response = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"diagnostic_type": "ENCOURAGEMENT"}, headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["diagnostic_type"] == "ENCOURAGEMENT"
    assert body["owner_id"] == owner_id
    assert "[STUB]" in body["message"]


def test_diagnostic_owner_id_body_is_ignored(client):
    owner_id, email, password = _create_user("diag-owner-a")
    other_id, _, _ = _create_user("diag-owner-b")
    headers = _headers(client, email, password)
    partner_id = _create_partner(owner_id)

    response = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"owner_id": other_id, "diagnostic_type": "CLARITY"}, headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["owner_id"] == owner_id


def test_diagnostic_wrong_jwt_owner_returns_403(client):
    owner_a, _, _ = _create_user("diag-jwt-owner-a")
    _, email_b, password_b = _create_user("diag-jwt-owner-b")
    headers_b = _headers(client, email_b, password_b)
    partner_id = _create_partner(owner_a)

    response = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"owner_id": owner_a, "diagnostic_type": "CLARITY"}, headers=headers_b,
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"


def test_send_wrong_jwt_owner_returns_403(client):
    owner_a, email_a, password_a = _create_user("send-owner-a")
    _, email_b, password_b = _create_user("send-owner-b")
    headers_a = _headers(client, email_a, password_a)
    headers_b = _headers(client, email_b, password_b)
    partner_id = _create_partner(owner_a)

    diagnostic = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"diagnostic_type": "ENCOURAGEMENT"}, headers=headers_a,
    )
    assert diagnostic.status_code == 201

    response = client.post(
        f"/api/v1/partners/{partner_id}/send",
        json={"owner_id": owner_a, "confirmed": True}, headers=headers_b,
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"


def test_diagnostic_nonexistent_partner_returns_403(client):
    _, email, password = _create_user("diag-nonexistent")
    headers = _headers(client, email, password)

    response = client.post(
        f"/api/v1/partners/{uuid4()}/diagnostic",
        json={"diagnostic_type": "NEXT_STEP"}, headers=headers,
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"


class TestInvalidPartnerIdReturns422:
    INVALID_ID = "nu-e-un-uuid-valid"

    def test_diagnostic_invalid_id_returns_422(self, client):
        _, email, password = _create_user("invalid-diag")
        headers = _headers(client, email, password)
        response = client.post(
            f"/api/v1/partners/{self.INVALID_ID}/diagnostic",
            json={"diagnostic_type": "ENCOURAGEMENT"}, headers=headers,
        )
        assert response.status_code == 422

    def test_send_invalid_id_returns_422(self, client):
        _, email, password = _create_user("invalid-send")
        headers = _headers(client, email, password)
        response = client.post(
            f"/api/v1/partners/{self.INVALID_ID}/send",
            json={"confirmed": True}, headers=headers,
        )
        assert response.status_code == 422


def test_full_http_flow_diagnostic_to_send_returns_scores(client):
    owner_id, email, password = _create_user("full-flow-partner")
    headers = _headers(client, email, password)
    partner_id = _create_partner(owner_id)

    r1 = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"diagnostic_type": "APPRECIATION"}, headers=headers,
    )
    assert r1.status_code == 201

    r2 = client.post(
        f"/api/v1/partners/{partner_id}/send",
        json={"confirmed": True}, headers=headers,
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body["pdi"] == 1.0
    assert body["pip"] == 1.0

    r3 = client.get(
        "/api/v1/partners/scores",
        params={"owner_id": str(uuid4())}, headers=headers,
    )
    assert r3.status_code == 200
    assert r3.json()["pdi"] == 1.0
    assert r3.json()["pip"] == 1.0


def test_send_without_confirmation_returns_400(client):
    owner_id, email, password = _create_user("send-noconfirm")
    headers = _headers(client, email, password)
    partner_id = _create_partner(owner_id)

    diagnostic = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"diagnostic_type": "NEXT_STEP"}, headers=headers,
    )
    assert diagnostic.status_code == 201

    response = client.post(
        f"/api/v1/partners/{partner_id}/send",
        json={"owner_id": str(uuid4()), "confirmed": False}, headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "CONFIRMATION_REQUIRED"


def test_second_diagnostic_same_day_returns_409(client):
    owner_id, email, password = _create_user("diag-duplicate")
    headers = _headers(client, email, password)
    partner_id = _create_partner(owner_id)

    first = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"diagnostic_type": "ENCOURAGEMENT"}, headers=headers,
    )
    assert first.status_code == 201

    response = client.post(
        f"/api/v1/partners/{partner_id}/diagnostic",
        json={"diagnostic_type": "CLARITY"}, headers=headers,
    )
    assert response.status_code == 409
    assert response.json()["error_code"] == "ALREADY_EXISTS"
