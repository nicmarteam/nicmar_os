"""Teste unitare pentru FollowUpEngine — cu mock, fara DB reala."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.rule.rule_engine import RuleEngine, FollowUpRuleEvaluationResult
from src.engines.followup.followup_engine import (
    FollowUpEngine, FollowUpDuplicateError, InvalidTransitionError,
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
    return FollowUpEngine(rule_engine=fake_rule_engine)


def test_create_from_trigger_esueaza_daca_duplicat(engine, fake_rule_engine):
    """create_from_trigger esueaza daca RuleEngine spune FOLLOWUP_DUPLICATE."""
    fake_rule_engine.evaluate_followup.return_value = FollowUpRuleEvaluationResult(
        rule_code="RULE-FOLLOWUP-DUPLICATE-001", rule_version="1.0.0",
        decision_outcome="FOLLOWUP_DUPLICATE", had_pending_duplicate=True,
    )
    with pytest.raises(FollowUpDuplicateError):
        engine.create_from_trigger(owner_id=uuid4(), contact_id=uuid4(), conversation_id=uuid4())


def test_create_from_trigger_reuseste_si_persista_dis(engine, fake_rule_engine):
    """create_from_trigger reuseste si persista DIS imediat (nu la finalizare)."""
    fake_rule_engine.evaluate_followup.return_value = FollowUpRuleEvaluationResult(
        rule_code="RULE-FOLLOWUP-DUPLICATE-001", rule_version="1.0.0",
        decision_outcome="FOLLOWUP_READY", had_pending_duplicate=False,
    )
    followup_id = uuid4()
    owner_id = uuid4()
    contact_id = uuid4()
    conversation_id = uuid4()
    dis_kpi_id = uuid4()

    with patch("src.engines.followup.followup_engine.get_connection") as mock_get_conn:
        mock_get_conn.return_value = make_mock_conn([
            (followup_id, owner_id, contact_id, conversation_id, "PENDING"),
            (dis_kpi_id,),
        ])
        followup = engine.create_from_trigger(owner_id, contact_id, conversation_id)

    assert followup.status == "PENDING"
    assert followup.id == followup_id


def test_complete_followup_fara_confirmare_esueaza(engine):
    """complete_followup fara confirmed=True ridica HumanConfirmationRequiredError."""
    with pytest.raises(HumanConfirmationRequiredError):
        engine.complete_followup(followup_id=uuid4(), owner_id=uuid4(), confirmed=False)


def test_tranzitie_interzisa_completed_e_terminala(engine):
    """COMPLETED e stare terminala — nicio tranzitie ulterioara nu e permisa."""
    with patch("src.engines.followup.followup_engine.get_connection") as mock_get_conn:
        mock_get_conn.return_value = make_mock_conn([("COMPLETED",)])
        with pytest.raises(InvalidTransitionError):
            engine._set_status(followup_id=uuid4(), owner_id=uuid4(), new_status="PENDING")
