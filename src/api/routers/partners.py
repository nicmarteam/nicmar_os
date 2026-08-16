"""
Router Partner — API, sursă: 16-partner-api-contract.md.

Diferență structurală față de Mission/FollowUp: PartnerAgent.confirm_and_send()
returnează None (Partner nu are tranziție de stare la acest pas — doar
persistă PDI/PIP). De aceea, endpoint-ul /send apelează confirm_and_send()
pentru efectul lui (persistență), apoi get_recent_scores() pentru
răspunsul HTTP (contract 16, secțiunea 1) — decizie explicită, nu
inventată arbitrar.

partner_id: UUID direct, din prima versiune (fără corectură ulterioară,
ca la Mission API).

Verificarea de ownership (_verify_ownership, PartnerAccessDeniedError)
rulează în interiorul PartnerEngine, PRIMA, înaintea oricărei alte
verificări — API-ul nu duplică această logică, doar o lasă să
propage prin excepție către exception_handlers.py.
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import get_partner_agent
from src.api.schemas import DiagnosticRequest, DiagnosticResponse, SendRequest, PartnerScoresResponse
from src.agents.partner.partner_agent import PartnerAgent

router = APIRouter(prefix="/api/v1/partners", tags=["partners"])


@router.post("/{partner_id}/diagnostic", response_model=DiagnosticResponse, status_code=201)
def request_diagnostic(
    partner_id: UUID,
    body: DiagnosticRequest,
    partner_agent: PartnerAgent = Depends(get_partner_agent),
):
    """Deleagă la PartnerAgent.request_diagnostic — ownership verificat în Engine, primul pas."""
    diagnostic = partner_agent.request_diagnostic(partner_id, body.owner_id, body.diagnostic_type)
    return DiagnosticResponse(
        partner_id=diagnostic.partner_id, owner_id=diagnostic.owner_id,
        diagnostic_type=diagnostic.diagnostic_type, message=diagnostic.message,
    )


@router.post("/{partner_id}/send", response_model=PartnerScoresResponse)
def send_message(
    partner_id: UUID,
    body: SendRequest,
    partner_agent: PartnerAgent = Depends(get_partner_agent),
):
    """
    Confirmare umană — deleagă la confirm_and_send() (persistă PDI/PIP),
    apoi citește scorurile proaspăt persistate cu get_recent_scores()
    (decizie de contract, secțiunea 1 — confirm_and_send() nu returnează
    nimic util pentru client).
    """
    partner_agent.confirm_and_send(partner_id, body.owner_id, confirmed=body.confirmed)
    scores = partner_agent.get_recent_scores(body.owner_id)
    return PartnerScoresResponse(pdi=scores.get("PDI"), pip=scores.get("PIP"))


@router.get("/scores", response_model=PartnerScoresResponse)
def get_scores(
    owner_id: UUID,
    partner_agent: PartnerAgent = Depends(get_partner_agent),
):
    """READ-ONLY — citește scorurile PDI/PIP ale owner-ului."""
    scores = partner_agent.get_recent_scores(owner_id)
    return PartnerScoresResponse(pdi=scores.get("PDI"), pip=scores.get("PIP"))
