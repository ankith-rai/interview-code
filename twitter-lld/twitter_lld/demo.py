from __future__ import annotations

from typing import Callable, List

from twitter_lld.models import Tweet, User
from twitter_lld.service import TwitterService


def print_timeline(
    title: str,
    tweets: List[Tweet],
    get_author: Callable[[int], User],
) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for tweet in tweets:
        author = get_author(tweet.author_id)
        print(
            f"[{tweet.created_at.strftime('%H:%M:%S')}] "
            f"@{author.handle}: {tweet.text} "
            f"(likes={len(tweet.like_user_ids)}, retweets={len(tweet.retweet_user_ids)})"
        )


def run_demo() -> None:
    service = TwitterService()

    alice = service.create_user("alice", "Alice Johnson")
    bob = service.create_user("bob", "Bob Smith")
    charlie = service.create_user("charlie", "Charlie Kim")

    service.follow(alice.user_id, bob.user_id)
    service.follow(alice.user_id, charlie.user_id)

    first = service.post_tweet(bob.user_id, "Design interviews are all about trade-offs.")
    second = service.post_tweet(charlie.user_id, "Fanout on write vs fanout on read: discuss both.")
    service.post_tweet(alice.user_id, "Practicing LLD daily.")

    service.like_tweet(alice.user_id, first.tweet_id)
    service.retweet(alice.user_id, second.tweet_id)

    def author(uid: int) -> User:
        return service.get_user(uid)

    print_timeline("Alice Home Timeline", service.get_home_timeline(alice.user_id), author)
    print_timeline("Bob User Timeline", service.get_user_timeline(bob.user_id), author)


def main() -> None:
    run_demo()


if __name__ == "__main__":
    main()
