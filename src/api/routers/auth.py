"""
Router Auth — /api/v1/auth/login.

Singurul endpoint din acest slice. get_current_user() (folosit de
celelalte routere) e o dependency, nu un endpoint propriu.
"""

from fastapi import APIRouter, HTTPException, Request

from src.api.schemas import LoginRequest, TokenResponse, RegisterRequest, RegisterResponse
from src.auth.rate_limit import login_rate_limiter
from src.auth.service import authenticate, InvalidCredentialsError
from src.auth.registration import register_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(body: RegisterRequest):
    """
    Creează un utilizator nou (Auth Registration v1, `30-auth-register-contract.md`).

    Nu returnează JWT — derivat explicit din criteriul de acceptare
    stabilit (register → user creat → ... → login separat → JWT).
    Pentru autentificare, apelantul face un request separat la `/login`.

    409 ALREADY_EXISTS dacă emailul există deja — propagat din
    `UniqueViolation`, prins de handler-ul global (`exception_handlers.py`).
    """
    user = register_user(email=body.email, password=body.password, full_name=body.full_name)
    return RegisterResponse(id=user.id, email=user.email, full_name=user.full_name, role=user.role)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request):
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
        raise HTTPException(
            status_code=429,
            detail="Prea multe încercări de autentificare. Încearcă din nou mai târziu.",
            headers={"Retry-After": str(login_rate_limiter.retry_after(client_ip))},
        )

    try:
        token = authenticate(body.email, body.password)
    except InvalidCredentialsError as e:
        login_rate_limiter.record_failure(client_ip)
        raise HTTPException(status_code=401, detail=str(e))

    login_rate_limiter.clear(client_ip)
    return TokenResponse(access_token=token, token_type="bearer")
