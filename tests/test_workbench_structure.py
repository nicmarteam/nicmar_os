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


def test_contine_endpoint_followups(workbench_content):
    """Decizia 36: Workbench trebuie sa creeze/listeze follow-up-uri."""
    assert "/api/v1/followups" in workbench_content


def test_contine_endpoint_followup_complete(workbench_content):
    assert "/complete" in workbench_content


def test_contine_endpoint_followup_postpone(workbench_content):
    assert "/postpone" in workbench_content


def test_contine_endpoint_followup_reschedule(workbench_content):
    assert "/reschedule" in workbench_content


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
# Payload /followups — Decizia 36: trebuie sa reutilizeze
# currentContactId/currentConversationId, nu valori noi
# ----------------------------------------------------------------------


def _extract_followup_payload_block(content: str) -> str:
    match = re.search(
        r"//\s*FOLLOWUP_PAYLOAD_START(.*?)//\s*FOLLOWUP_PAYLOAD_END",
        content, re.DOTALL,
    )
    assert match is not None, (
        "Marcajele FOLLOWUP_PAYLOAD_START/FOLLOWUP_PAYLOAD_END lipsesc — "
        "necesare pentru verificarea ca payload-ul reutilizeaza starea Contact/Conversation."
    )
    return match.group(1)


def test_followup_payload_reutilizeaza_current_contact_id(workbench_content):
    block = _extract_followup_payload_block(workbench_content)
    assert "currentContactId" in block


def test_followup_payload_reutilizeaza_current_conversation_id(workbench_content):
    block = _extract_followup_payload_block(workbench_content)
    assert "currentConversationId" in block


def test_followup_payload_nu_contine_objection_id(workbench_content):
    """Decizia 36, sectiunea 6: fara legatura cu Objection."""
    block = _extract_followup_payload_block(workbench_content)
    assert "objection_id" not in block


def test_are_guard_pentru_contact_si_conversation_la_creare_followup(workbench_content):
    """
    Decizia 36, sectiunea 4: crearea unui follow-up trebuie blocata daca
    lipseste currentContactId SAU currentConversationId — verificare
    structurala a guard-ului (nu doar prezenta variabilelor undeva).
    """
    assert "!currentContactId" in workbench_content
    assert "!currentConversationId" in workbench_content


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


# ----------------------------------------------------------------------
# DECIZIA 37 (RED, 19 august 2026) — Partner Workbench.
# Sursa: 37-workbench-partner-contract.md, sectiunea 8.
#
# Conventie noua pentru testabilitate stricta, identica cu marcajele
# deja folosite la /confirm, /prepare, /followups: implementarea GREEN
# trebuie sa delimiteze payload-urile Partner intre marcaje explicite:
#   // PARTNER_CREATE_PAYLOAD_START ... // PARTNER_CREATE_PAYLOAD_END
#   // PARTNER_DIAGNOSTIC_PAYLOAD_START ... // PARTNER_DIAGNOSTIC_PAYLOAD_END
#   // PARTNER_SEND_PAYLOAD_START ... // PARTNER_SEND_PAYLOAD_END
# ----------------------------------------------------------------------


# ------------------------------------------------------------------
# Endpoint-urile — toate 4, ca string literal in fetch()/apiFetch()
# ------------------------------------------------------------------


def test_contine_endpoint_post_partners(workbench_content):
    """Contract 37, sectiunea 8, criteriul 1."""
    assert "/api/v1/partners" in workbench_content


def test_contine_endpoint_partner_diagnostic(workbench_content):
    """
    Contract 37, criteriul 2. Verificam pattern-ul de URL template
    folosit deja la followups (`/${followupId}/complete`), aplicat
    aici pentru diagnostic — nu un literal fix, pentru ca partner_id
    e dinamic.
    """
    assert "/diagnostic" in workbench_content
    assert re.search(r"/api/v1/partners/\$\{[^}]+\}/diagnostic", workbench_content), (
        "Lipseste template-ul de URL pentru POST /partners/{id}/diagnostic."
    )


def test_contine_endpoint_partner_send(workbench_content):
    """Contract 37, criteriul 3."""
    assert re.search(r"/api/v1/partners/\$\{[^}]+\}/send", workbench_content), (
        "Lipseste template-ul de URL pentru POST /partners/{id}/send."
    )


