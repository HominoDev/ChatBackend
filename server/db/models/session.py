# server/db/models/session.py
# Libs
from sqlmodel import Field, Session, SQLModel, select
from typing import Optional
from datetime import datetime, timezone

# Local modules
from server.db.engine import engine

class UserSession(SQLModel, table=True):
    __tablename__ = "user_sessions"
    
    id:         Optional[int] = Field(default=None, primary_key=True)
    user_id:    int           = Field(index=True, nullable=False)
    uuid:       str           = Field(nullable=False, max_length=256)
    created_at: datetime      = Field(default_factory=lambda: datetime.now(timezone.utc))
    expired_at: datetime      = Field(nullable=False)

def create_user_session(user_id: int, uuid: str, expired_at: datetime) -> UserSession:
    with Session(engine) as session:
        user_session = UserSession(
            user_id=user_id,
            uuid=uuid,
            expired_at=expired_at
        )
        session.add(user_session)
        session.commit()
        session.refresh(user_session)
        return user_session

def delete_user_session(uuid: str) -> bool:
    with Session(engine) as session:
        statement = select(UserSession).where(UserSession.uuid == uuid)
        db_user_session = session.exec(statement).first()
        if not db_user_session:
            return False
        session.delete(db_user_session)
        session.commit()
        return True

def validate_user_session(uuid: str) -> Optional[UserSession]:
    with Session(engine) as session:
        statement = select(UserSession).where(UserSession.uuid == uuid)
        db_user_session = session.exec(statement).first()
        if db_user_session and db_user_session.expired_at > datetime.now(timezone.utc):
            return db_user_session
        if db_user_session:
            session.delete(db_user_session)
            session.commit()
        return None

def get_user_session_by_uuid(uuid: str) -> Optional[UserSession]:
    with Session(engine) as session:
        statement = select(UserSession).where(UserSession.uuid == uuid)
        return session.exec(statement).first()

def get_user_sessions_by_user_id(user_id: int) -> list[UserSession]:
    with Session(engine) as session:
        statement = select(UserSession).where(UserSession.user_id == user_id)
        return session.exec(statement).all()