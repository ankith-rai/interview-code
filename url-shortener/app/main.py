from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.config import settings
from app.schemas import CreateUrlRequest, CreateUrlResponse
from app.service import RESERVED_PATHS, create_short_url, resolve_long_url
from app.store import UrlStore


def get_store(request: Request) -> UrlStore:
    return request.app.state.url_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.url_store = UrlStore()
    yield


app = FastAPI(title="URL Shortener", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/urls", response_model=CreateUrlResponse, status_code=201)
async def shorten_url(
    body: CreateUrlRequest,
    store: UrlStore = Depends(get_store),
):
    if len(body.long_url) > settings.max_long_url_length:
        raise HTTPException(status_code=400, detail="long_url is too long")
    try:
        row = await create_short_url(
            store,
            long_url=body.long_url,
            custom_alias=body.custom_alias,
            expires_at=body.expires_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    base = settings.public_base_url.rstrip("/")
    return CreateUrlResponse(
        short_code=row.short_code,
        short_url=f"{base}/{row.short_code}",
        long_url=row.long_url,
    )


@app.get("/{code}")
async def redirect_to_long(
    code: str,
    store: UrlStore = Depends(get_store),
):
    if code.lower() in RESERVED_PATHS:
        raise HTTPException(status_code=404, detail="not found")
    long_url = await resolve_long_url(store, code)
    if long_url is None:
        raise HTTPException(status_code=404, detail="short code not found or expired")
    return RedirectResponse(url=long_url, status_code=302)


def main() -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=int(__import__("os").environ.get("PORT", "8000")),
        reload=True,
    )


if __name__ == "__main__":
    main()
