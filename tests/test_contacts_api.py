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


def _create_contact(client, session, full_name: str = "Contact Test") -> str:
    r = client.post(
        "/api/v1/contacts", json={"full_name": full_name}, headers=session["headers"],
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _create_partner(client, session, contact_id: str) -> str:
    r = client.post(
        "/api/v1/partners", json={"contact_id": contact_id}, headers=session["headers"],
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


# ----------------------------------------------------------------------
# DECIZIA 37A (RED, 19 august 2026) — GET /api/v1/contacts trebuie sa
# expuna partner_id, capat la capat prin HTTP + PostgreSQL real.
# Sursa: 37A-expose-partner-id-contract.md, sectiunea 5.
# ----------------------------------------------------------------------


def test_get_contacts_expune_partner_id_exact_pentru_contact_convertit(client):
    """
    Criteriul 1 (contract 37A), verificat prin HTTP real: dupa ce un
    contact e convertit in partener prin POST /api/v1/partners,
    GET /api/v1/contacts trebuie sa intoarca EXACT acel partner_id
    pentru contactul respectiv — nu doar un camp nenul.
    """
    session = _register_and_login(client, "contacts-partnerid")
    contact_id = _create_contact(client, session, "Contact De Convertit")
    partner_id = _create_partner(client, session, contact_id)

    r = client.get("/api/v1/contacts", headers=session["headers"])

    assert r.status_code == 200
    body = next(c for c in r.json() if c["contact_id"] == contact_id)
    assert body["converted_to"] == "partner"
    assert body["partner_id"] == partner_id


def test_get_contacts_partner_id_none_pentru_contact_neconvertit(client):
    """Criteriul 2 (contract 37A), verificat prin HTTP real."""
    session = _register_and_login(client, "contacts-nopartnerid")
    contact_id = _create_contact(client, session, "Contact Neconvertit")

    r = client.get("/api/v1/contacts", headers=session["headers"])

    assert r.status_code == 200
    body = next(c for c in r.json() if c["contact_id"] == contact_id)
    assert body["converted_to"] is None
    assert body["partner_id"] is None


def test_get_contacts_partner_id_izolat_intre_owneri(client):
    """
    Criteriul 3 (contract 37A), verificat prin HTTP real: liderul A
    converteste un contact in partener; liderul B, autentificat separat,
    nu trebuie sa vada niciodata acel partner_id (nici in propria lista,
    care nici nu contine contactul lui A — verificare explicita a
    rezultatului, nu doar increderea in filtrul owner_id din SQL).
    """
    session_a = _register_and_login(client, "contacts-partnerid-owner-a")
    session_b = _register_and_login(client, "contacts-partnerid-owner-b")

    contact_id_a = _create_contact(client, session_a, "Contact Al Lui A")
    partner_id_a = _create_partner(client, session_a, contact_id_a)

    r_b = client.get("/api/v1/contacts", headers=session_b["headers"])

    assert r_b.status_code == 200
    contact_ids_b = [c["contact_id"] for c in r_b.json()]
    partner_ids_b = [c["partner_id"] for c in r_b.json()]
    assert contact_id_a not in contact_ids_b
    assert partner_id_a not in partner_ids_b


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


# ----------------------------------------------------------------------
# DECIZIA 47 (RED, 20 august 2026) — campurile de relatie prin HTTP.
# Sursa: 47-lista-relatii-contract.md, criteriile 6-8.
# ----------------------------------------------------------------------


def test_post_contact_cu_campuri_de_relatie_returneaza_201(client):
    """Contract 47, criteriul 6."""
    session = _register_and_login(client, "contact-relatie-create")

    r = client.post(
        "/api/v1/contacts",
        json={
            "full_name": "Maria Prietena",
            "relationship_category": "PRIETENI",
            "relationship_level": "BUNA",
            "last_contact_approx": "SAPTAMANA_ACEASTA",
            "significant_context": "Ne-am vazut la o cafea.",
            "perceived_interest": "PROBABIL",
        },
        headers=session["headers"],
    )

    assert r.status_code == 201, r.text
    body = r.json()
    assert body["relationship_category"] == "PRIETENI"
    assert body["relationship_level"] == "BUNA"
    assert body["last_contact_approx"] == "SAPTAMANA_ACEASTA"
    assert body["significant_context"] == "Ne-am vazut la o cafea."
    assert body["perceived_interest"] == "PROBABIL"


def test_post_contact_categorie_invalida_returneaza_400(client):
    """Contract 47, criteriul 7 — validare la nivel de aplicatie."""
    session = _register_and_login(client, "contact-relatie-invalid")

    r = client.post(
        "/api/v1/contacts",
        json={"full_name": "X", "relationship_category": "COLEGI_DE_LICEU"},
        headers=session["headers"],
    )

    assert r.status_code == 400
    assert r.json()["error_code"] == "INVALID_VALUE"


def test_get_contacts_expune_campurile_de_relatie(client):
    """
    Contract 47, criteriul 8: campurile apar in GET /contacts, ca sa
    poata alimenta direct 46A (Prospectare Relationala) si restul
    sistemului — beneficiul principal al deciziei de a extinde Contact
    in loc sa cream Relationship.
    """
    session = _register_and_login(client, "contact-relatie-list")
    r_create = client.post(
        "/api/v1/contacts",
        json={
            "full_name": "Ana Colega",
            "relationship_category": "COLEGI",
            "relationship_level": "OCAZIONALA",
            "perceived_interest": "NU_STIU_INCA",
        },
        headers=session["headers"],
    )
    assert r_create.status_code == 201
    contact_id = r_create.json()["id"]

    r = client.get("/api/v1/contacts", headers=session["headers"])

    assert r.status_code == 200
    body = next(c for c in r.json() if c["contact_id"] == contact_id)
    assert body["relationship_category"] == "COLEGI"
    assert body["relationship_level"] == "OCAZIONALA"
    assert body["perceived_interest"] == "NU_STIU_INCA"
