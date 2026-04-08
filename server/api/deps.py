# api/deps.py
# Libs
from fastapi import Cookie, HTTPException, Request

# Local modules
from server.db.models.session import validate_user_session, UserSession
from server.runtime.registry import Registry

def get_user_session(session_uuid: str | None = Cookie(default=None)) -> UserSession:
    if not session_uuid:
        raise HTTPException(status_code=401, detail="No session cookie found")
    user_session = validate_user_session(session_uuid)
    if not user_session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user_session

def get_registry(request: Request) -> Registry:
    return request.app.state.registry
