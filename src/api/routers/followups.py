"""
Router FollowUp — API, sursă: 15-followup-api-contract.md, secțiunea 2
(corectată: dis-score primește doar owner_id, fără followup_id).

Decizie de design: GET /followups (listă) apelează
FollowUpEngine.list_pending_followups() direct, NU
FollowUpAgent.present_followup_list() — acesta din urmă întoarce un
singur string formatat (potrivit pentru afișare text unică), nu o
listă structurată JSON, de care are nevoie un consumator API/Dashboard.
Aceeași logică ca la Mission (create_mission apelează Engine direct,
fără metodă Agent de creare).

followup_id: UUID direct, din prima versiune (lecția de la Mission API,
unde a fost nevoie de o corectură ulterioară de la str la UUID).
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import get_followup_agent, get_followup_engine
from src.api.schemas import (
    CreateFollowUpRequest, FollowUpResponse, FollowUpActionRequest,
    CompleteFollowUpRequest, DisScoreResponse,
)
from src.agents.followup.followup_agent import FollowUpAgent
from src.engines.followup.followup_engine import FollowUpEngine

router = APIRouter(prefix="/api/v1/followups", tags=["followups"])


def _to_response(followup) -> FollowUpResponse:
    return FollowUpResponse(
        id=followup.id, owner_id=followup.owner_id,
        contact_id=followup.contact_id, conversation_id=followup.conversation_id,
        status=followup.status,
    )


@router.post("", response_model=FollowUpResponse, status_code=201)
def create_followup(
    body: CreateFollowUpRequest,
    followup_engine: FollowUpEngine = Depends(get_followup_engine),
):
    """Creează un follow-up nou — apelează FollowUpEngine direct (fără metodă Agent de creare)."""
    followup = followup_engine.create_from_trigger(
        body.owner_id, body.contact_id, body.conversation_id
    )
    return _to_response(followup)


@router.get("", response_model=list[FollowUpResponse])
def list_followups(
    owner_id: UUID,
    followup_engine: FollowUpEngine = Depends(get_followup_engine),
):
    """Listă structurată JSON — apelează FollowUpEngine.list_pending_followups() direct."""
    followups = followup_engine.list_pending_followups(owner_id)
    return [_to_response(f) for f in followups]


@router.post("/{followup_id}/complete", response_model=FollowUpResponse)
def complete_followup(
    followup_id: UUID,
    body: CompleteFollowUpRequest,
    followup_agent: FollowUpAgent = Depends(get_followup_agent),
):
    """Confirmare umană — deleagă la FollowUpAgent.confirm_completion."""
    followup = followup_agent.confirm_completion(followup_id, body.owner_id, confirmed=body.confirmed)
    return _to_response(followup)


@router.post("/{followup_id}/postpone", response_model=FollowUpResponse)
def postpone_followup(
    followup_id: UUID,
    body: FollowUpActionRequest,
    followup_agent: FollowUpAgent = Depends(get_followup_agent),
):
    """Deleagă la FollowUpAgent.request_postpone — fără confirmed (verificat, semnătura reală n-o cere)."""
    followup = followup_agent.request_postpone(followup_id, body.owner_id)
    return _to_response(followup)


@router.post("/{followup_id}/reschedule", response_model=FollowUpResponse)
def reschedule_followup(
    followup_id: UUID,
    body: FollowUpActionRequest,
    followup_agent: FollowUpAgent = Depends(get_followup_agent),
):
    """Deleagă la FollowUpAgent.request_reschedule — fără confirmed."""
    followup = followup_agent.request_reschedule(followup_id, body.owner_id)
    return _to_response(followup)


@router.get("/dis-score", response_model=DisScoreResponse)
def get_dis_score(
    owner_id: UUID,
    followup_agent: FollowUpAgent = Depends(get_followup_agent),
):
    """READ-ONLY — doar owner_id, fără followup_id (corectat față de propunerea inițială)."""
    score = followup_agent.get_recent_dis_score(owner_id)
    return DisScoreResponse(dis_score=score)
