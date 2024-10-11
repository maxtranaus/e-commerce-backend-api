from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.config import config
from app.models import User
from app.models.user import Role, TokenUser
from app.utils.auth_utils import bcrypt_context, oauth2_bearer


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User | None:
    result = await db.exec(select(User).where(User.email == email))
    user = result.first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.password):
        return None
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta) -> str:
    encode = {
        "sub": username,
        "id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(encode, config.secret_key, algorithm=config.algorithm)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> TokenUser:
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        if (
            (payload.get("sub") is None)
            or (payload.get("id") is None)
            or (not isinstance(payload.get("id"), int))
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
            )
        token_user = TokenUser(
            str(payload.get("sub")), int(str(payload.get("id"))), Role(str(payload.get("role")))
        )
        return token_user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
        )


def get_admin_user(logged_in_user: TokenUser = Depends(get_current_user)) -> TokenUser:
    if logged_in_user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin access required"
        )
    return logged_in_user


def check_admin_or_current_user(
    user_id: int, logged_in_user: TokenUser = Depends(get_current_user)
) -> TokenUser:
    if logged_in_user.role != Role.admin and logged_in_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin or current user access required"
        )
    return logged_in_user
