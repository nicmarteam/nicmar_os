"""
Schema Pydantic pentru API — Mission.

Sursă: 14-api-contract.md, secțiunea 3. Fiecare model reflectă exact
request/response-ul documentat, fără câmpuri suplimentare inventate.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateMissionRequest(BaseModel):
    owner_id: UUID
    title: str


class AssignMissionRequest(BaseModel):
    owner_id: UUID


class MissionResponse(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    status: str


class StartMissionRequest(BaseModel):
    owner_id: UUID
    confirmed: bool


class CompleteMissionRequest(BaseModel):
    owner_id: UUID


class PresentMissionResponse(BaseModel):
    text: str


class DisScoreResponse(BaseModel):
    dis_score: Optional[float]


class ErrorResponse(BaseModel):
    error_code: str
    message: str


# ------------------------------------------------------------------
# FollowUp — sursă: 15-followup-api-contract.md
# ------------------------------------------------------------------

class CreateFollowUpRequest(BaseModel):
    owner_id: UUID
    contact_id: UUID
    conversation_id: UUID


class FollowUpResponse(BaseModel):
    id: UUID
    owner_id: UUID
    contact_id: UUID
    conversation_id: Optional[UUID]
    status: str


class FollowUpActionRequest(BaseModel):
    """Folosit de complete, postpone, reschedule — toate au nevoie doar de owner_id."""
    owner_id: UUID


class CompleteFollowUpRequest(FollowUpActionRequest):
    confirmed: bool
