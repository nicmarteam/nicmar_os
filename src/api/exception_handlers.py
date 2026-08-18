"""
Handlere de erori — mapare exactă conform 14-api-contract.md, secțiunea 2,
extinsă cu Objections (26-objections-router-contract.md, Deciziile 26A/26B).

Nicio excepție nouă inventată aici — doar mapate cele deja existente
în src/engines/*.py, testate azi în cele 63 de teste.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from psycopg.errors import ForeignKeyViolation

from src.engines.mission.mission_engine import (
    MissionNotReadyError, MissionAccessDeniedError,
    InvalidTransitionError, HumanConfirmationRequiredError,
)
from src.engines.followup.followup_engine import (
    FollowUpDuplicateError, FollowUpAccessDeniedError,
    InvalidTransitionError as FollowUpInvalidTransitionError,
    HumanConfirmationRequiredError as FollowUpHumanConfirmationRequiredError,
)
from src.engines.partner.partner_engine import (
    PartnerDiagnosticAlreadyGeneratedError, PartnerAccessDeniedError,
    InvalidDiagnosticTypeError,
    HumanConfirmationRequiredError as PartnerHumanConfirmationRequiredError,
)
from src.engines.objection.objection_engine import ObjectionNotFoundError


def _error_response(status_code: int, error_code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


ALREADY_EXISTS_ERRORS = (
    MissionNotReadyError, FollowUpDuplicateError, PartnerDiagnosticAlreadyGeneratedError,
)
ACCESS_DENIED_ERRORS = (
    MissionAccessDeniedError, FollowUpAccessDeniedError, PartnerAccessDeniedError,
    # ObjectionNotFoundError — Decizia 26 (verificat): semantic identic cu
    # celelalte AccessDenied ("nu există SAU nu aparține owner_id-ului dat"),
    # deși numele conține "NotFound". Reutilizează categoria existentă,
    # nu introduce una nouă.
    ObjectionNotFoundError,
)
INVALID_TRANSITION_ERRORS = (
    InvalidTransitionError, FollowUpInvalidTransitionError, InvalidDiagnosticTypeError,
)
CONFIRMATION_REQUIRED_ERRORS = (
    HumanConfirmationRequiredError, FollowUpHumanConfirmationRequiredError,
    PartnerHumanConfirmationRequiredError,
)


def register_exception_handlers(app):
    """
    Înregistrează fiecare excepție INDIVIDUAL.

    Verificat direct (nu presupus): FastAPI/Starlette ACCEPTĂ sintaxă
    de tuplu la @app.exception_handler((A, B)) fără eroare, dar NU
    funcționează real la dispatch — testat cu TestClient, ambele
    excepții au dat 500, nu codul mapat. De aceea, înregistrare
    individuală, cu add_exception_handler, în buclă — regulă respectată
    și pentru cele două categorii noi (ValueError, ForeignKeyViolation).
    """
    async def handle_already_exists(request: Request, exc: Exception):
        return _error_response(409, "ALREADY_EXISTS", str(exc))

    async def handle_access_denied(request: Request, exc: Exception):
        return _error_response(403, "ACCESS_DENIED", str(exc))

    async def handle_invalid_transition(request: Request, exc: Exception):
        return _error_response(400, "INVALID_TRANSITION", str(exc))

    async def handle_confirmation_required(request: Request, exc: Exception):
        return _error_response(400, "CONFIRMATION_REQUIRED", str(exc))

    async def handle_invalid_category(request: Request, exc: ValueError):
        return _error_response(400, "INVALID_CATEGORY", str(exc))

    async def handle_invalid_reference(request: Request, exc: ForeignKeyViolation):
        return _error_response(400, "INVALID_REFERENCE", str(exc))

    for exc_cls in ALREADY_EXISTS_ERRORS:
        app.add_exception_handler(exc_cls, handle_already_exists)
    for exc_cls in ACCESS_DENIED_ERRORS:
        app.add_exception_handler(exc_cls, handle_access_denied)
    for exc_cls in INVALID_TRANSITION_ERRORS:
        app.add_exception_handler(exc_cls, handle_invalid_transition)
    for exc_cls in CONFIRMATION_REQUIRED_ERRORS:
        app.add_exception_handler(exc_cls, handle_confirmation_required)

    # Decizia 26A — ValueError (categorie invalidă la /prepare) -> 400 INVALID_CATEGORY
    app.add_exception_handler(ValueError, handle_invalid_category)
    # Decizia 26B — ForeignKeyViolation (conversation_id inexistent) -> 400 INVALID_REFERENCE
    app.add_exception_handler(ForeignKeyViolation, handle_invalid_reference)
