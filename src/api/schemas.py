"""
Schema Pydantic pentru API — Mission, FollowUp, Partner, Objections și Auth.
"""

from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class CreateMissionRequest(BaseModel):
    title: str


class MissionResponse(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    status: str


class StartMissionRequest(BaseModel):
    confirmed: bool


class PresentMissionResponse(BaseModel):
    text: str


class DisScoreResponse(BaseModel):
    dis_score: Optional[float]


class ErrorResponse(BaseModel):
    error_code: str
    message: str


# ------------------------------------------------------------------
# Auth
# ------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    """Sursă: 30-auth-register-contract.md, secțiunile 3-4."""

    email: str
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def _validate_password_length(cls, v: str) -> str:
        byte_length = len(v.encode("utf-8"))
        if len(v) < 8:
            raise ValueError("Parola trebuie să aibă minimum 8 caractere.")
        if byte_length > 72:
            raise ValueError("Parola nu poate depăși 72 de bytes (UTF-8).")
        return v


class RegisterResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ------------------------------------------------------------------
# FollowUp — sursă: 15-followup-api-contract.md
# ------------------------------------------------------------------

class CreateFollowUpRequest(BaseModel):
    contact_id: UUID
    conversation_id: UUID


class FollowUpResponse(BaseModel):
    id: UUID
    owner_id: UUID
    contact_id: UUID
    conversation_id: Optional[UUID]
    status: str


class CompleteFollowUpRequest(BaseModel):
    confirmed: bool


# ------------------------------------------------------------------
# Partner — sursă: 16-partner-api-contract.md
# ------------------------------------------------------------------

class DiagnosticRequest(BaseModel):
    diagnostic_type: str


class DiagnosticResponse(BaseModel):
    partner_id: UUID
    owner_id: UUID
    diagnostic_type: str
    message: str


class SendRequest(BaseModel):
    confirmed: bool


class PartnerScoresResponse(BaseModel):
    pdi: Optional[float] = None
    pip: Optional[float] = None


# ------------------------------------------------------------------
# Objections — sursă: 26-objections-router-contract.md
# ------------------------------------------------------------------

class AnalyzeObjectionRequest(BaseModel):
    objection_text: str


class AnalyzeObjectionResponse(BaseModel):
    detected_category: Optional[str]
    needs_manual_selection: bool


class CategoriesResponse(BaseModel):
    categories: List[str]


class PrepareResponseOptionsRequest(BaseModel):
    objection_text: str
    objection_category: str
    conversation_id: Optional[UUID] = None


class PrepareResponseOptionsResponse(BaseModel):
    objection_id: UUID
    variants: Dict[str, str]


class ConfirmResponseRequest(BaseModel):
    objection_id: UUID
    response_text: str
    response_variant_used: str


class ConfirmResponseResponseSchema(BaseModel):
    persisted: bool
    validation_level: str
    reason: Optional[str]
