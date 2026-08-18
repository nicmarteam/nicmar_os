"""
Teste RED pentru POST /api/v1/contacts — integrare HTTP completa, Auth reala.

Sursa: 31-contact-create-contract.md.
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


def test_post_contacts_valid_returneaza_201(client):
    session = _register_and_login(client, "contacts-ok")

    r = client.post(
        "/api/v1/contacts", json={"full_name": "Ion Popescu"}, headers=session["headers"],
    )

    assert r.status_code == 201
    body = r.json()
    assert body["owner_id"] == session["owner_id"]
    assert body["full_name"] == "Ion Popescu"
    assert body["status"] == "NEW"


def test_post_contacts_cu_toate_campurile_optionale(client):
    session = _register_and_login(client, "contacts-full")

    r = client.post(
        "/api/v1/contacts",
        json={
            "full_name": "Maria Ionescu", "phone": "0722000000", "email": "maria@test.ro",
            "source": "facebook", "metadata": {"nota": "prieten"},
        },
        headers=session["headers"],
    )

    assert r.status_code == 201
    body = r.json()
    assert body["phone"] == "0722000000"
    assert body["email"] == "maria@test.ro"
    assert body["source"] == "facebook"
    assert body["metadata"] == {"nota": "prieten"}


def test_post_contacts_fara_full_name_returneaza_422(client):
    session = _register_and_login(client, "contacts-nofn")

    r = client.post("/api/v1/contacts", json={}, headers=session["headers"])

    assert r.status_code == 422


def test_post_contacts_fara_auth_returneaza_401(client):
    r = client.post("/api/v1/contacts", json={"full_name": "Test"})
    assert r.status_code == 401


def test_post_contacts_owner_id_nu_poate_fi_controlat_de_client(client):
    """
    Chiar daca clientul trimite owner_id in payload, contactul creat
    apartine liderului autentificat (din JWT), niciodata valorii din body —
    RegisterRequest/ContactRequest nu au campul, deci Pydantic il ignora
    ca extra field (comportament implicit, neschimbat).
    """
    session_a = _register_and_login(client, "contacts-owner-a")
    session_b = _register_and_login(client, "contacts-owner-b")

    r = client.post(
        "/api/v1/contacts",
        json={"full_name": "Test", "owner_id": session_b["owner_id"]},  # incercare ilegitima
        headers=session_a["headers"],
    )

    assert r.status_code == 201
    assert r.json()["owner_id"] == session_a["owner_id"]  # NU session_b


def test_post_contacts_status_nu_poate_fi_controlat_de_client(client):
    session = _register_and_login(client, "contacts-status")

    r = client.post(
        "/api/v1/contacts",
        json={"full_name": "Test", "status": "CONVERTED"},  # incercare ilegitima
        headers=session["headers"],
    )

    assert r.status_code == 201
    assert r.json()["status"] == "NEW"  # NU CONVERTED


# ----------------------------------------------------------------------
# Integrare cu flux existent — ConversationEngine, ownership real
# (cerut explicit ca parte a criteriului de acceptare)
# ----------------------------------------------------------------------


def test_contact_creat_prin_api_functioneaza_cu_conversation_engine(client):
    """
    Contact creat prin fluxul real (POST /contacts, nu fixture SQL) e
    folosit cu succes de ConversationEngine.get_or_create_conversation()
    (Decizia 29) — confirma integrarea end-to-end.
    """
    from src.engines.conversation.conversation_engine import ConversationEngine
    from uuid import UUID

    session = _register_and_login(client, "contacts-integ-a")

    r = client.post(
        "/api/v1/contacts", json={"full_name": "Contact Integrare"}, headers=session["headers"],
    )
    contact_id = UUID(r.json()["id"])
    owner_id = UUID(session["owner_id"])

    conv_engine = ConversationEngine()
    conversation = conv_engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

    assert conversation.contact_id == contact_id
    assert conversation.owner_id == owner_id


def test_contact_creat_de_a_nu_e_accesibil_de_b_prin_conversation_engine(client):
    """
    Contact creat de liderul A, prin fluxul real HTTP — liderul B
    incearca get_or_create_conversation() pe el -> ConversationAccessDeniedError,
    mecanism deja existent (Decizia 29), verificat aici cu date organice,
    nu fixture SQL.
    """
    from src.engines.conversation.conversation_engine import (
        ConversationEngine, ConversationAccessDeniedError,
    )
    from uuid import UUID

    session_a = _register_and_login(client, "contacts-integ-owner-a")
    session_b = _register_and_login(client, "contacts-integ-owner-b")

    r = client.post(
        "/api/v1/contacts", json={"full_name": "Contact al lui A"}, headers=session_a["headers"],
    )
    contact_id_a = UUID(r.json()["id"])
    owner_id_b = UUID(session_b["owner_id"])

    conv_engine = ConversationEngine()

    with pytest.raises(ConversationAccessDeniedError):
        conv_engine.get_or_create_conversation(owner_id=owner_id_b, contact_id=contact_id_a)
