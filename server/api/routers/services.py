# api/routers/services.py
# Libs
from fastapi import APIRouter, Depends

# Local modules
from server.api.deps import get_session_uuid

router = APIRouter(prefix="/services", tags=["services"])

@router.get("/chats/get_message")
def get_message(session_uuid: str = Depends(get_session_uuid)):
    return {"ok": True}

@router.get("/test-session")
def test_session(session_uuid: str = Depends(get_session_uuid)):
    return {"ok": True}
