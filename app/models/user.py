import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from sqlmodel import Column, Enum, Field, Relationship, SQLModel

# resolve circular import
if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.order import Order


class Role(str, enum.Enum):
    admin = "admin"
    user = "user"


class UserBase(SQLModel):
    name: str
    email: str = Field(index=True)
    role: Role = Field(sa_column=Column(Enum(Role), default=Role.user, nullable=False))


# Create User model with email as username and password to login to the application
class User(UserBase, table=True):
    id: Optional[int] = Field(primary_key=True)
    password: str
    carts: Optional[list["Cart"]] = Relationship(back_populates="user")
    orders: Optional[list["Order"]] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserUpdatePassword(SQLModel):
    password: str
    new_password: str = Field(min_length=6)


class UserUpdateInfo(SQLModel):
    name: str | None = None
    email: str | None = None


class UserPublic(UserBase):
    id: int


@dataclass
class TokenUser:
    """User model that is extracted from the token."""

    username: str
    id: int
    role: Role
