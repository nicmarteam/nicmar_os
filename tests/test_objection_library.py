"""
Teste RED pentru Biblioteca Experientei (continut, Decizia 3).

Sursa: 21-objection-engine-contract.md, sectiunea 3 + 7.2;
biblioteca-experientei-variante-v1.md (39 texte, 13 categorii x 3 variante).
"""

import pytest

from src.engines.objection.library import (
    ALL_CATEGORIES,
    AUTO_CLASSIFIABLE_CATEGORIES,
    get_variants,
)


def test_all_categories_are_13():
    assert len(ALL_CATEGORIES) == 13


def test_neincredere_produs_nu_e_in_lista():
    """Eliminata definitiv - Decizia 2, nesustinuta de sursa reala."""
    assert "NEINCREDERE_PRODUS" not in ALL_CATEGORIES


def test_auto_classifiable_sunt_exact_6():
    assert AUTO_CLASSIFIABLE_CATEGORIES == {
        "PRET", "TIMP", "INCREDERE_STRUCTURA",
        "FAMILIE_SUPORT", "AMANARE", "FRICA_TEHNOLOGIE",
    }


@pytest.mark.parametrize("category", [
    "PRET", "TIMP", "INCREDERE_STRUCTURA", "FAMILIE_SUPORT", "AMANARE",
    "FRICA_TEHNOLOGIE", "FRICA_ESEC", "FRICA_VORBIT", "NU_CUNOSC_OAMENI",
    "VULNERABILITATE_IZOLARE", "IMAGINE_SOCIALA", "NU_VREAU_VANZARE",
    "PIATA_SATURATA",
])
def test_get_variants_returneaza_exact_3_variante(category):
    variants = get_variants(category)
    assert set(variants.keys()) == {"CALDA", "DIRECTA", "INTREBARE"}
    for text in variants.values():
        assert isinstance(text, str)
        assert len(text) > 0


def test_get_variants_categorie_inexistenta_ridica_eroare_explicita():
    """Contract sectiunea 7.2: categorie inexistenta -> eroare explicita, nu exceptie ascunsa."""
    with pytest.raises(ValueError, match="necunoscută"):
        get_variants("NEINCREDERE_PRODUS")

    with pytest.raises(ValueError, match="necunoscută"):
        get_variants("CATEGORIE_INVENTATA")
