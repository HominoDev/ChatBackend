# server/db/models/twitch_data.py
# Libs
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime, timezone
# Twitch Data Model
class TwitchData(SQLModel, table=True):
    __tablename__ = "twitch_data"

    id:            Optional[int] = Field(default=None, primary_key=True)
    client_id:     str           = Field(nullable=False, max_length=100)
    client_secret: str           = Field(nullable=False, max_length=100)
    access_token:  str           = Field(nullable=False, max_length=256)
    refresh_token: str           = Field(nullable=False, max_length=256)
    created_at:    datetime      = Field(default_factory=datetime.now(timezone.utc))
    updated_at:    datetime      = Field(default_factory=datetime.now(timezone.utc), sa_column_kwargs={"onupdate": datetime.now(timezone.utc)})
    
def authorize_twitch_data(db_twitch_data: TwitchData, access_token: str, refresh_token: str):
    db_twitch_data.access_token = access_token
    db_twitch_data.refresh_token = refresh_token
    db_twitch_data.updated_at = datetime.now(timezone.utc)
    
def update_tokens(self, access_token: str, refresh_token: str):