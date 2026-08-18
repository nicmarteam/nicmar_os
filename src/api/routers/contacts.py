"""
Router Contacts — API, sursă: 31-contact-create-contract.md.

Router subțire — fără logică de business, fără SQL. owner_id vine
exclusiv din JWT, status e hardcodat server-side în ContactEngine.
"""

from fastapi import APIRouter, Depends

from src.api.dependencies import get_contact_engine
from src.api.schemas import CreateContactRequest, ContactResponse
from src.auth.dependencies import get_current_user, CurrentUser
from src.engines.contact.contact_engine import ContactEngine

router = APIRouter(prefix="/api/v1/contacts", tags=["contacts"])


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
