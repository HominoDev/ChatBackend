# server/db/models/session.py
# Libs
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
from datetime import datetime
# Local modules
from server.utils.hashing import hash_password, verify_password
from server.db.engine import engine

class UserSession(SQLModel, table=True):
    __tablename__ = "user_sessions"

    id:         Optional[int] = Field(default=None, primary_key=True)
    user_id:    int           = Field(index=True, nullable=False)
    uuid:       str           = Field(nullable=False, max_length=256)
    created_at: datetime      = Field(default_factory=datetime.utcnow)
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

def get_user_session_by_uuid(uuid: str) -> Optional[UserSession]:
    with Session(engine) as session:
        statement = select(UserSession).where(UserSession.uuid == uuid)
        return session.exec(statement).first()
    return None

def get_user_sessions_by_user_id(user_id: int) -> list[UserSession]:
    with Session(engine) as session:
        statement = select(UserSession).where(UserSession.user_id == user_id)
        return session.exec(statement).all()

def delete_user_session(uuid: str) -> None:
    with Session(engine) as session:
        statement = select(UserSession).where(UserSession.uuid == uuid)
        db_user_session = session.exec(statement).first()
        if db_user_session:
            session.delete(db_user_session)
            session.commit()

def validate_user_session(uuid: str) -> Optional[UserSession]:
    with Session(engine) as session:
        statement = select(UserSession).where(UserSession.uuid == uuid)
        db_user_session = session.exec(statement).first()
        if db_user_session and db_user_session.expired_at > datetime.utcnow():
            return db_user_session
    return None