"""
Teste RED pentru Decizia 33 — Conversation -> Objection linkage.

Sursa: 33-conversation-objection-linkage-contract.md.

Acopera: GET /api/v1/contacts, POST /api/v1/conversations, si fluxul
complet pozitiv/negativ cerut explicit pentru legarea unei obiectii
de o conversatie reala, cu izolare owner_id verificata la nivel de DB.
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


def _create_conversation(client, session, contact_id):
    r = client.post(
        "/api/v1/conversations", json={"contact_id": contact_id}, headers=session["headers"],
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


# ----------------------------------------------------------------------
# GET /api/v1/contacts
# ----------------------------------------------------------------------


def test_get_contacts_returneaza_contactul_creat(client):
    session = _register_and_login(client, "linkage-getcontacts")
    contact_id = _create_contact(client, session, "Ion Popescu")

    r = client.get("/api/v1/contacts", headers=session["headers"])

    assert r.status_code == 200
    ids = [c["contact_id"] for c in r.json()]
    assert contact_id in ids


def test_get_contacts_fara_auth_returneaza_401(client):
    r = client.get("/api/v1/contacts")
    assert r.status_code == 401


def test_get_contacts_izoleaza_owner_id(client):
    session_a = _register_and_login(client, "linkage-contacts-owner-a")
    session_b = _register_and_login(client, "linkage-contacts-owner-b")
    contact_id_a = _create_contact(client, session_a, "Contact al lui A")

    r_b = client.get("/api/v1/contacts", headers=session_b["headers"])

    ids_b = [c["contact_id"] for c in r_b.json()]
    assert contact_id_a not in ids_b


# ----------------------------------------------------------------------
# POST /api/v1/conversations
# ----------------------------------------------------------------------


def test_post_conversations_valid_returneaza_201(client):
    session = _register_and_login(client, "linkage-createconv")
    contact_id = _create_contact(client, session)

    r = client.post(
        "/api/v1/conversations", json={"contact_id": contact_id}, headers=session["headers"],
    )

    assert r.status_code == 201
    body = r.json()
    assert body["owner_id"] == session["owner_id"]
    assert body["contact_id"] == contact_id
    assert body["channel"] == "WHATSAPP"


def test_post_conversations_idempotent(client):
    session = _register_and_login(client, "linkage-idempotent")
    contact_id = _create_contact(client, session)

    r1 = client.post(
        "/api/v1/conversations", json={"contact_id": contact_id}, headers=session["headers"],
    )
    r2 = client.post(
        "/api/v1/conversations", json={"contact_id": contact_id}, headers=session["headers"],
    )

    assert r1.json()["id"] == r2.json()["id"]


def test_post_conversations_contact_al_altui_owner_returneaza_403(client):
    session_a = _register_and_login(client, "linkage-conv-owner-a")
    session_b = _register_and_login(client, "linkage-conv-owner-b")
    contact_id_a = _create_contact(client, session_a)

    r = client.post(
        "/api/v1/conversations", json={"contact_id": contact_id_a}, headers=session_b["headers"],
    )

    assert r.status_code == 403
    assert r.json()["error_code"] == "ACCESS_DENIED"


# ----------------------------------------------------------------------
# FLUX POZITIV — cerut explicit, verificare din DB, nu doar status code
# ----------------------------------------------------------------------


def test_flux_pozitiv_contact_conversation_objection_legate_corect(client):
    from src.data.db import get_connection

    session = _register_and_login(client, "linkage-flux-pozitiv")
    contact_id = _create_contact(client, session, "Prospect Real")
    conversation_id = _create_conversation(client, session, contact_id)

    r = client.post(
        "/api/v1/objections/prepare",
        json={
            "objection_text": "e scump", "objection_category": "PRET",
            "conversation_id": conversation_id,
        },
        headers=session["headers"],
    )
    assert r.status_code == 201
    objection_id = r.json()["objection_id"]

    # Verificare EXPLICITA din DB, nu doar 201
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT conversation_id FROM objections WHERE id = %s", (objection_id,),
            )
            row = cur.fetchone()
            assert str(row[0]) == conversation_id


# ----------------------------------------------------------------------
# FLUX NEGATIV — cerut explicit, Leader B cu conversation_id al lui A
# ----------------------------------------------------------------------


def test_flux_negativ_leader_b_cu_conversation_id_al_lui_a_returneaza_403(client):
    from src.data.db import get_connection

    session_a = _register_and_login(client, "linkage-flux-negativ-a")
    session_b = _register_and_login(client, "linkage-flux-negativ-b")

    contact_a = _create_contact(client, session_a, "Contact al lui A")
    conversation_a = _create_conversation(client, session_a, contact_a)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM objections WHERE conversation_id = %s", (conversation_a,))
            count_before = cur.fetchone()[0]

    r = client.post(
        "/api/v1/objections/prepare",
        json={
            "objection_text": "incercare ilegitima", "objection_category": "PRET",
            "conversation_id": conversation_a,
        },
        headers=session_b["headers"],
    )

    assert r.status_code == 403
    assert r.json()["error_code"] == "ACCESS_DENIED"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM objections WHERE conversation_id = %s", (conversation_a,))
            count_after = cur.fetchone()[0]

    assert count_after == count_before  # ZERO INSERT


def test_conversation_id_none_flux_neschimbat(client):
    """Regresie: conversation_id=None continua sa functioneze identic."""
    session = _register_and_login(client, "linkage-none-regression")

    r = client.post(
        "/api/v1/objections/prepare",
        json={"objection_text": "nu am timp", "objection_category": "TIMP"},
        headers=session["headers"],
    )

    assert r.status_code == 201
