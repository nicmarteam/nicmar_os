"""
Router Mission — API, sursă: 14-api-contract.md, secțiunea 3, integrat
cu Auth (12 august 2026).

SCHIMBARE DE SECURITATE: owner_id NU mai vine din request (body/query).
Vine exclusiv din get_current_user() — orice owner_id trimis manual de
client e ignorat complet, fiindcă nu mai există câmpul owner_id în
schemele de request (CreateMissionRequest, StartMissionRequest) sau
în semnăturile endpoint-urilor (present, dis-score).

Engine-urile rămân neschimbate — primesc owner_id explicit, ca
parametru Python, exact ca înainte. Doar sursa lui s-a schimbat:
current_user.id (derivat din JWT), nu din request.
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import get_mission_agent, get_mission_engine
from src.api.schemas import (
    CreateMissionRequest, MissionResponse, StartMissionRequest, PresentMissionResponse,
    DisScoreResponse,
)
from src.auth.dependencies import get_current_user, CurrentUser
from src.agents.mission.mission_agent import MissionAgent
from src.engines.mission.mission_engine import MissionEngine

router = APIRouter(prefix="/api/v1/missions", tags=["missions"])


def _to_response(mission) -> MissionResponse:
    return MissionResponse(
        id=mission.id, owner_id=mission.owner_id,
        title=mission.title, status=mission.status,
    )


@router.post("", response_model=MissionResponse, status_code=201)
def create_mission(
    body: CreateMissionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    mission_engine: MissionEngine = Depends(get_mission_engine),
):
    """Generează o misiune pentru utilizatorul autentificat curent."""
    mission = mission_engine.generate_mission(current_user.id, body.title)
    return _to_response(mission)


@router.post("/{mission_id}/assign", response_model=MissionResponse)
def assign_mission(
    mission_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    mission_engine: MissionEngine = Depends(get_mission_engine),
):
    """
    GENERATED -> ASSIGNED. Fără body — nu mai are nevoie de owner_id
    din request, doar din identitatea autentificată.
    """
    mission = mission_engine.assign_mission(mission_id, current_user.id)
    return _to_response(mission)


@router.get("/{mission_id}/present", response_model=PresentMissionResponse)
def present_mission(
    mission_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    mission_agent: MissionAgent = Depends(get_mission_agent),
    mission_engine: MissionEngine = Depends(get_mission_engine),
):
    """Citește misiunea utilizatorului autentificat, apoi cere Agentului textul."""
    mission = mission_engine.get_mission(mission_id, current_user.id)
    text = mission_agent.present_daily_mission(mission)
    return PresentMissionResponse(text=text)


@router.post("/{mission_id}/start", response_model=MissionResponse)
def start_mission(
    mission_id: UUID,
    body: StartMissionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    mission_agent: MissionAgent = Depends(get_mission_agent),
):
    """Confirmare umană — 'Sunt gata, încep' — owner_id din identitate, nu din body."""
    mission = mission_agent.confirm_and_start(mission_id, current_user.id, confirmed=body.confirmed)
    return _to_response(mission)


@router.post("/{mission_id}/complete", response_model=MissionResponse)
def complete_mission(
    mission_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    mission_agent: MissionAgent = Depends(get_mission_agent),
):
    """Finalizare — fără body, owner_id din identitatea autentificată."""
    mission = mission_agent.confirm_completion(mission_id, current_user.id)
    return _to_response(mission)


@router.get("/dis-score", response_model=DisScoreResponse)
def get_dis_score(
    current_user: CurrentUser = Depends(get_current_user),
    mission_agent: MissionAgent = Depends(get_mission_agent),
):
    """READ-ONLY — scorul DIS al utilizatorului autentificat, nu al unui owner_id arbitrar."""
    score = mission_agent.get_recent_dis_score(current_user.id)
    return DisScoreResponse(dis_score=score)
