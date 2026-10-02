# Backend Docker runtime and health probes (#48)

The backend image uses Python 3.11-slim, installs requirements in a separate builder stage, and runs Uvicorn as `appuser` (UID/GID 10001). Only application code and installed dependencies enter the runtime image. Local environment files, credentials, virtual environments, tests and sample images are excluded from the build context. No database migrations run automatically.

## Build and run

From the backend repository, with Docker Desktop running:

```sh
docker build -t mealventory-backend:local .
docker run --rm --name mealventory-backend --env-file .env -p 127.0.0.1:8000:8000 mealventory-backend:local
```

These commands work in macOS Terminal and Windows PowerShell. Stop the locally running backend first if it already occupies port 8000. Keep AI services running separately. Supply actual runtime environment values via the ignored `.env` file or your deployment secret manager; never bake credentials into the image.

`DATABASE_URL` must reach your existing PostgreSQL/Supabase database. `AI_SERVICE_URL` must be reachable from inside the container: on Docker Desktop, use `http://host.docker.internal:8001` for AI services on the host computer, or the AI container's service name on a shared Docker network. `localhost` inside the backend container refers to that container. Configure Supabase authentication as described in [supabase-auth.md](../api/supabase-auth.md).

The app listens on port 8000. No development reload process is used. The command above publishes to the host's loopback address only; your existing Cloudflare tunnel can forward that port. Deploy behind your hosting platform's HTTPS ingress when hosting remotely.

Sample scans are disabled by default. For development sample scans, mount a sample folder read-only and set `ENABLE_SAMPLE_SCAN=true` and `SAMPLE_IMAGES_DIR` to its container path. If a feature requires a credential file, mount that file read-only and point the environment variable to the container path; do not add it to the Dockerfile.

## Health checks

- `GET /` retains the existing liveness response, `{"status":"API running"}`.
- `GET /api/v1/health` executes `SELECT 1` against the configured database. It requires no authentication and returns 200 with `{"status":"healthy","database":"available"}` or 503 with `{"status":"unhealthy","database":"unavailable"}`. Connection details and credentials are not returned.
- This is a connectivity probe, not a schema, Supabase auth or AI-service check. Apply required migrations separately.

Docker runs the readiness request every 30 seconds, with a 20-second startup grace period, a five-second process timeout, and three failed attempts before unhealthy status. The probe uses Python's standard HTTP library so curl is not needed in the image.

```sh
docker inspect --format '{{.State.Health.Status}}' mealventory-backend
docker exec mealventory-backend id
docker logs mealventory-backend
```

Expect `healthy` after startup and UID 10001. A Docker health status alone does not restart the container; configure your hosting platform's restart/readiness policy separately. If unhealthy, check runtime settings and database reachability. Restarting a tunnel does not fix an unreachable database.

## Verification

From the backend repository:

```sh
python -m pytest tests/ -q
```

Unit tests cover successful database checks and safe 503 responses while retaining the existing root liveness contract. Container verification should build the actual image, connect it to disposable PostgreSQL, verify healthy status and a non-root UID, stop PostgreSQL, and verify unhealthy status. Never stop the application's shared database for this test.

Run the automated container smoke test after building the test image (Docker must be on PATH):

```sh
docker build -t mealventory-backend:issue48 .
RUN_DOCKER_TESTS=1 python -m pytest tests/test_docker_runtime.py -q
```

For PowerShell, set `$env:RUN_DOCKER_TESTS="1"` before the pytest command. The test uses shorter probe intervals, creates its own private Docker network and PostgreSQL container, verifies both healthy and unhealthy states, and removes its containers/network afterward. It does not publish ports or use your `.env` database.
