"""
Safety Validation pentru ObjectionEngine — Decizia 4 + Decizia 5
(`21-objection-engine-decizii-preliminare.md`, 17 august 2026).

Model pe 3 niveluri, confirmat de owner:
- BLOCK: răspunsul nu poate fi persistat/trimis.
- PARTIAL_VALIDATION: semnalat, dar nu blocat — acoperire cunoscută
  ca parțială.
- HUMAN_REVIEW: semnalat pentru verificare umană explicită, nu blocat
  automat.

DECLARAȚIE EXPLICITĂ DE LIMITARE (obligatorie, contract secțiunea 5.2):
sistemul nu revendică detectarea deterministă a riscurilor care necesită
înțelegere semantică, verificarea adevărului factual sau context
conversațional istoric. Orice limitare identificată rămâne explicit
documentată și nu este prezentată ca protecție completă.
"""

import re
from dataclasses import dataclass
from typing import List, Literal, Optional

ValidationLevel = Literal["PASS", "BLOCK", "PARTIAL_VALIDATION", "HUMAN_REVIEW"]

DISCLAIMER_TEXT = "Rezultatele variază de la persoană la persoană și nu sunt garantate."

# --- BLOCK: promisiuni nerealiste / garantare rezultate ---
# Notă: NU folosim substringul generic "garant", pentru că apare legitim
# în texte factuale (ex. "investiție garantată prin politica de retur",
# text canonic aprobat pentru INCREDERE_STRUCTURA). Țintim exact tiparul
# de promisiune a unui rezultat PERSOANEI, nu descrieri structurale.
_GUARANTEE_KEYWORDS = [
    "garantez", "îți garantez", "iti garantez",
    "sigur vei", "100% vei", "cu siguranță vei", "cu siguranta vei",
]

# --- BLOCK: presiune financiară ---
_FINANCIAL_PRESSURE_KEYWORDS = [
    "trebuie să investești acum",
    "prețul crește",
    "prețul va crește",
]

# --- BLOCK: "trebuie să decizi acum" / urgență artificială ---
_URGENCY_KEYWORDS = [
    "acum sau niciodată",
    "doar azi",
    "ultima șansă",
    "nu rata",
    "trebuie să decizi acum",
]

# --- BLOCK: exploatarea vulnerabilității — derivat din audit real
# (biblioteca-experientei-v1-CONSOLIDAT.md, secțiunea 4) ---
_VULNERABILITY_EXPLOITATION_KEYWORDS = [
    "nicio valoare",
    "vei rămâne în stradă",
    "dorul de copii",
]

# --- HUMAN_REVIEW: testimoniale/dovezi suspecte, neverificabile ---
_UNVERIFIED_CLAIM_KEYWORDS = [
    "studiile arată",
    "studii arată",
    "cercetările arată",
    "conform cercetărilor",
    "conform studiilor",
]

# --- HUMAN_REVIEW: markeri de insistență, folosiți doar dacă
# objection_text conține un refuz explicit ---
_PUSHBACK_KEYWORDS = ["măcar încearcă", "gândește-te din nou", "dar totuși"]
_EXPLICIT_REFUSAL_KEYWORDS = [
    "nu, mulțumesc", "nu multumesc", "nu mă interesează", "nu ma intereseaza",
    "nu vreau",
]

# --- Decizia 5: detectare afirmație financiară (valoare + monedă + context) ---
_CURRENCY_PATTERN = r"(lei|ron|euro|eur)"
_FINANCIAL_CONTEXT_PATTERN = r"(venit|câștig|castig|lunar|pe lună|pe luna|\ban\b|pe an)"
_NUMBER_PATTERN = r"\d[\d.,]*"

# --- PARTIAL_VALIDATION: INCREDERE_STRUCTURA trebuie să confirme direct ---
_DIRECT_DISCLOSURE_MARKERS = ["nu, nu e piramidă", "nu e piramidă", "da, facem parte", "nu, nu este o piramida"]
_EVASION_MARKERS = ["de ce întrebi", "de ce intrebi", "hai să vedem mai întâi"]


