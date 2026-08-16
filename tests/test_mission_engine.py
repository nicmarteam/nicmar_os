"""Teste unitare pentru MissionEngine — cu mock, fara DB reala."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.rule.rule_engine import RuleEngine, RuleEvaluationResult
from src.engines.mission.mission_engine import (
    MissionEngine, MissionNotReadyError, InvalidTransitionError,
    HumanConfirmationRequiredError,
)


def make_mock_conn(fetchone_results):
    """Construieste o conexiune falsa care returneaza rezultatele date, pe rand."""
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
    return MissionEngine(rule_engine=fake_rule_engine)


def test_generate_mission_esueaza_daca_rule_engine_blocheaza(engine, fake_rule_engine):
    """generate_mission esueaza daca RuleEngine spune MISSION_BLOCKED."""
    fake_rule_engine.evaluate.return_value = RuleEvaluationResult(
        rule_code="RULE-MISSION-DAILY-001", rule_version="1.0.0",
        decision_outcome="MISSION_BLOCKED", active_mission_count=1,
    )
    with pytest.raises(MissionNotReadyError):
        engine.generate_mission(owner_id=uuid4(), title="Test")


def test_generate_mission_reuseste_daca_rule_engine_permite(engine, fake_rule_engine):
    """generate_mission reuseste daca RuleEngine spune MISSION_READY."""
    fake_rule_engine.evaluate.return_value = RuleEvaluationResult(
        rule_code="RULE-MISSION-DAILY-001", rule_version="1.0.0",
        decision_outcome="MISSION_READY", active_mission_count=0,
    )
    mission_id = uuid4()
    owner_id = uuid4()

    with patch("src.engines.mission.mission_engine.get_connection") as mock_get_conn:
        mock_get_conn.return_value = make_mock_conn([
            (mission_id, owner_id, "Test", "GENERATED"),
        ])
        mission = engine.generate_mission(owner_id=owner_id, title="Test")

    assert mission.status == "GENERATED"
    assert mission.id == mission_id


def test_start_mission_fara_confirmare_esueaza(engine):
    """start_mission fara confirmed=True ridica HumanConfirmationRequiredError."""
    with pytest.raises(HumanConfirmationRequiredError):
        engine.start_mission(mission_id=uuid4(), owner_id=uuid4(), confirmed=False)


def test_tranzitie_interzisa_generated_direct_completed(engine):
    """Nu se poate sari peste stari: GENERATED -> COMPLETED direct e interzis."""
    with patch("src.engines.mission.mission_engine.get_connection") as mock_get_conn:
        mock_get_conn.return_value = make_mock_conn([("GENERATED",)])
        with pytest.raises(InvalidTransitionError):
            engine._set_status(mission_id=uuid4(), owner_id=uuid4(), new_status="COMPLETED")
