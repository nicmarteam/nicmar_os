"""
Router Contacts — API, sursă: 31-contact-create-contract.md,
33-conversation-objection-linkage-contract.md.

Router subțire — fără logică de business, fără SQL. owner_id vine
exclusiv din JWT, status e hardcodat server-side în ContactEngine.
"""

from typing import List

from fastapi import APIRouter, Depends

from src.api.dependencies import get_contact_engine, get_contact_agent
from src.api.schemas import CreateContactRequest, ContactResponse, ContactSummaryResponse
from src.auth.dependencies import get_current_user, CurrentUser
from src.engines.contact.contact_engine import ContactEngine
from src.agents.contact.contact_agent import ContactAgent

router = APIRouter(prefix="/api/v1/contacts", tags=["contacts"])


@router.get("", response_model=List[ContactSummaryResponse])
def list_contacts(
    current_user: CurrentUser = Depends(get_current_user),
    contact_agent: ContactAgent = Depends(get_contact_agent),
):
    """
    Listă prioritizată de contacte ale liderului autentificat.

    READ-ONLY — deleagă integral la ContactAgent (Decizia 33), deja
    implementat și testat, doar neconectat la HTTP până acum.
    """
    summaries = contact_agent.list_prioritized_contacts(current_user.id)
    return [
        ContactSummaryResponse(
            contact_id=s.contact_id, full_name=s.full_name, status=s.status,
            last_followup_at=s.last_followup_at, last_followup_status=s.last_followup_status,
            converted_to=s.converted_to, pdi=s.pdi, pip=s.pip, reason=s.reason,
            partner_id=s.partner_id,
        )
        for s in summaries
    ]


@router.post("", response_model=ContactResponse, status_code=201)
def create_contact(
    body: CreateContactRequest,
    current_user: CurrentUser = Depends(get_current_user),
    contact_engine: ContactEngine = Depends(get_contact_engine),
):
    """
    Creează un contact nou pentru liderul autentificat.

    owner_id vine exclusiv din current_user.id — niciodată din body.
    status e hardcodat 'NEW' în ContactEngine — niciodată din body.
    """
    contact = contact_engine.create_contact(
        owner_id=current_user.id,
        full_name=body.full_name,
        phone=body.phone,
        email=body.email,
        source=body.source,
        metadata=body.metadata,
    )
    return ContactResponse(
        id=contact.id, owner_id=contact.owner_id, full_name=contact.full_name,
        phone=contact.phone, email=contact.email, status=contact.status,
        source=contact.source, metadata=contact.metadata,
    )
