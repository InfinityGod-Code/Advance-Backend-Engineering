from fastapi import APIRouter, HTTPException
from datetime import datetime
from uuid import UUID

from models.product import Product, products_db
from schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(payload: ProductCreate):
    now = datetime.utcnow().isoformat()
    product = Product(
        **payload.model_dump(),
        publisher="Rockstar Games",
        created_at=now,
        updated_at=now,
    )
    products_db[product.id] = product
    return product


@router.get("/", response_model=list[ProductResponse])
def list_products():
    return list(products_db.values())


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: UUID, payload: ProductUpdate):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    product = products_db[product_id]
    update_data = payload.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()
    updated = product.model_copy(update=update_data)
    products_db[product_id] = updated
    return updated


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: UUID):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    del products_db[product_id]
