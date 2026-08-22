"""
Teste RED pentru InviteEngine — Decizia 48, cu mock, fara DB reala.

Sursa: docs/architecture/48-invite-contract.md.

Principiul central testat (§6): INVITE e evenimentul de business,
MEETING e consecinta programata a unei invitatii acceptate — ACCEPTED
NU creeaza automat un Meeting.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.invite.invite_engine import (
    InviteEngine, InviteAccessDeniedError, InvalidFrameError,
    InvalidPurposeError, InvalidInviteToneError, InvalidInviteOutcomeError,
    InviteOutcomeAlreadyRecordedError,
)


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
def engine():
    return InviteEngine()


# ----------------------------------------------------------------------
# create_invitation() — validari + creare
# ----------------------------------------------------------------------


def test_create_invitation_emite_event_invite_sent(engine):
    """Contract 48 §5: faptul invitatiei se inregistreaza si emite eveniment."""
    owner_id = uuid4()
    contact_id = uuid4()
    invitation_id = uuid4()

    with patch("src.engines.invite.invite_engine.get_connection") as mock_get_conn, \
         patch.object(InviteEngine, "_emit_event") as mock_emit:
        mock_cur = _make_cursor([
            (1,),  # ownership OK
            (invitation_id, owner_id, contact_id, "CAFEA", "OPORTUNITATE",
             "Hai la o cafea?", "CALDA"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        invitation = engine.create_invitation(
            owner_id=owner_id, contact_id=contact_id, frame="CAFEA",
            purpose="OPORTUNITATE", message_text="Hai la o cafea?",
            tone_used="CALDA",
        )

        assert invitation.id == invitation_id
        assert invitation.frame == "CAFEA"
        mock_emit.assert_called_once()
        args = mock_emit.call_args[0]
        assert args[0] == "InviteSent"
        assert args[1] == invitation_id


def test_create_invitation_contact_al_altui_owner_ridica_eroare(engine):
    with patch("src.engines.invite.invite_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([None])
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(InviteAccessDeniedError):
            engine.create_invitation(
                owner_id=uuid4(), contact_id=uuid4(), frame="ZOOM",
                purpose="IDEE_NOUA", message_text="x", tone_used="CALDA",
            )


def test_create_invitation_frame_invalid_ridica_eroare_fara_apel_db(engine):
    """Contract 48 §5: cele 5 cadre din Conversatia 07, Pasul 3."""
    with patch("src.engines.invite.invite_engine.get_connection") as mock_get_conn:
        with pytest.raises(InvalidFrameError):
            engine.create_invitation(
                owner_id=uuid4(), contact_id=uuid4(), frame="RESTAURANT",
                purpose="IDEE_NOUA", message_text="x", tone_used="CALDA",
            )
        mock_get_conn.assert_not_called()


def test_create_invitation_purpose_invalid_ridica_eroare(engine):
    """Contract 48 §5: cele 5 motive din Conversatia 07, Pasul 4."""
    with patch("src.engines.invite.invite_engine.get_connection") as mock_get_conn:
        with pytest.raises(InvalidPurposeError):
            engine.create_invitation(
                owner_id=uuid4(), contact_id=uuid4(), frame="CAFEA",
                purpose="VANZARE", message_text="x", tone_used="CALDA",
            )
        mock_get_conn.assert_not_called()


def test_create_invitation_tone_invalid_ridica_eroare(engine):
    with patch("src.engines.invite.invite_engine.get_connection") as mock_get_conn:
        with pytest.raises(InvalidInviteToneError):
            engine.create_invitation(
                owner_id=uuid4(), contact_id=uuid4(), frame="CAFEA",
                purpose="IDEE_NOUA", message_text="x", tone_used="AGRESIVA",
            )
        mock_get_conn.assert_not_called()


# ----------------------------------------------------------------------
# record_outcome() — cele 5 rezultate, cardinalitate 0..1
# ----------------------------------------------------------------------


def test_record_outcome_invalid_ridica_eroare(engine):
    with patch("src.engines.invite.invite_engine.get_connection") as mock_get_conn:
        with pytest.raises(InvalidInviteOutcomeError):
            engine.record_outcome(
                owner_id=uuid4(), invitation_id=uuid4(), outcome="POATE",
            )
        mock_get_conn.assert_not_called()


def test_record_outcome_accepted_NU_creeaza_meeting_automat(engine):
    """
    Contract 48 §6.B — decizie inghetata: ACCEPTED inregistreaza DOAR
    acceptarea. Meeting-ul se creeaza separat, cand exista o data/ora
    stabilita. Rezolva problema scheduled_at NOT NULL si reflecta
    realitatea ("da, sigur, hai sa vorbim" — fara data inca).
    """
    owner_id = uuid4()
    invitation_id = uuid4()
    outcome_id = uuid4()

    with patch("src.engines.invite.invite_engine.get_connection") as mock_get_conn, \
         patch.object(InviteEngine, "_emit_event"):
        mock_cur = _make_cursor([
            (uuid4(),),  # invitatia exista, apartine owner-ului
            None,        # niciun outcome existent
            (outcome_id, invitation_id, "ACCEPTED"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = engine.record_outcome(
            owner_id=owner_id, invitation_id=invitation_id, outcome="ACCEPTED",
        )

        assert result.outcome == "ACCEPTED"
        assert result.meeting_id is None, (
            "ACCEPTED nu trebuie sa creeze automat un Meeting (contract 48, §6.B)."
        )


def test_record_outcome_declined_doar_inregistreaza(engine):
    """
    Contract 48 §6.D: DECLINED se inregistreaza, fara declansare
    automata de produs/recomandare/black box.
    """
    owner_id = uuid4()
    invitation_id = uuid4()
    outcome_id = uuid4()

    with patch("src.engines.invite.invite_engine.get_connection") as mock_get_conn, \
         patch.object(InviteEngine, "_emit_event"):
        mock_cur = _make_cursor([
            (uuid4(),), None, (outcome_id, invitation_id, "DECLINED"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = engine.record_outcome(
            owner_id=owner_id, invitation_id=invitation_id, outcome="DECLINED",
        )

        assert result.outcome == "DECLINED"
        assert result.meeting_id is None


def test_record_outcome_invitatie_a_altui_owner_ridica_eroare(engine):
    with patch("src.engines.invite.invite_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([None])
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(InviteAccessDeniedError):
            engine.record_outcome(
                owner_id=uuid4(), invitation_id=uuid4(), outcome="ACCEPTED",
            )


def test_record_outcome_a_doua_oara_ridica_eroare(engine):
    """Contract 48 §4: cardinalitate 0..1, tipar identic Decizia 46."""
    with patch("src.engines.invite.invite_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([
            (uuid4(),),  # invitatia exista
            (1,),        # deja are outcome
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(InviteOutcomeAlreadyRecordedError):
            engine.record_outcome(
                owner_id=uuid4(), invitation_id=uuid4(), outcome="POSTPONED",
            )


# ----------------------------------------------------------------------
# schedule_meeting() — Meeting doar cu data stabilita
# ----------------------------------------------------------------------


def test_schedule_meeting_creeaza_meeting_legat_de_invitatie(engine):
    """
    Contract 48 §6.B: Meeting-ul se creeaza separat, cu data explicita,
    si pastreaza legatura de provenienta catre invitatia acceptata.
    """
    owner_id = uuid4()
    invitation_id = uuid4()
    meeting_id = uuid4()

    with patch("src.engines.invite.invite_engine.get_connection") as mock_get_conn, \
         patch.object(InviteEngine, "_emit_event"):
        mock_cur = _make_cursor([
            (uuid4(), "ACCEPTED"),  # invitatia exista, cu outcome ACCEPTED
            (meeting_id, owner_id, "Cafea cu Maria", "SCHEDULED"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        meeting = engine.schedule_meeting(
            owner_id=owner_id, invitation_id=invitation_id,
            title="Cafea cu Maria", scheduled_at="2026-08-25T10:00:00Z",
        )

        assert meeting.id == meeting_id
        assert meeting.status == "SCHEDULED"
