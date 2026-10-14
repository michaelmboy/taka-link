# Database notes

The app creates the initial MVP tables at startup. Alembic is included for future migrations (`alembic revision --autogenerate -m "describe change"`, then `alembic upgrade head`). Tables: `users`, `hotspot_reports`, `collection_jobs`, `market_listings`, `sale_offers`.

Before a production-scale launch, add explicit audit history for every status transition, database indexes for common map filters, stronger transactional order handling, organization membership, material units/quality, and data-retention policies. Never treat client-submitted weight or a photo URL alone as proof of recycling.