@dataclass(frozen=True)
class ValidationResult:
    """Rezultatul Safety Validation pentru un `response_text`.

    Attributes:
        level: Nivelul rezultat — "PASS", "BLOCK", "PARTIAL_VALIDATION"
            sau "HUMAN_REVIEW".
        reason: Explicație scurtă, obligatorie dacă `level != "PASS"`.
    """

    level: ValidationLevel
    reason: Optional[str] = None


def _contains_any(text_lower: str, keywords: List[str]) -> bool:
    return any(keyword in text_lower for keyword in keywords)


def _has_financial_claim(text_lower: str) -> bool:
    """Detectează o afirmație financiară: cifră + monedă + context financiar.

    Args:
        text_lower: Textul, deja normalizat la minuscule.

    Returns:
        True dacă textul conține combinația (Decizia 5).
    """
    has_number = re.search(_NUMBER_PATTERN, text_lower) is not None
    has_currency = re.search(_CURRENCY_PATTERN, text_lower) is not None
    has_context = re.search(_FINANCIAL_CONTEXT_PATTERN, text_lower) is not None
    return has_number and has_currency and has_context


def validate_response(
    response_text: str, objection_category: str, objection_text: str
) -> ValidationResult:
    """Validează un răspuns înainte de persistare (Decizia 4 + Decizia 5).

    Args:
        response_text: Textul final al răspunsului (posibil editat de lider).
        objection_category: Categoria obiecției (una din cele 13).
        objection_text: Textul original al obiecției — folosit doar pentru
            regula de "ocolire a refuzului explicit" (secțiunea 5.2).

    Returns:
        `ValidationResult` cu nivelul și motivul. `level == "BLOCK"`
        înseamnă că răspunsul NU poate fi persistat — orice alt nivel
        permite persistarea (cu sau fără semnalare).
    """
    text_lower = response_text.lower()
    objection_lower = objection_text.lower()

    # --- BLOCK, în ordinea din contract ---
    if _contains_any(text_lower, _GUARANTEE_KEYWORDS):
        return ValidationResult("BLOCK", "Promisiune nerealistă / garantare rezultate.")

    if _contains_any(text_lower, _FINANCIAL_PRESSURE_KEYWORDS):
        return ValidationResult("BLOCK", "Presiune financiară detectată.")

    if _contains_any(text_lower, _URGENCY_KEYWORDS):
        return ValidationResult("BLOCK", "Urgență artificială / presiune de tip 'decide acum'.")

    if _contains_any(text_lower, _VULNERABILITY_EXPLOITATION_KEYWORDS):
        return ValidationResult("BLOCK", "Tipar de exploatare a vulnerabilității, identificat în audit.")

    if _has_financial_claim(text_lower) and DISCLAIMER_TEXT.lower() not in text_lower:
        return ValidationResult(
            "BLOCK",
            "Textul conține o afirmație privind venituri fără disclaimerul obligatoriu.",
        )

    # --- PARTIAL_VALIDATION ---
    if objection_category == "INCREDERE_STRUCTURA":
        is_short_pure_redirect = len(response_text.strip()) < 60
        if (
            _contains_any(text_lower, _EVASION_MARKERS)
            and not _contains_any(text_lower, _DIRECT_DISCLOSURE_MARKERS)
            and is_short_pure_redirect
        ):
            return ValidationResult(
                "PARTIAL_VALIDATION",
                "Răspunsul la INCREDERE_STRUCTURA nu conține confirmare directă.",
            )

    # --- HUMAN_REVIEW ---
    if _contains_any(text_lower, _UNVERIFIED_CLAIM_KEYWORDS):
        return ValidationResult("HUMAN_REVIEW", "Afirmație neverificabilă (tip testimonial/studiu).")

    if _contains_any(objection_lower, _EXPLICIT_REFUSAL_KEYWORDS) and _contains_any(
        text_lower, _PUSHBACK_KEYWORDS
    ):
        return ValidationResult(
            "HUMAN_REVIEW",
            "Posibilă ocolire a unui refuz explicit al prospectului.",
        )

    return ValidationResult("PASS")
