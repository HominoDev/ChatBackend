# api/routers/auth.py
# Libs
from fastapi import APIRouter, HTTPException, Response, Depends
from datetime import datetime, timezone, timedelta
import uuid

# Local modules
from server.db.schemas.user import UserCreate, UserAuthenticate
from server.db.models.user import create_user, authorize_user
from server.db.models.session import create_user_session, delete_user_session
from server.api.deps import get_session_uuid

router = APIRouter(prefix="/auth", tags=["auth"])

SESSION_EXPIRE_HOURS = 24

@router.post("/register")
def register_user(user: UserCreate):
    db_user = create_user(
        user.nickname,
        user.email, 
        user.password
    )
    return {
        "ok": True,
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "nickname": db_user.nickname,
            "created_at": db_user.created_at,
        },
    }

@router.post("/login")
def login_user(auth: UserAuthenticate, response: Response):
    user = authorize_user(auth.email, auth.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_uuid = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_EXPIRE_HOURS)
    create_user_session(user.id, session_uuid, expires_at)

    response.set_cookie(
        key="session_uuid",
        value=session_uuid,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        max_age=SESSION_EXPIRE_HOURS * 3600,
    )
    return {"ok": True}

@router.post("/logout")
def logout_user(response: Response, session_uuid: str = Depends(get_session_uuid)):
    delete_user_session(session_uuid)
    response.delete_cookie("session_uuid", path="/")
    return {"ok": True}
