# AI service readiness (#17)

Use the AI service's `GET /` as its liveness probe. It only confirms that the
FastAPI process responds and remains independent of Google Vision availability.
Use `GET /ready` as its readiness probe when routing scan traffic or reporting
whether the service can accept scans.

`/ready` returns HTTP 200 and `status: ready` only when the local MobileNetV2
model is loaded and an explicit Google credentials file is configured and
readable. Missing dependencies return HTTP 503. `status` is `degraded` when
some dependencies remain available and `unavailable` when none do. The response
only exposes dependency state, never credentials or filesystem paths.

This is a local configuration check. It does not call Google or establish that
the Vision API is enabled, billing is active, network access works, or the
credential is accepted. Those external Google Cloud settings still need to be
valid for OCR and Vision scans. Check them separately if live scans fail.

For local setup, configure `GOOGLE_APPLICATION_CREDENTIALS` to the existing
approved credential file (or use the setup documented in
[AI service setup](../../ai-services/SETUP.md)). Keep secrets out of images and
health-check output. For deployment, configure the same path or mount the
credential at the runtime path as a secret.

Example probes:

```sh
curl -i http://127.0.0.1:8001/
curl -i http://127.0.0.1:8001/ready
```

Configure orchestration liveness against `/` and readiness against `/ready`.
The backend's `/api/v1/health` checks its own database and is separate from
this AI service probe.
