"""
Teste RED pentru PartnerEngine.create_partner() / PartnerAgent.create_partner()
— Decizia 32, cu mock, fara DB reala.

Sursa: 32-partner-create-contract.md.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.partner.partner_engine import (
    Partner, PartnerEngine, PartnerAccessDeniedError,
)
from src.agents.partner.partner_agent import PartnerAgent


def _make_cursor(fetchone_results):
    mock_cur = MagicMock()
    mock_cur.fetchone.side_effect = fetchone_results
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__.return_value = False
    return mock_cur


def _make_conn(mock_cur):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = False
    return mock_conn


@pytest.fixture
def rule_engine():
    return MagicMock()


@pytest.fixture
def engine(rule_engine):
    return PartnerEngine(rule_engine=rule_engine)


# ----------------------------------------------------------------------
# PartnerEngine.create_partner() — ownership + status hardcodat
# ----------------------------------------------------------------------


def test_create_partner_verifica_ownership_contact_intai(engine):
    """SELECT 1 FROM contacts WHERE id=... AND owner_id=... esueaza -> PartnerAccessDeniedError."""
    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([None])  # ownership check esueaza
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(PartnerAccessDeniedError):
            engine.create_partner(owner_id=uuid4(), contact_id=uuid4())

        assert mock_cur.execute.call_count == 1  # doar verificarea, fara INSERT


def test_create_partner_ownership_verifica_owner_id_in_where(engine):
    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([None])
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(PartnerAccessDeniedError):
            engine.create_partner(owner_id=uuid4(), contact_id=uuid4())

        executed_sql = mock_cur.execute.call_args_list[0][0][0]
        assert "contacts" in executed_sql
        assert "owner_id" in executed_sql


def test_create_partner_status_hardcodat_activated(engine):
    owner_id = uuid4()
    contact_id = uuid4()
    partner_id = uuid4()

    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn, \
         patch.object(PartnerEngine, "_emit_event") as mock_emit:
        mock_cur = _make_cursor([
            (1,),  # ownership OK
            (partner_id, owner_id, contact_id, "ACTIVATED", "BRONZE"),  # INSERT RETURNING
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        partner = engine.create_partner(owner_id=owner_id, contact_id=contact_id)

        assert partner.status == "ACTIVATED"
        insert_sql = mock_cur.execute.call_args_list[1][0][0]
        assert "'ACTIVATED'" in insert_sql  # literal, nu parametru


def test_create_partner_returneaza_partner_complet(engine):
    owner_id = uuid4()
    contact_id = uuid4()
    partner_id = uuid4()

    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn, \
         patch.object(PartnerEngine, "_emit_event"):
        mock_cur = _make_cursor([
            (1,), (partner_id, owner_id, contact_id, "ACTIVATED", "BRONZE"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        partner = engine.create_partner(owner_id=owner_id, contact_id=contact_id)

        assert partner == Partner(
            id=partner_id, owner_id=owner_id, contact_id=contact_id,
            status="ACTIVATED", partner_level="BRONZE",
        )


def test_create_partner_emite_eveniment_partner_created(engine):
    owner_id = uuid4()
    contact_id = uuid4()
    partner_id = uuid4()

    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn, \
         patch.object(PartnerEngine, "_emit_event") as mock_emit:
        mock_cur = _make_cursor([
            (1,), (partner_id, owner_id, contact_id, "ACTIVATED", "BRONZE"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.create_partner(owner_id=owner_id, contact_id=contact_id)

        mock_emit.assert_called_once()
        args = mock_emit.call_args[0]
        assert args[0] == "PartnerCreated"
        assert args[1] == partner_id


def test_create_partner_nu_apeleaza_record_pdi_pip(engine):
    """Creare != finalizare — PDI/PIP raman exclusiv la confirm_and_complete()."""
    owner_id = uuid4()
    contact_id = uuid4()
    partner_id = uuid4()

    with patch("src.engines.partner.partner_engine.get_connection") as mock_get_conn, \
         patch.object(PartnerEngine, "_emit_event"), \
         patch.object(PartnerEngine, "_record_pdi_pip_scores") as mock_pdi_pip:
        mock_cur = _make_cursor([
            (1,), (partner_id, owner_id, contact_id, "ACTIVATED", "BRONZE"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.create_partner(owner_id=owner_id, contact_id=contact_id)

        mock_pdi_pip.assert_not_called()


# ----------------------------------------------------------------------
# PartnerAgent.create_partner() — delegare simpla
# ----------------------------------------------------------------------


def test_partner_agent_create_partner_deleaga_la_engine():
    fake_engine = MagicMock()
    fake_partner = Partner(
        id=uuid4(), owner_id=uuid4(), contact_id=uuid4(),
        status="ACTIVATED", partner_level="BRONZE",
    )
    fake_engine.create_partner.return_value = fake_partner
    agent = PartnerAgent(partner_engine=fake_engine)

    owner_id = uuid4()
    contact_id = uuid4()
    result = agent.create_partner(owner_id=owner_id, contact_id=contact_id)

    fake_engine.create_partner.assert_called_once_with(owner_id, contact_id)
    assert result == fake_partner
