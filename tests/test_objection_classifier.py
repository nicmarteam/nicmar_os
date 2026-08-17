"""
Teste RED pentru clasificarea deterministă a obiecțiilor.

Sursa: 21-objection-engine-decizii-preliminare.md, Decizia 2 (CONFIRMATA
17 august 2026) - clasificare pe cuvinte-cheie, DOAR pentru cele 6
categorii cu acoperire buna din audit (PRET, TIMP, INCREDERE_STRUCTURA,
FAMILIE_SUPORT, AMANARE, FRICA_TEHNOLOGIE). Restul categoriilor din
Biblioteca Experientei NU sunt tinta clasificarii automate in v1.

Cuvintele-cheie folosite in implementare provin EXCLUSIV din citate
reale gasite in cele ~24 fisiere sursa (verificat prin grep direct pe
sursa, nu inventate) - v. audit Decizia 2.

Acest test acopera STRICT mecanismul de clasificare, izolat de restul
ObjectionEngine (selectia variantelor de raspuns, scriere in DB, etc.)
- acele piese raman dupa Deciziile 3-5, inca deschise.
"""

import pytest

from src.engines.objection.classifier import classify_objection


# ----------------------------------------------------------------------
# Cele 6 categorii eligibile - cate un test per formulare reala gasita
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected_category",
    [
        # PRET - citate reale: "Produsele sunt scumpe.", "scump"
        ("Produsele sunt scumpe.", "PRET"),
        ("Mi se pare cam scump.", "PRET"),
        ("Nu știu, prețul mi se pare mare.", "PRET"),
        # TIMP - citate reale: "Nu am timp.", "n-am timp"
        ("Nu am timp.", "TIMP"),
        ("N-am timp de așa ceva acum.", "TIMP"),
        # INCREDERE_STRUCTURA - citate reale: "E o piramidă?", "Este MLM?"
        ("E o piramidă?", "INCREDERE_STRUCTURA"),
        ("Este MLM?", "INCREDERE_STRUCTURA"),
        ("Sună prea frumos ca să fie adevărat.", "INCREDERE_STRUCTURA"),
        # FAMILIE_SUPORT - citate reale: "Partenerul meu de viață râde de mine",
        # "Familia nu mă susține"
        ("Partenerul meu de viață râde de mine, zice că-i o prostie.", "FAMILIE_SUPORT"),
        ("Familia nu mă susține în privința asta.", "FAMILIE_SUPORT"),
        # AMANARE - citate reale: "Nu e momentul potrivit", "trebuie să mă mai gândesc"
        ("Nu e momentul potrivit acum.", "AMANARE"),
        ("Trebuie să mă mai gândesc.", "AMANARE"),
        # FRICA_TEHNOLOGIE - citat real: "Nu mă pricep la tehnologie."
        ("Nu mă pricep la tehnologie.", "FRICA_TEHNOLOGIE"),
    ],
)
def test_classify_objection_categorii_eligibile(text, expected_category):
    assert classify_objection(text) == expected_category


# ----------------------------------------------------------------------
# Text fara nicio potrivire -> None, nu o categorie ghicita
# ----------------------------------------------------------------------


def test_classify_objection_text_neconcludent_returneaza_none():
    """
    Text care nu se potriveste cu niciun cuvant-cheie din cele 6
    categorii eligibile trebuie sa returneze None - motorul nu trebuie
    sa ghiceasca o categorie fara semnal real (regula: cele 7 categorii
    ramase nu sunt tinta clasificarii automate, deci text specific lor
    trebuie sa dea None, nu o eticheta gresita).
    """
    assert classify_objection("Nu vreau să vând la prieteni.") is None
    assert classify_objection("Ce o să zică vecinii?") is None
    assert classify_objection("") is None


def test_classify_objection_text_gol_sau_none_nu_produce_eroare():
    assert classify_objection("") is None
    assert classify_objection("   ") is None


# ----------------------------------------------------------------------
# Insensibil la majuscule si spatii suplimentare (robustete minima)
# ----------------------------------------------------------------------


def test_classify_objection_insensibil_la_majuscule():
    assert classify_objection("NU AM TIMP.") == "TIMP"
    assert classify_objection("   nu am timp   ") == "TIMP"


# ----------------------------------------------------------------------
# NEINCREDERE_PRODUS nu mai e categorie - nu poate fi returnata NICIODATA
# ----------------------------------------------------------------------


def test_classify_objection_nu_returneaza_niciodata_categoria_eliminata():
    """
    NEINCREDERE_PRODUS a fost eliminata din lista oficiala (Decizia 2) -
    clasificatorul nu trebuie sa o returneze niciodata, indiferent de text.
    """
    for text in ["Nu cred că produsul funcționează.", "Nu are efect."]:
        assert classify_objection(text) != "NEINCREDERE_PRODUS"
