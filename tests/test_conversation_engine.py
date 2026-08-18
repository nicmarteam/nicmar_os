"""
Teste RED pentru ConversationEngine ("Conversation Writer") — cu mock, fara DB reala.

Sursa: 29-conversation-writer-contract.md.

Atentie la nume: ConversationEngine (acest fisier) e complet diferit de
ConversationAgent (src/agents/conversation/) — al doilea orchestreaza
fluxul Objection, n-are nicio legatura cu tabela conversations.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.conversation.conversation_engine import (
    Conversation, ConversationEngine, ConversationAccessDeniedError,
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
    return ConversationEngine()


# ----------------------------------------------------------------------
# Ownership — pasul 1 obligatoriu, inainte de orice altceva
# ----------------------------------------------------------------------


def test_contact_inexistent_sau_owner_gresit_ridica_access_denied(engine):
    """
    SELECT 1 FROM contacts WHERE id=... AND owner_id=... nu gaseste
    nimic -> ConversationAccessDeniedError, ZERO alt apel SQL.
    """
    with patch("src.engines.conversation.conversation_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([None])  # ownership check esueaza
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(ConversationAccessDeniedError):
            engine.get_or_create_conversation(owner_id=uuid4(), contact_id=uuid4())

        assert mock_cur.execute.call_count == 1  # doar verificarea de ownership


def test_ownership_verifica_owner_id_in_where(engine):
    with patch("src.engines.conversation.conversation_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([None])
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(ConversationAccessDeniedError):
            engine.get_or_create_conversation(owner_id=uuid4(), contact_id=uuid4())

        executed_sql = mock_cur.execute.call_args_list[0][0][0]
        assert "contacts" in executed_sql
        assert "owner_id" in executed_sql


# ----------------------------------------------------------------------
# Idempotency — conversatie existenta -> fara INSERT
# ----------------------------------------------------------------------


def test_returneaza_conversatie_existenta_fara_insert(engine):
    owner_id = uuid4()
    contact_id = uuid4()
    conversation_id = uuid4()

    with patch("src.engines.conversation.conversation_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([
            (1,),  # ownership OK
            (conversation_id, owner_id, contact_id, "WHATSAPP", "ACTIVE"),  # conversatie existenta
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        conversation = engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

        assert conversation == Conversation(
            id=conversation_id, owner_id=owner_id, contact_id=contact_id,
            channel="WHATSAPP", status="ACTIVE",
        )
        assert mock_cur.execute.call_count == 2  # ownership + lookup, FARA insert


def test_lookup_filtreaza_doar_statusuri_deschise(engine):
    owner_id = uuid4()
    contact_id = uuid4()

    with patch("src.engines.conversation.conversation_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor([
            (1,),
            (uuid4(), owner_id, contact_id, "WHATSAPP", "ACTIVE"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

        # SQL parametrizat corect (%s), nu concatenare -> statusurile
        # apar in parametrii transmisi, nu in string-ul SQL
        lookup_sql = mock_cur.execute.call_args_list[1][0][0]
        lookup_params = mock_cur.execute.call_args_list[1][0][1]
        assert lookup_sql.count("%s") == 6  # owner_id, contact_id + 4 statusuri
        assert "INITIATED" in lookup_params
        assert "ACTIVE" in lookup_params
        assert "WAITING" in lookup_params
        assert "FOLLOWUP_NEEDED" in lookup_params


# ----------------------------------------------------------------------
# Creare noua — cand nu exista conversatie deschisa
# ----------------------------------------------------------------------


def test_creeaza_conversatie_noua_cand_nu_exista(engine):
    owner_id = uuid4()
    contact_id = uuid4()
    new_id = uuid4()

    with patch("src.engines.conversation.conversation_engine.get_connection") as mock_get_conn, \
         patch.object(ConversationEngine, "_emit_event") as mock_emit:
        mock_cur = _make_cursor([
            (1,),  # ownership OK
            None,  # nicio conversatie deschisa existenta
            (new_id, owner_id, contact_id, "WHATSAPP", "INITIATED"),  # INSERT ... RETURNING
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        conversation = engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

        assert conversation.id == new_id
        assert conversation.status == "INITIATED"
        assert mock_cur.execute.call_count == 3  # ownership + lookup + insert


def test_creare_noua_emite_event_conversation_created(engine):
    owner_id = uuid4()
    contact_id = uuid4()
    new_id = uuid4()

    with patch("src.engines.conversation.conversation_engine.get_connection") as mock_get_conn, \
         patch.object(ConversationEngine, "_emit_event") as mock_emit:
        mock_cur = _make_cursor([
            (1,), None, (new_id, owner_id, contact_id, "WHATSAPP", "INITIATED"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

        mock_emit.assert_called_once()
        args = mock_emit.call_args[0]
        assert args[0] == "ConversationCreated"
        assert args[1] == new_id


def test_conversatie_existenta_nu_emite_event(engine):
    """Idempotency real: returnarea unei conversatii existente NU e o creare -> zero event."""
    owner_id = uuid4()
    contact_id = uuid4()

    with patch("src.engines.conversation.conversation_engine.get_connection") as mock_get_conn, \
         patch.object(ConversationEngine, "_emit_event") as mock_emit:
        mock_cur = _make_cursor([
            (1,), (uuid4(), owner_id, contact_id, "WHATSAPP", "ACTIVE"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

        mock_emit.assert_not_called()


def test_channel_implicit_whatsapp(engine):
    owner_id = uuid4()
    contact_id = uuid4()
    new_id = uuid4()

    with patch("src.engines.conversation.conversation_engine.get_connection") as mock_get_conn, \
         patch.object(ConversationEngine, "_emit_event"):
        mock_cur = _make_cursor([
            (1,), None, (new_id, owner_id, contact_id, "WHATSAPP", "INITIATED"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        conversation = engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

        assert conversation.channel == "WHATSAPP"
        insert_params = mock_cur.execute.call_args_list[2][0][1]
        assert "WHATSAPP" in insert_params


def test_channel_explicit_transmis_corect(engine):
    owner_id = uuid4()
    contact_id = uuid4()
    new_id = uuid4()

    with patch("src.engines.conversation.conversation_engine.get_connection") as mock_get_conn, \
         patch.object(ConversationEngine, "_emit_event"):
        mock_cur = _make_cursor([
            (1,), None, (new_id, owner_id, contact_id, "MESSENGER", "INITIATED"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        conversation = engine.get_or_create_conversation(
            owner_id=owner_id, contact_id=contact_id, channel="MESSENGER",
        )

        assert conversation.channel == "MESSENGER"


# ----------------------------------------------------------------------
# Dataclass Conversation
# ----------------------------------------------------------------------


def test_conversation_are_exact_campurile_contractate():
    c = Conversation(
        id=uuid4(), owner_id=uuid4(), contact_id=uuid4(),
        channel="WHATSAPP", status="INITIATED",
    )
    assert hasattr(c, "id")
    assert hasattr(c, "owner_id")
    assert hasattr(c, "contact_id")
    assert hasattr(c, "channel")
    assert hasattr(c, "status")
