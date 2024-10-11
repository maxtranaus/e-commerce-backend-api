from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.category import Category


class ProductBase(SQLModel):
    name: str
    quantity: int
    description: str
    price: float
    category_id: int = Field(foreign_key="category.id")


class Product(ProductBase, table=True):
    id: Optional[int] = Field(primary_key=True)
    category: Category = Relationship(back_populates="products")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    quantity: int | None = None
    price: float | None = None


class ProductPublic(ProductBase):
    id: int
