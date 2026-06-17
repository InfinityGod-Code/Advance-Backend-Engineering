from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4


class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)
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
    created_at: str
    updated_at: str


