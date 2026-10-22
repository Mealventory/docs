# Cross-Repo QA Regression Matrix & Release Checklist (DOCS-19)

This document defines the authoritative quality assurance regression matrix, release-blocking gates, and service restart rules across Mealventory's four repositories (`frontend`, `backend`, `ai-services`, and `docs`).

---

## 🚦 Release Gate Protocol & Defect Severity

Every candidate release or coordinated multi-repo merge must pass the gates below before deployment:

| Severity | Definition | Release Policy |
|---|---|---|
| **P0 (Blocker)** | Data loss, cross-household data leakage (RLS failure), crash on startup, auth lockout, or unhandled 500 error in core user journey. | **Immediate Release Blocker**. Zero P0 defects permitted. |
| **P1 (Major)** | Visual scanner failure, duplicate inventory generation, push notification delivery failure, or broken recipe deduction. | **Release Blocker** unless an explicit hotfix or feature flag rollback is approved. |
| **P2 (Minor)** | UI alignment flaw, dark-mode color inconsistency, missing non-critical food icon, or non-blocking translation issue. | Non-blocking for internal staging; must be scheduled for next sprint. |
| **P3 (Trivial)** | Minor copy typo, console debug log warning, or non-functional aesthetic enhancement. | Non-blocking. |

---

## 🔄 Service Restart & Cache Invalidation Rules

When testing cross-repo changes, restart affected services according to the change class:

| Class of Change | Affected Repositories | Required Action | Verification Command |
|---|---|---|---|
| **Database Schema / Migration** | `backend`, `docs` | 1. Apply migration: `alembic upgrade head`<br>2. Restart backend to refresh connection pools. | `python -m pytest tests/test_household_inventory.py` |
| **Backend Core Logic / OpenAPI** | `backend`, `frontend` | 1. Uvicorn auto-reloads (or restart container).<br>2. If tunnel address changed, update `frontend/.env.local`. | `curl -f http://localhost:8000/api/v1/health` |
| **AI Vision & Contract Changes** | `ai-services`, `backend` | 1. Restart AI Uvicorn process.<br>2. Verify typed schema snapshot in `contracts/openapi.json`. | `python -m benchmarks.runner` |
| **Mobile Client UI & Caching** | `frontend` | 1. Restart Metro bundler with cache clear: `npx expo start -c`<br>2. If auth state is corrupted, clear MMKV via Settings -> Sign Out. | `npm test` |

---

## 🧪 Comprehensive QA Regression Matrix

### Legend
- **Type**: 🤖 Automated Test | 📱 Physical Device / Manual | 🌐 API Contract Test
- **Owner**: `FE` (Frontend), `BE` (Backend), `AI` (AI Services)

