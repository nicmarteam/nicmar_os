"""
Teste RED pentru routerul Objections API — integrat cu Auth real.

Sursa: 26-objections-router-contract.md.

Fiecare test creeaza un utilizator CU parola, face login real prin
/api/v1/auth/login, si trimite token-ul ca Authorization: Bearer.
owner_id NU apare in niciun payload — identitatea vine exclusiv din JWT
(identic pattern cu test_mission_api.py).
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
    assert login_resp.status_code == 200, f"Login eșuat pentru {email}: {login_resp.json()}"
    token = login_resp.json()["access_token"]

    return user_id, {"Authorization": f"Bearer {token}"}


# ------------------------------------------------------------------
# Flux HTTP complet, autentificat
# ------------------------------------------------------------------


def test_flux_complet_analyze_prepare_confirm_autentificat(client):
    """analyze -> prepare -> confirm, PASS, capat la capat, prin HTTP real."""
    owner_id, headers = _create_authenticated_user(client, "objections-flow")

    r1 = client.post(
        "/api/v1/objections/analyze", json={"objection_text": "Nu am timp."}, headers=headers,
    )
    assert r1.status_code == 200
    assert r1.json()["detected_category"] == "TIMP"
    assert r1.json()["needs_manual_selection"] is False

    r2 = client.post(
        "/api/v1/objections/prepare",
        json={"objection_text": "Nu am timp.", "objection_category": "TIMP"},
        headers=headers,
    )
    assert r2.status_code == 201
    objection_id = r2.json()["objection_id"]
    assert set(r2.json()["variants"].keys()) == {"CALDA", "DIRECTA", "INTREBARE"}

    r3 = client.post(
        "/api/v1/objections/confirm",
        json={
            "objection_id": objection_id,
            "response_text": r2.json()["variants"]["DIRECTA"],
            "response_variant_used": "DIRECTA",
        },
        headers=headers,
    )
    assert r3.status_code == 200
    assert r3.json()["persisted"] is True
    assert r3.json()["validation_level"] == "PASS"
    assert r3.json()["reason"] is None


def test_categories_returneaza_cele_13(client):
    _, headers = _create_authenticated_user(client, "objections-categories")

    r = client.get("/api/v1/objections/categories", headers=headers)

    assert r.status_code == 200
    assert len(r.json()["categories"]) == 13
    assert r.json()["categories"] == sorted(r.json()["categories"])


# ------------------------------------------------------------------
# BLOCK — 200, nu eroare HTTP
# ------------------------------------------------------------------


def test_confirm_block_returneaza_200_cu_persisted_false(client):
    """BLOCK e rezultat normal de business — 200, nu eroare HTTP."""
    owner_id, headers = _create_authenticated_user(client, "objections-block")

    r_prepare = client.post(
        "/api/v1/objections/prepare",
        json={"objection_text": "e scump", "objection_category": "PRET"},
        headers=headers,
    )
    objection_id = r_prepare.json()["objection_id"]

    r_confirm = client.post(
        "/api/v1/objections/confirm",
        json={
            "objection_id": objection_id,
            "response_text": "Îți garantez că vei câștiga bani.",
            "response_variant_used": "CALDA",
        },
        headers=headers,
    )

    assert r_confirm.status_code == 200
    assert r_confirm.json()["persisted"] is False
    assert r_confirm.json()["validation_level"] == "BLOCK"
    assert r_confirm.json()["reason"] is not None


# ------------------------------------------------------------------
# Securitate — verificarea-cheie a Deciziei 8A la granita API
# ------------------------------------------------------------------


def test_user_b_nu_poate_confirma_obiectia_lui_user_a_prin_http(client):
    """
    User A creeaza o obiectie prin /prepare. User B (JWT diferit) cunoaste
    objection_id-ul lui A si incearca /confirm — trebuie respins cu
    403 ACCESS_DENIED, NU 200, indiferent ca cunoaste id-ul real.
    """
    owner_a, headers_a = _create_authenticated_user(client, "objections-owner-a")
    owner_b, headers_b = _create_authenticated_user(client, "objections-owner-b")

    r_prepare = client.post(
        "/api/v1/objections/prepare",
        json={"objection_text": "nu am timp", "objection_category": "TIMP"},
        headers=headers_a,
    )
    objection_id = r_prepare.json()["objection_id"]

    r_confirm = client.post(
        "/api/v1/objections/confirm",
        json={
            "objection_id": objection_id,
            "response_text": "Înțeleg, poți începe cu 10 minute pe zi.",
            "response_variant_used": "DIRECTA",
        },
        headers=headers_b,
    )

    assert r_confirm.status_code == 403
    assert r_confirm.json()["error_code"] == "ACCESS_DENIED"

    # Confirmare suplimentara: nimic nu s-a scris in DB pentru raspunsul lui B
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT response_text FROM objections WHERE id = %s", (objection_id,),
            )
            assert cur.fetchone()[0] is None


def test_confirm_objection_id_inexistent_returneaza_403_nu_404(client):
    """
    objection_id complet inexistent -> 403 ACCESS_DENIED, identic cu
    cazul owner gresit — previne enumerarea (nu dezvaluie daca id-ul
    exista pentru alt owner sau nu exista deloc).
    """
    _, headers = _create_authenticated_user(client, "objections-inexistent")

    r = client.post(
        "/api/v1/objections/confirm",
        json={
            "objection_id": str(uuid4()),
            "response_text": "text",
            "response_variant_used": "CALDA",
        },
        headers=headers,
    )

    assert r.status_code == 403
    assert r.json()["error_code"] == "ACCESS_DENIED"


def test_fara_authorization_header_returneaza_401(client):
    """Toate cele 4 endpoint-uri necesita autentificare — verificat pe unul, comportament comun."""
    r = client.post("/api/v1/objections/analyze", json={"objection_text": "text"})
    assert r.status_code == 401


# ------------------------------------------------------------------
# Erori de input — Decizia 26A, 26B
# ------------------------------------------------------------------


def test_prepare_categorie_invalida_returneaza_400_invalid_category(client):
    """Decizia 26A: ValueError (categorie invalida) -> 400 INVALID_CATEGORY."""
    _, headers = _create_authenticated_user(client, "objections-bad-category")

    r = client.post(
        "/api/v1/objections/prepare",
        json={"objection_text": "text oarecare", "objection_category": "CATEGORIE_INEXISTENTA"},
        headers=headers,
    )

    assert r.status_code == 400
    assert r.json()["error_code"] == "INVALID_CATEGORY"


def test_prepare_conversation_id_inexistent_returneaza_403_access_denied(client):
    """
    ACTUALIZAT la Decizia 33 (33-conversation-objection-linkage-contract.md):
    inainte, conversation_id inexistent trecea direct la create_objection()
    si esua cu ForeignKeyViolation -> 400 INVALID_REFERENCE (Decizia 26B).
    Acum, ConversationAgent verifica ownership-ul PRIN
    ConversationEngine.get_conversation() INAINTE de create_objection() —
    un conversation_id inexistent e prins mai devreme, ca "nu exista sau
    nu apartine acestui owner" -> 403 ACCESS_DENIED, consecvent cu
    principiul anti-enumerare folosit peste tot in proiect (nu se mai
    distinge "nu exista" de "apartine altcuiva").
    """
    _, headers = _create_authenticated_user(client, "objections-bad-conversation")

    r = client.post(
        "/api/v1/objections/prepare",
        json={
            "objection_text": "e scump", "objection_category": "PRET",
            "conversation_id": str(uuid4()),
        },
        headers=headers,
    )

    assert r.status_code == 403
    assert r.json()["error_code"] == "ACCESS_DENIED"
