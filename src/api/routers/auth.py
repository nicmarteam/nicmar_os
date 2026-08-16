"""
Router Auth — /api/v1/auth/login.

Singurul endpoint din acest slice. get_current_user() (folosit de
celelalte routere) e o dependency, nu un endpoint propriu.
"""

from fastapi import APIRouter, HTTPException

from src.api.schemas import LoginRequest, TokenResponse
from src.auth.service import authenticate, InvalidCredentialsError

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    """
    Verifică email+parolă, returnează access token JWT.

    401 pentru orice combinație invalidă — mesaj identic (email
    inexistent, parolă greșită, password_hash=NULL), previne
    enumerarea de conturi.
    """
    try:
        token = authenticate(body.email, body.password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))

    return TokenResponse(access_token=token, token_type="bearer")
