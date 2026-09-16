from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.models.models import User

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    unauthorized = HTTPException(status_code=401, detail="请登录后继续", headers={"WWW-Authenticate": "Bearer"})
    if credentials is None:
        raise unauthorized
    payload = decode_token(credentials.credentials)
    try:
        user_id = int(payload.get("sub")) if payload else 0
    except (TypeError, ValueError):
        raise unauthorized
    user = db.query(User).filter(User.id == user_id).first() if user_id > 0 else None
    if user is None:
        raise unauthorized
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user
