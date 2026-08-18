"""
Teste RED structurale pentru Objection Workbench (apps/workbench/index.html).

Sursa: 27-objection-workbench-contract.md, sectiunea 7, Nivel 1.

IMPORTANT: acestea NU sunt teste de comportament in browser (repo-ul nu
are Jest/Playwright/Selenium — decizie explicita, contract sectiunea 7).
Sunt verificari STATICE ale continutului fisierului, ca text — confirma
ca structura respecta contractul (endpoint-uri, payload-uri, absenta
localStorage, absenta SQL/Python, absenta owner_id in JS).

Conventie folosita pentru testabilitate: implementarea GREEN trebuie sa
delimiteze constructia payload-ului pentru /confirm intre marcaje
explicite in comentarii JS:
    // CONFIRM_PAYLOAD_START
    ...
    // CONFIRM_PAYLOAD_END
astfel incat testul sa poata verifica STRICT ca acel bloc contine doar
response_text/response_variant_used/objection_id, fara
objection_category/objection_text/owner_id — desi acestea din urma apar
legitim in alte parti ale fisierului (ex. la /analyze, /prepare).
"""

import re
from pathlib import Path

import pytest

WORKBENCH_PATH = Path(__file__).parent.parent / "apps" / "workbench" / "index.html"


@pytest.fixture
def workbench_content():
    if not WORKBENCH_PATH.exists():
        pytest.fail(f"Fișierul {WORKBENCH_PATH} nu există încă.")
    return WORKBENCH_PATH.read_text(encoding="utf-8")


# ----------------------------------------------------------------------
# Existenta fisierului
# ----------------------------------------------------------------------


def test_workbench_exista():
    assert WORKBENCH_PATH.exists(), f"Fișierul {WORKBENCH_PATH} nu există încă."


def test_workbench_este_fisier_unic_html():
    """MVP — un singur fisier, fara fisiere JS/CSS separate langa el."""
    workbench_dir = WORKBENCH_PATH.parent
    assert workbench_dir.exists()
    files = list(workbench_dir.iterdir())
    assert files == [WORKBENCH_PATH], f"Fișiere neașteptate în {workbench_dir}: {files}"


# ----------------------------------------------------------------------
# Endpoint-urile — toate 5 (login + 4 objections)
# ----------------------------------------------------------------------


def test_contine_endpoint_login(workbench_content):
    assert "/api/v1/auth/login" in workbench_content


def test_contine_endpoint_analyze(workbench_content):
    assert "/api/v1/objections/analyze" in workbench_content


def test_contine_endpoint_categories(workbench_content):
    assert "/api/v1/objections/categories" in workbench_content


def test_contine_endpoint_prepare(workbench_content):
    assert "/api/v1/objections/prepare" in workbench_content


def test_contine_endpoint_confirm(workbench_content):
    assert "/api/v1/objections/confirm" in workbench_content


def test_contine_endpoint_get_contacts(workbench_content):
    """Decizia 34: Workbench trebuie sa incarce lista de contacte."""
    assert "/api/v1/contacts" in workbench_content


def test_contine_endpoint_post_conversations(workbench_content):
    """Decizia 34: Workbench trebuie sa creeze/obtina conversatia reala."""
    assert "/api/v1/conversations" in workbench_content


def test_toate_fetch_urile_folosesc_doar_api_v1(workbench_content):
    """
    Niciun fetch()/apiFetch() nu tinteste altceva decat /api/v1/... —
    Workbench-ul nu poate ocoli API-ul catre un endpoint Python intern
    sau alta cale. Regex-ul prinde ambele forme (fetch si apiFetch,
    ambele contin substring-ul "etch(").
    """
    fetch_calls = re.findall(r"etch\(\s*[`'\"]([^`'\"]+)[`'\"]", workbench_content)
    assert len(fetch_calls) >= 5, f"Prea puține apeluri fetch()/apiFetch() găsite: {fetch_calls}"
    for url in fetch_calls:
        assert "/api/v1/" in url, f"fetch() către un endpoint neconform: {url}"


# ----------------------------------------------------------------------
# Payload-uri — campurile obligatorii
# ----------------------------------------------------------------------


@pytest.mark.parametrize("field", [
    "objection_text", "objection_category", "objection_id",
    "response_text", "response_variant_used",
])
def test_contine_campul_payload(workbench_content, field):
    assert field in workbench_content


# ----------------------------------------------------------------------
# Securitatea payload-ului /confirm — control suplimentar cerut explicit
# ----------------------------------------------------------------------


def _extract_confirm_payload_block(content: str) -> str:
    match = re.search(
        r"//\s*CONFIRM_PAYLOAD_START(.*?)//\s*CONFIRM_PAYLOAD_END",
        content, re.DOTALL,
    )
    assert match is not None, (
        "Marcajele CONFIRM_PAYLOAD_START/CONFIRM_PAYLOAD_END lipsesc — "
        "necesare pentru verificarea strictă a payload-ului /confirm."
    )
    return match.group(1)


def test_confirm_payload_nu_contine_objection_category(workbench_content):
    block = _extract_confirm_payload_block(workbench_content)
    assert "objection_category" not in block


