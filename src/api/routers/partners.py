"""
Router Partner — API, sursă: 16-partner-api-contract.md.

SECURITATE:
owner_id NU mai vine din request (body/query). Vine exclusiv din
get_current_user(). PartnerEngine păstrează verificarea reală
partner_id + owner_id, iar API-ul transmite identitatea JWT.
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import get_partner_agent
from src.api.schemas import DiagnosticRequest, DiagnosticResponse, SendRequest, PartnerScoresResponse
from src.auth.dependencies import get_current_user, CurrentUser
from src.agents.partner.partner_agent import PartnerAgent

router = APIRouter(prefix="/api/v1/partners", tags=["partners"])


@router.post("/{partner_id}/diagnostic", response_model=DiagnosticResponse, status_code=201)
def request_diagnostic(
    partner_id: UUID,
    body: DiagnosticRequest,
    current_user: CurrentUser = Depends(get_current_user),
    partner_agent: PartnerAgent = Depends(get_partner_agent),
):
    """Diagnostic pentru partenerul utilizatorului autentificat."""
    diagnostic = partner_agent.request_diagnostic(
        partner_id, current_user.id, body.diagnostic_type
    )
    return DiagnosticResponse(
        partner_id=diagnostic.partner_id,
        owner_id=diagnostic.owner_id,
        diagnostic_type=diagnostic.diagnostic_type,
        message=diagnostic.message,
    )


@router.post("/{partner_id}/send", response_model=PartnerScoresResponse)
def send_message(
    partner_id: UUID,
    body: SendRequest,
    current_user: CurrentUser = Depends(get_current_user),
    partner_agent: PartnerAgent = Depends(get_partner_agent),
):
    """Confirmare umană — owner_id este identitatea JWT."""
    partner_agent.confirm_and_send(
        partner_id, current_user.id, confirmed=body.confirmed
    )
    scores = partner_agent.get_recent_scores(current_user.id)
    return PartnerScoresResponse(
        pdi=scores.get("PDI"),
        pip=scores.get("PIP"),
    )


@router.get("/scores", response_model=PartnerScoresResponse)
def get_scores(
    current_user: CurrentUser = Depends(get_current_user),
    partner_agent: PartnerAgent = Depends(get_partner_agent),
):
    """READ-ONLY — citește scorurile utilizatorului autentificat."""
    scores = partner_agent.get_recent_scores(current_user.id)
    return PartnerScoresResponse(pdi=scores.get("PDI"), pip=scores.get("PIP"))
