"""
Clasificator determinist de obiecții — mecanismul de potrivire confirmat
în Decizia 2 (`21-objection-engine-decizii-preliminare.md`, 17 august 2026).

Acoperă STRICT cele 6 categorii cu acoperire bună din auditul de sursă:
`PRET`, `TIMP`, `INCREDERE_STRUCTURA`, `FAMILIE_SUPORT`, `AMANARE`,
`FRICA_TEHNOLOGIE`. Restul categoriilor din Biblioteca Experienței rămân
documentate, dar NU sunt ținta clasificării automate în v1 — un text ce
corespunde uneia din ele trebuie să returneze `None`, nu o ghicire.

Cuvintele-cheie provin exclusiv din citate reale găsite în materialul
sursă (verificat prin extragere directă, nu inventate) — v. audit
Decizia 2. Nu se adaugă cuvinte-cheie suplimentare fără o nouă
verificare de sursă.

Acesta e doar mecanismul de clasificare, izolat de restul
`ObjectionEngine` (selecția variantelor de răspuns, persistarea în DB) —
acele piese depind de Deciziile 3-5, încă deschise.
"""

import re
import unicodedata
from typing import Dict, List, Optional

# Cuvinte-cheie per categorie, EXCLUSIV din citate reale confirmate în
# auditul Deciziei 2 (nu se adaugă termeni noi fără o nouă verificare
# de sursă). Ordinea listei = ordinea de verificare (prima potrivire
# câștigă) — text ambiguu ce ar potrivi mai multe categorii primește
# categoria cu prioritate mai mare în această listă.
_KEYWORDS: Dict[str, List[str]] = {
    "INCREDERE_STRUCTURA": ["piramida", "piramidă", "mlm", "prea frumos"],
    "FRICA_TEHNOLOGIE": ["nu ma pricep la tehnologie", "frica de tehnologie", "nu ma pricep deloc"],
    "FAMILIE_SUPORT": ["nu ma sustine", "nu ma sprijina", "rade de mine", "familia nu"],
    "AMANARE": ["nu e momentul", "ma mai gandesc", "mai astept"],
    "PRET": ["pret", "scump"],
    "TIMP": ["nu am timp", "n-am timp"],
}


def _normalize(text: str) -> str:
    """Normalizează textul pentru potrivire: minuscule, fără diacritice.

    Args:
        text: Textul brut al obiecției.

    Returns:
        Textul normalizat (minuscule, diacritice românești eliminate,
        spații de la capete tăiate).
    """
    lowered = text.strip().lower()
    decomposed = unicodedata.normalize("NFD", lowered)
    without_diacritics = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", without_diacritics)


def classify_objection(text: str) -> Optional[str]:
    """Clasifică o obiecție într-una din cele 6 categorii eligibile v1.

    Args:
        text: Textul liber al obiecției, exact cum a fost introdus de
            lider (v. `05-competente-37-motor1.md`, pasul "Clarificarea").

    Returns:
        Codul categoriei (`PRET`, `TIMP`, `INCREDERE_STRUCTURA`,
        `FAMILIE_SUPORT`, `AMANARE`, `FRICA_TEHNOLOGIE`) dacă textul
        conține un cuvânt-cheie confirmat din sursă, altfel `None`.
        Niciodată nu returnează o categorie din afara celor 6 eligibile
        (ex. `NEINCREDERE_PRODUS`, eliminată complet din listă).
    """
    if not text or not text.strip():
        return None

    normalized = _normalize(text)

    for category, keywords in _KEYWORDS.items():
        for keyword in keywords:
            if _normalize(keyword) in normalized:
                return category

    return None
