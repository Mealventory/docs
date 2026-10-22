# C4 Level 2: Container Diagram (DOCS-05)

The **Containers** diagram zooms into the Mealventory system boundary, detailing the major executable services, mobile applications, data stores, inter-process communication protocols, and port allocations.

---

## 🗺️ Containers Diagram

```mermaid
C4Container
    title Container Diagram for Mealventory Platform

    Person(user, "Household User", "Household shopper or member interacting via mobile device.")

    System_Boundary(b1, "Mealventory System Boundary") {
        Container(mobile_app, "Cross-Platform Mobile Client", "React Native 0.74, Expo SDK 51, TypeScript", "Provides responsive UI for pantry management, live camera scanning, AI review, recipes, and shopping.")
        
        Container(backend_api, "Backend Core API Service", "FastAPI (Python 3.11), Uvicorn, SQLAlchemy 2.0, Pydantic v2", "Exposes typed REST endpoints for household inventory, scan reviews, shopping lists, activity feeds, and notification triggers.", $port="8000")
        
        Container(ai_service, "AI Vision & OCR Service", "FastAPI (Python 3.11), Uvicorn, Pillow, MobileNetV2", "Handles image preprocessing, EXIF orientation correction, receipt OCR line parsing, and produce classification.", $port="8001")
        
        ContainerDb(database, "Relational Database", "PostgreSQL 16 / Supabase", "Persists households, memberships, catalogue foods, storage locations, inventory items, recipes, and shopping entries with RLS.", $port="5432")
    }

    System_Ext(supabase_auth, "Supabase Auth", "JWT Identity provider validating user sessions.")
    System_Ext(google_vision, "Google Cloud Vision API", "Cloud OCR and label detection engine.")
    System_Ext(openrouter, "OpenRouter LLM", "AI recipe recommendation service.")
    System_Ext(expo_push, "Expo Push Service", "Apple APNs and Google FCM mobile push notification relay.")
    System_Ext(openfoodfacts, "OpenFoodFacts API", "Public barcode product resolution.")

    Rel(user, mobile_app, "Interacts with screens, captures camera photos, views radar", "Touch / Native UI")
    
    Rel(mobile_app, supabase_auth, "Signs in, refreshes JWT tokens", "HTTPS / REST (JSON)")
    Rel(mobile_app, openfoodfacts, "Resolves scanned GTIN/UPC barcode numbers", "HTTPS / REST (JSON)")
    Rel(mobile_app, backend_api, "Performs CRUD, uploads images, commits batches", "HTTPS / REST (JSON with Bearer JWT)")

    Rel(backend_api, database, "Executes transactional queries and schema migrations", "PostgreSQL Wire Protocol / AsyncPG (Port 5432)")
    Rel(backend_api, ai_service, "Dispatches preprocessed scan requests", "HTTP / REST (Multipart Form) (Port 8001)")
    Rel(backend_api, openrouter, "Requests inventory-grounded recipe suggestions", "HTTPS / REST (JSON)")
    Rel(backend_api, expo_push, "Dispatches push notification batches for expiring items", "HTTPS / REST (JSON)")

    Rel(ai_service, google_vision, "Sends raw image bytes for document OCR & labels", "HTTPS / gRPC")
```

---

## 📦 Container Specifications

### 1. Cross-Platform Mobile Client (`frontend`)
- **Technology Stack**: React Native 0.74, Expo SDK 51, TypeScript, Expo Router v3, TanStack Query v5.
- **State & Persistence**:
  - `SecureStore`: Encrypted storage for Supabase session JWTs.
  - `MMKV` / Memory Cache: High-performance caching for offline inventory queries.
- **Hardware Integration**:
  - `expo-camera` / `expo-barcode-scanner`: Hardware camera viewfinder with live barcode framing.
  - `expo-notifications`: Device push token registration and foreground banner handling.

### 2. Backend Core API Service (`backend`)
- **Technology Stack**: FastAPI, Uvicorn, Python 3.11, Pydantic v2, SQLAlchemy 2.0 Async, Alembic.
- **Runtime Environment**: Docker Container (`mealventory-backend:local`), Non-root user `appuser` (UID 10001), Port 8000.
- **Core Modules**:
  - `app.api.v1`: Routers for households, inventory, recipes, shopping, stores, activity, and notifications.
  - `app.services`: Business logic layer implementing duplicate item stacking, recipe deduction, and invite enrollments.
  - `app.core.security`: Cryptographic verification of Supabase JWTs with audience and role validation.

### 3. AI Computer Vision Service (`ai-services`)
- **Technology Stack**: FastAPI, Python 3.11, Pillow (PIL), TensorFlow / Keras MobileNetV2, Google Cloud Vision SDK.
- **Runtime Environment**: Docker Container (`mealventory-ai:local`), Non-root user `aiuser` (UID 10002), Port 8001.
- **Core Modules**:
  - `services.image_preprocessing`: EXIF transpose, RGB normalization, dynamic contrast/sharpness enhancement.
  - `services.ocr_service`: Layout analysis, line-item extraction, date regex parsing.
  - `utils.confidence_scoring`: Calibrated scoring, softmax margin penalties, `needs_review` evaluation.
  - `services.mock_engine`: Deterministic offline evaluation pipeline (< 50ms).

### 4. Relational Database (`database`)
- **Technology Stack**: PostgreSQL 16 (Hosted via Supabase or local Docker instance).
- **Security & Multi-Tenancy**:
  - Row-Level Security (RLS) policies on `inventory_items`, `households`, and `recipes` enforcing tenant isolation by `household_id`.
  - Scoped transaction rollbacks guaranteeing atomic multi-item batch saves.
