"""Teste unitare pentru PartnerAgent — cu mock, fara DB reala."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.partner.partner_engine import PartnerDiagnostic
from src.agents.partner.partner_agent import PartnerAgent


@pytest.fixture
def fake_engine():
    return MagicMock()


@pytest.fixture
def agent(fake_engine):
    return PartnerAgent(partner_engine=fake_engine)


def test_request_diagnostic_deleaga_la_engine(agent, fake_engine):
    """request_diagnostic deleaga integral la PartnerEngine."""
    partner_id = uuid4()
    owner_id = uuid4()
    fake_engine.generate_diagnostic.return_value = PartnerDiagnostic(
        partner_id=partner_id, owner_id=owner_id,
        diagnostic_type="CLARITY", message="[STUB] Mesaj de claritate.",
    )

    diagnostic = agent.request_diagnostic(partner_id, owner_id, "CLARITY")

    fake_engine.generate_diagnostic.assert_called_once_with(partner_id, owner_id, "CLARITY")
    assert diagnostic.diagnostic_type == "CLARITY"


def test_present_diagnostic_formateaza_corect(agent):
    """present_diagnostic include tipul si mesajul in text."""
    diagnostic = PartnerDiagnostic(
        partner_id=uuid4(), owner_id=uuid4(),
        diagnostic_type="CLARITY", message="[STUB] Mesaj de claritate.",
    )
    text = agent.present_diagnostic(diagnostic)
    assert "CLARITY" in text
    assert "[STUB]" in text


def test_confirm_and_send_deleaga_la_engine(agent, fake_engine):
    """confirm_and_send deleaga integral, PartnerAgent nu scrie singur."""
    partner_id = uuid4()
    owner_id = uuid4()

    agent.confirm_and_send(partner_id, owner_id, confirmed=True)

    fake_engine.confirm_and_complete.assert_called_once_with(partner_id, owner_id, confirmed=True)


def test_get_recent_scores_filtreaza_prin_owner_id():
    """
    get_recent_scores e READ-ONLY si FILTREAZA corect prin owner_id.

    Acest test a fost extins dupa ce testul de integrare a prins un bug
    real: lipsa filtrarii dupa owner_id (scurgere de date intre lideri).
    """
    fake_engine = MagicMock()
    agent = PartnerAgent(partner_engine=fake_engine)
    target_owner_id = uuid4()

    with patch("src.agents.partner.partner_agent.get_connection") as mock_get_conn:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [("PDI", 1.0), ("PIP", 1.0)]
        mock_cur.__enter__.return_value = mock_cur
        mock_cur.__exit__.return_value = False
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = False
        mock_get_conn.return_value = mock_conn

        scores = agent.get_recent_scores(target_owner_id)

        executed_sql = mock_cur.execute.call_args[0][0]
        executed_params = mock_cur.execute.call_args[0][1]

        assert "SELECT" in executed_sql
        assert "INSERT" not in executed_sql
        assert "UPDATE" not in executed_sql
        assert "JOIN partners" in executed_sql
        assert target_owner_id in executed_params
        assert scores == {"PDI": 1.0, "PIP": 1.0}
