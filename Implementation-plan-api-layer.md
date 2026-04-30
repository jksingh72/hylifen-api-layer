# FastAPI `apilayer` — Implementation Plan

## Goal
A production-ready FastAPI server at `c:\jksingh\apilayer\` (standalone folder, sibling to `App-React`) that:
- Runs on **port 4000**
- Supports **multiple modular APIs** — each API is a self-contained folder under `app/modules/`
- Uses **`uv`** as the Python package manager
- **Google JWT authentication** with an env-flag bypass for dev/testing
- **PostgreSQL** database connection via async SQLAlchemy + asyncpg
- **Alembic** for DB schema migrations (optional — can be managed manually)

---

## Actual Folder Structure

```
c:\jksingh\
├── App-React\                        # React frontend (unchanged)
└── apilayer\                         # FastAPI backend
    ├── pyproject.toml                # uv project manifest — deps
    ├── .python-version               # Pins Python 3.12
    ├── .env                          # Local secrets (never committed to git)
    ├── .env.example                  # Template checked into git
    ├── .gitignore                    # Excludes .env, .venv, __pycache__
    ├── Implementation-plan-api-layer.md
    ├── README.md
    ├── main.py                       # App entry point
    ├── alembic.ini                   # Alembic config (optional)
    ├── alembic/
    │   ├── env.py                    # Alembic runtime (reads DB URL from config)
    │   └── versions/                 # Auto-generated migration scripts
    └── app/
        ├── __init__.py
        ├── core/                     # Shared infrastructure — do not modify per API
        │   ├── __init__.py
        │   ├── config.py             # Pydantic Settings — reads .env
        │   ├── middleware.py         # CORS setup (allows React on port 3000)
        │   ├── database.py           # Async SQLAlchemy engine + session
        │   └── security.py          # Google JWT validation + bypass logic
        ├── api/
        │   ├── __init__.py
        │   └── v1/
        │       ├── __init__.py
        │       ├── router.py         # ★ Register new modules here (one line each)
        │       └── routes/
        │           ├── __init__.py
        │           ├── health.py     # GET /api/v1/health — public, no auth
        │           └── example.py   # Example stub (template pattern)
        └── modules/                  # ★ All new APIs go here as subfolders
            ├── __init__.py
            └── stocks/               # Stock price API
                ├── __init__.py
                ├── models.py         # Pydantic request/response shapes
                └── router.py         # Route handlers + mock price table
```

---

## Modular API Pattern — How to Add a New API

Every new API = one new subfolder under `app/modules/`. Steps:

1. Create `app/modules/mymodule/` with `__init__.py`, `models.py`, `router.py`
2. Define Pydantic shapes in `models.py`
3. Write route handlers in `router.py`
4. Register in `app/api/v1/router.py` with **one line**:
   ```python
   api_v1_router.include_router(mymodule_router, prefix="/mymodule", tags=["MyModule"])
   ```

---

## Key Design Decisions

### Authentication — Google JWT
- Every protected route uses `get_current_user` FastAPI dependency
- Caller passes: `Authorization: Bearer <google_id_token>`
- Server validates via `google-auth` library against Google's public JWKS
- **Bypass:** `AUTH_BYPASS_ENABLED=true` in `.env` → returns a mock user, no token needed
- `GET /api/v1/health` is intentionally **public** (no auth)

### Database — PostgreSQL (async)
- `asyncpg` driver + SQLAlchemy async engine
- Connection string in `.env`: `DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname`
- `get_db()` in `app/core/database.py` is the FastAPI session dependency
- Alembic handles schema migrations (optional — can manage tables manually via psql/pgAdmin)

### CORS
- `CORSMiddleware` allows origins defined in `ALLOWED_ORIGINS` env var
- Default: `["http://localhost:3000"]` (the React frontend)

---

## Dependencies (`pyproject.toml`)

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn[standard]` | ASGI server |
| `pydantic-settings` | Typed env var config |
| `python-dotenv` | Loads `.env` file |
| `google-auth` | Validates Google ID tokens |
| `requests` | Required by google-auth transport |
| `sqlalchemy[asyncio]` | Async ORM |
| `asyncpg` | Async PostgreSQL driver |
| `alembic` | Database migrations |

---

## `.env` Variables

```dotenv
# Server
APP_ENV=local
PORT=4000

# Auth — set AUTH_BYPASS_ENABLED=true to skip Google JWT during development
AUTH_BYPASS_ENABLED=true
GOOGLE_CLIENT_ID=your-google-client-id-here

# CORS — must be a JSON array
ALLOWED_ORIGINS=["http://localhost:3000"]

# Database
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/application
```

---

## Running the Server

```powershell
cd c:\jksingh\apilayer

# First time only — install dependencies
uv sync

# Start dev server (hot-reload)
uv run uvicorn main:app --host 0.0.0.0 --port 4000 --reload
```

| URL | Description |
|---|---|
| `http://localhost:4000/docs` | Swagger UI — interactive API tester |
| `http://localhost:4000/api/v1/health` | Public liveness check |
| `http://localhost:4000/api/v1/stocks/AAPL` | Stock price (mock data) |

---

## Implemented APIs

| Module | Endpoint | Auth | Description |
|---|---|---|---|
| Health | `GET /api/v1/health` | ❌ Public | Liveness check |
| Stocks | `GET /api/v1/stocks/{ticker}` | ✅ Required | Returns mock stock price |
| Example | `GET /api/v1/example` | ✅ Required | Template stub |

**Available stock tickers (mock):** `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `TSLA`, `NVDA`, `META`, `NFLX`

---

## Alembic — DB Migrations (Optional)

| Action | Command |
|---|---|
| Apply all migrations | `uv run alembic upgrade head` |
| Generate new migration | `uv run alembic revision --autogenerate -m "description"` |
| Roll back one | `uv run alembic downgrade -1` |
