import asyncio

from app.models import ShortUrl


class UrlStore:
    """In-memory code → URL map (interview / local dev; not durable across restarts)."""

    def __init__(self) -> None:
        self._by_code: dict[str, ShortUrl] = {}
        self._lock = asyncio.Lock()

    async def put(self, row: ShortUrl) -> None:
        """Insert or replace if existing row is expired. Raises ValueError if code is taken and active."""
        async with self._lock:
            existing = self._by_code.get(row.short_code)
            if existing is not None and not existing.is_expired():
                raise ValueError("short code already exists")
            self._by_code[row.short_code] = row

    async def get_long_url(self, short_code: str) -> str | None:
        async with self._lock:
            row = self._by_code.get(short_code)
            if row is None:
                return None
            if row.is_expired():
                del self._by_code[short_code]
                return None
            return row.long_url
