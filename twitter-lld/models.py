from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Set


@dataclass(frozen=True)
class User:
    user_id: int
    handle: str
    name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Tweet:
    tweet_id: int
    author_id: int
    text: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    like_user_ids: Set[int] = field(default_factory=set)
    retweet_user_ids: Set[int] = field(default_factory=set)

    def like(self, user_id: int) -> None:
        self.like_user_ids.add(user_id)

    def retweet(self, user_id: int) -> None:
        self.retweet_user_ids.add(user_id)
