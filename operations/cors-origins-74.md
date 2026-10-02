# Browser origin configuration (#74)

Set `CORS_ORIGINS` in the backend runtime environment to a comma-separated list of frontend web origins. Restart the backend after changing it.

```dotenv
CORS_ORIGINS=http://localhost:8082,https://app.example.com
```

Replace the example domain with the actual frontend domain. An origin is a scheme, hostname, and optional port; do not include a page path. Localhost and 127.0.0.1 are different origins, as are different ports. Whitespace and duplicate entries are removed; a trailing slash is accepted and normalized.

The unset default is `*`, preserving local development access. **Production must explicitly set the allowed frontend origins.** There is no automatic production-environment detection. An empty value allows no cross-origin browser access. Do not combine `*` with explicit origins. Domain patterns such as `https://*.trycloudflare.com` and `exp://` links are rejected at startup.

## Expo and tunnels

For Expo web, allow the browser frontend's URL, such as `http://localhost:8082`. If you expose that web frontend through a tunnel, allow its exact HTTPS origin and update the environment when it changes. A tunnel exposing only the backend is the API destination, not the frontend origin, and usually does not belong in this list.

Native Expo Go/React Native requests are not subject to browser CORS enforcement. Requests without an Origin header continue normally; bearer authentication and household membership checks still apply. CORS does not replace authentication or block direct non-browser clients.

Explicit origin lists support credentialed browser requests. Wildcard development mode does not advertise credentialed-cookie support, because browsers cannot use wildcard origins for credentialed CORS. The app's explicit Authorization bearer header remains allowed, as do Content-Type and X-Household-ID.

## Verification

From the backend repository:

```sh
python -m pytest tests/test_cors.py -q
python -m pytest tests/ -q
```

Tests import the actual application with isolated environment values, exercise allowed/rejected preflight requests, verify disallowed origins receive no allow-origin header, and confirm requests without Origin still reach the app and still require authentication for protected routes.

The tracked backend `.env.example` contains placeholders only. If real credentials were previously committed, replacing the example does not revoke them or erase history; rotate those credentials with the provider.
