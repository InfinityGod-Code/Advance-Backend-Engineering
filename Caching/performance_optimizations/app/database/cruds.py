from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.product import get_product_catalog
from app.database.models import Product, ProductCreate, ProductUpdate


async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def get_product(db: AsyncSession, product_id: UUID) -> Product | None:

    # we will be using the redis cache system to cache the product data for faster retrieval.
    #  If the product is not found in the cache, we will query the database and then
    #  store the result in the cache for future requests. This will help reduce database load and
    #  improve response times for frequently accessed products.
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def get_optimized_product(
    product_id: UUID,
    db: AsyncSession,
    redis,
) -> Product | None:
    return await get_product_catalog(
        product_id=product_id,
        db=db,
        redis=redis,
        execute_heavy_db_query=get_product,
    )


async def list_products(db: AsyncSession) -> list[Product]:
    result = await db.execute(select(Product))
    return list(result.scalars().all())


async def update_product(
    db: AsyncSession, product_id: UUID, data: ProductUpdate
) -> Product | None:
    product = await get_product(db, product_id)
    if not product:
        return None
    update_data = data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()
    for key, value in update_data.items():
        setattr(product, key, value)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product_id: UUID) -> bool:
    product = await get_product(db, product_id)
    if not product:
        return False
    await db.delete(product)
    await db.commit()
    return True
