# server/utils/hashing.py
# Libs
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_BCRYPT_BYTES = 72

def hash_password(password: str) -> str:
    # Truncate to avoid bcrypt limit
    truncated = password.encode("utf-8")[:MAX_BCRYPT_BYTES].decode("utf-8", "ignore")
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password.encode("utf-8")[:MAX_BCRYPT_BYTES].decode("utf-8", "ignore")
    return pwd_context.verify(truncated, hashed_password)
