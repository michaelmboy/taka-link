from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
from app.core.security import decode_token

def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("takalink_session")
    if not token: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in")
    try: payload = decode_token(token); uid = int(payload.get("sub", ""))
    except Exception: raise HTTPException(status_code=401, detail="Session expired or invalid")
    user = db.get(User, uid)
    if not user or not user.active: raise HTTPException(status_code=401, detail="Account unavailable")
    return user

def roles(*allowed: str):
    def checker(user: User = Depends(current_user)) -> User:
        if user.role not in allowed: raise HTTPException(status_code=403, detail="You do not have permission for this action")
        return user
    return checker
