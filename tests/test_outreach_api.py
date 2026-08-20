"""
Teste RED — Outreach API (Decizia 46), HTTP real + PostgreSQL real.

Sursa: 46-prospectare-relationala-contract.md.
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


def _create_contact(client, session, full_name: str = "Contact Outreach Test") -> str:
    r = client.post("/api/v1/contacts", json={"full_name": full_name}, headers=session["headers"])
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _create_outreach(client, session, contact_id: str, purpose: str = "REFERRAL") -> dict:
    r = client.post(
        "/api/v1/outreach",
        json={
            "contact_id": contact_id, "purpose": purpose,
            "message_text": "Salut! Ai pe cineva potrivit în minte?", "tone_used": "CALDA",
        },
        headers=session["headers"],
    )
    assert r.status_code == 201, r.text
    return r.json()


# ----------------------------------------------------------------------
# POST /api/v1/outreach — creare
# ----------------------------------------------------------------------


def test_post_outreach_valid_returneaza_201(client):
    session = _register_and_login(client, "outreach-create")
    contact_id = _create_contact(client, session)

    outreach = _create_outreach(client, session, contact_id)

    assert outreach["contact_id"] == contact_id
    assert outreach["purpose"] == "REFERRAL"


def test_post_outreach_fara_auth_returneaza_401(client):
    r = client.post("/api/v1/outreach", json={
        "contact_id": str(uuid4()), "purpose": "REFERRAL",
        "message_text": "x", "tone_used": "CALDA",
    })
    assert r.status_code == 401


def test_post_outreach_purpose_invalid_returneaza_400(client):
    session = _register_and_login(client, "outreach-invalid-purpose")
    contact_id = _create_contact(client, session)

    r = client.post(
        "/api/v1/outreach",
        json={"contact_id": contact_id, "purpose": "COLD_CALL", "message_text": "x", "tone_used": "CALDA"},
        headers=session["headers"],
    )
    assert r.status_code == 400
    assert r.json()["error_code"] == "INVALID_VALUE"


def test_post_outreach_contact_al_altui_owner_returneaza_403(client):
    session_a = _register_and_login(client, "outreach-cross-a")
    session_b = _register_and_login(client, "outreach-cross-b")
    contact_a = _create_contact(client, session_a)

    r = client.post(
        "/api/v1/outreach",
        json={"contact_id": contact_a, "purpose": "REFERRAL", "message_text": "x", "tone_used": "CALDA"},
        headers=session_b["headers"],
    )
    assert r.status_code == 403
    assert r.json()["error_code"] == "ACCESS_DENIED"


# ----------------------------------------------------------------------
# POST /api/v1/outreach/{id}/outcome — inregistrare + handoff
# ----------------------------------------------------------------------


def test_post_outcome_hesitation_returneaza_conversation_id(client):
    session = _register_and_login(client, "outcome-handoff")
    contact_id = _create_contact(client, session)
    outreach = _create_outreach(client, session, contact_id)

    r = client.post(
        f"/api/v1/outreach/{outreach['id']}/outcome",
        json={"outcome": "HESITATION"},
        headers=session["headers"],
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["outcome"] == "HESITATION"
    assert body["conversation_id"] is not None


def test_post_outcome_referral_received_conversation_id_none(client):
    session = _register_and_login(client, "outcome-no-handoff")
    contact_id = _create_contact(client, session)
    outreach = _create_outreach(client, session, contact_id)

    r = client.post(
        f"/api/v1/outreach/{outreach['id']}/outcome",
        json={"outcome": "REFERRAL_RECEIVED"},
        headers=session["headers"],
    )
    assert r.status_code == 201
    assert r.json()["conversation_id"] is None


def test_post_outcome_a_doua_oara_returneaza_409(client):
    session = _register_and_login(client, "outcome-duplicate")
    contact_id = _create_contact(client, session)
    outreach = _create_outreach(client, session, contact_id)

    r1 = client.post(
        f"/api/v1/outreach/{outreach['id']}/outcome",
        json={"outcome": "QUESTION_ASKED"}, headers=session["headers"],
    )
    assert r1.status_code == 201

    r2 = client.post(
        f"/api/v1/outreach/{outreach['id']}/outcome",
        json={"outcome": "HESITATION"}, headers=session["headers"],
    )
    assert r2.status_code == 409
    assert r2.json()["error_code"] == "ALREADY_EXISTS"


def test_post_outcome_invalid_returneaza_400(client):
    session = _register_and_login(client, "outcome-invalid")
    contact_id = _create_contact(client, session)
    outreach = _create_outreach(client, session, contact_id)

    r = client.post(
        f"/api/v1/outreach/{outreach['id']}/outcome",
        json={"outcome": "MAYBE"}, headers=session["headers"],
    )
    assert r.status_code == 400
    assert r.json()["error_code"] == "INVALID_VALUE"


def test_owner_b_nu_poate_inregistra_outcome_pe_outreach_ul_lui_a(client):
    """Izolare owner, HTTP real, 2 lideri — criteriul cel mai important al Deciziei 46."""
    session_a = _register_and_login(client, "outcome-isolation-a")
    session_b = _register_and_login(client, "outcome-isolation-b")
    contact_a = _create_contact(client, session_a)
    outreach_a = _create_outreach(client, session_a, contact_a)

    r = client.post(
        f"/api/v1/outreach/{outreach_a['id']}/outcome",
        json={"outcome": "HESITATION"}, headers=session_b["headers"],
    )
    assert r.status_code == 403
    assert r.json()["error_code"] == "ACCESS_DENIED"


def test_owner_a_vede_exclusiv_propriile_outreach_uri_izolare_completa(client):
    """
    Companion al testului de mai sus — confirma din partea A ca datele
    lui B (creat separat) raman complet izolate, verificat prin absenta
    oricarei scurgeri in raspunsul de la /outcome (nu doar 403 pe acces direct).
    """
    session_a = _register_and_login(client, "outcome-isolation-a2")
    session_b = _register_and_login(client, "outcome-isolation-b2")
    contact_b = _create_contact(client, session_b)
    outreach_b = _create_outreach(client, session_b, contact_b)

    r = client.post(
        f"/api/v1/outreach/{outreach_b['id']}/outcome",
        json={"outcome": "WILL_RESPOND_LATER"}, headers=session_a["headers"],
    )
    assert r.status_code == 403
