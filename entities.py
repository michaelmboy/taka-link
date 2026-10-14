from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

def now(): return datetime.now(timezone.utc)
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="producer", nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40))
    organization: Mapped[str | None] = mapped_column(String(180))
    service_area: Mapped[str | None] = mapped_column(String(180))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class HotspotReport(Base):
    __tablename__ = "hotspot_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    waste_type: Mapped[str] = mapped_column(String(80), default="Mixed waste")
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(30), default="reported")
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(1000))
    estimated_kg: Mapped[float | None] = mapped_column(Float)
    actual_kg: Mapped[float | None] = mapped_column(Float)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    reporter = relationship("User", foreign_keys=[created_by])
    collector = relationship("User", foreign_keys=[assigned_to])
class CollectionJob(Base):
    __tablename__ = "collection_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("hotspot_reports.id"), unique=True, nullable=False)
    collector_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(30), default="open")
    proof_image_url: Mapped[str | None] = mapped_column(String(1000))
    proof_latitude: Mapped[float | None] = mapped_column(Float)
    proof_longitude: Mapped[float | None] = mapped_column(Float)
    actual_kg: Mapped[float | None] = mapped_column(Float)
    material_breakdown: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    report = relationship("HotspotReport")
class MarketListing(Base):
    __tablename__ = "market_listings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    material: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    price_per_kg: Mapped[float] = mapped_column(Float, nullable=False)
    min_kg: Mapped[float] = mapped_column(Float, default=1)
    location: Mapped[str] = mapped_column(String(180), nullable=False)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    buyer = relationship("User")
class SaleOffer(Base):
    __tablename__ = "sale_offers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("market_listings.id"), nullable=False)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    proposed_price_per_kg: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="offered")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    listing = relationship("MarketListing")
    seller = relationship("User")