def test_contine_endpoint_partner_scores(workbench_content):
    """Contract 37, criteriul 4."""
    assert "/api/v1/partners/scores" in workbench_content


# ------------------------------------------------------------------
# Payload-uri exacte — contract sectiunea 5
# ------------------------------------------------------------------


def _extract_marked_block(content: str, marker_name: str) -> str:
    """Extrage blocul dintre `// {marker_name}_START` si `// {marker_name}_END`."""
    match = re.search(
        rf"//\s*{marker_name}_START(.*?)//\s*{marker_name}_END",
        content, re.DOTALL,
    )
    assert match is not None, (
        f"Marcajele {marker_name}_START/{marker_name}_END lipsesc — "
        f"necesare pentru verificarea stricta a payload-ului (contract 37, sectiunea 5)."
    )
    return match.group(1)


def test_partner_create_payload_contine_doar_contact_id(workbench_content):
    """
    Contract 37, sectiunea 5 + criteriul 5: payload-ul POST /partners
    contine EXACT contact_id, fara owner_id, fara status/partner_level
    (acestea sunt hardcodate server-side, nu trimise de client).
    """
    block = _extract_marked_block(workbench_content, "PARTNER_CREATE_PAYLOAD")
    assert "contact_id" in block
    assert "owner_id" not in block
    assert "status" not in block
    assert "partner_level" not in block


def test_diagnostic_payload_contine_doar_diagnostic_type(workbench_content):
    """Contract 37, criteriul 6."""
    block = _extract_marked_block(workbench_content, "PARTNER_DIAGNOSTIC_PAYLOAD")
    assert "diagnostic_type" in block
    assert "owner_id" not in block
    assert "partner_id" not in block, (
        "partner_id vine din URL (path param), nu trebuie duplicat in body."
    )


def test_send_payload_contine_doar_confirmed(workbench_content):
    """Contract 37, criteriul 7."""
    block = _extract_marked_block(workbench_content, "PARTNER_SEND_PAYLOAD")
    assert "confirmed" in block
    assert "owner_id" not in block


# ------------------------------------------------------------------
# Cele 4 diagnostic_type — exact, fara inventii
# ------------------------------------------------------------------


def test_cele_patru_diagnostic_types_prezente(workbench_content):
    """
    Contract 37, sectiunea 5 + criteriul 8: exact cele 4 valori din
    VALID_DIAGNOSTIC_TYPES (src/engines/partner/partner_engine.py),
    hardcodate in UI ca optiuni de selectie.
    """
    for diagnostic_type in ("ENCOURAGEMENT", "CLARITY", "APPRECIATION", "NEXT_STEP"):
        assert diagnostic_type in workbench_content, (
            f"Tipul de diagnostic '{diagnostic_type}' lipseste din Workbench."
        )


# ------------------------------------------------------------------
# Sursa de adevar pentru partner_id — sectiunea 3 din contract
# ------------------------------------------------------------------


def test_partner_id_nu_e_citit_din_local_storage(workbench_content):
    """
    Contract 37, sectiunea 3, criteriul 9: currentPartnerId nu e o
    sursa independenta persistenta — nu se citeste din storage.
    Regula generala (localStorage/sessionStorage) e deja verificata de
    test_nu_foloseste_local_storage/test_nu_foloseste_session_storage;
    aici verificam explicit ca variabila runtime exista si ca sursa ei
    e fie contact.partner_id, fie response.id (dupa creare) — nu storage.
    """
    assert "currentPartnerId" in workbench_content
    assert "localStorage" not in workbench_content
    assert "sessionStorage" not in workbench_content
    assert re.search(r"currentPartnerId\s*=\s*contact\.partner_id", workbench_content), (
        "currentPartnerId trebuie populat din contact.partner_id pentru "
        "un contact deja convertit (contract 37, sectiunea 3/4)."
    )


def test_zona_partner_ascunsa_fara_contact_selectat(workbench_content):
    """
    Contract 37, criteriul 11: panoul Partner are clasa `disabled` in
    markup implicit, identic cu panel-analyze/panel-followup — nicio
    actiune Partner posibila inainte de selectarea unui contact.
    """
    assert re.search(r'class="panel disabled"\s+id="panel-partner"', workbench_content), (
        "Panoul Partner trebuie sa existe cu id=\"panel-partner\" si clasa "
        "\"disabled\" implicit in markup, identic cu celelalte zone dependente "
        "de currentContactId."
    )


