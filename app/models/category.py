from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

# Solve the circular import problem by using TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.product import Product


class CategoryBase(SQLModel):
    name: str


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(primary_key=True)
    products: list["Product"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(SQLModel):
    name: str | None = None


class CategoryPublic(CategoryBase):
    id: int
