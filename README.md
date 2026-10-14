# TakaLink — Waste Reporting, Collection & Recycling Marketplace

TakaLink is a deployable MVP for reporting waste hotspots, coordinating collection jobs, and connecting recoverable materials with buyers. It includes a Next.js frontend, FastAPI REST API, PostgreSQL persistence, cookie-based JWT authentication, role checks, and a Render Blueprint.

## Included
- Public homepage, producer and buyer pages, and marketplace preview
- Registration/login/logout and current-user session endpoint
- Roles: producer, collector, buyer, admin
- Waste hotspot reporting and map view (Leaflet/OpenStreetMap)
- Collection job claiming and proof submission form
- Material demand listings and sale offers
- Dashboard summaries and admin overview
- PostgreSQL models, Alembic migrations, API tests, Render configuration
- Seed/demo data endpoint is intentionally not public; create an account and add records through the UI/API

## Deploy to Render
1. Extract the ZIP and upload the **contents** of `takalink/` to a new GitHub repository.
2. In Render, choose **New → Blueprint**, connect the repository, and select `render.yaml`.
3. Review the proposed database and two web services, then deploy. Render will create a database, API, and frontend.
4. After the first deploy, open the `takalink-web` service URL and register an account.
5. To use the admin workspace, set a user role to `admin` directly in the database only after verifying the account and understanding the consequences. Never allow public admin registration.

### Important Render configuration after first deploy
The Blueprint sets the frontend origin to `https://takalink-web.onrender.com`. If Render assigns a different hostname, update the API service's `FRONTEND_ORIGIN` environment variable to the exact frontend URL and redeploy the API. The frontend discovers the API host from `NEXT_PUBLIC_API_URL`; the client helper adds `https://` when Render provides only a hostname.

Render free services may sleep and cold-start. A free database may have retention/availability limitations. Review current Render pricing and database policies before using this for real operations.

## Local development
Requirements: Python 3.11+, Node.js 20+, PostgreSQL 14+.

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows, after copying backend/.env.example; on macOS/Linux use cp backend/.env.example backend/.env
uvicorn app.main:app --reload
```
Create `backend/.env` with `DATABASE_URL`, `SECRET_KEY`, `FRONTEND_ORIGIN=http://localhost:3000`, `COOKIE_SECURE=false`, and `COOKIE_SAMESITE=lax`. Create the PostgreSQL database first. On startup, SQLAlchemy creates tables for the MVP; Alembic migration files are also included for controlled schema changes.

### Frontend
```bash
cd frontend
npm install
# Set NEXT_PUBLIC_API_URL=http://localhost:8000 in frontend/.env.local
npm run dev
```
Open http://localhost:3000. API docs are at http://localhost:8000/docs.

## Authentication and security
- Passwords are hashed with bcrypt.
- JWTs are stored in HttpOnly cookies, not localStorage.
- API routes validate the session and role on the server.
- CORS is restricted to `FRONTEND_ORIGIN` with credentials enabled.
- Use HTTPS in production and a long, unique `SECRET_KEY`.
- Admin role is not selectable at public registration.
- This is an MVP starter, not a security audit or a guarantee of production readiness. Before processing real money or sensitive data, add email verification, password reset, rate limiting, CSRF review, monitoring, backups, moderation/dispute policies, and a professional security review.

## Product and data notes
- Reported/estimated weight is separate from actual recorded weight.
- A report marked collected is not automatically counted as verified recycled material.
- Marketplace payments are status tracking only; no money is moved and no M-Pesa integration is included.
- Image upload storage is not wired to a paid external provider. The MVP stores an optional image URL; add Cloudinary or another durable storage provider before relying on uploads. Do not use ephemeral service disk for important images.
- Map tiles and geocoding are provided by third parties; follow their usage policies.

## Main API routes
- `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
- `GET/POST /api/reports`, `GET/PATCH /api/reports/{id}`
- `GET/POST /api/jobs`, `POST /api/jobs/{id}/claim`, `POST /api/jobs/{id}/proof`
- `GET/POST /api/listings`, `GET /api/listings/{id}`
- `POST /api/offers`, `GET /api/offers/mine`, `PATCH /api/offers/{id}`
- `GET /api/dashboard/summary`, `GET /api/admin/overview`
- `GET /health`
