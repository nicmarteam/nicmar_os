"""
InviteEngine — Decizia 48, `48-invite-contract.md`.

SCHELET RED: clasele de excepție și semnăturile publice există pentru
ca testele să poată rula și eșua din motivul corect (comportament
lipsă), nu din `ModuleNotFoundError`. Implementarea vine la GREEN.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


class InviteAccessDeniedError(Exception):
    """Contactul sau invitația nu există, sau nu aparțin owner-ului dat."""


class InvalidFrameError(Exception):
    """`frame` în afara valorilor permise (Contract 48, §5)."""


class InvalidPurposeError(Exception):
    """`purpose` în afara valorilor permise (Contract 48, §5)."""


class InvalidInviteToneError(Exception):
    """`tone_used` în afara valorilor permise."""


class InvalidInviteOutcomeError(Exception):
    """`outcome` în afara celor 5 valori permise (Contract 48, §6)."""


class InviteOutcomeAlreadyRecordedError(Exception):
    """Această invitație are deja un Outcome — cardinalitate 0..1."""


@dataclass
class Invitation:
    id: UUID
    owner_id: UUID
    contact_id: UUID
    frame: str
    purpose: str
    message_text: str
    tone_used: str


@dataclass
class InvitationOutcomeResult:
    id: UUID
    invitation_id: UUID
    outcome: str
    meeting_id: Optional[UUID]


@dataclass
class Meeting:
    id: UUID
    owner_id: UUID
    title: str
    status: str


class InviteEngine:
    """Proprietarul ciclului de viață `invitations`/`invitation_outcomes`."""

    def create_invitation(
        self,
        owner_id: UUID,
        contact_id: UUID,
        frame: str,
        purpose: str,
        message_text: str,
        tone_used: str,
    ) -> Invitation:
        raise NotImplementedError("Decizia 48 — GREEN neimplementat încă.")

    def record_outcome(
        self,
        owner_id: UUID,
        invitation_id: UUID,
        outcome: str,
    ) -> InvitationOutcomeResult:
        raise NotImplementedError("Decizia 48 — GREEN neimplementat încă.")

    def schedule_meeting(
        self,
        owner_id: UUID,
        invitation_id: UUID,
        title: str,
        scheduled_at: str,
    ) -> Meeting:
        raise NotImplementedError("Decizia 48 — GREEN neimplementat încă.")
