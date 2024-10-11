from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.engine import ScalarResult
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.product import Product, ProductCreate, ProductUpdate


async def create_new_product(product_request: ProductCreate, db: AsyncSession) -> Product:
    product = Product(**product_request.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def get_all_products(db: AsyncSession) -> list[Product]:
    result: ScalarResult[Product] = await db.exec(select(Product))
    return list(result.all())


async def get_product_by_id(product_id: int, db: AsyncSession) -> Product | None:
    result: Product | None = await db.get(Product, product_id)
    return result


async def update_product_info(
    product_view: ProductUpdate, product_id: int, db: AsyncSession
) -> Product:
    db_product: Product | None = await db.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    product_data: dict[str, Any] = product_view.model_dump(exclude_unset=True)
    db_product.sqlmodel_update(product_data)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def delete_product_by_id(product_id: int, db: AsyncSession) -> None:
    db_product: Product | None = await db.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    await db.delete(db_product)
    await db.commit()
