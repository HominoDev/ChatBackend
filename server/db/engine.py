# server/db/engine.py
# Libs
from sqlmodel import create_engine
import os
import logging

log = logging.getLogger(__name__)

def get_database_url() -> str:
    db_password = os.getenv("DB_PASSWORD")
    db_user = os.getenv("DB_USER")
    db_ip = os.getenv("DB_IP")
    db_port = os.getenv("DB_PORT")
    if not all([db_user, db_password, db_ip, db_port]):
        raise ValueError("Missing DB environment variables")
    return f"postgresql://{db_user}:{db_password}@{db_ip}:{db_port}/postgres"

# Disable SQL echo in production to avoid credential leakage in logs
echo_sql = os.getenv("SQL_ECHO", "false").lower() == "true"
log.info(f"SQL echo mode: {echo_sql}")
engine = create_engine(get_database_url(), echo=echo_sql)
