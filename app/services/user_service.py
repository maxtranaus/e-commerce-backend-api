from typing import Any

from fastapi import HTTPException
from sqlalchemy.engine import ScalarResult
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.models.user import User, UserCreate, UserUpdateInfo, UserUpdatePassword
from app.utils.auth_utils import bcrypt_context


async def get_all_users(db: AsyncSession) -> list[User]:
    result: ScalarResult[User] = await db.exec(select(User))
    return list(result.all())


async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    result: User | None = await db.get(User, user_id)
    return result


async def create_new_user(create_user_request: UserCreate, db: AsyncSession) -> User:
    create_user_model = User(
        email=create_user_request.email,
        name=create_user_request.name,
        password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
    )
    db.add(create_user_model)
    await db.commit()
    await db.refresh(create_user_model)
    return create_user_model


async def update_password(user_view: UserUpdatePassword, user_id: int, db: AsyncSession) -> None:
    db_user: User | None = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not bcrypt_context.verify(user_view.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password")
    db_user.password = bcrypt_context.hash(user_view.new_password)
    await db.commit()


async def update_information(user_view: UserUpdateInfo, user_id: int, db: AsyncSession) -> User:
    db_user: User | None = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_data: dict[str, Any] = user_view.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user_by_id(user_id: int, db: AsyncSession) -> None:
    db_user: User | None = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(db_user)
    await db.commit()
