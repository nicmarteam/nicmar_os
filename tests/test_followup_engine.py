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


def make_mock_conn_fetchall(fetchall_result):
    """La fel ca make_mock_conn, dar pentru metode care folosesc fetchall(), nu fetchone()."""
    mock_cur = MagicMock()
    mock_cur.fetchall.return_value = fetchall_result
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__.return_value = False
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = False
    return mock_conn


class TestListPendingFollowups:
    """
    4 scenarii cerute explicit: izolare owner A/B, lista goala, mai
    multe follow-up-uri relevante. Toate READ-ONLY, mock la nivel de
    SQL — izolarea reala se verifica separat pe PostgreSQL real
    (v. test_real_postgres.py), aici verificam doar ca metoda
    construieste corect lista din randurile primite.
    """

    def test_owner_fara_followup_returneaza_lista_goala(self, engine):
        with patch("src.engines.followup.followup_engine.get_connection") as mock_get_conn:
            mock_get_conn.return_value = make_mock_conn_fetchall([])
            result = engine.list_pending_followups(owner_id=uuid4())
        assert result == []

    def test_returneaza_toate_followup_urile_owner_ului(self, engine):
        owner_id = uuid4()
        fid1, fid2 = uuid4(), uuid4()
        contact1, contact2 = uuid4(), uuid4()
        conv1, conv2 = uuid4(), uuid4()

        with patch("src.engines.followup.followup_engine.get_connection") as mock_get_conn:
            mock_get_conn.return_value = make_mock_conn_fetchall([
                (fid1, owner_id, contact1, conv1, "PENDING"),
                (fid2, owner_id, contact2, conv2, "PENDING"),
            ])
            result = engine.list_pending_followups(owner_id=owner_id)

        assert len(result) == 2
        assert {f.id for f in result} == {fid1, fid2}
        assert all(f.owner_id == owner_id for f in result)
        assert all(f.status == "PENDING" for f in result)

    def test_query_filtreaza_prin_owner_id_ca_parametru(self, engine):
        """
        Verifica explicit ca owner_id ajunge ca parametru real in query
        (nu doar ca metoda 'pare' sa filtreze) — aceeasi disciplina ca
        la bug-ul gasit anterior la PartnerAgent.get_recent_scores.
        """
        target_owner_id = uuid4()
        with patch("src.engines.followup.followup_engine.get_connection") as mock_get_conn:
            mock_conn = make_mock_conn_fetchall([])
            mock_get_conn.return_value = mock_conn
            engine.list_pending_followups(owner_id=target_owner_id)

            cur = mock_conn.cursor.return_value
            executed_sql = cur.execute.call_args[0][0]
            executed_params = cur.execute.call_args[0][1]

        assert "WHERE owner_id = %s" in executed_sql
        assert "status = 'PENDING'" in executed_sql
        assert target_owner_id in executed_params

    def test_doar_pending_nu_completed_sau_postponed(self, engine):
        """
        Query-ul insusi filtreaza status='PENDING' — testul verifica
        ca acest filtru e prezent in SQL (owner B "vede doar ale lui"
        + "doar PENDING" sunt ambele in aceeasi clauza WHERE).
        """
        with patch("src.engines.followup.followup_engine.get_connection") as mock_get_conn:
            mock_conn = make_mock_conn_fetchall([])
            mock_get_conn.return_value = mock_conn
            engine.list_pending_followups(owner_id=uuid4())

            cur = mock_conn.cursor.return_value
            executed_sql = cur.execute.call_args[0][0]

        assert "'PENDING'" in executed_sql
        assert "COMPLETED" not in executed_sql
        assert "POSTPONED" not in executed_sql
