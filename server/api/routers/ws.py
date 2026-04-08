# server/api/routers/ws.py
# Libs
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Cookie
import logging

# Local modules
from server.db.models.session import validate_user_session

log = logging.getLogger(__name__)
router = APIRouter(tags=["ws"])

@router.websocket("/ws/{channel_key}")
async def ws_channel(websocket: WebSocket, channel_key: str, session_uuid: str | None = Cookie(default=None)):
    """WebSocket endpoint with session authentication"""
    # Validate session before accepting connection
    if not session_uuid:
        await websocket.close(code=1008, reason="No session cookie found")
        return
    
    user_session = validate_user_session(session_uuid)
    if not user_session:
        await websocket.close(code=1008, reason="Invalid or expired session")
        return
    
    await websocket.accept()
    log.info(f"WebSocket connection established for user {user_session.user_id} on channel {channel_key}")

    registry = websocket.app.state.registry
    await registry.hub.acquire(channel_key, websocket)

    try:
        while True:
            await websocket.receive_text()  # hold connection
    except WebSocketDisconnect:
        log.debug(f"WebSocket disconnected for user {user_session.user_id}")
    except Exception as e:
        log.error(f"WebSocket error for user {user_session.user_id}: {e}")
    finally:
        await registry.hub.release(channel_key, websocket)
        log.info(f"WebSocket released for user {user_session.user_id}")