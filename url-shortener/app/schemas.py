import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

ALLOWED_SCHEMES = frozenset({"http", "https"})
_ALIAS_RE = re.compile(r"^[A-Za-z0-9_-]{3,64}$")


class CreateUrlRequest(BaseModel):
    long_url: str = Field(..., max_length=2048)
    custom_alias: str | None = Field(None, max_length=64)
    expires_at: datetime | None = None

    @field_validator("long_url")
    @classmethod
    def validate_long_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("long_url must not be empty")
        parsed = urlparse(v)
        if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
            raise ValueError("long_url must be a valid http(s) URL with a host")
        return v

    @field_validator("custom_alias")
    @classmethod
    def validate_custom_alias(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if not _ALIAS_RE.fullmatch(v):
            raise ValueError(
                "custom_alias must be 3–64 chars: letters, digits, hyphen, underscore only"
            )
        return v

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return None
        now = datetime.now(timezone.utc)
        exp = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        if exp <= now:
            raise ValueError("expires_at must be in the future")
        return exp


class CreateUrlResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: str
