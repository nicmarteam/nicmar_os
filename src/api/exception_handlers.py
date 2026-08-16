"""
Handlere de erori — mapare exactă conform 14-api-contract.md, secțiunea 2.

Nicio excepție nouă inventată aici — doar mapate cele deja existente
în src/engines/*.py, testate azi în cele 63 de teste.
"""

from fastapi import Request
from fastapi.responses import JSONResponse

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
    individuală, cu add_exception_handler, în buclă.
    """
    async def handle_already_exists(request: Request, exc: Exception):
        return _error_response(409, "ALREADY_EXISTS", str(exc))

    async def handle_access_denied(request: Request, exc: Exception):
        return _error_response(403, "ACCESS_DENIED", str(exc))

    async def handle_invalid_transition(request: Request, exc: Exception):
        return _error_response(400, "INVALID_TRANSITION", str(exc))

    async def handle_confirmation_required(request: Request, exc: Exception):
        return _error_response(400, "CONFIRMATION_REQUIRED", str(exc))

    for exc_cls in ALREADY_EXISTS_ERRORS:
        app.add_exception_handler(exc_cls, handle_already_exists)
    for exc_cls in ACCESS_DENIED_ERRORS:
        app.add_exception_handler(exc_cls, handle_access_denied)
    for exc_cls in INVALID_TRANSITION_ERRORS:
        app.add_exception_handler(exc_cls, handle_invalid_transition)
    for exc_cls in CONFIRMATION_REQUIRED_ERRORS:
        app.add_exception_handler(exc_cls, handle_confirmation_required)
