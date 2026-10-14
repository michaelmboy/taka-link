import bcrypt, jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings
ALGORITHM = "HS256"
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
def verify_password(password: str, password_hash: str) -> bool:
    try: return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception: return False
def create_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "role": role, "iat": now, "exp": now + timedelta(minutes=settings.token_expire_minutes)}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
def decode_token(token: str):
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
