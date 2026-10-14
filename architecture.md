# TakaLink architecture

- **Frontend:** Next.js 14 / React / TypeScript; public marketing pages and authenticated role workspaces.
- **Backend:** FastAPI; request validation, authentication, authorization, business workflows and REST API.
- **Database:** PostgreSQL via SQLAlchemy. The MVP uses latitude/longitude columns; PostGIS can be added when spatial querying becomes necessary.
- **Session:** signed JWT in an HttpOnly cookie. Browser requests use `credentials: include`.
- **Maps:** Leaflet + OpenStreetMap tiles.
- **Deployment:** Render Blueprint provisions PostgreSQL, API and frontend services.

## Main entities
User, HotspotReport, CollectionJob, MarketListing, SaleOffer. For a larger rollout, add an audit/status-history table, organizations/memberships, dedicated orders and payments, report photos, conversations/messages, disputes, notifications, material categories and review records.

## Workflows
Report: reported → claimed → collected → verified, with cancelled/disputed states. Buyer offer: offered → accepted → delivered → paid, with rejected/cancelled/disputed states. Actual collected weight is recorded separately from estimates. The MVP's `paid` state is a manual status only.
