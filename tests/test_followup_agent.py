"""Teste unitare pentru FollowUpAgent — cu mock, fara DB reala."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.followup.followup_engine import FollowUp
from src.agents.followup.followup_agent import FollowUpAgent


@pytest.fixture
def fake_engine():
    return MagicMock()


@pytest.fixture
def agent(fake_engine):
    return FollowUpAgent(followup_engine=fake_engine)


def test_present_followup_list_lista_goala(agent):
    """present_followup_list, cu lista goala, returneaza mesaj clar."""
    text = agent.present_followup_list([])
    assert "Niciun follow-up" in text


def test_present_followup_list_cu_followup(agent):
    """present_followup_list include contact_id in text pentru fiecare follow-up."""
    f1 = FollowUp(id=uuid4(), owner_id=uuid4(), contact_id=uuid4(),
                  conversation_id=uuid4(), status="PENDING")
    text = agent.present_followup_list([f1])
    assert str(f1.contact_id) in text


def test_confirm_completion_deleaga_la_engine(agent, fake_engine):
    """confirm_completion deleaga integral la FollowUpEngine, nu scrie singur."""
    followup_id = uuid4()
    owner_id = uuid4()
    fake_engine.complete_followup.return_value = FollowUp(
        id=followup_id, owner_id=owner_id, contact_id=uuid4(),
        conversation_id=uuid4(), status="COMPLETED",
    )

    result = agent.confirm_completion(followup_id, owner_id, confirmed=True)

    fake_engine.complete_followup.assert_called_once_with(followup_id, owner_id, confirmed=True)
    assert result.status == "COMPLETED"


def test_request_postpone_deleaga_la_engine(agent, fake_engine):
    """request_postpone deleaga integral la FollowUpEngine."""
    followup_id = uuid4()
    owner_id = uuid4()
    fake_engine.postpone_followup.return_value = FollowUp(
        id=followup_id, owner_id=owner_id, contact_id=uuid4(),
        conversation_id=uuid4(), status="POSTPONED",
    )

    result = agent.request_postpone(followup_id, owner_id)

    fake_engine.postpone_followup.assert_called_once_with(followup_id, owner_id)
    assert result.status == "POSTPONED"


def test_get_recent_dis_score_e_readonly():
    """get_recent_dis_score executa strict SELECT, niciodata INSERT/UPDATE."""
    fake_engine = MagicMock()
    agent = FollowUpAgent(followup_engine=fake_engine)

    with patch("src.agents.followup.followup_agent.get_connection") as mock_get_conn:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = (2.0,)
        mock_cur.__enter__.return_value = mock_cur
        mock_cur.__exit__.return_value = False
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = False
        mock_get_conn.return_value = mock_conn

        score = agent.get_recent_dis_score(owner_id=uuid4())

        executed_sql = mock_cur.execute.call_args[0][0]
        assert "SELECT" in executed_sql
        assert "INSERT" not in executed_sql
        assert "UPDATE" not in executed_sql
        assert score == 2.0
