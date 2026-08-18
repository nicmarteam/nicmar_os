"""
Router Objections — API, sursă: 26-objections-router-contract.md.

Router subțire — fără logică de business, fără SQL, fără acces direct la
library.py, fără reconstruirea obiectului Objection. Doar transport:
HTTP -> auth -> ConversationAgent -> response.

Regulă de securitate esențială (Decizia 8A, verificată pe PostgreSQL real):
owner_id NU vine niciodată din request — exclusiv din CurrentUser.id (JWT).
objection_category/objection_text NU sunt acceptate la /confirm — se
recuperează server-side, prin ConversationAgent.confirm_response(), care la
rândul lui apelează ObjectionEngine.get_objection() intern.
"""

from fastapi import APIRouter, Depends

from src.api.dependencies import get_conversation_agent
from src.api.schemas import (
    AnalyzeObjectionRequest, AnalyzeObjectionResponse, CategoriesResponse,
    ConfirmResponseRequest, ConfirmResponseResponseSchema,
    PrepareResponseOptionsRequest, PrepareResponseOptionsResponse,
)
from src.auth.dependencies import get_current_user, CurrentUser
from src.agents.conversation.conversation_agent import ConversationAgent

router = APIRouter(prefix="/api/v1/objections", tags=["objections"])


@router.post("/analyze", response_model=AnalyzeObjectionResponse)
def analyze_objection(
    body: AnalyzeObjectionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    agent: ConversationAgent = Depends(get_conversation_agent),
):
    """Clasifică determinist textul obiecției — fără nicio scriere în DB."""
    result = agent.analyze_objection(body.objection_text)
    return AnalyzeObjectionResponse(
        detected_category=result.detected_category,
        needs_manual_selection=result.needs_manual_selection,
    )


@router.get("/categories", response_model=CategoriesResponse)
def get_categories(
    current_user: CurrentUser = Depends(get_current_user),
    agent: ConversationAgent = Depends(get_conversation_agent),
):
    """Listează cele 13 categorii oficiale, pentru selecția manuală a liderului."""
    return CategoriesResponse(categories=agent.list_categories())


@router.post("/prepare", response_model=PrepareResponseOptionsResponse, status_code=201)
def prepare_response_options(
    body: PrepareResponseOptionsRequest,
    current_user: CurrentUser = Depends(get_current_user),
    agent: ConversationAgent = Depends(get_conversation_agent),
):
    """
    Creează obiecția și pregătește cele 3 variante de răspuns.

    owner_id vine exclusiv din current_user.id — niciodată din body.
    """
    result = agent.prepare_response_options(
        owner_id=current_user.id,
        objection_text=body.objection_text,
        objection_category=body.objection_category,
        conversation_id=body.conversation_id,
    )
    return PrepareResponseOptionsResponse(objection_id=result.objection.id, variants=result.variants)


@router.post("/confirm", response_model=ConfirmResponseResponseSchema)
def confirm_response(
    body: ConfirmResponseRequest,
    current_user: CurrentUser = Depends(get_current_user),
    agent: ConversationAgent = Depends(get_conversation_agent),
):
    """
    Confirmă și persistă răspunsul final ales/editat de lider.

    owner_id vine exclusiv din current_user.id — niciodată din body.
    objection_category/objection_text NU sunt acceptate aici — vin din DB,
    prin ConversationAgent.confirm_response() -> ObjectionEngine.get_objection().
    BLOCK e rezultat normal (200), nu eroare HTTP — vezi contract secțiunea 3.4.
    """
    result = agent.confirm_response(
        objection_id=body.objection_id,
        owner_id=current_user.id,
        response_text=body.response_text,
        response_variant_used=body.response_variant_used,
    )
    return ConfirmResponseResponseSchema(
        persisted=result.persisted,
        validation_level=result.validation_level,
        reason=result.reason,
    )
