# Mealventory documentation

Maintained guides for running, testing and understanding Mealventory. Application code lives in the [frontend](https://github.com/Mealventory/frontend), [backend](https://github.com/Mealventory/backend) and [AI services](https://github.com/Mealventory/ai-services) repositories. This page describes the checked-in implementation; it does not verify what is currently deployed.

## Start here

1. [Launch the app on Mac or Windows](getting-started/starting-the-project.md).
2. [Connect authentication and households](getting-started/live-households.md).
3. [Test account flows](getting-started/auth-testing.md).
4. [Verify shared inventory on two phones](features/shared-inventory.md).

## Implementation status

The matrix below distinguishes implemented behavior from unfinished or planned work. Issue links point to tracked work in the owning repository; check GitHub for the latest status.

| Area | Implemented now | Unfinished or planned work |
| --- | --- | --- |
| Frontend | Expo and React Native app for household pantry, item editing, scan review, recipe suggestions, shopping lists and activity. See [feature guides](features/README.md). | [Item detail and waste analytics (#8)](https://github.com/Mealventory/frontend/issues/8), [email receipt import (#99)](https://github.com/Mealventory/frontend/issues/99), [duplicate inventory stacking (#129)](https://github.com/Mealventory/frontend/issues/129), and [frontend cleanup (#127)](https://github.com/Mealventory/frontend/issues/127). |
| Backend | FastAPI v1 APIs for household-scoped inventory, scanning, recipes, shopping, stores, activity and notifications. Schema changes use Alembic migrations. | [Legacy user-scoped inventory cleanup (#76)](https://github.com/Mealventory/backend/issues/76), [scan-save idempotency (#85)](https://github.com/Mealventory/backend/issues/85), [structured request logging and correlation IDs (#89)](https://github.com/Mealventory/backend/issues/89), and [household expiry-model integration (#95, in progress)](https://github.com/Mealventory/backend/issues/95). |
| AI service | FastAPI scan service uses Google Vision for OCR/labels and Keras MobileNetV2 as a local classification fallback. Current routes are documented by the [AI service repository](https://github.com/Mealventory/ai-services). | [FoodKeeper shelf-life data (#6)](https://github.com/Mealventory/ai-services/issues/6), [OpenFoodFacts service fallback (#7)](https://github.com/Mealventory/ai-services/issues/7), [offline mock vision (#8)](https://github.com/Mealventory/ai-services/issues/8), [production Docker image (#9)](https://github.com/Mealventory/ai-services/issues/9), [typed scan contract (#15)](https://github.com/Mealventory/ai-services/issues/15), [scan benchmarks (#16)](https://github.com/Mealventory/ai-services/issues/16), [image preprocessing hardening (#18)](https://github.com/Mealventory/ai-services/issues/18), and [recognition confidence calibration (#19)](https://github.com/Mealventory/ai-services/issues/19). |
| Database | PostgreSQL/Supabase schema with household ownership, row-level security policies and versioned Alembic migrations. See [database guides](database/README.md). | Apply migrations as a separate deployment step; they are not run automatically at app startup. |
| Authentication | Supabase sign-in on the client; the backend validates Supabase access tokens and enforces household context. See [auth setup](api/supabase-auth.md). | [Authentication and account data-isolation fixes (#33)](https://github.com/Mealventory/frontend/issues/33) are marked “Needs work” in the backlog. |
| Scanning | Food, receipt and expiry-tag images go through backend review endpoints to the AI service. Barcode lookup currently runs in the client against OpenFoodFacts. Users can review scan results before saving. See [scanner recognition](features/scanner-recognition.md) and [scan integrity](features/scan-review-integrity.md). | Confidence calibration, typed cross-service contracts and preprocessing work are tracked in [AI service issues #15](https://github.com/Mealventory/ai-services/issues/15), [#18](https://github.com/Mealventory/ai-services/issues/18) and [#19](https://github.com/Mealventory/ai-services/issues/19). |
| Recipes | The backend requests inventory-grounded suggestions from OpenRouter; saved recipes and reviewed ingredient deduction are supported. Configure the provider key for generation. See [household recipes](features/household-recipes.md). | No separate open recipe issue is listed in the supplied backlog. Recipe generation depends on an external provider and its runtime configuration. |
| Shopping | Shared household shopping-list create, update, check and delete endpoints are implemented. See [shopping list](features/shopping-list-71.md). | No unfinished shopping-specific issue is listed in the supplied backlog. |
| Notifications | The backend registers Expo push tokens and sends low-stock and expiry notifications. The daily expiry job must be invoked by an external scheduler. | Deployment still needs a configured scheduler and secrets; see [notification operations](operations/README.md). No scheduler-specific issue is listed in the supplied backlog. |
| Offline support | Inventory query results are persisted on native development/release builds. Expo Go uses memory-only storage. | This is not full offline-first support: there is no offline write queue or synchronization engine. No active full-offline issue is listed in the supplied backlog. |

The AI service does **not** currently use Gemini or ingest FoodKeeper data. The app does **not** provide full offline synchronization. Those designs appear only in historical proposals unless linked to current work above.

## Guides by topic

| Folder | Contents |
| --- | --- |
| [Getting started](getting-started/README.md) | Startup, networking and account checks |
| [Features](features/README.md) | Household, pantry, scanner, expiry, recipes and shopping |
| [API](api/README.md) | Authentication and the retained OpenAPI snapshot |
| [Database](database/README.md) | Initial schema and row-level security |
| [Operations](operations/README.md) | Containers, CORS, demo data, health probes and AI failures |
| [Architecture](architecture/README.md) | Authentication session persistence |
| [Archive](archive/README.md) | Historical proposals and superseded task lists |

## Maintaining these docs

- Update the existing topic guide instead of duplicating its content here.
- Use relative links for local documents and add new guides to their folder index.
- State which repository commands run in. Use placeholders for machine paths and environment values. Never include credentials or temporary team tunnel URLs.
- Label proposals and historical notes; use the active GitHub issue as the source of task status.
- Keep the launch guide as the single source for local startup instructions.
- Before a PR, check links and conflict markers with `python3 scripts/check_docs.py` (Windows: `py scripts/check_docs.py`).

See [moved documents](MOVED.md) for previous filenames.
