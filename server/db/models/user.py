# server/db/models/user.py
# Libs
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
from datetime import datetime, timezone
# Local modules
from server.utils.hashing import hash_password, verify_password
from server.db.engine import engine

class User(SQLModel, table=True):
    __tablename__ = "users"

    id:              Optional[int] = Field(default=None, primary_key=True)
    email:           str           = Field(index=True, unique=True, nullable=False, max_length=100)
    nickname:        str           = Field(index=True, unique=True, nullable=False, max_length=50)
    hashed_password: str           = Field(nullable=False, max_length=128)
    created_at:      datetime      = Field(default_factory=lambda: datetime.now(timezone.utc))

def create_user(nickname: str, email: str, password: str) -> User:
    with Session(engine) as session:
        user = User(
            nickname=nickname, 
            email=email, 
            hashed_password=hash_password(password)
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
def authorize_user(email: str, password: str) -> Optional[User]:
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if user and verify_password(password, user.hashed_password):
            return user
        return None