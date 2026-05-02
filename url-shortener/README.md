# URL shortener

Interview-sized **FastAPI** service that maps short codes to long URLs in memory (no database). Data is lost when the process stops.

## Setup

```bash
cd url-shortener
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Or:

```bash
python -m app.main
```

- Interactive API docs: `http://127.0.0.1:8000/docs`
- Health: `GET /health`

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/urls` | Create a short link. Body: `long_url` (required), optional `custom_alias`, optional `expires_at` (future datetime). Returns `201` with `short_code`, `short_url`, `long_url`. |
| `GET` | `/{code}` | Redirect (`302`) to the stored URL, or `404` if missing / expired. |

Reserved path segments (cannot be used as `custom_alias` and are not resolved as codes): `api`, `docs`, `redoc`, `openapi.json`, `health`, `favicon.ico`.

## Configuration

Optional environment variables (see `app/config.py`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Base URL used in JSON responses (`short_url`). |
| `SHORT_CODE_LENGTH` | `7` | Length of generated random codes. |
| `MAX_LONG_URL_LENGTH` | `2048` | Max accepted length after validation. |

You can also use a local `.env` file (loaded by `pydantic-settings`).

## Layout

- `app/main.py` — FastAPI app and routes
- `app/store.py` — in-memory store (`asyncio` lock)
- `app/service.py` — code generation and resolution
- `app/schemas.py` — Pydantic request/response models
- `app/models.py` — `ShortUrl` dataclass
- `app/config.py` — settings
- `client_demo.py` — optional `requests` smoke test against a running server

## Client demo

With the server running:

```bash
python client_demo.py
```

Override the base URL with `SHORTENER_URL` (default `http://127.0.0.1:8000`).
