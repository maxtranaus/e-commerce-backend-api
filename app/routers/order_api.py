from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_async_session
from app.models.order import Order, OrderCreate, OrderPublicWithItems
from app.models.user import TokenUser
from app.services.auth_service import get_admin_user, get_current_user
from app.services.order_service import (
    create_new_order,
    get_order_by_id,
    get_orders,
    update_order_status_by_order_id,
)

router = APIRouter(prefix="/order", tags=["order"])


# For login user: create order from cart, add all cart items into order items
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Order)
async def create_order_from_cart(
    order_request: OrderCreate,
    user: TokenUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Order:
    order: Order = await create_new_order(order_request, db, user.id)
    return order


# Get all orders for login user, admin can see orders of all users
@router.get("", status_code=status.HTTP_200_OK, response_model=list[Order])
async def get_all_orders(
    user: TokenUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> list[Order] | None:
    orders: list[Order] | None = await get_orders(db, user)
    return orders


# Get order by id, user can get order created by themselves, admin can get any order
@router.get(
    "/order/{order_id}", status_code=status.HTTP_200_OK, response_model=OrderPublicWithItems
)
async def get_order_id(
    order_id: int,
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Order:
    order: Order | None = await get_order_by_id(order_id, session, user)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


# Update order status by order id, only admin can update order status
@router.put("/order/{order_id}", status_code=status.HTTP_200_OK)
async def update_order_status(
    order_id: int,
    order_status: str,
    user: TokenUser = Depends(get_admin_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await update_order_status_by_order_id(order_id, order_status, session, user)
