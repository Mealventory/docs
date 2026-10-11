# Rate limiting for join and scan endpoints (#88)
Invite joining and AI-backed scans are throttled in the backend process. Limits are not enforced in the Expo app.
## Defaults
Set these in `backend/.env`. Restart the backend after changing them.
```dotenv
RATE_LIMIT_ENABLED=true
RATE_LIMIT_JOIN_ATTEMPTS=10
RATE_LIMIT_JOIN_WINDOW_SECONDS=60
RATE_LIMIT_SCAN_ATTEMPTS=20
RATE_LIMIT_SCAN_WINDOW_SECONDS=60
```
| Scope | Routes | Default |
| --- | --- | --- |
| Join | `POST /api/v1/households/join` | 10 attempts / 60 seconds / user |
| Scan | `POST /api/v1/scan/`, `/preview`, `/sample` | 20 attempts / 60 seconds / user |
Normal household creation, pantry edits, and a typical scan session stay under these defaults.
When a limit is exceeded, the response is `429` `application/problem+json` with `Retry-After` (seconds) and the same generic detail for every caller. Join throttling runs **before** invite lookup, so the body does not say whether a code exists.
## Proxies and Cloudflare tunnels
These routes require a verified Supabase access token. The limiter keys on the token `sub` (user id), not `request.client.host`.
A Cloudflare Quick Tunnel (`cloudflared tunnel --url http://localhost:8000`) makes the TCP peer the tunnel or localhost. Per-IP limiting would count the whole team as one client. Expo's own tunnel only serves the JavaScript bundle; it does not change this backend behavior.
This limiter is **per process**. Two backend workers do not share counters. Redis/distributed limiting is out of scope.
## Tests
From the backend repository:
```powershell
.\.venv311\Scripts\python.exe -m pytest tests/test_rate_limit.py tests/ -q
```
Tests use the in-memory limiter only. They do not start Redis, Cloudflare, or a live AI provider.