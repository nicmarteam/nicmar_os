"""
Router Priority — API, sursă: 39-priority-api-contract.md.

Un singur endpoint, GET /api/v1/priority — Planul Zilei (maximum 5
activități), fără body, fără parametri de query. owner_id vine exclusiv
din get_current_user() — PriorityEngine nu primește niciun ID din
exterior, deci nu există risc de enumerare.

PriorityEngine.py rămâne neatins — deja validat prin contractul 19.
Acest router doar îl expune, fără să dubleze logica de calcul.
"""

from fastapi import APIRouter, Depends

from src.api.dependencies import get_priority_engine
from src.api.schemas import PrioritizedActivityResponse
from src.auth.dependencies import get_current_user, CurrentUser
from src.engines.priority.priority_engine import PriorityEngine

router = APIRouter(prefix="/api/v1/priority", tags=["priority"])


@router.get("", response_model=list[PrioritizedActivityResponse])
def get_priority(
    current_user: CurrentUser = Depends(get_current_user),
    priority_engine: PriorityEngine = Depends(get_priority_engine),
):
    """
    Planul Zilei — activitățile prioritare ale utilizatorului
    autentificat, maximum 5, deja sortate de PriorityEngine.
    """
    activities = priority_engine.build_priority_list(current_user.id)
    top_activities = PriorityEngine.apply_workload_filter(activities)
    return [
        PrioritizedActivityResponse(
            entity_type=a.entity_type,
            entity_id=a.entity_id,
            title=a.title,
            impact=a.impact,
            urgency=a.urgency,
            vechime_seconds=a.vechime_seconds,
        )
        for a in top_activities
    ]
