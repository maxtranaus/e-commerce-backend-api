from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.database import get_async_session
from app.schemas.auth_schema import Token
from app.services.auth_service import authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


# Create JSON Web Token for user login
# Return the string of access token and token type
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_async_session),
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
        )

    if not user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    token = create_access_token(form_data.username, user.id, user.role, timedelta(minutes=20))
    return Token(access_token=token, token_type="bearer")
