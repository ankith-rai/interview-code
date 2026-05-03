# interview-code

Small, self-contained practice snippets and interview exercises. There is **no** shared root `requirements.txt` or repo-level virtualenv—each folder has its own `requirements.txt` so you only install what that exercise needs.

## Projects

| Folder | Notes |
|--------|--------|
| `url-shortener` | FastAPI in-memory URL shortener — see [url-shortener/README.md](url-shortener/README.md). |
| `twitter-lld` | Python in-memory Twitter low-level design exercise. |
| `api-requests` | HTTP client examples (`requests`). |
| `merck` | AWS-style scripting (`boto3`). |
| `zepto` | Small Flask app. |

## Setup (per project)

From the repo root:

```bash
cd <project-folder>
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

For how to run the URL shortener, its API, and env vars, use **[url-shortener/README.md](url-shortener/README.md)**.
