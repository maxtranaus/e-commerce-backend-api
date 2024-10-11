from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from app.models.product import Product
from app.models.user import User

if TYPE_CHECKING:
    from app.models.order import Order


class CartBase(SQLModel):
    created_date: Optional[date] = Field(default_factory=date.today, nullable=False)


class Cart(CartBase, table=True):
    id: Optional[int] = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="carts")
    cart_items: list["CartItem"] = Relationship(
        sa_relationship=relationship(
            "CartItem", cascade="all, delete", back_populates="cart", lazy="selectin"
        )
    )
    order: Optional["Order"] = Relationship(
        sa_relationship_kwargs={"uselist": False}, back_populates="cart"
    )


class CartCreate(CartBase):
    pass


class CartPublic(CartBase):
    id: int
    user_id: int


class CartItemBase(SQLModel):
    created_date: Optional[date] = Field(default_factory=date.today, nullable=False)
    product_id: int = Field(foreign_key="product.id")


class CartItem(CartItemBase, table=True):
    id: Optional[int] = Field(primary_key=True)
    product: Product = Relationship()
    cart_id: int = Field(foreign_key="cart.id")
    cart: Cart = Relationship(back_populates="cart_items")


class CartItemCreate(CartItemBase):
    pass


class CartItemPublic(CartItemBase):
    id: int


class CartPublicWithItems(CartPublic):
    cart_items: list[CartItemPublic] = []
