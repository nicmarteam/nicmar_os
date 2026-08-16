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
