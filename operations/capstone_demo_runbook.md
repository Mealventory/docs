# Capstone Live Demo Script & Evaluation Runbook (DOCS-06)

This runbook defines the formal presentation choreography, pre-seeded demo environment, and contingency fail-safe procedures for the **Mealventory Capstone Evaluation Panel**.

---

## ⏱️ Executive Presentation Summary

- **Total Allocated Time**: 7 Minutes Live Demonstration + 3 Minutes Technical Q&A.
- **Presenters**:
  - **Speaker 1 (Product & UX Flow)**: Drives the mobile client on physical device / screen mirror.
  - **Speaker 2 (Architecture & Systems)**: Narrates technical implementation, tenant boundaries, and telemetry.
- **Core Narrative**: Reducing domestic food waste and grocery over-purchasing through intelligent multimodal inventory tracking, shared household collaboration, and expiry-weighted recipe planning.

---

## 📋 Pre-Flight Checklist (T-Minus 15 Minutes)

Execute these checks before taking the presentation stage:

| Check | Target / Verification Command | Expected State |
|---|---|---|
| **Workstation Power** | AC adapter plugged in; screen sleep disabled | Active / No screen timeout |
| **Network Hotspot** | Dedicated mobile hotspot active (avoid campus Wi-Fi congestion) | Subnet assigned |
| **Backend Service** | `GET http://localhost:8000/v1/health` or tunnel URL | `{"status":"ok"}` (HTTP 200) |
| **AI Vision Service** | `GET http://localhost:8001/ready` | `{"status":"ready"}` (HTTP 200) |
| **Database Seed** | Run database seeder (see [Demo Fixtures](#-demo-fixtures--seeder-procedure)) | 50 items seeded |
| **Mobile App Build** | Expo Go or EAS Development Client booted on primary device | Clean launch, logged into demo account |
| **Screen Mirroring** | Scrcpy / AirPlay / QuickTime screen mirroring connected to projector | Crisp 1080p display |
| **Offline Fail-Safe** | `MOCK_VISION=true` flag tested and verified in reserve terminal | Fallback ready |

---

## 🎬 7-Minute Choreographed Demo Script

```mermaid
journey
    title 7-Minute Live Capstone Demo Journey
    section 00:00 - 01:00
      Login & Household Isolation : 5: Presenter
    section 01:00 - 02:00
      Expiry Radar & Pantry View  : 5: Presenter
    section 02:00 - 03:30
      Multimodal Receipt Scan     : 5: Presenter
    section 03:30 - 04:45
      AI Review & Batch Save      : 5: Presenter
    section 04:45 - 06:00
      Expiry Recipe Recommendation: 5: Presenter
    section 06:00 - 07:00
      Cook Deduction & Architecture Recap: 5: Presenter
```

### [00:00 – 01:00] Scene 1: Problem Space, Authentication & Multi-Tenant Isolation
- **Presenter 1 Action**:
  - Open the Mealventory app to the login screen.
  - Sign in with the primary demo account: `demo@mealventory.app`.
  - App opens directly into the **Demo Family** household.
- **Presenter 2 Narrative**:
  > *"Every year, the average Canadian household discards over $1,300 in edible groceries due to forgotten shelf-lives and disorganized shopping. Mealventory eliminates this friction through automated tracking.*
  > *Notice that upon login, our client authenticates via Supabase Auth and establishes a cryptographic JWT session. In the backend, PostgreSQL Row-Level Security (RLS) strictly isolates inventory records by household UUID, guaranteeing zero cross-tenant data leakage."*

---

### [01:00 – 02:00] Scene 2: Expiry Radar & Pantry Storage Zones
- **Presenter 1 Action**:
  - Show the **Pantry Dashboard**.
  - Tap through the urgency filters: **All**, **Expiring Soon (< 48 hrs)**, and **Expired**.
  - Switch tabs between storage locations: **Fridge**, **Freezer**, and **Pantry**.
  - Open a sample item (`Strawberries`) showing shelf-life metadata and storage suggestions.
- **Presenter 2 Narrative**:
  > *"Our Expiry Radar categorizes inventory into real-time risk tiers. Items expiring within 48 hours are automatically elevated to the top banner.*
  > *Notice how items are partitioned by storage zone. Storage conditions directly influence shelf-life decay formulas calculated by our backend expiry prediction microservice."*

---

### [02:00 – 03:30] Scene 3: Multimodal Scanning & Receipt Ingestion
- **Presenter 1 Action**:
  - Tap the prominent **Scan** button in the bottom navigation bar.
  - Show the mode selector: **Product**, **Receipt**, **Tag**, or **Barcode**.
  - Select **Receipt Mode** and photograph the prepared physical receipt fixture (or choose from demo camera roll).
  - An animated scan hud activates while the image streams to the AI service.
- **Presenter 2 Narrative**:
  > *"Instead of tedious manual data entry, Mealventory supports multimodal visual ingestion. The image is preprocessed for contrast and orientation, then processed via Google Vision OCR and our custom layout extraction pipeline.*
  > *The service parses supermarket line items, filters out non-food entries, extracts quantities and unit prices, and normalizes food names against our standardized catalogue."*

---

### [03:30 – 04:45] Scene 4: AI Review BottomSheet & Duplicate Item Stacking
- **Presenter 1 Action**:
  - The scan resolves, opening the **AI Review BottomSheet**.
  - Point out extracted items: `Whole Milk`, `Sourdough Bread`, `Apples`.
  - Note the confidence badges and calibrated review indicators (`needs_review`).
  - Adjust quantity on `Whole Milk` from 1 to 2.
  - Tap **Save to Inventory**.
  - Navigate to Pantry: point out that because `Whole Milk` already existed in the Fridge, Mealventory **automatically stacked the quantity** instead of creating duplicate clutter.
- **Presenter 2 Narrative**:
  > *"Our AI pipeline adheres to an explicit human-in-the-loop review contract. When confidence falls below 80%, items are clearly highlighted with a 'Review Needed' badge.*
  > *When committed, our newly implemented inventory consolidation engine matches candidates by name, storage zone, and expiry date, stacking identical items in-place with optimistic React Query updates."*

---

### [04:45 – 06:00] Scene 5: Expiry-Weighted Recipe Recommendation
- **Presenter 1 Action**:
  - Tap the **Recipes** tab.
  - Tap **Generate Recipes for My Pantry**.
  - Show the suggested recipe: *"Skillet Apple Cinnamon Sourdough French Toast"*.
  - Expand the recipe card to display:
    - Pantry Match: **3 of 4 ingredients in stock**.
    - Urgent Ingredients Used: `Apples (Expires Tomorrow)`, `Milk`, `Bread`.
    - Missing Ingredient: `Cinnamon`.
  - Tap **Add Missing Ingredients to Shopping List**.
  - Switch to **Shopping List** tab: show `Cinnamon` now present under the shared household list.
- **Presenter 2 Narrative**:
  > *"Traditional recipe apps suggest meals without regard to what's already wilting in your fridge. Mealventory's recipe engine prioritizes expiring inventory first.*
  > *If a recipe requires ingredients you lack, a single tap synchronizes the missing items into the household's shared shopping list, visible instantly to all family members."*

---

### [06:00 – 07:00] Scene 6: "Cook Meal" Auto-Deduction & Architectural Recap
- **Presenter 1 Action**:
  - Return to the Recipe screen and tap **Cook This Meal**.
  - Confirm the deduction prompt.
  - Return to the Pantry: demonstrate that `Apples`, `Bread`, and `Milk` quantities have been accurately decremented, and fully consumed items transitioned to the `consumed` state for waste analytics.
- **Presenter 2 Narrative**:
  > *"Tapping 'Cook Meal' executes an atomic database transaction that decrements stock from your inventory, closing the complete loop from scan to plate.*
  > *Under the hood, Mealventory is built as a robust multi-service platform: FastAPI v1 with typed OpenAPI contracts, React Native Expo with local offline persistence, and calibrated AI services.*
  > *Thank you—we are now open for technical questions."*

---

## 🗄️ Demo Fixtures & Seeder Procedure

To guarantee a clean state identical to the script, seed the local database prior to the presentation.

### Seed Execution (From `backend/` directory)

```bash
# Windows PowerShell
$env:SEED_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mealventory_demo"
python -m app.scripts.seed_db --reset --items=50

# macOS / Linux
export SEED_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mealventory_demo"
python -m app.scripts.seed_db --reset --items=50
```

### Seeded Credentials & Entities

| Entity | ID / Value | Purpose |
|---|---|---|
| **Primary Demo Account** | `demo@mealventory.app` / `Password123!` | Presenter login account |
| **Primary Household** | `Demo Family` (Code: `DEMO01` / `DEMO42`) | Main demonstration tenant |
| **Secondary Household** | `Single Student` (Code: `STUD02`) | Used to prove multi-tenant isolation |
| **Initial Inventory Items** | 50 pre-seeded items | Provides realistic expiry radar distribution |
| **Expiring Items** | `Strawberries`, `Fresh Milk`, `Spinach` | Trigger immediate expiry warnings |

---

## 🛡️ Offline Mock Fail-Safe Protocol

If presentation venue Wi-Fi becomes unstable or external APIs (Google Vision, OpenRouter) experience outages, activate the **Deterministic Mock Pipeline** immediately:

### 1. AI Service Failover (< 5 Seconds)
In the terminal running `ai-services`:
```bash
# Force zero-cost deterministic mock responses
export MOCK_VISION=true
export GEMINI_API_KEY=mock
```
- The mock engine immediately intercepts `/scan/` and `/scan/multi` requests.
- Returns deterministic produce (`milk`, `egg`, `bread`, `apple`, `chicken`) and receipt fixtures in `< 50ms`.
- Guaranteed zero network dependency.

### 2. Mobile Client Offline Persistence
- The Expo client uses **TanStack Query** with local persistence.
- Already queried pantry items remain completely interactive and searchable even in airplane mode.

---

## 🎓 Capstone Grading Rubric Alignment Matrix

| Evaluation Criteria | Demonstrated Feature in Runbook | Technical Proof Point |
|---|---|---|
| **Multi-Tenant Security** | Household switching & isolation | PostgreSQL RLS policies enforce `household_id` filtering on all queries |
| **AI / Computer Vision** | Receipt OCR, food recognition & tag parsing | Multi-stage FastAPI microservice with calibrated confidence scoring |
| **Full Lifecycle Closed-Loop** | Scan -> Review -> Recipe -> Cook Deduction | End-to-end integration across frontend, backend, and AI service |
| **Error Handling & Resilience** | Calibrated `needs_review` badge & offline mock | Soft degrade on low confidence (< 0.80); deterministic mock failover |
| **UI/UX Craftsmanship** | Expiry Radar, BottomSheets & Optimistic UI | React Native Expo with smooth transitions and zero layout shifts |
