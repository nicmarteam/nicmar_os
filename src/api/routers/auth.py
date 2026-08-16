"""
Router Auth — /api/v1/auth/login.

Singurul endpoint din acest slice. get_current_user() (folosit de
celelalte routere) e o dependency, nu un endpoint propriu.
"""

from fastapi import APIRouter, HTTPException, Request, Response

from src.api.schemas import LoginRequest, TokenResponse
from src.auth.rate_limit import login_rate_limiter
from src.auth.service import authenticate, InvalidCredentialsError

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, response: Response):
    """
    Verifică email+parolă, returnează access token JWT.

    401 pentru orice combinație invalidă — mesaj identic (email
    inexistent, parolă greșită, password_hash=NULL), previne
    enumerarea de conturi.

    Rate limiting: maximum 5 încercări nereușite per IP în 60 secunde.
    După depășire, răspunde 429 cu Retry-After. Un login reușit
    resetează contorul pentru IP.
    """
    client_ip = request.client.host if request.client else "unknown"

    if login_rate_limiter.is_limited(client_ip):
        response.headers["Retry-After"] = str(login_rate_limiter.retry_after(client_ip))
        raise HTTPException(
            status_code=429,
            detail="Prea multe încercări de autentificare. Încearcă din nou mai târziu.",
        )

    try:
        token = authenticate(body.email, body.password)
    except InvalidCredentialsError as e:
        login_rate_limiter.record_failure(client_ip)
        raise HTTPException(status_code=401, detail=str(e))

    login_rate_limiter.clear(client_ip)
    return TokenResponse(access_token=token, token_type="bearer")
