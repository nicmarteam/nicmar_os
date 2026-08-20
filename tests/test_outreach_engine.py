"""
Teste RED pentru OutreachEngine — cu mock, fara DB reala.

Sursa: 46-prospectare-relationala-contract.md.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.outreach.outreach_engine import (
    OutreachEngine, OutreachAccessDeniedError, InvalidPurposeError,
    InvalidToneError, InvalidOutcomeError, OutcomeAlreadyRecordedError,
)
from src.engines.conversation.conversation_engine import Conversation


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
def conversation_engine_mock():
    return MagicMock()


@pytest.fixture
def engine(conversation_engine_mock):
    return OutreachEngine(conversation_engine=conversation_engine_mock)


# ----------------------------------------------------------------------
# create_outreach() — validare + creare
# ----------------------------------------------------------------------


def test_create_outreach_emite_event_outreach_sent(engine):
    owner_id = uuid4()
    contact_id = uuid4()
    outreach_id = uuid4()

    with patch("src.engines.outreach.outreach_engine.get_connection") as mock_get_conn, \
         patch.object(OutreachEngine, "_emit_event") as mock_emit:
        mock_cur = _make_cursor([
            (1,),  # ownership OK
            (outreach_id, owner_id, contact_id, "REFERRAL", "Salut!", "CALDA"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        outreach = engine.create_outreach(
            owner_id=owner_id, contact_id=contact_id, purpose="REFERRAL",
            message_text="Salut!", tone_used="CALDA",
        )

        assert outreach.id == outreach_id
        mock_emit.assert_called_once()
        args = mock_emit.call_args[0]
        assert args[0] == "OutreachSent"
        assert args[1] == outreach_id


def test_create_outreach_owner_gresit_ridica_eroare(engine):
    with patch("src.engines.outreach.outreach_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([None])  # ownership FAIL
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(OutreachAccessDeniedError):
            engine.create_outreach(
                owner_id=uuid4(), contact_id=uuid4(), purpose="REFERRAL",
                message_text="x", tone_used="CALDA",
            )


def test_create_outreach_purpose_invalid_ridica_eroare_fara_apel_db(engine):
    with patch("src.engines.outreach.outreach_engine.get_connection") as mock_get_conn:
        with pytest.raises(InvalidPurposeError):
            engine.create_outreach(
                owner_id=uuid4(), contact_id=uuid4(), purpose="COLD_CALL",
                message_text="x", tone_used="CALDA",
            )
        mock_get_conn.assert_not_called()


def test_create_outreach_tone_invalid_ridica_eroare_fara_apel_db(engine):
    with patch("src.engines.outreach.outreach_engine.get_connection") as mock_get_conn:
        with pytest.raises(InvalidToneError):
            engine.create_outreach(
                owner_id=uuid4(), contact_id=uuid4(), purpose="REFERRAL",
                message_text="x", tone_used="AGRESIVA",
            )
        mock_get_conn.assert_not_called()


# ----------------------------------------------------------------------
# record_outcome() — cardinalitate 0..1, handoff selectiv
# ----------------------------------------------------------------------


def test_record_outcome_invalid_ridica_eroare(engine):
    with patch("src.engines.outreach.outreach_engine.get_connection") as mock_get_conn:
        with pytest.raises(InvalidOutcomeError):
            engine.record_outcome(owner_id=uuid4(), outreach_id=uuid4(), outcome="MAYBE")
        mock_get_conn.assert_not_called()


def test_record_outcome_outreach_gresit_ridica_eroare(engine):
    with patch("src.engines.outreach.outreach_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([None])  # outreach nu apartine owner-ului
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(OutreachAccessDeniedError):
            engine.record_outcome(owner_id=uuid4(), outreach_id=uuid4(), outcome="HESITATION")


def test_record_outcome_deja_existent_ridica_eroare(engine):
    with patch("src.engines.outreach.outreach_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([
            (uuid4(),),  # outreach exista, apartine owner-ului -> contact_id
            (1,),        # deja exista un outcome
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(OutcomeAlreadyRecordedError):
            engine.record_outcome(owner_id=uuid4(), outreach_id=uuid4(), outcome="HESITATION")


def test_record_outcome_hesitation_declanseaza_handoff_conversation(
    engine, conversation_engine_mock,
):
    """Contract 46, §3.3: QUESTION_ASKED/HESITATION/WILL_RESPOND_LATER predau automat catre Conversation."""
    owner_id = uuid4()
    contact_id = uuid4()
    outreach_id = uuid4()
    outcome_id = uuid4()
    conversation_id = uuid4()

    conversation_engine_mock.get_or_create_conversation.return_value = Conversation(
        id=conversation_id, owner_id=owner_id, contact_id=contact_id,
        channel="WHATSAPP", status="INITIATED",
    )

    with patch("src.engines.outreach.outreach_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([
            (contact_id,),   # outreach gasit, apartine owner-ului
            None,            # niciun outcome existent
            (outcome_id, outreach_id, "HESITATION"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = engine.record_outcome(owner_id=owner_id, outreach_id=outreach_id, outcome="HESITATION")

        assert result.conversation_id == conversation_id
        conversation_engine_mock.get_or_create_conversation.assert_called_once_with(
            owner_id=owner_id, contact_id=contact_id, source_outreach_id=outreach_id,
        )


def test_record_outcome_referral_received_nu_declanseaza_handoff(
    engine, conversation_engine_mock,
):
    """Contract 46, §3.3: REFERRAL_RECEIVED NU creeaza automat nimic — persoana e alta, inca fara Contact."""
    owner_id = uuid4()
    contact_id = uuid4()
    outreach_id = uuid4()
    outcome_id = uuid4()

    with patch("src.engines.outreach.outreach_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([
            (contact_id,),
            None,
            (outcome_id, outreach_id, "REFERRAL_RECEIVED"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = engine.record_outcome(
            owner_id=owner_id, outreach_id=outreach_id, outcome="REFERRAL_RECEIVED",
        )

        assert result.conversation_id is None
        conversation_engine_mock.get_or_create_conversation.assert_not_called()
