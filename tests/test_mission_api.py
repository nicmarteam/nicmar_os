"""
Router Mission — API, sursă: 14-api-contract.md, secțiunea 3.

Fiecare endpoint apelează exclusiv MissionAgent (nu MissionEngine
direct din endpoint, cu o singură excepție justificată: POST /missions,
care generează — MissionAgent nu are metodă de generare, verificat
în contract, secțiunea 3).

owner_id vine explicit din request (secțiunea 0 din contract —
limitare temporară, până la Auth).
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import get_mission_agent, get_mission_engine
from src.api.schemas import (
    CreateMissionRequest, MissionResponse, StartMissionRequest,
    CompleteMissionRequest, PresentMissionResponse, DisScoreResponse,
)
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
    mission_engine: MissionEngine = Depends(get_mission_engine),
):
    """Generează o misiune nouă — apelează MissionEngine direct (fără metodă Agent de generare)."""
    mission = mission_engine.generate_mission(body.owner_id, body.title)
    return _to_response(mission)


@router.get("/{mission_id}/present", response_model=PresentMissionResponse)
def present_mission(
    mission_id: str,
    owner_id: str,
    mission_agent: MissionAgent = Depends(get_mission_agent),
    mission_engine: MissionEngine = Depends(get_mission_engine),
):
    """Citește misiunea, apoi cere Agentului textul de prezentare."""
    mission = mission_engine.get_mission(UUID(mission_id), UUID(owner_id))
    text = mission_agent.present_daily_mission(mission)
    return PresentMissionResponse(text=text)


@router.post("/{mission_id}/start", response_model=MissionResponse)
def start_mission(
    mission_id: str,
    body: StartMissionRequest,
    mission_agent: MissionAgent = Depends(get_mission_agent),
):
    """Confirmare umană — 'Sunt gata, încep' — deleagă la MissionAgent."""
    mission = mission_agent.confirm_and_start(UUID(mission_id), body.owner_id, confirmed=body.confirmed)
    return _to_response(mission)


@router.post("/{mission_id}/complete", response_model=MissionResponse)
def complete_mission(
    mission_id: str,
    body: CompleteMissionRequest,
    mission_agent: MissionAgent = Depends(get_mission_agent),
):
    """Finalizare — deleagă la MissionAgent, care persistă și DIS."""
    mission = mission_agent.confirm_completion(UUID(mission_id), body.owner_id)
    return _to_response(mission)


@router.get("/dis-score", response_model=DisScoreResponse)
def get_dis_score(
    owner_id: str,
    mission_agent: MissionAgent = Depends(get_mission_agent),
):
    """READ-ONLY — citește ultimul scor DIS al owner-ului."""
    score = mission_agent.get_recent_dis_score(UUID(owner_id))
    return DisScoreResponse(dis_score=score)
