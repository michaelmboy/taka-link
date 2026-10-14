from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Literal
class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Literal["producer", "collector", "buyer"] = "producer"
    phone: str | None = None
    organization: str | None = None
    service_area: str | None = None
class LoginIn(BaseModel):
    email: EmailStr
    password: str
class UserOut(BaseModel):
    id: int; name: str; email: EmailStr; role: str; phone: str | None = None; organization: str | None = None; service_area: str | None = None
    model_config = ConfigDict(from_attributes=True)
class ReportIn(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str = ""
    waste_type: str = "Mixed waste"
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    image_url: str | None = None
    estimated_kg: float | None = Field(default=None, ge=0)
class ReportStatusIn(BaseModel):
    status: Literal["reported", "claimed", "collected", "verified", "cancelled", "disputed"]
class ListingIn(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    material: str = Field(min_length=2, max_length=80)
    description: str = ""
    price_per_kg: float = Field(gt=0)
    min_kg: float = Field(gt=0)
    location: str = Field(min_length=2, max_length=180)
class OfferIn(BaseModel):
    listing_id: int
    quantity_kg: float = Field(gt=0)
    proposed_price_per_kg: float = Field(gt=0)
    notes: str | None = None
class OfferStatusIn(BaseModel):
    status: Literal["accepted", "rejected", "delivered", "paid", "cancelled", "disputed"]