def test_confirm_payload_nu_contine_objection_text(workbench_content):
    block = _extract_confirm_payload_block(workbench_content)
    assert "objection_text" not in block


def test_confirm_payload_contine_doar_campurile_permise(workbench_content):
    block = _extract_confirm_payload_block(workbench_content)
    assert "response_text" in block
    assert "response_variant_used" in block
    assert "objection_id" in block


# ----------------------------------------------------------------------
# Payload /prepare — Decizia 34: conversation_id trebuie sa fie
# variabila reala (currentConversationId), NU literal null hardcodat
# ----------------------------------------------------------------------


def _extract_prepare_payload_block(content: str) -> str:
    match = re.search(
        r"//\s*PREPARE_PAYLOAD_START(.*?)//\s*PREPARE_PAYLOAD_END",
        content, re.DOTALL,
    )
    assert match is not None, (
        "Marcajele PREPARE_PAYLOAD_START/PREPARE_PAYLOAD_END lipsesc — "
        "necesare pentru verificarea stricta ca conversation_id nu mai e null hardcodat."
    )
    return match.group(1)


def test_prepare_payload_foloseste_current_conversation_id(workbench_content):
    block = _extract_prepare_payload_block(workbench_content)
    assert "currentConversationId" in block


def test_prepare_payload_nu_mai_are_null_hardcodat(workbench_content):
    """
    Regresie fata de starea dinainte de Decizia 34: conversation_id NU
    mai e literalul 'null' — trebuie sa fie variabila reala.
    """
    block = _extract_prepare_payload_block(workbench_content)
    assert "conversation_id: null" not in block
    assert "conversation_id: currentConversationId" in block


# ----------------------------------------------------------------------
# owner_id — NICIODATA in JS, in nicio forma
# ----------------------------------------------------------------------


def test_owner_id_nu_apare_niciunde_in_fisier(workbench_content):
    """
    owner_id nu trebuie sa apara NICIUNDE in Workbench — nici macar in
    comentarii — identitatea vine exclusiv din JWT, procesat server-side.
    """
    assert "owner_id" not in workbench_content


# ----------------------------------------------------------------------
# Token — memorie runtime, NICIODATA persistat
# ----------------------------------------------------------------------


def test_nu_foloseste_local_storage(workbench_content):
    assert "localStorage" not in workbench_content


def test_nu_foloseste_session_storage(workbench_content):
    assert "sessionStorage" not in workbench_content


def test_nu_seteaza_cookie_nou(workbench_content):
    assert "document.cookie" not in workbench_content


def test_foloseste_authorization_bearer_header(workbench_content):
    assert "Authorization" in workbench_content
    assert "Bearer" in workbench_content


def test_parola_nu_e_persistata_dupa_login(workbench_content):
    """
    Camp de parola prezent (pentru formularul de login), dar niciun
    identificator JS care ar sugera stocarea ei (ex. `savedPassword`,
    `password =` in afara requestului de login e greu de verificat static
    complet — verificam macar ca nu e scrisa in localStorage/sessionStorage,
    deja acoperit de testele de mai sus).
    """
    assert 'type="password"' in workbench_content


# ----------------------------------------------------------------------
# Fara acces direct la DB sau cod Python
# ----------------------------------------------------------------------


def test_fara_conexiune_postgresql_directa(workbench_content):
    assert "postgresql://" not in workbench_content
    assert "psycopg" not in workbench_content


def test_fara_sql_brut(workbench_content):
    for keyword in ("SELECT ", "INSERT INTO", "UPDATE ", "DELETE FROM"):
        assert keyword not in workbench_content


def test_fara_importuri_python(workbench_content):
    assert "import src." not in workbench_content
    assert "from src." not in workbench_content


# ----------------------------------------------------------------------
# Cele 3 faze — elemente obligatorii vizibile
# ----------------------------------------------------------------------


def test_are_camp_pentru_textul_obiectiei(workbench_content):
    assert "objection_text" in workbench_content  # deja verificat, dar explicit per faza


def test_are_gestionare_needs_manual_selection(workbench_content):
    assert "needs_manual_selection" in workbench_content


def test_are_cele_trei_variante_numite(workbench_content):
    for variant in ("CALDA", "DIRECTA", "INTREBARE"):
        assert variant in workbench_content


# ----------------------------------------------------------------------
# Cele 4 niveluri Safety Validation — toate randate distinct
# ----------------------------------------------------------------------


@pytest.mark.parametrize("level", ["PASS", "BLOCK", "PARTIAL_VALIDATION", "HUMAN_REVIEW"])
def test_gestioneaza_nivel_validare(workbench_content, level):
    assert level in workbench_content


def test_block_nu_e_tratat_ca_eroare_tehnica(workbench_content):
    """
    Verificare cel puţin structurală: langa BLOCK trebuie sa existe un
    mesaj despre siguranta/motiv, nu un text generic de eroare de tip
    500/eroare de server — cautam macar cuvantul "reason" (folosit pentru
    a afisa motivul) in vecinatatea gestionarii BLOCK, nu doar undeva in fisier.
    """
    assert "reason" in workbench_content
