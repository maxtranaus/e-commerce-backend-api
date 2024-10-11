from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.database import get_async_session
from app.models.product import Product, ProductCreate, ProductPublic, ProductUpdate
from app.models.user import TokenUser
from app.services.auth_service import get_admin_user, get_current_user
from app.services.product_service import (
    create_new_product,
    delete_product_by_id,
    get_all_products,
    get_product_by_id,
    update_product_info,
)

router = APIRouter(prefix="/product", tags=["product"])


# Create a new product in the database, only admin can access this API
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductPublic)
async def create_product(
    product_request: ProductCreate,
    _: TokenUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
) -> Product:
    product: Product = await create_new_product(product_request, db)
    return product


# Get all products in the database, all users can access this API
@router.get("", status_code=status.HTTP_200_OK, response_model=list[ProductPublic])
async def get_products(
    _: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[Product]:
    products: list[Product] = await get_all_products(session)
    return products


# Get product by id, all users can access this API
@router.get("/product/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductPublic)
async def get_product_id(
    product_id: int,
    _: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Product:
    product: Product | None = await get_product_by_id(product_id, session)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


# Update product information, only admin can access this API
@router.put("/product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def change_product(
    product_view: ProductUpdate,
    product_id: int,
    _: TokenUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    await update_product_info(product_view, product_id, db)


# Delete product by id, only admin can access this API
@router.delete("/product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    _: TokenUser = Depends(get_admin_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await delete_product_by_id(product_id, session)
