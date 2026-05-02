"""
Exercise the shortener with `requests` (HTTP client).

Run the server in another terminal:
  uvicorn app.main:app --reload --port 8000
  # or: python -m app.main

Then:
  python client_demo.py
"""

from __future__ import annotations

import os
import sys

import requests

BASE = os.environ.get("SHORTENER_URL", "http://127.0.0.1:8000")


def main() -> None:
    r = requests.post(
        f"{BASE.rstrip('/')}/api/v1/urls",
        json={"long_url": "https://example.com/path?q=1"},
        headers={"Content-Type": "application/json"},
        timeout=5,
    )
    r.raise_for_status()
    data = r.json()
    short = data["short_url"]
    print("created:", data)

    redir = requests.get(short, allow_redirects=False, timeout=5)
    print("GET short URL:", redir.status_code, redir.headers.get("Location"))


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to {BASE}. Start the server: python -m app.main", file=sys.stderr)
        sys.exit(1)
