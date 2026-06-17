from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    platform: str
    release_date: str
    genre: str = "Action-Adventure"
    age_rating: str = "M (Mature 17+)"
    edition: str = "Standard"
    features: list[str] = []
    currency: str = "USD"
    sale_status: str = "coming_soon"
    max_per_user: int = 2
    sale_starts_at: Optional[str] = None
    sale_ends_at: Optional[str] = None
    image_url: Optional[str] = None
    rating: float = 0.0
    discount_percent: Optional[float] = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    platform: Optional[str] = None
    release_date: Optional[str] = None
    genre: Optional[str] = None
    age_rating: Optional[str] = None
    edition: Optional[str] = None
    features: Optional[list[str]] = None
    currency: Optional[str] = None
    sale_status: Optional[str] = None
    max_per_user: Optional[int] = None
    sale_starts_at: Optional[str] = None
    sale_ends_at: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    discount_percent: Optional[float] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str
    price: float
    stock: int
    platform: str
    publisher: str
    release_date: str
    genre: str
    age_rating: str
    edition: str
    features: list[str]
    currency: str
    sale_status: str
    max_per_user: int
    sale_starts_at: Optional[str] = None
    sale_ends_at: Optional[str] = None
    image_url: Optional[str] = None
    rating: float
    discount_percent: Optional[float] = None
    is_active: bool
    created_at: str
    updated_at: str