| ID | User Journey / Feature | Type | Owner | Test Steps | Expected Result | Pass Criteria |
|---|---|---|---|---|---|---|
| **REG-01** | **Authentication & Session Hydration** | 🤖/📱 | `FE`/`BE` | 1. Launch app on cold boot.<br>2. Log in with valid credentials (`demo@mealventory.app`).<br>3. Kill app and reopen. | Splash screen hydrates session from SecureStore; user enters Pantry screen directly without login prompt. | Zero logout loops or blank screen flickers. |
| **REG-02** | **Password Recovery Flow** | 📱 | `FE`/`BE` | 1. Tap "Forgot Password" on login screen.<br>2. Enter registered email.<br>3. Submit request. | Supabase dispatches reset email; client displays confirmation dialog and does not crash. | Success toast displayed; rate limiting enforced. |
| **REG-03** | **Household Creation & Isolation (RLS)** | 🤖/🌐 | `BE` | 1. User A creates Household 1 (`DEMO01`).<br>2. User B creates Household 2 (`STUD02`).<br>3. User B queries items using User A's token. | PostgreSQL Row-Level Security filters all queries by `auth.uid()`; zero items from Household 1 are accessible to User B. | HTTP 403 or empty array; zero data leakage. |
| **REG-04** | **Household Join via Invite Code** | 🤖/📱 | `FE`/`BE` | 1. User B enters invite code `DEMO01` on join screen.<br>2. Confirm household enrollment. | User B is enrolled as member; household switcher reveals shared pantry instantly. | Invite code case-insensitive; duplicate joins rejected. |
| **REG-05** | **Manual Inventory CRUD** | 🤖/📱 | `FE`/`BE` | 1. Add item ("Fresh Spinach", 1 bag, Fridge, Expiry: +5 days).<br>2. Edit quantity from 1 to 2.<br>3. Delete item. | Item created, modified, and removed in PostgreSQL; UI updates optimistically via React Query. | UI reflects change immediately without layout shifts. |
| **REG-06** | **Receipt Scanning & Line Extraction** | 🤖/📱 | `FE`/`AI` | 1. Photograph grocery receipt.<br>2. Stream to `/api/v1/scan/upload` (mode: receipt).<br>3. Inspect parsed items. | OCR parses item names, quantities, and prices; filters non-food headers; returns valid `ScanResponse`. | Extracted items match physical receipt; confidence >= 80%. |
| **REG-07** | **Produce Visual Classification** | 🤖/📱 | `AI` | 1. Photograph apple or banana.<br>2. Stream to `/scan/` (mode: food). | Visual detector or MobileNetV2 identifies food category and returns normalized name. | Top item correctly classified; `type: food`. |
| **REG-08** | **Tag Expiry Parsing** | 🤖/🌐 | `AI` | 1. Photograph packaging with "BEST BEFORE 2026-11-20".<br>2. Stream to `/scan/` (mode: tag). | OCR extracts explicit date "2026-11-20"; suppresses unlabelled numeric strings. | Date exact match; `type: tag`. |
| **REG-09** | **Live Barcode Auto-Scan** | 📱 | `FE` | 1. Frame UPC/EAN barcode in camera viewfinder.<br>2. Trigger live scanner. | Viewfinder detects barcode instantly; queries OpenFoodFacts; populates product name and image. | Detection in < 500ms; duplicate auto-triggers debounced. |
| **REG-10** | **AI Review Sheet & Duplicate Stacking** | 🤖/📱 | `FE`/`BE` | 1. Scan receipt containing existing pantry item ("Whole Milk", 1 gal, Fridge).<br>2. Review items and tap "Save to Inventory". | Stacking engine matches active candidate; updates `quantity = 1 + 1 = 2` in-place rather than creating duplicate row. | Single pantry card with stacked quantity 2; no duplicates. |
| **REG-11** | **Consume & Discard State Transitions** | 🤖/📱 | `FE`/`BE` | 1. Swipe pantry item and tap "Consume" or "Discard".<br>2. Inspect Waste Analytics. | Item status transitions from `active` to `consumed` or `discarded`; item removed from active pantry list. | Accurate count in waste analytics; database record preserved. |
| **REG-12** | **Expiry-Weighted Recipe Recommendation** | 🤖/📱 | `FE`/`BE` | 1. Open Recipes tab with items expiring in < 48 hours.<br>2. Request recommendations. | Backend prompts LLM prioritizing urgent ingredients; displays recipe matching pantry inventory. | Recipe highlights urgent items; shows match percentage. |
| **REG-13** | **"Cook Meal" Atomic Stock Deduction** | 🤖/📱 | `FE`/`BE` | 1. Open recipe requiring 2 eggs and 1 cup milk.<br>2. Tap "Cook This Meal". | Backend executes atomic transaction deducting required quantities from pantry; marks depleted items as consumed. | Quantities decremented accurately; failure rolls back. |
| **REG-14** | **Missing Ingredients to Shopping List** | 🤖/📱 | `FE`/`BE` | 1. Open recipe with missing ingredient ("Cinnamon").<br>2. Tap "Add Missing to Shopping List". | Missing item automatically inserted into household's shared shopping list. | Appears in Shopping List tab immediately with correct unit. |
| **REG-15** | **Shared Shopping List Real-Time Sync** | 📱 | `FE`/`BE` | 1. User A checks off item on Phone 1.<br>2. User B observes Shopping List on Phone 2. | Item marked as completed across both devices; strike-through animation renders smoothly. | State synchronizes within polling/realtime window. |
| **REG-16** | **Two-Phone Household Inventory Sync** | 📱 | `FE` | 1. Phone 1 adds grocery item.<br>2. Phone 2 pulls to refresh or navigates to Pantry. | Phone 2 displays newly added item; storage location and expiry badges match exactly. | Identical counts and metadata on both devices. |
| **REG-17** | **Light and Dark Theme Consistency** | 📱 | `FE` | 1. Toggle system appearance between Light and Dark mode.<br>2. Review all tabs (Pantry, Scan, Recipes, Shopping, Settings). | High-contrast readability preserved; all text legible; cards and bottom sheets adapt smoothly without jarring flash. | Zero unstyled white backgrounds in dark mode. |
| **REG-18** | **AI Vision Failure / Outage Handling** | 🤖/📱 | `FE`/`AI` | 1. Disconnect AI service or simulate Vision 503 outage.<br>2. Attempt receipt scan in mobile client. | Client displays graceful error: "Scanning is temporarily unavailable; you can enter items manually." App does not crash. | Zero unhandled red-screen errors; manual entry option visible. |

