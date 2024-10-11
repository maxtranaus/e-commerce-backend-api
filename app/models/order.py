import enum
from datetime import date
from typing import Optional

from sqlalchemy.orm import relationship
from sqlmodel import Column, Enum, Field, Relationship, SQLModel

from app.models.cart import Cart
from app.models.user import User


class Status(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    shipping = "shipping"
    delivered = "delivered"


class OrderBase(SQLModel):
    order_date: Optional[date] = Field(default_factory=date.today, nullable=False)
    order_status: Status = Field(
        sa_column=Column(Enum(Status), default=Status.pending, nullable=False)
    )
    shipping_address: str
    cart_id: Optional[int] = Field(default=None, foreign_key="cart.id")


class Order(OrderBase, table=True):
    id: Optional[int] = Field(primary_key=True)
    order_amount: float
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="orders")
    # Delete Order, all OrderItem related to this Order will be deleted
    # Delete Cart, Order will be set to None
    # lazy="selectin" is used to load all OrderItem related to this Order for displaying at frontend
    order_items: Optional[list["OrderItem"]] = Relationship(
        sa_relationship=relationship(
            "OrderItem", cascade="all, delete", back_populates="order", lazy="selectin"
        )
    )
    cart: Optional["Cart"] = Relationship(back_populates="order")


class OrderCreate(OrderBase):
    pass


class OrderPublic(OrderBase):
    id: int
    user_id: int
    order_amount: float


class OrderItemBase(SQLModel):
    quantity: int
    created_date: Optional[date] = Field(default_factory=date.today, nullable=False)
    product_id: int = Field(foreign_key="product.id")


class OrderItem(OrderItemBase, table=True):
    id: Optional[int] = Field(primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    order: Order = Relationship(back_populates="order_items")


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemPublic(OrderItemBase):
    id: int


class OrderPublicWithItems(OrderPublic):
    order_items: list[OrderItemPublic] = []
