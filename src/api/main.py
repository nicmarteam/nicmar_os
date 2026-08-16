"""
NicMar OS — API principal.

Sursă: 14-api-contract.md. Include doar Mission (primul vertical slice
API), conform ordinii stabilite. FollowUp și Partner urmează separat.
"""

from fastapi import FastAPI

from src.api.routers import missions, followups, partners, auth
from src.api.exception_handlers import register_exception_handlers

app = FastAPI(
    title="NicMar OS API",
    version="0.1.0",
    description="API pentru NicMar OS — v1, Mission + FollowUp + Partner + Auth.",
)

register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(missions.router)
app.include_router(followups.router)
app.include_router(partners.router)


@app.get("/health")
def health_check():
    """Verificare simplă că API-ul răspunde — nu atinge baza de date."""
    return {"status": "ok"}
