# server/app.py
# Libs
from fastapi import FastAPI, HTTPException, Response, Request
import logging
from datetime import datetime, timezone, timedelta
import uuid

# Local modules
from server.db.models.user import User, create_user, authorize_user
from server.db.engine import engine
from server.db.schemas.user import UserCreate, UserAuthenticate
from server.db.models.session import UserSession, create_user_session, validate_user_session, delete_user_session

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.info(f"Database engine initialized {engine}")

# FastAPI app
app = FastAPI()

# Settings section
SESSION_EXPIRE_HOURS = 24

# Functions
def get_session(request: Request) -> str:
    session_uuid = request.cookies.get("session_uuid")
    if not session_uuid:
        raise HTTPException(status_code=401, detail="No session cookie found")
    user_session = validate_user_session(session_uuid) 
    if not user_session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return session_uuid

# Endpoints
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Auth endpoints
@app.post("/auth/register")
def register_user(user: UserCreate):
    db_user = create_user(user.nickname, user.email, user.password)
    return {
        "ok": True,
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "nickname": db_user.nickname,
            "created_at": db_user.created_at
        }
    }

@app.post("/auth/login")
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
        secure=False, # Set to True in production with HTTPS
        path="/",
        max_age=SESSION_EXPIRE_HOURS * 3600
    )
    
    return {"ok": True}

@app.post("/auth/logout")
def logout_user(request: Request, response: Response):
    session_uuid = get_session(request)
    delete_user_session(session_uuid)
    response.delete_cookie("session_uuid")
    return {"ok": True}

# Widget endpoints
@app.get("/widgets/chats/get_message")
def get_message(request: Request):
    session_uuid = get_session(request)
    
    return {"ok": True}

# 
@app.get("/test-session")
def test_session(request: Request):
    session_uuid = get_session(request)
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)