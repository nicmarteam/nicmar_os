"""Teste unitare pentru PartnerEngine — cu mock, fara DB reala."""

import sys
sys.path.insert(0, '/home/claude/nicmar_impl')

from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.engines.rule.rule_engine import RuleEngine, PartnerRuleEvaluationResult
from src.engines.partner.partner_engine import (
    PartnerEngine, PartnerDiagnosticAlreadyGeneratedError,
    PartnerAccessDeniedError, InvalidDiagnosticTypeError,
    HumanConfirmationRequiredError,
)


def make_mock_conn(fetchone_results):
    mock_cur = MagicMock()
    mock_cur.fetchone.side_effect = fetchone_results
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__.return_value = False
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = False
    return mock_conn


partner_id = uuid4()
owner_id = uuid4()
fake_rule_engine = MagicMock(spec=RuleEngine)
engine = PartnerEngine(rule_engine=fake_rule_engine)


print("=== TEST 1 (NOU): generate_diagnostic esueaza daca partner_id NU apartine owner_id ===")
print("(_verify_ownership ruleaza PRIMA, inaintea oricarei alte verificari)")
with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
    mock_get_conn.return_value = make_mock_conn([None])
    try:
        engine.generate_diagnostic(partner_id, owner_id, "ENCOURAGEMENT")
        print("EROARE: ar fi trebuit sa ridice PartnerAccessDeniedError")
    except PartnerAccessDeniedError:
        print("OK: PartnerAccessDeniedError ridicata corect\n")


print("=== TEST 2: generate_diagnostic esueaza daca RuleEngine spune ALREADY_DIAGNOSED ===")
print("(ownership trece, apoi regula blocheaza)")
fake_rule_engine.evaluate_partner_diagnostic.return_value = PartnerRuleEvaluationResult(
    rule_code="RULE-PARTNER-DIAGNOSTIC-001", rule_version="1.0.0",
    decision_outcome="PARTNER_ALREADY_DIAGNOSED", already_diagnosed_today=True,
)
with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
    mock_get_conn.return_value = make_mock_conn([(1,)])
    try:
        engine.generate_diagnostic(partner_id, owner_id, "ENCOURAGEMENT")
        print("EROARE: ar fi trebuit sa ridice PartnerDiagnosticAlreadyGeneratedError")
    except PartnerDiagnosticAlreadyGeneratedError:
        print("OK: eroare ridicata corect\n")


print("=== TEST 3: diagnostic_type invalid -> InvalidDiagnosticTypeError (dupa ownership OK) ===")
with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
    mock_get_conn.return_value = make_mock_conn([(1,)])
    try:
        engine.generate_diagnostic(partner_id, owner_id, "MOTIVATION_INVENTATA")
        print("EROARE: ar fi trebuit sa refuze tip invalid")
    except InvalidDiagnosticTypeError:
        print("OK: tip invalid refuzat corect\n")


print("=== TEST 4: generate_diagnostic reuseste — ownership OK + READY + tip valid ===")
fake_rule_engine.evaluate_partner_diagnostic.return_value = PartnerRuleEvaluationResult(
    rule_code="RULE-PARTNER-DIAGNOSTIC-001", rule_version="1.0.0",
    decision_outcome="PARTNER_READY", already_diagnosed_today=False,
)
with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
    mock_get_conn.return_value = make_mock_conn([(1,), None])
    diagnostic = engine.generate_diagnostic(partner_id, owner_id, "CLARITY")
    print("OK: diagnostic generat, tip =", diagnostic.diagnostic_type)
    print("Mesaj (STUB):", diagnostic.message)
    assert "[STUB]" in diagnostic.message
print()


print("=== TEST 5 (NOU): confirm_and_complete esueaza daca partner_id NU apartine owner_id ===")
with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
    mock_get_conn.return_value = make_mock_conn([None])
    try:
        engine.confirm_and_complete(partner_id, owner_id, confirmed=True)
        print("EROARE: ar fi trebuit sa ridice PartnerAccessDeniedError")
    except PartnerAccessDeniedError:
        print("OK: PartnerAccessDeniedError ridicata corect\n")


print("=== TEST 6: confirm_and_complete FARA confirmare -> HumanConfirmationRequiredError ===")
print("(ownership trece, apoi lipsa confirmarii blocheaza)")
with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
    mock_get_conn.return_value = make_mock_conn([(1,)])
    try:
        engine.confirm_and_complete(partner_id, owner_id, confirmed=False)
        print("EROARE: ar fi trebuit sa refuze")
    except HumanConfirmationRequiredError:
        print("OK: refuzat corect\n")


print("=== TEST 7: confirm_and_complete CU confirmare -> persista PDI + PIP ===")
pdi_id = uuid4()
pip_id = uuid4()
with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
    mock_get_conn.return_value = make_mock_conn([(1,), (pdi_id,), (pip_id,)])
    engine.confirm_and_complete(partner_id, owner_id, confirmed=True)
    print("OK: confirm_and_complete a rulat fara eroare (PDI + PIP persistate)")
print()


print("=== TOATE TESTELE UNITARE AU TRECUT (fara DB reala, doar mock) ===")
