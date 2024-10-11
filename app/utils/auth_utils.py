from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.models.cart import Cart

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


def check_cart_owner(cart: Cart, user_id: int, text: str) -> None:
    if cart.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{text}")