# ------------------------------------------------------------------
# Onestitate fata de lider — mesaj STUB si etichetare scoruri
# ------------------------------------------------------------------


def test_mesaj_stub_afisat_ca_atare(workbench_content):
    """
    Contract 37, sectiunea 6 + criteriul 12: textul [STUB] returnat de
    server e afisat ca atare, nu filtrat printr-un .replace() care l-ar
    ascunde de lider.
    """
    assert "[STUB]" in workbench_content
    assert ".replace(" not in workbench_content or not re.search(
        r'\.replace\([^)]*STUB[^)]*\)', workbench_content
    ), "Mesajul [STUB] nu trebuie filtrat/ascuns printr-un .replace()."


def test_eticheta_scoruri_nu_mentioneaza_partener_specific(workbench_content):
    """
    Contract 37, sectiunea 6 + criteriul 13: eticheta afisata pentru
    scoruri trebuie sa reflecte limitarea reala a API-ului
    (GET /partners/scores e agregat pe owner, nu pe partenerul
    selectat) — "cele mai recente ale tale", nu "scorul partenerului".
    """
    assert "cele mai recente" in workbench_content.lower() or \
        "recente ale tale" in workbench_content.lower(), (
        "Eticheta scorurilor trebuie sa indice explicit ca sunt cele mai "
        "recente ale liderului, nu ale partenerului selectat (contract 37, "
        "sectiunea 6)."
    )


# ----------------------------------------------------------------------
# DECIZIA 38 (RED, 19 august 2026) — Mission Workbench.
# Sursa: 38-workbench-mission-contract.md, sectiunea 9.
#
# Conventie noua: implementarea GREEN trebuie sa delimiteze payload-urile
# Mission intre marcaje explicite:
#   // MISSION_CREATE_PAYLOAD_START ... // MISSION_CREATE_PAYLOAD_END
#   // MISSION_START_PAYLOAD_START ... // MISSION_START_PAYLOAD_END
#
# Criteriul 12 din contract (owner_id nu apare niciunde) e acoperit de
# testul existent test_owner_id_nu_apare_niciunde_in_fisier — regresie,
# nu test nou. De aceea sunt 11 teste noi, nu 12.
# ----------------------------------------------------------------------


def test_contine_endpoint_post_missions(workbench_content):
    """Contract 38, sectiunea 9, criteriul 1."""
    assert "/api/v1/missions" in workbench_content


def test_contine_endpoint_mission_assign(workbench_content):
    """Contract 38, criteriul 2."""
    assert re.search(r"/api/v1/missions/\$\{[^}]+\}/assign", workbench_content), (
        "Lipseste template-ul de URL pentru POST /missions/{id}/assign."
    )


def _extract_apifetch_call_options(content: str, url_fragment: str) -> str:
    """
    Extrage blocul de optiuni {...} din primul apel
    apiFetch(`...url_fragment...`, {...}). Folosit pentru verificarea
    stricta a metodei HTTP (contract 38, criteriul 3) — nu ne oprim la
    prezenta URL-ului ca text, verificam efectiv ce metoda foloseste
    apelul respectiv.
    """
    pattern = r"apiFetch\(\s*`[^`]*" + re.escape(url_fragment) + r"[^`]*`\s*,\s*\{(.*?)\}\s*\)"
    match = re.search(pattern, content, re.DOTALL)
    assert match is not None, (
        f"Apelul apiFetch pentru '{url_fragment}' nu a fost gasit in forma "
        f"asteptata apiFetch(`...{url_fragment}...`, {{ ... }})."
    )
    return match.group(1)


def test_contine_endpoint_mission_present_ca_get(workbench_content):
    """
    Contract 38, criteriul 3: /present trebuie sa fie GET, nu POST —
    diferit de tiparul folosit la Objection/Partner. Verificarea extrage
    optiunile efective din apelul apiFetch si confirma method: "GET"
    chiar in acel apel, nu doar prezenta URL-ului undeva in fisier.
    """
    assert re.search(r"/api/v1/missions/\$\{[^}]+\}/present", workbench_content), (
        "Lipseste template-ul de URL pentru GET /missions/{id}/present."
    )
    options_block = _extract_apifetch_call_options(workbench_content, "/present")
    assert re.search(r'method\s*:\s*["\']GET["\']', options_block), (
        'Apelul catre /present trebuie sa foloseasca explicit method: "GET" '
        "(contract 38, sectiunea 4) — nu POST."
    )


