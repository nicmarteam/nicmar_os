"""
Router Conversations — API, sursă: 33-conversation-objection-linkage-contract.md.

Router subțire — expune ConversationEngine.get_or_create_conversation().
channel NU e acceptat din request — rămâne hardcodat 'WHATSAPP' server-side
(nicio altă valoare de canal nu e folosită real nicăieri, componenta 5
fiind neconstruită încă).
"""

from fastapi import APIRouter, Depends

from src.api.dependencies import get_conversation_engine
from src.api.schemas import CreateConversationRequest, ConversationResponse
from src.auth.dependencies import get_current_user, CurrentUser
from src.engines.conversation.conversation_engine import ConversationEngine

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=201)
def create_conversation(
    body: CreateConversationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    conversation_engine: ConversationEngine = Depends(get_conversation_engine),
):
    """
    Returnează conversația deschisă existentă, sau creează una nouă.

    owner_id vine exclusiv din current_user.id — niciodată din body.
    Idempotent — un al doilea apel, același contact, returnează
    aceeași conversație (nu creează un rând nou).
    """
    conversation = conversation_engine.get_or_create_conversation(
        owner_id=current_user.id, contact_id=body.contact_id,
    )
    return ConversationResponse(
        id=conversation.id, owner_id=conversation.owner_id, contact_id=conversation.contact_id,
        channel=conversation.channel, status=conversation.status,
    )
