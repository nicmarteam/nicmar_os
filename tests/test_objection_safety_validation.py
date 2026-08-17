"""
Teste RED pentru Safety Validation (Decizia 4 + Decizia 5).

Sursa: 21-objection-engine-contract.md, sectiunea 5, criterii 7.4/7.5.
Model pe 3 niveluri: BLOCK / PARTIAL_VALIDATION / HUMAN_REVIEW.
"""

import pytest

from src.engines.objection.safety_validation import validate_response


# ----------------------------------------------------------------------
# BLOCK - promisiuni nerealiste / garantare
# ----------------------------------------------------------------------


@pytest.mark.parametrize("text", [
    "Îți garantez că vei câștiga bani.",
    "Sigur vei avea succes cu asta.",
    "100% vei reuși dacă începi acum.",
])
def test_block_promisiuni_nerealiste(text):
    result = validate_response(text, objection_category="PRET", objection_text="e scump")
    assert result.level == "BLOCK"


# ----------------------------------------------------------------------
# BLOCK - presiune financiara
# ----------------------------------------------------------------------


def test_block_presiune_financiara():
    result = validate_response(
        "Trebuie să investești acum, prețul crește curând.",
        objection_category="PRET", objection_text="e scump",
    )
    assert result.level == "BLOCK"


# ----------------------------------------------------------------------
# BLOCK - urgenta artificiala
# ----------------------------------------------------------------------


@pytest.mark.parametrize("text", [
    "Trebuie să decizi acum sau niciodată.",
    "E valabil doar azi, nu rata ultima șansă.",
])
def test_block_urgenta_artificiala(text):
    result = validate_response(text, objection_category="AMANARE", objection_text="ma mai gandesc")
    assert result.level == "BLOCK"


# ----------------------------------------------------------------------
# BLOCK - exploatarea vulnerabilitatii (tipare din audit)
# ----------------------------------------------------------------------


def test_block_exploatare_vulnerabilitate():
    result = validate_response(
        "Boala te-a făcut să simți că nu mai ai nicio valoare, dar aici poți schimba asta.",
        objection_category="VULNERABILITATE_IZOLARE", objection_text="ma simt singura",
    )
    assert result.level == "BLOCK"


# ----------------------------------------------------------------------
# BLOCK - Decizia 5: cifre de venit fara disclaimer
# ----------------------------------------------------------------------


def test_block_cifra_venit_fara_disclaimer():
    result = validate_response(
        "Poți ajunge la 3.000 lei pe lună.",
        objection_category="PRET", objection_text="e scump",
    )
    assert result.level == "BLOCK"
    assert "disclaimer" in result.reason.lower()


def test_pass_cifra_venit_cu_disclaimer():
    result = validate_response(
        "Poți ajunge la 3.000 lei pe lună. Rezultatele variază de la "
        "persoană la persoană și nu sunt garantate.",
        objection_category="PRET", objection_text="e scump",
    )
    assert result.level == "PASS"


def test_pass_cifra_neconcludenta_nu_e_financiara():
    """'Programul durează 15 zile' contine o cifra, dar NU e financiara -
    nu trebuie sa produca fals-pozitiv (contract, criteriu 7.4)."""
    result = validate_response(
        "Programul durează 15 zile.",
        objection_category="TIMP", objection_text="nu am timp",
    )
    assert result.level == "PASS"


# ----------------------------------------------------------------------
# PARTIAL_VALIDATION - INCREDERE_STRUCTURA fara confirmare directa
# ----------------------------------------------------------------------


def test_partial_validation_increderea_structura_fara_confirmare_directa():
    """Raspuns pentru INCREDERE_STRUCTURA care evita subiectul printr-un
    redirect pur, scurt (exact tiparul din Pasii_de_baza_afacerii.docx,
    exclus la Decizia 4: 'De ce întrebi?' fara alt continut) -
    PARTIAL_VALIDATION, nu BLOCK (nu poate fi detectat cu certitudine
    deterministic)."""
    result = validate_response(
        "De ce întrebi asta?",
        objection_category="INCREDERE_STRUCTURA", objection_text="e piramida?",
    )
    assert result.level == "PARTIAL_VALIDATION"


def test_pass_increderea_structura_cu_confirmare_directa():
    result = validate_response(
        "Nu, nu e piramidă. Investiția e mică și garantată prin politica "
        "de retur.",
        objection_category="INCREDERE_STRUCTURA", objection_text="e piramida?",
    )
    assert result.level == "PASS"


# ----------------------------------------------------------------------
# HUMAN_REVIEW - testimoniale/dovezi suspecte
# ----------------------------------------------------------------------


@pytest.mark.parametrize("text", [
    "Studiile arată că produsul funcționează în 90% din cazuri.",
    "Conform cercetărilor recente, este cel mai bun produs.",
])
def test_human_review_testimoniale_suspecte(text):
    result = validate_response(text, objection_category="PRET", objection_text="e scump")
    assert result.level == "HUMAN_REVIEW"


# ----------------------------------------------------------------------
# HUMAN_REVIEW - ocolirea refuzului explicit
# ----------------------------------------------------------------------


def test_human_review_ocolire_refuz_explicit():
    result = validate_response(
        "Dar măcar încearcă, gândește-te din nou.",
        objection_category="NU_VREAU_VANZARE",
        objection_text="Nu, mulțumesc, nu mă interesează.",
    )
    assert result.level == "HUMAN_REVIEW"


def test_pass_raspuns_normal_fara_refuz_explicit():
    result = validate_response(
        "Dar măcar încearcă, gândește-te din nou.",
        objection_category="NU_VREAU_VANZARE",
        objection_text="Nu sunt sigură dacă e pentru mine.",
    )
    # fara refuz explicit in objection_text, nu se declanseaza regula
    assert result.level != "HUMAN_REVIEW" or result.level == "PASS"


# ----------------------------------------------------------------------
# PASS - text complet curat
# ----------------------------------------------------------------------


def test_pass_text_curat():
    result = validate_response(
        "Înțeleg de ce întrebi, mulți au aceeași primă impresie. Vrei să-ți "
        "arăt cum funcționează?",
        objection_category="INCREDERE_STRUCTURA", objection_text="e piramida?",
    )
    assert result.level == "PASS"


# ----------------------------------------------------------------------
# Regresie: toate cele 39 de texte canonice deja aprobate trebuie sa
# treaca Safety Validation fara BLOCK - altfel am aproba continut pe
# care propriul motor l-ar respinge (exact bug-ul gasit cu "garantata").
# ----------------------------------------------------------------------


def test_toate_cele_39_texte_canonice_nu_sunt_niciodata_block():
    from src.engines.objection.library import ALL_CATEGORIES, get_variants

    for category in ALL_CATEGORIES:
        variants = get_variants(category)
        for variant_name, text in variants.items():
            result = validate_response(text, objection_category=category, objection_text="")
            assert result.level != "BLOCK", (
                f"Text canonic aprobat respins: {category}/{variant_name}: {result.reason}"
            )
