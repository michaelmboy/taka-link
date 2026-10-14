"""Initial TakaLink schema.

Revision ID: 20261014_initial
Revises:
Create Date: 2026-10-14
"""
from alembic import op
from app.db.base import Base
from app.models import User, HotspotReport, CollectionJob, MarketListing, SaleOffer  # noqa: F401
from app.db.session import engine
revision = "20261014_initial"
down_revision = None
branch_labels = None
depends_on = None
def upgrade():
    Base.metadata.create_all(bind=engine)
def downgrade():
    Base.metadata.drop_all(bind=engine)
