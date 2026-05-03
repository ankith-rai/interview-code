# Twitter LLD (Python)

Small in-memory Low Level Design implementation for a Twitter-like system.

## Layout

```text
twitter-lld/
  twitter_lld/          # package
    __init__.py         # public exports
    models.py           # User, Tweet
    service.py          # TwitterService
    demo.py             # CLI walkthrough
```

## Features

- Create users
- Follow and unfollow users
- Post tweets (280 characters)
- Like and retweet
- Fetch user timeline
- Fetch home timeline (pull model merge at read time)

## Run demo

```bash
cd twitter-lld
python3 -m twitter_lld.demo
```

## Notes for Interviews

- This is intentionally in-memory to focus on object modeling and service design.
- For production discussion, explain:
  - persistence layer split (users, tweets, graph, timeline cache),
  - hybrid fanout model (push for normal users, pull for celebrities),
  - eventual consistency and caching strategy.
