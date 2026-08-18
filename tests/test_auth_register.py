"""
Teste RED pentru POST /api/v1/auth/register — Auth Registration v1.

Sursa: 30-auth-register-contract.md.

Sarite (skip) daca DATABASE_URL nu e setat, la fel ca test_auth.py.
"""

import os
from uuid import uuid4

import bcrypt
import pytest
from pydantic import ValidationError

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


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid4()}@nicmar.local"


# ----------------------------------------------------------------------
# RegisterRequest — validator Pydantic pentru parolă (fara DB, fara HTTP)
# ----------------------------------------------------------------------


def test_register_request_respinge_parola_prea_scurta():
    from src.api.schemas import RegisterRequest

    with pytest.raises(ValidationError):
        RegisterRequest(email="a@b.com", password="1234567", full_name="Test")  # 7 caractere


def test_register_request_accepta_parola_de_exact_8_caractere():
    from src.api.schemas import RegisterRequest

    req = RegisterRequest(email="a@b.com", password="12345678", full_name="Test")
    assert req.password == "12345678"


def test_register_request_respinge_parola_peste_72_bytes():
    from src.api.schemas import RegisterRequest

    with pytest.raises(ValidationError):
        RegisterRequest(email="a@b.com", password="a" * 73, full_name="Test")


def test_register_request_accepta_parola_de_exact_72_bytes():
    from src.api.schemas import RegisterRequest

    req = RegisterRequest(email="a@b.com", password="a" * 72, full_name="Test")
    assert len(req.password.encode("utf-8")) == 72


def test_register_request_verifica_bytes_nu_caractere_pentru_multibyte():
    """
    Caractere multi-byte (ex. diacritice) trebuie numărate în bytes UTF-8,
    nu în caractere Python — 40 de 'ă' (2 bytes fiecare) = 80 bytes, peste limita.
    """
    from src.api.schemas import RegisterRequest

    parola_40_caractere_diacritice = "ă" * 40  # 40 caractere, dar 80 bytes UTF-8
    assert len(parola_40_caractere_diacritice) == 40  # confirmare: sub limita de caractere
    with pytest.raises(ValidationError):
        RegisterRequest(email="a@b.com", password=parola_40_caractere_diacritice, full_name="Test")


# ----------------------------------------------------------------------
# register_user() — direct, cu DB reala
# ----------------------------------------------------------------------


def test_register_user_creeaza_randul_in_db():
    from src.auth.registration import register_user

    email = _unique_email("reg-basic")
    result = register_user(email=email, password="parola123", full_name="Ion Popescu")

    assert result.email == email
    assert result.full_name == "Ion Popescu"
    assert result.role == "LEADER"
    assert result.id is not None


def test_register_user_seteaza_password_hash_bcrypt_valid():
    from src.auth.registration import register_user
    from src.data.db import get_connection

    email = _unique_email("reg-hash")
    result = register_user(email=email, password="parola123", full_name="Test")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT password_hash FROM users WHERE id = %s", (result.id,))
            password_hash = cur.fetchone()[0]

    assert password_hash is not None
    assert password_hash != "parola123"  # nu e parola in clar
    assert bcrypt.checkpw(b"parola123", password_hash.encode())


def test_register_user_email_duplicat_ridica_unique_violation():
    from src.auth.registration import register_user
    import psycopg.errors

    email = _unique_email("reg-dup")
    register_user(email=email, password="parola123", full_name="Primul")

    with pytest.raises(psycopg.errors.UniqueViolation):
        register_user(email=email, password="altaparola", full_name="Al doilea")


def test_register_user_dupa_esec_duplicat_urmatorul_register_functioneaza():
    """
    DoD suplimentar (cerut explicit): verifica indirect ca UniqueViolation
    nu lasa conexiunea/tranzactia intr-o stare defecta pentru request-ul urmator.
    """
    from src.auth.registration import register_user
    import psycopg.errors

    email_x = _unique_email("reg-rollback-x")
    email_y = _unique_email("reg-rollback-y")

    register_user(email=email_x, password="parola123", full_name="X")

    with pytest.raises(psycopg.errors.UniqueViolation):
        register_user(email=email_x, password="altaparola", full_name="X din nou")

    # Imediat dupa esecul de mai sus, un register valid, diferit, trebuie sa functioneze
    result_y = register_user(email=email_y, password="parola123", full_name="Y")
    assert result_y.email == email_y


def test_register_user_role_este_leader_din_db_default_nu_din_cod():
    """role vine din DB DEFAULT 'LEADER', nu e setat explicit de register_user()."""
    from src.auth.registration import register_user
    from src.data.db import get_connection

    email = _unique_email("reg-role")
    result = register_user(email=email, password="parola123", full_name="Test")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT role FROM users WHERE id = %s", (result.id,))
            role = cur.fetchone()[0]

    assert role == "LEADER"
    assert result.role == "LEADER"


# ----------------------------------------------------------------------
# POST /api/v1/auth/register — integrare HTTP completa
# ----------------------------------------------------------------------


def test_post_register_valid_returneaza_201(client):
    email = _unique_email("api-reg-ok")
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "parola123", "full_name": "Maria Ionescu"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == email
    assert body["full_name"] == "Maria Ionescu"
    assert body["role"] == "LEADER"
    assert "id" in body


def test_post_register_nu_returneaza_parola_sau_hash(client):
    email = _unique_email("api-reg-nopass")
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "parola123", "full_name": "Test"},
    )
    assert response.status_code == 201  # altfel testul de mai jos trece fals-pozitiv pe 404
    body = response.json()
    assert "password" not in body
    assert "password_hash" not in body


def test_post_register_nu_returneaza_token(client):
    """/register NU emite JWT — derivat din criteriul de acceptare, contract sectiunea 1."""
    email = _unique_email("api-reg-notoken")
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "parola123", "full_name": "Test"},
    )
    assert response.status_code == 201  # altfel testul de mai jos trece fals-pozitiv pe 404
    body = response.json()
    assert "access_token" not in body


def test_post_register_email_duplicat_returneaza_409(client):
    email = _unique_email("api-reg-dup")
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "parola123", "full_name": "Primul"},
    )
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "altaparola", "full_name": "Al doilea"},
    )
    assert response.status_code == 409
    assert response.json()["error_code"] == "ALREADY_EXISTS"


def test_post_register_full_name_lipsa_returneaza_422(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": _unique_email("api-reg-nofn"), "password": "parola123"},
    )
    assert response.status_code == 422


def test_post_register_parola_scurta_returneaza_422(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": _unique_email("api-reg-shortpw"), "password": "1234567", "full_name": "Test"},
    )
    assert response.status_code == 422


def test_post_register_parola_lunga_returneaza_422(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": _unique_email("api-reg-longpw"), "password": "a" * 73, "full_name": "Test"},
    )
    assert response.status_code == 422


# ----------------------------------------------------------------------
# Fluxul complet — register -> login -> JWT -> endpoint protejat
# ----------------------------------------------------------------------


def test_flux_complet_register_apoi_login_apoi_endpoint_protejat(client):
    email = _unique_email("api-reg-flow")
    password = "parola123"

    r_register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Flux Complet"},
    )
    assert r_register.status_code == 201

    r_login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]

    r_protected = client.get(
        "/api/v1/objections/categories", headers={"Authorization": f"Bearer {token}"},
    )
    assert r_protected.status_code == 200
    assert len(r_protected.json()["categories"]) == 13
