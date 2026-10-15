# Multi-Repo Local Development Setup & Verification Runbook (DOCS-01)

An authoritative, step-by-step setup guide enabling any engineer to clone all 4 Mealventory repositories, boot the unified local microservice stack, launch the mobile client, and verify the complete workflow on a clean workstation in **under 15 minutes**.

---

## 🏗️ System Architecture & Workspace Layout

Mealventory is distributed across 4 coordinated repositories:

```text
Mealventory/
├── frontend/        # React Native / Expo cross-platform mobile client
├── backend/         # FastAPI v1 REST API, PostgreSQL database models, Alembic migrations
├── ai-services/     # FastAPI computer vision, Google Vision OCR & MobileNetV2
└── docs/            # Centralized system blueprints, API contracts, and runbooks
```

### Clone All Repositories

```bash
mkdir -p Mealventory && cd Mealventory
git clone https://github.com/Mealventory/frontend.git
git clone https://github.com/Mealventory/backend.git
git clone https://github.com/Mealventory/ai-services.git
git clone https://github.com/Mealventory/docs.git
```

---

## ⚙️ Prerequisites & Workstation Tooling

Verify required tools before running the stack:

| Tool | Minimum Version | Purpose | Verification |
|---|---|---|---|
| **Git** | 2.40+ | Version control | `git --version` |
| **Node.js & npm** | Node 18.18+ / npm 9+ | Expo client runtime & package management | `node -v && npm -v` |
| **Python** | 3.11.9+ | Backend & AI Services microservices | `python --version` |
| **Docker & Docker Compose** | Docker 24+ / Compose v2 | Containerized local database and services | `docker --version` |
| **Cloudflared** *(Optional)* | Latest | Tunnels for testing physical mobile devices | `cloudflared --version` |
| **Expo CLI** | Latest | Native development tooling | `npx expo -v` |

---

## 🔐 Environment Configuration

Each repository provides an audited `.env.example` template. Configure each file as follows:

### 1. AI Service Configuration (`ai-services/.env`)

```bash
cd ai-services
cp .env.example .env
```

Key environment settings:
```dotenv
PORT=8001
HOST=0.0.0.0
# For local offline testing without Google Cloud billing:
MOCK_VISION=true
GEMINI_API_KEY=mock
# For live cloud OCR:
GOOGLE_APPLICATION_CREDENTIALS=credentials/google_vision_key.json
```

### 2. Backend Configuration (`backend/.env`)

```bash
cd ../backend
cp .env.example .env
```

Key environment settings:
```dotenv
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mealventory_demo
AI_SERVICE_URL=http://127.0.0.1:8001
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
SUPABASE_ALGORITHM=HS256
CORS_ORIGINS=["http://localhost:8081","http://localhost:19006","http://localhost:3000"]
```

### 3. Frontend Configuration (`frontend/.env.local`)

```bash
cd ../frontend
cp .env.example .env.local
```

Key environment settings:
```dotenv
EXPO_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
# Point to local backend (or tunnel URL if testing physical device):
EXPO_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## 🚀 One-Command Unified Stack Boot

You can run the entire backend and AI services stack using unified Docker Compose or multi-terminal native processes.

### Option A: Native Fast Boot (Recommended for Daily Development)

#### Terminal 1 — AI Vision Service
```bash
cd Mealventory/ai-services
python -m venv .venv
# Windows: .\.venv\Scripts\activate | macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```
*Health Probe*: Verify `http://localhost:8001/ready` returns `{"status":"ready"}`.

#### Terminal 2 — FastAPI Backend
```bash
cd Mealventory/backend
python -m venv .venv
# Windows: .\.venv\Scripts\activate | macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*Health Probe*: Verify `http://localhost:8000/api/v1/health` returns `{"status":"healthy","database":"available"}`.

#### Terminal 3 — Expo Mobile Client
```bash
cd Mealventory/frontend
npm install
npx expo start --clear
```
- Press `w` to open in Web Browser.
- Press `i` to launch in iOS Simulator (macOS only).
- Press `a` to launch in Android Emulator.
- Scan QR code with Expo Go on physical device (ensure `EXPO_PUBLIC_BACKEND_URL` points to your LAN IP or Cloudflare tunnel).

---

### Option B: Dockerized Multi-Container Boot

From the `backend/` directory:
```bash
# Build production images and boot with local PostgreSQL
docker compose up -d --build
```
Inspect container health:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## 🧪 Database Initialization & Test Seeding

Seed 50 realistic pantry items, demo households, and recipe fixtures:

```bash
cd Mealventory/backend
# Windows PowerShell
$env:SEED_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mealventory_demo"
python -m app.scripts.seed_db --reset --items=50

# macOS / Linux
export SEED_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mealventory_demo"
python -m app.scripts.seed_db --reset --items=50
```

Verify seeded records:
```bash
python -m pytest tests/test_seed_db.py -q
```

---

## 📱 Physical Device Testing (Cloudflare Tunnel)

To test mobile devices on cellular or distinct Wi-Fi subnets without network friction:

1. Launch a Cloudflare Tunnel:
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```
2. Copy the generated address (e.g., `https://random-words.trycloudflare.com`).
3. Update `frontend/.env.local`:
   ```dotenv
   EXPO_PUBLIC_BACKEND_URL=https://random-words.trycloudflare.com
   ```
4. Restart Expo: `npx expo start -c`.

---

## 🔍 Verification & Health Check Matrix

| Component | Target URL | Expected Response |
|---|---|---|
| **AI Liveness** | `http://localhost:8001/` | `{"status":"API running"}` |
| **AI Readiness** | `http://localhost:8001/ready` | `{"status":"ready","checks":{"model":"ready","vision":"configured"}}` |
| **Backend Liveness** | `http://localhost:8000/` | `{"status":"API running"}` |
| **Backend Database** | `http://localhost:8000/api/v1/health` | `{"status":"healthy","database":"available"}` |
| **Backend OpenAPI** | `http://localhost:8000/docs` | Swagger interactive UI |
| **Frontend Web** | `http://localhost:8081/` | Mealventory Pantry Dashboard |

---

## 🛠️ Common Troubleshooting

### 1. Android Emulator Networking
- Inside Android Emulator, `localhost` refers to the emulator itself.
- Set `EXPO_PUBLIC_BACKEND_URL=http://10.0.2.2:8000` or use a Cloudflare tunnel URL.

### 2. CORS Errors in Web Browser
- If the browser console reports CORS blockage:
- Check `backend/.env` `CORS_ORIGINS` includes `http://localhost:8081` and `http://localhost:19006`.
- Refer to [operations/cors-origins-74.md](cors-origins-74.md).

### 3. Port Conflicts
- Port 8000: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (macOS).
- Port 8001: Kill lingering Uvicorn instances before restarting.
