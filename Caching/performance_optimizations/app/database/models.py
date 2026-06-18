from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON


class ProductBase(SQLModel):
    name: str
    description: str
    price: float
    stock: int
    platform: str
    publisher: str = "Rockstar Games"
    release_date: str
    genre: str = "Action-Adventure"
    age_rating: str = "M (Mature 17+)"
    edition: str = "Standard"
    features: list[str] = Field(default=[], sa_column=Column(JSON))
    currency: str = "USD"
    sale_status: str = "coming_soon"
    max_per_user: int = 2
    sale_starts_at: Optional[str] = None
    sale_ends_at: Optional[str] = None
    image_url: Optional[str] = None
    rating: float = 0.0
    discount_percent: Optional[float] = None
    is_active: bool = True


class Product(ProductBase, table=True):
    __tablename__ = "products"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
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


class ProductPublic(ProductBase):
    id: UUID
    created_at: str
    updated_at: str
