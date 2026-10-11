# Starting Mealventory

Use this guide for local development with the existing configured repositories. Keep each service in its own terminal. Commands below do not reset databases or replace your environment files.

## Before starting

- Use the team-agreed compatible backend/frontend branches. Uncommitted local changes are not available to teammates until committed and pushed.
- Python 3.11.9, Node/npm, and cloudflared must be installed. Use a compatible Expo Go installation or the team's development build.
- Keep backend/.env, ai-services/.env and frontend/.env.local configured; do not overwrite them each time.
- Backend DATABASE_URL must point to the intended Supabase PostgreSQL database with the application schema installed. AI_SERVICE_URL should be http://127.0.0.1:8001 when both services run on the same computer.
- Backend Supabase authentication settings must match the frontend's Supabase project. HS256 requires the JWT secret; asymmetric signing uses the configured algorithm and project URL. See [authentication setup](../api/supabase-auth.md).
- Real OCR requires valid Google credentials, enabled Vision API and active project billing. Use the existing approved credentials file; do not create a new key for each launch.
- Always use the URL printed by your current backend tunnel; do not copy an old temporary address from another developer’s environment.

## Mac: everyday startup

These examples assume the repositories are under `~/Documents/Mealventory`. Substitute your own checkout location.

### Terminal 1 — AI service

```sh
cd ~/Documents/Mealventory/ai-services
source .venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Wait for `Application startup complete`. Model loading may take time. Check
`http://127.0.0.1:8001/` for process liveness and
`http://127.0.0.1:8001/ready` for scan readiness. Use `/` for deployment
liveness probes and `/ready` for readiness probes; see the [AI readiness
guide](../operations/ai-readiness-17.md).

AI is needed for backend scan requests, but is not required for sign-in, households, or manual inventory actions. Live scanning sends captured or selected images for review before saving confirmed items.

### Terminal 2 — backend

```sh
cd ~/Documents/Mealventory/backend
source .venv311/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wait for `Application startup complete`. Open http://127.0.0.1:8000/docs. Check http://127.0.0.1:8000/api/v1/health for database readiness; the root page alone only proves the server is running.

### Terminal 3 — backend tunnel

```sh
cloudflared tunnel --url http://localhost:8000
```

Keep this terminal open. Copy the new `https://...trycloudflare.com` address printed in its output. Open that address with `/docs` appended to verify it reaches the backend.

In frontend/.env.local, set the existing line to the new address, without `/docs`:

```dotenv
EXPO_PUBLIC_BACKEND_URL=https://YOUR-CURRENT-TUNNEL.trycloudflare.com
```

Keep the Supabase URL and public publishable key already in that file. Never put the database password, service-role key or JWT secret into an EXPO_PUBLIC variable.

A quick tunnel address is temporary. Starting another tunnel produces a new address; update the frontend and restart Expo when it changes. Restarting only the backend on the same port does not require replacing a still-running tunnel.

### Terminal 4 — Expo

```sh
cd ~/Documents/Mealventory/frontend
npx expo start --dev-client --tunnel --clear
```

Open the installed Mealventory development build using the QR code. If testing with a compatible Expo Go version instead, use `npx expo start --go --tunnel --clear`. Push-notification testing requires the development build. For browser testing, press `w` in the Expo terminal and use the address it prints.

The Expo tunnel serves the app; the Cloudflare tunnel serves the backend. Both must remain running for this setup. They are different URLs.

## Windows: everyday startup

Use PowerShell. Replace `C:\Mealventory` with the folder containing your repos. These commands run the virtual environment's Python directly, avoiding PowerShell activation-policy problems.

Terminal 1:

```powershell
cd C:\Mealventory\ai-services
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Terminal 2:

```powershell
cd C:\Mealventory\backend
.\.venv311\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 3:

```powershell
cloudflared tunnel --url http://localhost:8000
```

Update frontend/.env.local with the printed backend tunnel URL, then start Terminal 4:

```powershell
cd C:\Mealventory\frontend
npx expo start --dev-client --tunnel --clear
```

If the existing backend environment is named `.venv` instead, substitute that folder for `.venv311`.

## Dependencies: first setup or after dependency changes

Do this before starting the services, not on every launch. Do not overwrite an existing environment made with the wrong Python version; create a separate Python 3.11 environment instead.

Mac, from each respective repository:

```sh
# ai-services
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

# backend
python3.11 -m venv .venv311
.venv311/bin/python -m pip install -r requirements-dev.txt

# frontend
npm ci
```

Windows, from each respective repository:

```powershell
# ai-services
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# backend
py -3.11 -m venv .venv311
.\.venv311\Scripts\python.exe -m pip install -r requirements-dev.txt

# frontend
npm ci
```

Only create missing .env files from the examples, then fill in the team's configuration securely. For a new database, follow [initial schema setup](../database/initial-schema.md); do not initialize or reset the shared database as a routine startup step.

## Testing with teammates

One person can host the backend and its Cloudflare tunnel. Everyone using that backend sets the same current tunnel URL in their frontend/.env.local. Each teammate can run their own Expo instance. Alternatively, each developer can run their own backend/tunnel and use the URL generated on their machine.

The hosting computer must stay awake and connected. The backend and AI service must use compatible configuration, and all clients must use the matching Supabase project.

To test inventory status, sign in on two phones in the same household. Mark an item consumed or discarded on one phone. Refresh the other phone, or allow the foreground inventory poll about five seconds. The item should disappear from active inventory while remaining in database history.

## Troubleshooting

- **Hostname could not be found:** verify the current Cloudflare URL, update .env.local, and restart Expo with `--clear`.
- **Tunnel opens but returns 502:** check the backend is running on port 8000 and local `/docs` opens.
- **Sign-in works but households fail:** check backend `/api/v1/health`, database connection and matching Supabase authentication settings. Supabase login alone does not prove backend connectivity.
- **Port already in use:** stop the previous service with Ctrl+C in its terminal before restarting. If changing the backend port, also change the tunnel target.
- **cloudflared command not found:** install Cloudflare's cloudflared client and reopen the terminal.
- **Browser-only request failure:** check [CORS configuration](../operations/cors-origins-74.md) against the actual Expo web origin.
- **Expired password-recovery link:** request a new email and verify the Supabase redirect matches the current app URL. Restarting the backend tunnel does not fix an Expo recovery redirect.

## Stop the project

Press Ctrl+C in each of the four terminals. No database reset is needed. On the next launch, use the new backend tunnel address if the quick tunnel was stopped.

## Same-network alternative

On a reachable shared Wi-Fi network, set `EXPO_PUBLIC_BACKEND_URL=http://<computer-LAN-IP>:8000` and run `npx expo start --dev-client --lan`. A physical phone’s `localhost` points to the phone, not your computer. Allow the backend port through the host firewall on the trusted development network. Expo’s tunnel only carries the app bundle; it does not tunnel backend traffic.

For the macOS iOS Simulator, install and configure Xcode and its simulator runtime, then start Expo and press `i`. Use a simulator-compatible build. A simulator on the backend Mac can reach `http://127.0.0.1:8000`.
