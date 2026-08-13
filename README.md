# Hylifen API Layer

FastAPI server for the Hylifen Main Application. Runs on **port 4000**.

## Prerequisites
- Python 3.12
- `uv` package manager — [install](https://docs.astral.sh/uv/getting-started/installation/)
- PostgreSQL running locally

## Setup

```bash
# 1. Copy env template and fill in your values
cp .env.example .env

# 2. Install dependencies and create virtual environment
uv sync

# 3. Start the dev server (hot-reload enabled)
uv run python main.py
```

The API will be available at: **http://localhost:4000**
Interactive docs (Swagger UI): **http://localhost:4000/docs**

## Database Migrations (Alembic)

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Generate a new migration after changing app/db/tables.py
uv run alembic revision --autogenerate -m "describe your change"

# Roll back one migration
uv run alembic downgrade -1
```

## Adding a New API Module

1. Create `app/api/v1/routes/mymodule.py` — copy `example.py` as a starting point
2. Add Pydantic models to `app/models/mymodule.py`
3. Add ORM table(s) to `app/db/tables.py`
4. Register the router in `app/api/v1/router.py` with one `include_router()` call
5. Generate and apply the migration

## Environment Variables

See `.env.example` for all available variables.

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `local` | Environment name |
| `PORT` | `4000` | Server port |
| `AUTH_BYPASS_ENABLED` | `false` | Skip JWT validation (dev only) |
| `GOOGLE_CLIENT_ID` | — | Google OAuth client ID |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated CORS origins |
| `DATABASE_URL` | — | PostgreSQL async connection string |