---

## 🤖 Automated vs. Physical Device Test Separation

To optimize team execution velocity, testing responsibilities are segregated:

### 1. Automated CI Test Suites (Execute on every Pull Request)

```bash
# Frontend Test Suite (Jest / React Native Testing Library)
cd frontend && npm test
# Total: 282 tests passing (Auth, Inventory, AI Review, Duplicate Stacking)

# Backend Test Suite (Pytest / AsyncPG)
cd backend && pytest tests/ -q
# Total: 318 tests passing (RLS, Stacking, Recipes, Shopping, Docker runtime)

# AI Services Test Suite (Unittest / Fast Microservice Coroutines)
cd ai-services && python -m unittest discover tests
# Total: 47 tests passing (Confidence calibration, contracts, preprocessing)

# AI Benchmark Suite (Regression Prevention)
cd ai-services && python -m benchmarks.runner --baseline benchmarks/baselines/default_baseline.json
# Total: 10 fixtures passing with zero regressions
```

### 2. Physical Device Manual Verification (Execute before Releases)
- **Hardware Camera Viewfinder**: Test camera autofocus, barcode detection latency, and low-light receipt legibility.
- **Push Notification Banners**: Verify Apple APNs and Google FCM lock-screen banners on physical iOS and Android hardware.
- **Airplane Mode / Network Drop**: Switch device to Airplane Mode while browsing pantry; verify TanStack Query MMKV cache displays inventory with zero delay.
- **Biometric / Keychain Session**: Verify face ID / fingerprint and secure token preservation across device reboots.

---

## 📋 Pre-Release Sign-Off Checklist

Before tagging a production release:

- [ ] All 4 repository test suites passing with 100% success rate (FE: 282, BE: 318, AI: 47, Benchmarks: 10).
- [ ] Zero unmerged schema migrations; `alembic upgrade head` verified on staging database.
- [ ] OpenAPI contracts in `backend/contracts/v1-openapi.json` and `ai-services/contracts/openapi.json` verified with zero drift.
- [ ] No hardcoded secrets, staging URLs, or tunnel addresses committed in tracked files.
- [ ] Physical device smoke test completed on both iOS (TestFlight) and Android (Internal Track).
- [ ] Capstone live demo script ([operations guide](README.md)) and demo fixtures ([demo-seeder-60.md](demo-seeder-60.md)) verified end-to-end.
