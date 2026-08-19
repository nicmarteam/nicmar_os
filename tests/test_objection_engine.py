"""
Teste RED pentru ObjectionEngine (clasa care leaga clasificare +
biblioteca + safety validation + persistare).

Sursa: 21-objection-engine-contract.md, sectiunile 1, 4, 5; criterii 7.3.
Sursa create_objection(): 20-2A-create-objection-contract.md.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import psycopg.errors
import pytest

from src.engines.objection.objection_engine import Objection, ObjectionEngine, ObjectionNotFoundError


def _make_cursor(rowcount=1):
    mock_cur = MagicMock()
    mock_cur.rowcount = rowcount
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__.return_value = False
    return mock_cur


def _make_conn(mock_cur):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = False
    return mock_conn


def _make_cursor_fetchone(fetchone_results):
    """Cursor mock pentru INSERT ... RETURNING (create_objection)."""
    mock_cur = MagicMock()
    mock_cur.fetchone.side_effect = fetchone_results
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__.return_value = False
    return mock_cur


def _make_cursor_raises(exc):
    """Cursor mock al carui execute() ridica exc — pentru FK violation."""
    mock_cur = MagicMock()
    mock_cur.execute.side_effect = exc
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__.return_value = False
    return mock_cur


@pytest.fixture
def engine():
    return ObjectionEngine()


# ----------------------------------------------------------------------
# classify() - deleaga la classifier.py, deja testat separat
# ----------------------------------------------------------------------


def test_classify_deleaga_la_classifier(engine):
    assert engine.classify("Nu am timp.") == "TIMP"
    assert engine.classify("text fara nicio potrivire") is None


# ----------------------------------------------------------------------
# get_variants() - deleaga la library.py
# ----------------------------------------------------------------------


def test_get_variants_deleaga_la_library(engine):
    variants = engine.get_variants("PRET")
    assert set(variants.keys()) == {"CALDA", "DIRECTA", "INTREBARE"}


# ----------------------------------------------------------------------
# submit_response - BLOCK nu persista
# ----------------------------------------------------------------------


def test_submit_response_block_nu_scrie_in_db(engine):
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn, \
         patch.object(ObjectionEngine, "_emit_event"):
        mock_cur = _make_cursor()
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = engine.submit_response(
            objection_id=uuid4(),
            owner_id=uuid4(),
            objection_category="PRET",
            objection_text="e scump",
            response_text="Îți garantez că vei câștiga bani.",
            response_variant_used="CALDA",
        )

        assert result.persisted is False
        assert result.validation.level == "BLOCK"
        mock_cur.execute.assert_not_called()


# ----------------------------------------------------------------------
# submit_response - PASS persista corect
# ----------------------------------------------------------------------


def test_submit_response_pass_scrie_response_text_si_variant(engine):
    owner_id = uuid4()
    objection_id = uuid4()

    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn, \
         patch.object(ObjectionEngine, "_emit_event"):
        mock_cur = _make_cursor(rowcount=1)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = engine.submit_response(
            objection_id=objection_id,
            owner_id=owner_id,
            objection_category="PRET",
            objection_text="e scump",
            response_text="Înțeleg, chiar poate părea o investiție.",
            response_variant_used="CALDA",
        )

        assert result.persisted is True
        assert result.validation.level == "PASS"

        executed_sql = mock_cur.execute.call_args[0][0]
        executed_params = mock_cur.execute.call_args[0][1]

        assert "UPDATE" in executed_sql
        assert "response_text" in executed_sql
        assert "response_variant_used" in executed_sql
        assert objection_id in executed_params
        assert owner_id in executed_params


# ----------------------------------------------------------------------
# submit_response - izolare owner_id in WHERE
# ----------------------------------------------------------------------


def test_submit_response_filtreaza_owner_id_in_where(engine):
    owner_id = uuid4()

    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn, \
         patch.object(ObjectionEngine, "_emit_event"):
        mock_cur = _make_cursor(rowcount=1)
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.submit_response(
            objection_id=uuid4(),
            owner_id=owner_id,
            objection_category="TIMP",
            objection_text="nu am timp",
            response_text="Înțeleg, poți începe cu 10 minute pe zi.",
            response_variant_used="DIRECTA",
        )

        executed_sql = mock_cur.execute.call_args[0][0]
        assert "owner_id" in executed_sql


# ----------------------------------------------------------------------
# submit_response - obiectie inexistenta / owner gresit -> eroare explicita
# ----------------------------------------------------------------------


def test_submit_response_obiectie_inexistenta_ridica_eroare(engine):
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(rowcount=0)
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(ObjectionNotFoundError):
            engine.submit_response(
                objection_id=uuid4(),
                owner_id=uuid4(),
                objection_category="TIMP",
                objection_text="nu am timp",
                response_text="Înțeleg, poți începe cu 10 minute pe zi.",
                response_variant_used="DIRECTA",
            )


# ----------------------------------------------------------------------
# submit_response - PARTIAL_VALIDATION / HUMAN_REVIEW nu blocheaza persistarea
# ----------------------------------------------------------------------


def test_submit_response_partial_validation_tot_persista(engine):
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn, \
         patch.object(ObjectionEngine, "_emit_event"):
        mock_cur = _make_cursor(rowcount=1)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = engine.submit_response(
            objection_id=uuid4(),
            owner_id=uuid4(),
            objection_category="INCREDERE_STRUCTURA",
            objection_text="e piramida?",
            response_text="De ce întrebi asta?",
            response_variant_used="INTREBARE",
        )

        assert result.persisted is True
        assert result.validation.level == "PARTIAL_VALIDATION"
        mock_cur.execute.assert_called_once()


# ----------------------------------------------------------------------
# response_variant_used ramane cel trimis, motorul nu il modifica
# ----------------------------------------------------------------------


def test_submit_response_pastreaza_exact_variant_used_trimis(engine):
    """Editarea response_text nu schimba response_variant_used - motorul
    persista exact ce i se transmite, nu recalculeaza originea."""
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn, \
         patch.object(ObjectionEngine, "_emit_event"):
        mock_cur = _make_cursor(rowcount=1)
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.submit_response(
            objection_id=uuid4(),
            owner_id=uuid4(),
            objection_category="PRET",
            objection_text="e scump",
            response_text="Text complet editat de lider, diferit de original.",
            response_variant_used="CALDA",
        )

        executed_params = mock_cur.execute.call_args[0][1]
        assert "CALDA" in executed_params


# ----------------------------------------------------------------------
# create_objection - categorie invalida -> ValueError, ZERO apel DB
# (Decizia 2A, 20-2A-create-objection-contract.md, sectiunea 5)
# ----------------------------------------------------------------------


def test_create_objection_categorie_invalida_ridica_value_error(engine):
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn:
        with pytest.raises(ValueError):
            engine.create_objection(
                owner_id=uuid4(),
                objection_text="nu am incredere",
                objection_category="CATEGORIE_INEXISTENTA",
            )
        mock_get_conn.assert_not_called()


# ----------------------------------------------------------------------
# create_objection - conversation_id=None permis, INSERT reuseste
# ----------------------------------------------------------------------


def test_create_objection_fara_conversation_id(engine):
    owner_id = uuid4()
    objection_id = uuid4()

    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn, \
         patch.object(ObjectionEngine, "_emit_event"):
        mock_cur = _make_cursor_fetchone([
            (objection_id, owner_id, None, "PRET", "e scump", "OPEN"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        objection = engine.create_objection(
            owner_id=owner_id,
            objection_text="e scump",
            objection_category="PRET",
        )

        assert objection == Objection(
            id=objection_id,
            owner_id=owner_id,
            conversation_id=None,
            objection_category="PRET",
            objection_text="e scump",
            resolution_status="OPEN",
        )

        executed_sql = mock_cur.execute.call_args[0][0]
        assert "INSERT INTO objections" in executed_sql
        assert "RETURNING" in executed_sql


# ----------------------------------------------------------------------
# create_objection - cu conversation_id valid
# ----------------------------------------------------------------------


def test_create_objection_cu_conversation_id(engine):
    owner_id = uuid4()
    conversation_id = uuid4()
    objection_id = uuid4()

    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn, \
         patch.object(ObjectionEngine, "_emit_event"):
        mock_cur = _make_cursor_fetchone([
            (objection_id, owner_id, conversation_id, "TIMP", "nu am timp", "OPEN"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        objection = engine.create_objection(
            owner_id=owner_id,
            objection_text="nu am timp",
            objection_category="TIMP",
            conversation_id=conversation_id,
        )

        assert objection.conversation_id == conversation_id

        executed_params = mock_cur.execute.call_args[0][1]
        assert conversation_id in executed_params


# ----------------------------------------------------------------------
# create_objection - toate campurile din Objection provin din RETURNING,
# nu din presupuneri locale (verifica fiecare camp explicit)
# ----------------------------------------------------------------------


def test_create_objection_toate_campurile_din_returning(engine):
    owner_id = uuid4()
    conversation_id = uuid4()
    objection_id = uuid4()

    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor_fetchone([
            (objection_id, owner_id, conversation_id, "AMANARE", "ma mai gandesc", "OPEN"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        objection = engine.create_objection(
            owner_id=owner_id,
            objection_text="ma mai gandesc",
            objection_category="AMANARE",
            conversation_id=conversation_id,
        )

        assert objection.id == objection_id
        assert objection.owner_id == owner_id
        assert objection.conversation_id == conversation_id
        assert objection.objection_category == "AMANARE"
        assert objection.objection_text == "ma mai gandesc"
        assert objection.resolution_status == "OPEN"


# ----------------------------------------------------------------------
# create_objection - owner_id invalid -> FK violation propaga neprinsa
# (Decizia 2A: nu se prinde separat, consecvent cu restul repo-ului)
# ----------------------------------------------------------------------


def test_create_objection_owner_invalid_propaga_fk_violation(engine):
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor_raises(psycopg.errors.ForeignKeyViolation("owner_id inexistent"))
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            engine.create_objection(
                owner_id=uuid4(),
                objection_text="e scump",
                objection_category="PRET",
            )


# ----------------------------------------------------------------------
# create_objection - conversation_id invalid -> FK violation propaga neprinsa
# ----------------------------------------------------------------------


def test_create_objection_conversation_invalid_propaga_fk_violation(engine):
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor_raises(psycopg.errors.ForeignKeyViolation("conversation_id inexistent"))
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            engine.create_objection(
                owner_id=uuid4(),
                objection_text="e scump",
                objection_category="PRET",
                conversation_id=uuid4(),
            )


# ----------------------------------------------------------------------
# create_objection - doua obiectii identice -> doua randuri distincte,
# fara verificare de duplicat (Decizia 2A, sectiunea 5)
# ----------------------------------------------------------------------


def test_create_objection_apeluri_identice_creeaza_doua_randuri(engine):
    owner_id = uuid4()
    first_id = uuid4()
    second_id = uuid4()

    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn, \
         patch.object(ObjectionEngine, "_emit_event"):
        mock_cur = _make_cursor_fetchone([
            (first_id, owner_id, None, "PRET", "e scump", "OPEN"),
            (second_id, owner_id, None, "PRET", "e scump", "OPEN"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        first = engine.create_objection(
            owner_id=owner_id, objection_text="e scump", objection_category="PRET",
        )
        second = engine.create_objection(
            owner_id=owner_id, objection_text="e scump", objection_category="PRET",
        )

        assert first.id != second.id
        assert mock_cur.execute.call_count == 2


# ----------------------------------------------------------------------
# list_categories - Decizia 6, 23-list-categories-contract.md
# ----------------------------------------------------------------------


def test_list_categories_returneaza_toate_cele_13(engine):
    categories = engine.list_categories()
    assert len(categories) == 13
    assert set(categories) == {
        "PRET", "TIMP", "INCREDERE_STRUCTURA", "FAMILIE_SUPORT", "AMANARE",
        "FRICA_TEHNOLOGIE", "FRICA_ESEC", "FRICA_VORBIT", "NU_CUNOSC_OAMENI",
        "VULNERABILITATE_IZOLARE", "IMAGINE_SOCIALA", "NU_VREAU_VANZARE", "PIATA_SATURATA",
    }


def test_list_categories_este_sortata_alfabetic(engine):
    categories = engine.list_categories()
    assert categories == sorted(categories)


def test_list_categories_nu_atinge_db(engine):
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn:
        engine.list_categories()
        mock_get_conn.assert_not_called()


def test_list_categories_returneaza_lista_nu_frozenset(engine):
    categories = engine.list_categories()
    assert isinstance(categories, list)


# ----------------------------------------------------------------------
# get_objection - Decizia 8A, 25-get-objection-contract.md
# ----------------------------------------------------------------------


def test_get_objection_returneaza_objection_complet(engine):
    owner_id = uuid4()
    conversation_id = uuid4()
    objection_id = uuid4()

    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor_fetchone([
            (objection_id, owner_id, conversation_id, "PRET", "e scump", "OPEN"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        objection = engine.get_objection(objection_id=objection_id, owner_id=owner_id)

        assert objection == Objection(
            id=objection_id, owner_id=owner_id, conversation_id=conversation_id,
            objection_category="PRET", objection_text="e scump", resolution_status="OPEN",
        )

        executed_sql = mock_cur.execute.call_args[0][0]
        executed_params = mock_cur.execute.call_args[0][1]
        assert "SELECT" in executed_sql
        assert "FROM objections" in executed_sql
        assert "owner_id" in executed_sql
        assert objection_id in executed_params
        assert owner_id in executed_params


def test_get_objection_filtreaza_owner_id_in_where(engine):
    """owner_id trebuie sa fie in WHERE, nu doar id — existenta id-ului singura nu acorda acces."""
    owner_id = uuid4()

    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor_fetchone([
            (uuid4(), owner_id, None, "TIMP", "nu am timp", "OPEN"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.get_objection(objection_id=uuid4(), owner_id=owner_id)

        executed_sql = mock_cur.execute.call_args[0][0]
        assert "WHERE" in executed_sql
        assert "owner_id" in executed_sql


def test_get_objection_inexistent_ridica_eroare(engine):
    """Rand inexistent -> ObjectionNotFoundError (reuseste exceptia, nu una noua)."""
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor_fetchone([None])
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(ObjectionNotFoundError):
            engine.get_objection(objection_id=uuid4(), owner_id=uuid4())


def test_get_objection_owner_gresit_ridica_aceeasi_eroare(engine):
    """
    Owner gresit -> SELECT nu gaseste randul (filtrat de WHERE owner_id) ->
    ObjectionNotFoundError — identic cu 'nu exista', fara sa dezvaluie ca
    id-ul e valid pentru alt owner (previne enumerare).
    """
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn:
        mock_cur = _make_cursor_fetchone([None])
        mock_get_conn.return_value = _make_conn(mock_cur)

        with pytest.raises(ObjectionNotFoundError):
            engine.get_objection(objection_id=uuid4(), owner_id=uuid4())


# ----------------------------------------------------------------------
# DECIZIA 43 (RED, 19 august 2026) — evenimente ObjectionEngine.
# Sursa: 43-objection-events-contract.md, sectiunea 5, criteriile 1-3.
# Pattern identic cu test_creare_noua_emite_event_conversation_created
# (tests/test_conversation_engine.py) si cu testele Decizia 42 (Contact).
# ----------------------------------------------------------------------


def test_create_objection_emite_event_objection_created(engine):
    """Contract 43, criteriul 1."""
    owner_id = uuid4()
    objection_id = uuid4()

    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn, \
         patch.object(ObjectionEngine, "_emit_event") as mock_emit:
        mock_cur = _make_cursor_fetchone([
            (objection_id, owner_id, None, "PRET", "e scump", "OPEN"),
        ])
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.create_objection(
            owner_id=owner_id, objection_text="e scump", objection_category="PRET",
        )

        mock_emit.assert_called_once()
        args = mock_emit.call_args[0]
        assert args[0] == "ObjectionCreated"
        assert args[1] == objection_id


def test_submit_response_pass_emite_event_cu_persisted_true(engine):
    """Contract 43, criteriul 2."""
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn, \
         patch.object(ObjectionEngine, "_emit_event") as mock_emit:
        mock_cur = _make_cursor(rowcount=1)
        mock_get_conn.return_value = _make_conn(mock_cur)

        engine.submit_response(
            objection_id=uuid4(),
            owner_id=uuid4(),
            objection_category="PRET",
            objection_text="e scump",
            response_text="Înțeleg, chiar poate părea o investiție.",
            response_variant_used="CALDA",
        )

        mock_emit.assert_called_once()
        args = mock_emit.call_args[0]
        assert args[0] == "ObjectionResponseSubmitted"
        payload = args[2]
        assert payload["persisted"] is True
        assert payload["validation_level"] == "PASS"


def test_submit_response_block_emite_event_cu_persisted_false(engine):
    """
    Contract 43, criteriul 3: evenimentul TREBUIE emis si pe ramura BLOCK,
    desi nimic nu se scrie in objections — BLOCK e o decizie reala de
    business, nu absenta unei actiuni (decizie aprobata explicit).
    """
    with patch("src.engines.objection.objection_engine.get_connection") as mock_get_conn, \
         patch.object(ObjectionEngine, "_emit_event") as mock_emit:
        mock_cur = _make_cursor()
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = engine.submit_response(
            objection_id=uuid4(),
            owner_id=uuid4(),
            objection_category="PRET",
            objection_text="e scump",
            response_text="Îți garantez că vei câștiga bani.",
            response_variant_used="CALDA",
        )

        assert result.persisted is False
        mock_emit.assert_called_once()
        args = mock_emit.call_args[0]
        assert args[0] == "ObjectionResponseSubmitted"
        payload = args[2]
        assert payload["persisted"] is False
        assert payload["validation_level"] == "BLOCK"
