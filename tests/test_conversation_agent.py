"""
Teste RED pentru ConversationAgent v1 — cu mock pe ObjectionEngine, fara DB reala.

Sursa: 22-conversation-agent-contract.md.
"""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.engines.objection.objection_engine import Objection, SubmitResponseResult
from src.engines.objection.safety_validation import ValidationResult
from src.agents.conversation.conversation_agent import (
    AnalyzeObjectionResult,
    ConfirmResponseResult,
    ConversationAgent,
    PrepareResponseOptionsResult,
)


@pytest.fixture
def fake_engine():
    return MagicMock()


@pytest.fixture
def agent(fake_engine):
    return ConversationAgent(objection_engine=fake_engine)


# ----------------------------------------------------------------------
# analyze_objection() — fara DB, deleaga la classify()
# ----------------------------------------------------------------------


def test_analyze_objection_deleaga_la_classify(agent, fake_engine):
    """analyze_objection apeleaza ObjectionEngine.classify(), nimic altceva."""
    fake_engine.classify.return_value = "TIMP"

    result = agent.analyze_objection("Nu am timp.")

    fake_engine.classify.assert_called_once_with("Nu am timp.")
    assert isinstance(result, AnalyzeObjectionResult)


def test_analyze_objection_categorie_gasita(agent, fake_engine):
    """Cand classify() gaseste o categorie, needs_manual_selection e False."""
    fake_engine.classify.return_value = "PRET"

    result = agent.analyze_objection("e scump")

    assert result.detected_category == "PRET"
    assert result.needs_manual_selection is False


def test_analyze_objection_fara_potrivire_cere_selectie_manuala(agent, fake_engine):
    """Cand classify() returneaza None, needs_manual_selection e True."""
    fake_engine.classify.return_value = None

    result = agent.analyze_objection("text fara nicio potrivire")

    assert result.detected_category is None
    assert result.needs_manual_selection is True


def test_analyze_objection_nu_atinge_db(agent, fake_engine):
    """analyze_objection nu apeleaza create_objection/submit_response/get_variants."""
    fake_engine.classify.return_value = "TIMP"

    agent.analyze_objection("nu am timp")

    fake_engine.create_objection.assert_not_called()
    fake_engine.submit_response.assert_not_called()
    fake_engine.get_variants.assert_not_called()


# ----------------------------------------------------------------------
# prepare_response_options() — create_objection() + get_variants()
# ----------------------------------------------------------------------


def test_prepare_response_options_apeleaza_create_objection(agent, fake_engine):
    """prepare_response_options apeleaza create_objection cu parametrii corecti."""
    owner_id = uuid4()
    conversation_id = uuid4()
    objection = Objection(
        id=uuid4(), owner_id=owner_id, conversation_id=conversation_id,
        objection_category="PRET", objection_text="e scump", resolution_status="OPEN",
    )
    fake_engine.create_objection.return_value = objection
    fake_engine.get_variants.return_value = {"CALDA": "a", "DIRECTA": "b", "INTREBARE": "c"}

    agent.prepare_response_options(
        owner_id=owner_id, objection_text="e scump",
        objection_category="PRET", conversation_id=conversation_id,
    )

    fake_engine.create_objection.assert_called_once_with(
        owner_id=owner_id, objection_text="e scump",
        objection_category="PRET", conversation_id=conversation_id,
    )


def test_prepare_response_options_conversation_id_none_by_default(agent, fake_engine):
    """conversation_id nu e obligatoriu — implicit None, transmis corect."""
    owner_id = uuid4()
    objection = Objection(
        id=uuid4(), owner_id=owner_id, conversation_id=None,
        objection_category="TIMP", objection_text="nu am timp", resolution_status="OPEN",
    )
    fake_engine.create_objection.return_value = objection
    fake_engine.get_variants.return_value = {"CALDA": "a", "DIRECTA": "b", "INTREBARE": "c"}

    agent.prepare_response_options(
        owner_id=owner_id, objection_text="nu am timp", objection_category="TIMP",
    )

    fake_engine.create_objection.assert_called_once_with(
        owner_id=owner_id, objection_text="nu am timp",
        objection_category="TIMP", conversation_id=None,
    )


def test_prepare_response_options_apeleaza_get_variants_cu_categoria_din_objection(agent, fake_engine):
    """get_variants() e apelat cu categoria din Objection-ul returnat de create_objection, nu cu inputul brut."""
    owner_id = uuid4()
    objection = Objection(
        id=uuid4(), owner_id=owner_id, conversation_id=None,
        objection_category="PRET", objection_text="e scump", resolution_status="OPEN",
    )
    fake_engine.create_objection.return_value = objection
    fake_engine.get_variants.return_value = {"CALDA": "a", "DIRECTA": "b", "INTREBARE": "c"}

    agent.prepare_response_options(
        owner_id=owner_id, objection_text="e scump", objection_category="PRET",
    )

    fake_engine.get_variants.assert_called_once_with("PRET")


