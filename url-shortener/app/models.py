from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ShortUrl:
    short_code: str
    long_url: str
    created_at: datetime
    expires_at: datetime | None = None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        now = datetime.now(timezone.utc)
        exp = self.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return now > exp
