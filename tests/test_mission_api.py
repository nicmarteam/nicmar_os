"""
Teste pentru Mission API — integrat complet cu Auth (12 august 2026).

Fiecare test creează un utilizator CU parolă, face login real prin
/auth/login, și trimite token-ul ca Authorization: Bearer. owner_id
NU mai apare în niciun payload — identitatea vine exclusiv din JWT.
"""

import os
from uuid import uuid4

import bcrypt
import pytest
from fastapi.testclient import TestClient

from src.data.db import get_connection

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-doar-pentru-teste-minim-32-bytes-lungime")

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


def _create_authenticated_user(client, prefix: str, password: str = "parola_test_123") -> tuple:
    """Creează un utilizator cu parolă, face login, returnează (user_id, auth_headers)."""
    email = f"{prefix}-{uuid4()}@nicmar.local"
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, full_name, role, password_hash) "
                "VALUES (%s, %s, 'LEADER', %s) RETURNING id",
                (email, f"Test {prefix}", password_hash),
            )
            user_id = str(cur.fetchone()[0])

    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200, f"Login esuat pentru {email}: {login_resp.json()}"
    token = login_resp.json()["access_token"]

    return user_id, {"Authorization": f"Bearer {token}"}


# ------------------------------------------------------------------
# Flux HTTP complet, autentificat
# ------------------------------------------------------------------

def test_full_authenticated_flow(client):
    """create -> assign -> present -> start -> complete -> DIS, toate autentificate."""
    owner_id, headers = _create_authenticated_user(client, "full-flow")

    r1 = client.post("/api/v1/missions", json={"title": "Sună clientul"}, headers=headers)
    assert r1.status_code == 201
    mission_id = r1.json()["id"]
    assert r1.json()["owner_id"] == owner_id

    r2 = client.post(f"/api/v1/missions/{mission_id}/assign", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "ASSIGNED"

    r3 = client.get(f"/api/v1/missions/{mission_id}/present", headers=headers)
    assert r3.status_code == 200
    assert "Sună clientul" in r3.json()["text"]

    r4 = client.post(
        f"/api/v1/missions/{mission_id}/start", json={"confirmed": True}, headers=headers
    )
    assert r4.status_code == 200
    assert r4.json()["status"] == "IN_PROGRESS"

    r5 = client.post(f"/api/v1/missions/{mission_id}/complete", headers=headers)
    assert r5.status_code == 200
    assert r5.json()["status"] == "COMPLETED"

    r6 = client.get("/api/v1/missions/dis-score", headers=headers)
    assert r6.status_code == 200
    assert r6.json()["dis_score"] == 1.0


# ------------------------------------------------------------------
# Fără autentificare -> 401, pe toate endpoint-urile
# ------------------------------------------------------------------

class TestNoAuthReturns401:

    def test_create_without_auth_returns_401(self, client):
        response = client.post("/api/v1/missions", json={"title": "Test"})
        assert response.status_code == 401

    def test_dis_score_without_auth_returns_401(self, client):
        response = client.get("/api/v1/missions/dis-score")
        assert response.status_code == 401


# ------------------------------------------------------------------
# TESTUL DE ATAC — cerut explicit
# ------------------------------------------------------------------

def test_attack_forged_owner_id_in_body_is_ignored(client):
    """
    Testul decisiv: User A autentificat, încearcă să opereze pe
    misiunea lui B, trimițând owner_id=B manual — dar API-ul NU MAI
    ACCEPTĂ owner_id în body deloc (eliminat din schema), deci
    atacul e imposibil de format, nu doar respins.

    Verificăm 2 lucruri separat:
    1. Chiar dacă am forța owner_id în JSON, Pydantic îl ignoră
       (nu mai există câmpul în schemă).
    2. Misiunea creată aparține STRICT lui A (din JWT), niciodată
       valorii trimise suplimentar.
    """
    owner_a, headers_a = _create_authenticated_user(client, "attack-a")
    owner_b, headers_b = _create_authenticated_user(client, "attack-b")

    # Body contine owner_id=B, desi request-ul e autentificat ca A.
    # Schema CreateMissionRequest nu mai are camp owner_id -> Pydantic
    # il ignora silentios (extra field, nu produce eroare, dar nici
    # nu e folosit).
    response = client.post(
        "/api/v1/missions",
        json={"title": "Incercare de atac", "owner_id": owner_b},
        headers=headers_a,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["owner_id"] == owner_a, (
        f"ATAC REUSIT: misiunea a fost creata pentru {body['owner_id']}, "
        f"desi userul autentificat era {owner_a}!"
    )
    assert body["owner_id"] != owner_b


def test_attack_user_b_cannot_access_user_a_data(client):
    """
    Inversul testului de mai sus: User B autentificat (JWT valid,
    al lui B), incearca sa acceseze o misiune a lui A -> 403, verificat
    de Engine (MissionAccessDeniedError), nu doar de router.
    """
    owner_a, headers_a = _create_authenticated_user(client, "cross-a")
    owner_b, headers_b = _create_authenticated_user(client, "cross-b")

    create_resp = client.post(
        "/api/v1/missions", json={"title": "Misiune privata A"}, headers=headers_a
    )
    mission_id = create_resp.json()["id"]

    # B (autentificat cu propriul JWT valid) incearca sa asigneze misiunea lui A
    response = client.post(f"/api/v1/missions/{mission_id}/assign", headers=headers_b)
    assert response.status_code == 403
    assert response.json()["error_code"] == "ACCESS_DENIED"