def test_prepare_response_options_returneaza_objection_si_cele_3_variante(agent, fake_engine):
    """Rezultatul contine Objection-ul complet (cu id) + exact cele 3 variante."""
    owner_id = uuid4()
    objection = Objection(
        id=uuid4(), owner_id=owner_id, conversation_id=None,
        objection_category="AMANARE", objection_text="ma mai gandesc", resolution_status="OPEN",
    )
    fake_engine.create_objection.return_value = objection
    fake_engine.get_variants.return_value = {
        "CALDA": "text calda", "DIRECTA": "text directa", "INTREBARE": "text intrebare",
    }

    result = agent.prepare_response_options(
        owner_id=owner_id, objection_text="ma mai gandesc", objection_category="AMANARE",
    )

    assert isinstance(result, PrepareResponseOptionsResult)
    assert result.objection == objection
    assert result.objection.id == objection.id
    assert set(result.variants.keys()) == {"CALDA", "DIRECTA", "INTREBARE"}


def test_prepare_response_options_propaga_value_error_categorie_invalida(agent, fake_engine):
    """Eroarea ValueError a create_objection() (categorie invalida) propaga neprinsa."""
    fake_engine.create_objection.side_effect = ValueError("Categorie necunoscută: 'X'")

    with pytest.raises(ValueError):
        agent.prepare_response_options(
            owner_id=uuid4(), objection_text="text", objection_category="X",
        )

    fake_engine.get_variants.assert_not_called()


def test_prepare_response_options_propaga_fk_violation(agent, fake_engine):
    """Erorile psycopg (FK violation) ale create_objection() propaga neprinse."""
    fake_engine.create_objection.side_effect = RuntimeError("simulare ForeignKeyViolation")

    with pytest.raises(RuntimeError):
        agent.prepare_response_options(
            owner_id=uuid4(), objection_text="text", objection_category="PRET",
        )


# ----------------------------------------------------------------------
# confirm_response() — primeste Objection persistent, nu campuri separate
# ----------------------------------------------------------------------


def _make_objection():
    return Objection(
        id=uuid4(), owner_id=uuid4(), conversation_id=None,
        objection_category="PRET", objection_text="e scump", resolution_status="OPEN",
    )


def test_confirm_response_apeleaza_submit_response_cu_datele_din_objection_persistent(agent, fake_engine):
    """
    submit_response() primeste objection_id/owner_id/objection_category/objection_text
    EXCLUSIV din obiectul Objection transmis — niciodata reintroduse separat de UI.
    """
    objection = _make_objection()
    fake_engine.submit_response.return_value = SubmitResponseResult(
        persisted=True, validation=ValidationResult(level="PASS", reason=None),
    )

    agent.confirm_response(
        objection=objection, response_text="Înțeleg, poate fi o investiție.",
        response_variant_used="CALDA",
    )

    fake_engine.submit_response.assert_called_once_with(
        objection_id=objection.id,
        owner_id=objection.owner_id,
        objection_category=objection.objection_category,
        objection_text=objection.objection_text,
        response_text="Înțeleg, poate fi o investiție.",
        response_variant_used="CALDA",
    )


def test_confirm_response_pass_returneaza_persisted_true(agent, fake_engine):
    objection = _make_objection()
    fake_engine.submit_response.return_value = SubmitResponseResult(
        persisted=True, validation=ValidationResult(level="PASS", reason=None),
    )

    result = agent.confirm_response(
        objection=objection, response_text="text ok", response_variant_used="DIRECTA",
    )

    assert isinstance(result, ConfirmResponseResult)
    assert result.persisted is True
    assert result.validation_level == "PASS"
    assert result.reason is None


def test_confirm_response_block_returneaza_persisted_false_cu_motiv(agent, fake_engine):
    objection = _make_objection()
    fake_engine.submit_response.return_value = SubmitResponseResult(
        persisted=False,
        validation=ValidationResult(level="BLOCK", reason="Promisiune nerealistă."),
    )

    result = agent.confirm_response(
        objection=objection, response_text="Îți garantez câștig.", response_variant_used="CALDA",
    )

    assert result.persisted is False
    assert result.validation_level == "BLOCK"
    assert result.reason == "Promisiune nerealistă."


def test_confirm_response_human_review_persista_dar_semnaleaza(agent, fake_engine):
    objection = _make_objection()
    fake_engine.submit_response.return_value = SubmitResponseResult(
        persisted=True,
        validation=ValidationResult(level="HUMAN_REVIEW", reason="Testimoniale neverificabile."),
    )

    result = agent.confirm_response(
        objection=objection, response_text="De ce întrebi?", response_variant_used="INTREBARE",
    )

    assert result.persisted is True
    assert result.validation_level == "HUMAN_REVIEW"
    assert result.reason == "Testimoniale neverificabile."


def test_confirm_response_propaga_objection_not_found_error(agent, fake_engine):
    """ObjectionNotFoundError propaga neprinsa — ConversationAgent nu o traduce."""
    from src.engines.objection.objection_engine import ObjectionNotFoundError

    objection = _make_objection()
    fake_engine.submit_response.side_effect = ObjectionNotFoundError("nu exista")

    with pytest.raises(ObjectionNotFoundError):
        agent.confirm_response(
            objection=objection, response_text="text", response_variant_used="CALDA",
        )
