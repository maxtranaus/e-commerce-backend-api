from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.database import get_async_session
from app.models.cart import Cart, CartCreate, CartItemCreate, CartPublicWithItems
from app.models.user import TokenUser
from app.services.auth_service import get_current_user
from app.services.cart_service import (
    add_item,
    create_new_cart,
    delete_cart_by_id,
    delete_item,
    get_cart_by_id,
    get_carts,
)

router = APIRouter(prefix="/cart", tags=["cart"])


# Create a new cart for login user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Cart)
async def create_cart(
    cart_request: CartCreate,
    user: TokenUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Cart:
    cart: Cart = await create_new_cart(cart_request, db, user.id)
    return cart


# Get all carts created by login user, admin can see carts of all users
@router.get("", status_code=status.HTTP_200_OK, response_model=list[Cart])
async def get_all_carts(
    user: TokenUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> list[Cart] | None:
    carts: list[Cart] | None = await get_carts(db, user)
    return carts


# Get cart by id, user can get cart created by themselves, admin can get any cart
# Return cart with all items in it
@router.get("/cart/{cart_id}", status_code=status.HTTP_200_OK, response_model=CartPublicWithItems)
async def get_cart_id(
    cart_id: int,
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Cart:
    cart: Cart | None = await get_cart_by_id(cart_id, session, user)
    if cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart


# Add item to cart, only login user can add item to their cart
@router.post("/cart/{cart_id}/item", status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    cart_id: int,
    item_request: CartItemCreate,
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await add_item(cart_id, item_request, session, user.id)


# Delete item from cart, only login user can delete item from their cart
@router.delete("/cart/{cart_id}/item/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_from_cart(
    cart_id: int,
    item_id: int,
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await delete_item(cart_id, item_id, session, user.id)


# Delete cart by id, only login user can delete their cart
@router.delete("/cart/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(
    cart_id: int,
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await delete_cart_by_id(cart_id, session, user.id)
