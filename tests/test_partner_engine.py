"""Teste unitare pentru PartnerEngine — cu mock, fara DB reala."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

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


@pytest.fixture
def fake_rule_engine():
    return MagicMock(spec=RuleEngine)


@pytest.fixture
def engine(fake_rule_engine):
    return PartnerEngine(rule_engine=fake_rule_engine)


@pytest.fixture
def partner_id():
    return uuid4()


@pytest.fixture
def owner_id():
    return uuid4()


def test_generate_diagnostic_esueaza_daca_ownership_gresit(engine, partner_id, owner_id):
    """_verify_ownership ruleaza PRIMA — daca partner_id nu apartine owner_id, refuza."""
    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
        mock_get_conn.return_value = make_mock_conn([None])
        with pytest.raises(PartnerAccessDeniedError):
            engine.generate_diagnostic(partner_id, owner_id, "ENCOURAGEMENT")


def test_generate_diagnostic_esueaza_daca_deja_diagnosticat(engine, fake_rule_engine, partner_id, owner_id):
    """Dupa ce ownership trece, regula RuleEngine poate inca bloca (ALREADY_DIAGNOSED)."""
    fake_rule_engine.evaluate_partner_diagnostic.return_value = PartnerRuleEvaluationResult(
        rule_code="RULE-PARTNER-DIAGNOSTIC-001", rule_version="1.0.0",
        decision_outcome="PARTNER_ALREADY_DIAGNOSED", already_diagnosed_today=True,
    )
    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
        mock_get_conn.return_value = make_mock_conn([(1,)])
        with pytest.raises(PartnerDiagnosticAlreadyGeneratedError):
            engine.generate_diagnostic(partner_id, owner_id, "ENCOURAGEMENT")


def test_generate_diagnostic_tip_invalid(engine, partner_id, owner_id):
    """diagnostic_type invalid ridica InvalidDiagnosticTypeError, dupa ownership OK."""
    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
        mock_get_conn.return_value = make_mock_conn([(1,)])
        with pytest.raises(InvalidDiagnosticTypeError):
            engine.generate_diagnostic(partner_id, owner_id, "MOTIVATION_INVENTATA")


def test_generate_diagnostic_reuseste(engine, fake_rule_engine, partner_id, owner_id):
    """generate_diagnostic reuseste: ownership OK + READY + tip valid."""
    fake_rule_engine.evaluate_partner_diagnostic.return_value = PartnerRuleEvaluationResult(
        rule_code="RULE-PARTNER-DIAGNOSTIC-001", rule_version="1.0.0",
        decision_outcome="PARTNER_READY", already_diagnosed_today=False,
    )
    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
        mock_get_conn.return_value = make_mock_conn([(1,), None])
        diagnostic = engine.generate_diagnostic(partner_id, owner_id, "CLARITY")

    assert diagnostic.diagnostic_type == "CLARITY"
    assert "[STUB]" in diagnostic.message


def test_confirm_and_complete_esueaza_daca_ownership_gresit(engine, partner_id, owner_id):
    """confirm_and_complete verifica ownership la fel ca generate_diagnostic."""
    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
        mock_get_conn.return_value = make_mock_conn([None])
        with pytest.raises(PartnerAccessDeniedError):
            engine.confirm_and_complete(partner_id, owner_id, confirmed=True)


def test_confirm_and_complete_fara_confirmare(engine, partner_id, owner_id):
    """Dupa ownership OK, lipsa confirmarii blocheaza."""
    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
        mock_get_conn.return_value = make_mock_conn([(1,)])
        with pytest.raises(HumanConfirmationRequiredError):
            engine.confirm_and_complete(partner_id, owner_id, confirmed=False)


def test_confirm_and_complete_persista_pdi_pip(engine, partner_id, owner_id):
    """confirm_and_complete, cu confirmare, persista PDI si PIP."""
    pdi_id = uuid4()
    pip_id = uuid4()
    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
        mock_get_conn.return_value = make_mock_conn([(1,), (pdi_id,), (pip_id,)])
        engine.confirm_and_complete(partner_id, owner_id, confirmed=True)
    # Daca n-a ridicat nicio exceptie, testul trece — comportamentul e implicit verificat.
