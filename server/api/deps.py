# api/deps.py
# Libs
from fastapi import Cookie, HTTPException

# Local modules
from server.db.models.session import validate_user_session

def get_session_uuid(session_uuid: str | None = Cookie(default=None)) -> str:
    if not session_uuid:
        raise HTTPException(status_code=401, detail="No session cookie found")
    user_session = validate_user_session(session_uuid)
    if not user_session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return session_uuid
