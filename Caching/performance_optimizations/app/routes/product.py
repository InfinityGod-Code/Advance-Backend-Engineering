from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database.cruds import get_optimized_product

from app.dependancy.db import get_db
from app.dependancy.depandancies import get_redis_client
from app.database.cruds import (
    create_product,
    list_products,
    update_product,
    delete_product,
)
from app.schemas.product import ProductCreate, ProductUpdate, ProductPublic

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductPublic, status_code=201)
async def create(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await create_product(db, data)


@router.get("/", response_model=list[ProductPublic])
async def list_all(db: AsyncSession = Depends(get_db)):
    return await list_products(db)


@router.get("/{product_id}", response_model=ProductPublic)
async def get(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis_client),
):
    product = await get_optimized_product(product_id, db, redis)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductPublic)
async def update(
    product_id: UUID, data: ProductUpdate, db: AsyncSession = Depends(get_db)
):
    product = await update_product(db, product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=204)
async def delete(product_id: UUID, db: AsyncSession = Depends(get_db)):
    deleted = await delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
