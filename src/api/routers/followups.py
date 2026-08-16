"""
Router FollowUp — API, sursă: 15-followup-api-contract.md.

SECURITATE:
owner_id NU mai vine din request (body/query). Vine exclusiv din
get_current_user() — orice owner_id trimis manual de client este ignorat.

Engine-ul păstrează owner_id ca parametru Python pentru verificarea
ownership-ului. Doar sursa lui s-a schimbat: JWT -> current_user.id.
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import get_followup_agent, get_followup_engine
from src.api.schemas import (
    CreateFollowUpRequest,
    FollowUpResponse,
    CompleteFollowUpRequest,
    DisScoreResponse,
)
from src.auth.dependencies import get_current_user, CurrentUser
from src.agents.followup.followup_agent import FollowUpAgent
from src.engines.followup.followup_engine import FollowUpEngine

router = APIRouter(prefix="/api/v1/followups", tags=["followups"])


def _to_response(followup) -> FollowUpResponse:
    return FollowUpResponse(
        id=followup.id,
        owner_id=followup.owner_id,
        contact_id=followup.contact_id,
        conversation_id=followup.conversation_id,
        status=followup.status,
    )


@router.post("", response_model=FollowUpResponse, status_code=201)
def create_followup(
    body: CreateFollowUpRequest,
    current_user: CurrentUser = Depends(get_current_user),
    followup_engine: FollowUpEngine = Depends(get_followup_engine),
):
    """Creează follow-up pentru utilizatorul autentificat."""
    followup = followup_engine.create_from_trigger(
        current_user.id, body.contact_id, body.conversation_id
    )
    return _to_response(followup)


@router.get("", response_model=list[FollowUpResponse])
def list_followups(
    current_user: CurrentUser = Depends(get_current_user),
    followup_engine: FollowUpEngine = Depends(get_followup_engine),
):
    """Listează doar follow-up-urile PENDING ale utilizatorului autentificat."""
    followups = followup_engine.list_pending_followups(current_user.id)
    return [_to_response(f) for f in followups]


@router.post("/{followup_id}/complete", response_model=FollowUpResponse)
def complete_followup(
    followup_id: UUID,
    body: CompleteFollowUpRequest,
    current_user: CurrentUser = Depends(get_current_user),
    followup_agent: FollowUpAgent = Depends(get_followup_agent),
):
    """Confirmare umană — owner_id este identitatea JWT."""
    followup = followup_agent.confirm_completion(
        followup_id, current_user.id, confirmed=body.confirmed
    )
    return _to_response(followup)


@router.post("/{followup_id}/postpone", response_model=FollowUpResponse)
def postpone_followup(
    followup_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    followup_agent: FollowUpAgent = Depends(get_followup_agent),
):
    """Amână follow-up-ul utilizatorului autentificat."""
    followup = followup_agent.request_postpone(followup_id, current_user.id)
    return _to_response(followup)


@router.post("/{followup_id}/reschedule", response_model=FollowUpResponse)
def reschedule_followup(
    followup_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    followup_agent: FollowUpAgent = Depends(get_followup_agent),
):
    """Reprogramează follow-up-ul utilizatorului autentificat."""
    followup = followup_agent.request_reschedule(followup_id, current_user.id)
    return _to_response(followup)


@router.get("/dis-score", response_model=DisScoreResponse)
def get_dis_score(
    current_user: CurrentUser = Depends(get_current_user),
    followup_agent: FollowUpAgent = Depends(get_followup_agent),
):
    """READ-ONLY — scorul DIS al utilizatorului autentificat."""
    score = followup_agent.get_recent_dis_score(current_user.id)
    return DisScoreResponse(dis_score=score)
