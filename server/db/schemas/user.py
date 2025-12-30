# server/db/schemas/user.py
# Libs
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    nickname: str
    email: EmailStr
    password: str 
    
class UserAuthenticate(BaseModel):
    email: EmailStr
    password: str