"""
Router Outreach — API, sursă: 46-prospectare-relationala-contract.md.

2 endpoint-uri mutante + listă. `owner_id` exclusiv din JWT, identic
tipar cu tot restul API-ului.
"""

from fastapi import APIRouter, Depends
from uuid import UUID

from src.api.dependencies import get_outreach_engine
from src.api.schemas import (
    CreateOutreachRequest, OutreachResponse,
    RecordOutcomeRequest, OutcomeResponse,
)
from src.auth.dependencies import get_current_user, CurrentUser
from src.engines.outreach.outreach_engine import OutreachEngine

router = APIRouter(prefix="/api/v1/outreach", tags=["outreach"])


@router.post("", response_model=OutreachResponse, status_code=201)
def create_outreach(
    payload: CreateOutreachRequest,
    current_user: CurrentUser = Depends(get_current_user),
    outreach_engine: OutreachEngine = Depends(get_outreach_engine),
):
    """Creează intervenția (Recomandare sau Reactivare) — imutabilă de la creare."""
    outreach = outreach_engine.create_outreach(
        owner_id=current_user.id,
        contact_id=payload.contact_id,
        purpose=payload.purpose,
        message_text=payload.message_text,
        tone_used=payload.tone_used,
    )
    return OutreachResponse(
        id=outreach.id, owner_id=outreach.owner_id, contact_id=outreach.contact_id,
        purpose=outreach.purpose, message_text=outreach.message_text,
        tone_used=outreach.tone_used,
    )


@router.post("/{outreach_id}/outcome", response_model=OutcomeResponse, status_code=201)
def record_outcome(
    outreach_id: UUID,
    payload: RecordOutcomeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    outreach_engine: OutreachEngine = Depends(get_outreach_engine),
):
    """
    Înregistrează reacția imediată observată — o singură dată per
    Outreach. Pentru QUESTION_ASKED/HESITATION/WILL_RESPOND_LATER,
    predă automat către Conversation (conversation_id în răspuns).
    """
    result = outreach_engine.record_outcome(
        owner_id=current_user.id, outreach_id=outreach_id, outcome=payload.outcome,
    )
    return OutcomeResponse(
        id=result.id, outreach_id=result.outreach_id, outcome=result.outcome,
        conversation_id=result.conversation_id,
    )
