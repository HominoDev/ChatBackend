# server/db/engine.py
# Libs
from sqlmodel import create_engine
import os

# Load environment variables
db_password = os.getenv("DB_PASSWORD")
db_user = os.getenv("DB_USER")
db_ip = os.getenv("DB_IP")
db_port = os.getenv("DB_PORT")
if not all([db_user, db_password, db_ip, db_port]): # Проверка на 
    raise ValueError("⚠️ Missing one or more DB environment variables")

# Database engineex
database_url = f"postgresql://{db_user}:{db_password}@{db_ip}:{db_port}/postgres"
engine = create_engine(database_url, echo=True)