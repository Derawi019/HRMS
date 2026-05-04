from __future__ import annotations

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db as get_db_dependency
from app.models import Employee, Role
from app.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_token_payload(
    cred: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
) -> dict:
    if not cred:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    payload = decode_access_token(cred.credentials)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return payload


def get_current_user(
    db: Annotated[Session, Depends(get_db_dependency)],
    payload: Annotated[dict, Depends(get_token_payload)],
) -> Employee:
    email = payload.get("sub")
    if not email or not isinstance(email, str):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token subject")
    user = db.query(Employee).filter(Employee.email == email.lower()).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def require_roles(*roles: Role):

    def _inner(user: Annotated[Employee, Depends(get_current_user)]) -> Employee:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user

    return _inner


DbSession = Annotated[Session, Depends(get_db_dependency)]
CurrentUser = Annotated[Employee, Depends(get_current_user)]