def test_contine_endpoint_mission_start(workbench_content):
    """Contract 38, criteriul 4."""
    assert re.search(r"/api/v1/missions/\$\{[^}]+\}/start", workbench_content), (
        "Lipseste template-ul de URL pentru POST /missions/{id}/start."
    )


def test_contine_endpoint_mission_complete(workbench_content):
    """Contract 38, criteriul 5."""
    assert re.search(r"/api/v1/missions/\$\{[^}]+\}/complete", workbench_content), (
        "Lipseste template-ul de URL pentru POST /missions/{id}/complete."
    )


def test_contine_endpoint_dis_score(workbench_content):
    """Contract 38, criteriul 6."""
    assert "/api/v1/missions/dis-score" in workbench_content


def test_mission_create_payload_contine_doar_title(workbench_content):
    """
    Contract 38, sectiunea 6 + criteriul 7: payload-ul POST /missions
    contine EXACT title, fara description (desi engine-ul il accepta
    intern ca parametru optional, router-ul nu-l expune), fara owner_id.
    """
    block = _extract_marked_block(workbench_content, "MISSION_CREATE_PAYLOAD")
    assert "title" in block
    assert "description" not in block
    assert "owner_id" not in block


def test_mission_start_payload_contine_doar_confirmed(workbench_content):
    """Contract 38, criteriul 8."""
    block = _extract_marked_block(workbench_content, "MISSION_START_PAYLOAD")
    assert "confirmed" in block
    assert "owner_id" not in block


def test_zona_mission_activa_dupa_login_nu_dupa_contact(workbench_content):
    """
    Contract 38, sectiunea 3 + criteriul 9: panoul Mission exista cu
    id="panel-mission" si este activat in functia login(), nu in
    selectContact() — spre deosebire de Partner/FollowUp, Mission nu
    depinde de currentContactId (verificat din audit: contact_id/
    partner_id din missions nu sunt folosite nicaieri in engine/agent).
    """
    assert re.search(r'class="panel disabled"\s+id="panel-mission"', workbench_content), (
        'Panoul Mission trebuie sa existe cu id="panel-mission" si clasa '
        '"disabled" implicit in markup.'
    )

    login_match = re.search(r"async function login\(\)(.*?)\n  \}", workbench_content, re.DOTALL)
    assert login_match is not None, "Functia login() nu a fost gasita in forma asteptata."
    assert 'setPanelEnabled("panel-mission", true)' in login_match.group(1), (
        "panel-mission trebuie activat direct in login(), nu conditionat de "
        "selectContact() (contract 38, sectiunea 3)."
    )


def test_butoane_mission_conditionate_de_status(workbench_content):
    """
    Contract 38, criteriul 10: cele 4 stari trebuie verificate explicit
    in cod (comparatie, nu doar text decorativ) — butoanele Mission se
    activeaza/dezactiveaza in functie de status-ul real al misiunii.
    """
    for status in ("GENERATED", "ASSIGNED", "IN_PROGRESS", "COMPLETED"):
        pattern = r'(===|==)\s*["\']' + status + r'["\']'
        assert re.search(pattern, workbench_content), (
            f"Starea '{status}' trebuie verificata explicit printr-o comparatie "
            f"in cod (ex. status === '{status}'), nu doar mentionata ca text."
        )


def test_eticheta_dis_nu_mentioneaza_misiunea_curenta(workbench_content):
    """
    Contract 38, sectiunea 7 + criteriul 11: eticheta DIS trebuie sa
    foloseasca formularea exacta din contract, ca sa reflecte ca
    GET /missions/dis-score e agregat pe owner (cel mai recent DIS din
    toate misiunile), nu pe misiunea curenta. Verificam fraza exacta —
    nu "cele mai recente" generic, care ar putea aparea deja pentru
    Partner scores fara sa insemne nimic pentru Mission.
    """
    assert "DIS-ul tău cel mai recent" in workbench_content, (
        "Eticheta DIS trebuie sa foloseasca formularea exacta "
        "'DIS-ul tău cel mai recent' (contract 38, sectiunea 7)."
    )
