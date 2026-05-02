import secrets
import string
from datetime import datetime, timezone

from app.config import settings
from app.models import ShortUrl
from app.store import UrlStore

ALPHABET = string.digits + string.ascii_letters
RESERVED_PATHS = frozenset(
    {
        "api",
        "docs",
        "redoc",
        "openapi.json",
        "health",
        "favicon.ico",
    }
)


def _random_code(length: int) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


async def create_short_url(
    store: UrlStore,
    *,
    long_url: str,
    custom_alias: str | None,
    expires_at: datetime | None,
) -> ShortUrl:
    created_at = datetime.now(timezone.utc)
    if custom_alias:
        if custom_alias.lower() in RESERVED_PATHS:
            raise ValueError("custom_alias is reserved")
        row = ShortUrl(
            short_code=custom_alias,
            long_url=long_url,
            created_at=created_at,
            expires_at=expires_at,
        )
        try:
            await store.put(row)
        except ValueError as e:
            raise ValueError("custom_alias already exists") from e
        return row

    for _ in range(8):
        short_code = _random_code(settings.short_code_length)
        if short_code.lower() in RESERVED_PATHS:
            continue
        row = ShortUrl(
            short_code=short_code,
            long_url=long_url,
            created_at=created_at,
            expires_at=expires_at,
        )
        try:
            await store.put(row)
            return row
        except ValueError:
            continue
    raise RuntimeError("could not allocate a unique short code")


async def resolve_long_url(store: UrlStore, short_code: str) -> str | None:
    return await store.get_long_url(short_code)
