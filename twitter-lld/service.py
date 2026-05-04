from __future__ import annotations

from itertools import count
from typing import Dict, List, Set

from models import Tweet, User


class TwitterService:
    """In-memory LLD model for interview discussion and quick demos."""

    def __init__(self) -> None:
        self._user_id_seq = count(start=1)
        self._tweet_id_seq = count(start=1)

        self._users: Dict[int, User] = {}
        self._users_by_handle: Dict[str, int] = {}
        self._tweets: Dict[int, Tweet] = {}
        self._tweets_by_user: Dict[int, List[int]] = {}

        self._following: Dict[int, Set[int]] = {}
        self._followers: Dict[int, Set[int]] = {}

    def create_user(self, handle: str, name: str) -> User:
        handle = handle.strip().lower()
        if not handle:
            raise ValueError("handle cannot be empty")
        if handle in self._users_by_handle:
            raise ValueError(f"handle '{handle}' already exists")

        user_id = next(self._user_id_seq)
        user = User(user_id=user_id, handle=handle, name=name.strip())
        self._users[user_id] = user
        self._users_by_handle[handle] = user_id
        self._tweets_by_user[user_id] = []
        self._following[user_id] = set()
        self._followers[user_id] = set()
        return user

    def get_user(self, user_id: int) -> User:
        self._ensure_user_exists(user_id)
        return self._users[user_id]

    def follow(self, follower_id: int, followee_id: int) -> None:
        self._ensure_user_exists(follower_id)
        self._ensure_user_exists(followee_id)

        if follower_id == followee_id:
            raise ValueError("a user cannot follow themselves")

        self._following[follower_id].add(followee_id)
        self._followers[followee_id].add(follower_id)

    def unfollow(self, follower_id: int, followee_id: int) -> None:
        self._ensure_user_exists(follower_id)
        self._ensure_user_exists(followee_id)
        self._following[follower_id].discard(followee_id)
        self._followers[followee_id].discard(follower_id)

    def post_tweet(self, author_id: int, text: str) -> Tweet:
        self._ensure_user_exists(author_id)
        text = text.strip()
        if not text:
            raise ValueError("tweet text cannot be empty")
        if len(text) > 280:
            raise ValueError("tweet text exceeds 280 characters")

        tweet_id = next(self._tweet_id_seq)
        tweet = Tweet(tweet_id=tweet_id, author_id=author_id, text=text)
        self._tweets[tweet_id] = tweet
        self._tweets_by_user[author_id].append(tweet_id)
        return tweet

    def like_tweet(self, user_id: int, tweet_id: int) -> None:
        self._ensure_user_exists(user_id)
        tweet = self._get_tweet(tweet_id)
        tweet.like(user_id)

    def retweet(self, user_id: int, tweet_id: int) -> Tweet:
        self._ensure_user_exists(user_id)
        original = self._get_tweet(tweet_id)
        original.retweet(user_id)
        return self.post_tweet(
            user_id,
            f"RT @{self._users[original.author_id].handle}: {original.text}",
        )

    def get_user_timeline(self, user_id: int, limit: int = 10) -> List[Tweet]:
        self._ensure_user_exists(user_id)
        tweet_ids = self._tweets_by_user[user_id]
        return [self._tweets[tid] for tid in reversed(tweet_ids[-limit:])]

    def get_home_timeline(self, user_id: int, limit: int = 10) -> List[Tweet]:
        self._ensure_user_exists(user_id)

        candidate_user_ids = {user_id, *self._following[user_id]}
        candidate_tweets: List[Tweet] = []
        for uid in candidate_user_ids:
            for tid in self._tweets_by_user[uid]:
                candidate_tweets.append(self._tweets[tid])

        candidate_tweets.sort(key=lambda t: t.created_at, reverse=True)
        return candidate_tweets[:limit]

    def followers_count(self, user_id: int) -> int:
        self._ensure_user_exists(user_id)
        return len(self._followers[user_id])

    def following_count(self, user_id: int) -> int:
        self._ensure_user_exists(user_id)
        return len(self._following[user_id])

    def _ensure_user_exists(self, user_id: int) -> None:
        if user_id not in self._users:
            raise ValueError(f"user_id '{user_id}' does not exist")

    def _get_tweet(self, tweet_id: int) -> Tweet:
        tweet = self._tweets.get(tweet_id)
        if tweet is None:
            raise ValueError(f"tweet_id '{tweet_id}' does not exist")
        return tweet
