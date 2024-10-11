from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.engine import ScalarResult
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.category import Category, CategoryCreate, CategoryUpdate


async def create_new_category(category_request: CategoryCreate, db: AsyncSession) -> Category:
    category = Category(**category_request.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def get_all_categories(db: AsyncSession) -> list[Category]:
    result: ScalarResult[Category] = await db.exec(select(Category))
    return list(result.all())


async def get_category_by_id(category_id: int, db: AsyncSession) -> Category | None:
    result: Category | None = await db.get(Category, category_id)
    return result


async def update_category_info(
    category_view: CategoryUpdate, category_id: int, db: AsyncSession
) -> Category:
    db_category: Category | None = await db.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    category_data: dict[str, Any] = category_view.model_dump(exclude_unset=True)
    db_category.sqlmodel_update(category_data)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def delete_category_by_id(category_id: int, db: AsyncSession) -> None:
    db_category: Category | None = await db.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    await db.delete(db_category)
    await db.commit()
