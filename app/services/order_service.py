from collections import Counter

from fastapi import HTTPException, status
from sqlalchemy.engine import ScalarResult
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.cart import Cart
from app.models.order import Order, OrderCreate, OrderItem, Status
from app.models.product import Product
from app.models.user import Role, TokenUser
from app.utils.auth_utils import check_cart_owner


async def create_new_order(order_request: OrderCreate, db: AsyncSession, user_id: int) -> Order:
    cart: Cart | None = await db.get(Cart, order_request.cart_id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    check_cart_owner(cart, user_id, "You can only create order based on your cart")

    # Get a list of product_id from cart items and count the quantity of each product_id
    # to calculate the order amount and update the order item
    cart_item_product: list[int] = [item.product_id for item in cart.cart_items]
    dict_items = dict(Counter(cart_item_product))
    order_amount: float = 0
    order_items: list[OrderItem] = []
    for prod_id, quantity in dict_items.items():
        product: Product | None = await db.get(Product, prod_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        order_amount += quantity * product.price
        order_items.append(OrderItem(quantity=quantity, product_id=prod_id))

    order = Order(**order_request.model_dump())
    order.user_id = user_id
    order.order_amount = order_amount
    order.order_items = order_items
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def get_orders(db: AsyncSession, user: TokenUser) -> list[Order] | None:
    result: ScalarResult[Order] | None = None
    if user.role == Role.admin:
        result = await db.exec(select(Order))
    else:
        result = await db.exec(select(Order).where(Order.user_id == user.id))
    return list(result.all())


async def get_order_by_id(order_id: int, db: AsyncSession, user: TokenUser) -> Order | None:
    result: ScalarResult[Order] | None = None
    if user.role == Role.admin:
        result = await db.exec(select(Order).where(Order.id == order_id))
    else:
        result = await db.exec(
            select(Order).where(Order.id == order_id).where(Order.user_id == user.id)
        )
    return result.first()


async def update_order_status_by_order_id(
    order_id: int, order_status: str, db: AsyncSession, user: TokenUser
) -> None:
    order: Order | None = await get_order_by_id(order_id, db, user)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order.order_status = Status(order_status)
    await db.commit()
