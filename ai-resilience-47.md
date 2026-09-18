# AI scan resilience (#47)

The backend keeps the existing scan contracts: uploads at `/api/v1/scan/` and development samples at `/api/v1/scan/sample` call the AI service's `/scan/` endpoint. Successful responses are unchanged. The proposed `/scan/multi` endpoint is not implemented in the current AI service, so this change does not switch to it.

## Failure behavior

The AI request has a 15-second total deadline, including network work and retry delay. Timeouts return HTTP 504. Connection failures, upstream errors, invalid JSON, invalid item lists, and an open circuit return HTTP 503 (upstream 504 also maps to 504). Both return:

```json
{"detail":{"code":"AI_SERVICE_UNAVAILABLE","message":"Scanning is temporarily unavailable. Please enter your items manually or try again shortly.","action":"manual_entry"}}
```

The frontend should display the message and offer manual item entry. No inventory writes occur after an AI failure. The error never includes upstream response bodies, internal hostnames, or credentials.

Connection establishment failures and upstream 502/503/504 responses may retry once after 200ms. Timeouts and other failures do not retry. Both attempts share the original deadline. The retry forwards the same image to the detection-only service; database writes still occur only after a successful response. The existing buffered multipart upload is retained; this does not introduce streaming uploads or change scan persistence.

## Circuit breaker

After three failed scan calls, new scans fail fast for 30 seconds without sending images. Then one recovery probe is allowed. Success restores scanning; failure starts another cooldown. Concurrent requests cannot all act as probes, and late results from before the circuit opened cannot close it. Cancellation releases the recovery probe.

The circuit is in memory per backend process, shared by scan modes and households. Multiple workers have separate circuits. Restarting the backend resets circuit state. It is not a distributed outage monitor.

Optional backend environment settings:

| Variable | Default | Allowed |
| --- | --- | --- |
| `AI_REQUEST_TIMEOUT_SECONDS` | 15 | Greater than 0, at most 15 |
| `AI_CIRCUIT_FAILURE_THRESHOLD` | 3 | 1–100 |
| `AI_CIRCUIT_COOLDOWN_SECONDS` | 30 | Greater than 0, at most 300 |

The deadline starts when the AI call begins, after the backend reads the upload. It does not bound the phone's upload time or subsequent database writes. Recipe requests are unchanged.

## Verification

From the backend repository:

```sh
python -m pytest tests/test_ai_client.py -q
python -m pytest tests/ -q
```

Tests use mocked HTTP transport, not Google Cloud or the live AI service. They cover multipart compatibility, transient retries, the total deadline including retry delay, safe errors, opening/cooldown/recovery, stale concurrent results, cancellation, and an authenticated scan failure without inventory writes. The OpenAPI contract baseline changes only the intentional scan 503/504 definitions.
