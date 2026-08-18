"""
Teste RED pentru POST /api/v1/partners — integrare HTTP completa, Auth reala.

Sursa: 32-partner-create-contract.md.
"""

import os
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


@pytest.fixture(autouse=True)
def reset_login_rate_limiter():
    from src.auth.rate_limit import login_rate_limiter
    login_rate_limiter.reset()
    yield
    login_rate_limiter.reset()


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


def _create_contact(client, session, full_name="Contact Test"):
    r = client.post("/api/v1/contacts", json={"full_name": full_name}, headers=session["headers"])
    assert r.status_code == 201, r.text
    return r.json()["id"]


# ----------------------------------------------------------------------
# Flux fericit
# ----------------------------------------------------------------------


def test_post_partners_valid_returneaza_201(client):
    session = _register_and_login(client, "partners-ok")
    contact_id = _create_contact(client, session)

    r = client.post(
        "/api/v1/partners", json={"contact_id": contact_id}, headers=session["headers"],
    )

    assert r.status_code == 201
    body = r.json()
    assert body["owner_id"] == session["owner_id"]
    assert body["contact_id"] == contact_id
    assert body["status"] == "ACTIVATED"
    assert body["partner_level"] == "BRONZE"


def test_post_partners_fara_contact_id_returneaza_422(client):
    session = _register_and_login(client, "partners-nocid")

    r = client.post("/api/v1/partners", json={}, headers=session["headers"])

    assert r.status_code == 422


def test_post_partners_fara_auth_returneaza_401(client):
    r = client.post("/api/v1/partners", json={"contact_id": str(uuid4())})
    assert r.status_code == 401


def test_post_partners_status_nu_poate_fi_controlat_de_client(client):
    session = _register_and_login(client, "partners-status")
    contact_id = _create_contact(client, session)

    r = client.post(
        "/api/v1/partners",
        json={"contact_id": contact_id, "status": "ACTIVE"},  # incercare ilegitima
        headers=session["headers"],
    )

    assert r.status_code == 201
    assert r.json()["status"] == "ACTIVATED"  # NU ACTIVE


def test_post_partners_partner_level_nu_poate_fi_controlat_de_client(client):
    session = _register_and_login(client, "partners-level")
    contact_id = _create_contact(client, session)

    r = client.post(
        "/api/v1/partners",
        json={"contact_id": contact_id, "partner_level": "GOLD"},  # incercare ilegitima
        headers=session["headers"],
    )

    assert r.status_code == 201
    assert r.json()["partner_level"] == "BRONZE"  # NU GOLD


def test_partner_created_scris_in_events_fara_pdi_pip(client):
    session = _register_and_login(client, "partners-event")
    contact_id = _create_contact(client, session)

    from src.data.db import get_connection

    r = client.post(
        "/api/v1/partners", json={"contact_id": contact_id}, headers=session["headers"],
    )
    partner_id = r.json()["id"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT event_name FROM events WHERE target_object_id = %s AND target_object = 'partner'",
                (partner_id,),
            )
            assert cur.fetchone() == ("PartnerCreated",)

            cur.execute("SELECT COUNT(*) FROM scores WHERE entity_id = %s", (partner_id,))
            assert cur.fetchone()[0] == 0  # PDI/PIP NU apar la creare


# ----------------------------------------------------------------------
# TEST 1 — ownership la creare (cerut explicit)
# ----------------------------------------------------------------------


def test_leader_b_nu_poate_crea_partner_din_contact_lui_a(client):
    """
    Leader A creeaza Contact A. Leader B incearca POST /partners cu
    contact_id-ul lui A -> 403 ACCESS_DENIED, verificat ca NU exista
    rand nou in partners.
    """
    from src.data.db import get_connection

    session_a = _register_and_login(client, "partners-owner-a")
    session_b = _register_and_login(client, "partners-owner-b")
    contact_id_a = _create_contact(client, session_a, "Contact al lui A")

    r = client.post(
        "/api/v1/partners", json={"contact_id": contact_id_a}, headers=session_b["headers"],
    )

    assert r.status_code == 403
    assert r.json()["error_code"] == "ACCESS_DENIED"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM partners WHERE contact_id = %s", (contact_id_a,))
            assert cur.fetchone()[0] == 0


# ----------------------------------------------------------------------
# TEST 2 — duplicate + rollback (cerut explicit, disciplina de la Register)
# ----------------------------------------------------------------------


def test_duplicate_contact_id_409_apoi_urmatorul_partner_functioneaza(client):
    """
    Leader A -> Partner(contact X) -> 201
    Leader A -> Partner(contact X) din nou -> 409 ALREADY_EXISTS
    Leader A -> Partner(contact Y, diferit) -> 201, imediat dupa esecul de mai sus
    """
    session = _register_and_login(client, "partners-dup")
    contact_x = _create_contact(client, session, "Contact X")
    contact_y = _create_contact(client, session, "Contact Y")

    r1 = client.post(
        "/api/v1/partners", json={"contact_id": contact_x}, headers=session["headers"],
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/api/v1/partners", json={"contact_id": contact_x}, headers=session["headers"],
    )
    assert r2.status_code == 409
    assert r2.json()["error_code"] == "ALREADY_EXISTS"

    r3 = client.post(
        "/api/v1/partners", json={"contact_id": contact_y}, headers=session["headers"],
    )
    assert r3.status_code == 201


# ----------------------------------------------------------------------
# Flux complet
# ----------------------------------------------------------------------


def test_flux_complet_register_login_contact_partner(client):
    session = _register_and_login(client, "partners-flow")
    contact_id = _create_contact(client, session, "Flux Complet")

    r = client.post(
        "/api/v1/partners", json={"contact_id": contact_id}, headers=session["headers"],
    )

    assert r.status_code == 201
    assert r.json()["owner_id"] == session["owner_id"]
    assert r.json()["contact_id"] == contact_id
    assert r.json()["status"] == "ACTIVATED"
