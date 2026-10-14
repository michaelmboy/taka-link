# Render deployment checklist

1. Push the ZIP contents (not the ZIP file itself) to GitHub.
2. Create a Render Blueprint from `render.yaml`.
3. Wait for database, API and frontend deployments.
4. Confirm API `/health` returns `{"status":"ok"}`.
5. Set API `FRONTEND_ORIGIN` to the actual frontend service URL if the generated hostname differs from the placeholder, then redeploy the API.
6. Visit frontend, register producer, collector and buyer test accounts, then test permissions and core workflows.
7. Create an admin only through a controlled DB operation after confirming account identity; never expose admin registration publicly.
8. Set up backup/retention policy and monitoring before using real operational data.

Do not commit `.env` files or secrets. Free-tier availability, sleep behaviour and database retention can change; check current provider terms.
