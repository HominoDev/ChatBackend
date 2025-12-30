# server/db_init.py
# Libs
from sqlmodel import SQLModel
from server.db.engine import engine

from server.db.models.user import User

def init_db():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
