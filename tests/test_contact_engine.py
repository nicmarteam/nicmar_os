"""
Teste RED pentru ContactEngine.create_contact() — Decizia 31, cu mock, fara DB reala.

Sursa: 31-contact-create-contract.md.

ContactAgent (READ-ONLY, 20-contact-agent-contract.md) ramane neatins —
acest fisier testeaza exclusiv ContactEngine (WRITE), fisier nou, separat.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.contact.contact_engine import (
    Contact, ContactEngine, InvalidRelationshipValueError,
)


def _make_cursor(fetchone_result):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = fetchone_result
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
    return ContactEngine()


def test_create_contact_status_este_hardcodat_new_nu_din_parametru(engine):
    """create_contact() nu are parametru 'status' — hardcodat 'NEW' in INSERT."""
    owner_id = uuid4()
    contact_id = uuid4()

    with patch("src.engines.contact.contact_engine.get_connection") as mock_get_conn, \
         patch.object(ContactEngine, "_emit_event"):
        mock_cur = _make_cursor(
            (contact_id, owner_id, "Ion Popescu", None, None, "NEW", None, {}),
        )
        mock_get_conn.return_value = _make_conn(mock_cur)

        contact = engine.create_contact(owner_id=owner_id, full_name="Ion Popescu")

        assert contact.status == "NEW"
        executed_sql = mock_cur.execute.call_args[0][0]
        assert "'NEW'" in executed_sql  # literal in SQL, nu parametru


def test_create_contact_returneaza_contact_complet(engine):
    owner_id = uuid4()
    contact_id = uuid4()

    with patch("src.engines.contact.contact_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(
            (contact_id, owner_id, "Maria Ionescu", "0722000000", "maria@test.ro",
             "NEW", "facebook", {"nota": "prieten"}),
        )
        mock_get_conn.return_value = _make_conn(mock_cur)

        contact = engine.create_contact(
            owner_id=owner_id, full_name="Maria Ionescu",
            phone="0722000000", email="maria@test.ro",
            source="facebook", metadata={"nota": "prieten"},
        )

        assert contact == Contact(
            id=contact_id, owner_id=owner_id, full_name="Maria Ionescu",
            phone="0722000000", email="maria@test.ro", status="NEW",
            source="facebook", metadata={"nota": "prieten"},
        )


def test_create_contact_campuri_optionale_none_by_default(engine):
    owner_id = uuid4()
    contact_id = uuid4()

    with patch("src.engines.contact.contact_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(
            (contact_id, owner_id, "Test Minim", None, None, "NEW", None, {}),
        )
        mock_get_conn.return_value = _make_conn(mock_cur)

        contact = engine.create_contact(owner_id=owner_id, full_name="Test Minim")

        assert contact.phone is None
        assert contact.email is None
        assert contact.source is None
        assert contact.metadata == {}


def test_create_contact_metadata_none_devine_dict_gol(engine):
    owner_id = uuid4()
    contact_id = uuid4()

    with patch("src.engines.contact.contact_engine.get_connection") as mock_get_conn, \
         patch.object(ContactEngine, "_emit_event"):
        mock_cur = _make_cursor(
            (contact_id, owner_id, "Test", None, None, "NEW", None, {}),
        )
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.create_contact(owner_id=owner_id, full_name="Test", metadata=None)

        executed_params = mock_cur.execute.call_args[0][1]
        json_param = executed_params[-1]  # ultimul parametru = metadata, invelit in Json()
        assert json_param.obj == {}  # psycopg.types.json.Json pastreaza obiectul original in .obj


def test_create_contact_owner_id_folosit_exact_cel_transmis(engine):
    owner_id = uuid4()
    contact_id = uuid4()

    with patch("src.engines.contact.contact_engine.get_connection") as mock_get_conn, \
         patch.object(ContactEngine, "_emit_event"):
        mock_cur = _make_cursor(
            (contact_id, owner_id, "Test", None, None, "NEW", None, {}),
        )
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.create_contact(owner_id=owner_id, full_name="Test")

        executed_params = mock_cur.execute.call_args[0][1]
        assert owner_id in executed_params


# ----------------------------------------------------------------------
# DECIZIA 42 (RED, 19 august 2026) — ContactCreated event.
# Sursa: 42-contact-events-contract.md, sectiunea 4, criteriul 1.
# Pattern identic cu test_creare_noua_emite_event_conversation_created
# (tests/test_conversation_engine.py).
# ----------------------------------------------------------------------


def test_create_contact_emite_event_contact_created(engine):
    """
    Contract 42, criteriul 1: create_contact() trebuie sa emita
    evenimentul ContactCreated, cu target_object_id = contact.id,
    dupa ce INSERT-ul a reusit.
    """
    owner_id = uuid4()
    contact_id = uuid4()

    with patch("src.engines.contact.contact_engine.get_connection") as mock_get_conn, \
         patch.object(ContactEngine, "_emit_event") as mock_emit:
        mock_cur = _make_cursor(
            (contact_id, owner_id, "Test Event", None, None, "NEW", None, {}),
        )
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.create_contact(owner_id=owner_id, full_name="Test Event")

        mock_emit.assert_called_once()
        args = mock_emit.call_args[0]
        assert args[0] == "ContactCreated"
        assert args[1] == contact_id


# ----------------------------------------------------------------------
# DECIZIA 47 (RED, 20 august 2026) — Construirea Listei de Relatii
# (Competenta 18). Sursa: 47-lista-relatii-contract.md, sectiunea 6.
#
# Regula centrala: NU se creeaza entitatea Relationship. Cele 5 campuri
# devin atribute ale Contact-ului deja existent — o persoana, un traseu.
# ----------------------------------------------------------------------


def test_create_contact_accepta_campurile_de_relatie(engine):
    """Contract 47, criteriul 1: toate 5 campurile ajung in INSERT."""
    owner_id = uuid4()
    contact_id = uuid4()

    with patch("src.engines.contact.contact_engine.get_connection") as mock_get_conn, \
         patch.object(ContactEngine, "_emit_event"):
        mock_cur = _make_cursor(
            (contact_id, owner_id, "Maria", None, None, "NEW", None, {}),
        )
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.create_contact(
            owner_id=owner_id,
            full_name="Maria",
            relationship_category="PRIETENI",
            relationship_level="BUNA",
            last_contact_approx="LUNA_ACEASTA",
            significant_context="Si-a schimbat jobul recent.",
            perceived_interest="PROBABIL",
        )

        executed_params = mock_cur.execute.call_args[0][1]
        assert "PRIETENI" in executed_params
        assert "BUNA" in executed_params
        assert "LUNA_ACEASTA" in executed_params
        assert "Si-a schimbat jobul recent." in executed_params
        assert "PROBABIL" in executed_params


def test_create_contact_fara_campuri_de_relatie_ramane_valid(engine):
    """
    Contract 47, criteriul 2 — REGRESIE: semnatura veche functioneaza
    neschimbata, campurile noi devin None. Zero breaking change pentru
    cele ~500 de teste existente.
    """
    owner_id = uuid4()
    contact_id = uuid4()

    with patch("src.engines.contact.contact_engine.get_connection") as mock_get_conn, \
         patch.object(ContactEngine, "_emit_event"):
        mock_cur = _make_cursor(
            (contact_id, owner_id, "Ion", None, None, "NEW", None, {}),
        )
        mock_get_conn.return_value = _make_conn(mock_cur)

        contact = engine.create_contact(owner_id=owner_id, full_name="Ion")

        assert contact.full_name == "Ion"
        executed_params = mock_cur.execute.call_args[0][1]
        assert executed_params.count(None) >= 5


def test_create_contact_categorie_invalida_ridica_eroare(engine):
    """
    Contract 47, criteriul 3: validare la nivel de aplicatie, INAINTE de
    DB (tipar identic InvalidDiagnosticTypeError de la Partner) — nu se
    bazeaza doar pe CHECK-ul din schema ca plasa de siguranta.
    """
    with patch("src.engines.contact.contact_engine.get_connection") as mock_get_conn:
        with pytest.raises(InvalidRelationshipValueError):
            engine.create_contact(
                owner_id=uuid4(), full_name="X", relationship_category="COLEGI_DE_LICEU",
            )
        mock_get_conn.assert_not_called()
