# Mealventory Platform Documentation: Target Final State & Purpose

## 1. Purpose of the Repository
The `docs` repository serves as the centralized **Single Source of Truth (SSOT)** and enterprise architectural repository for the **Mealventory** ecosystem. While implementation code is distributed across the multi-repo landscape (`frontend`, `backend`, `ai-services`), this repository provides living documentation, system blueprints, database schema specifications, security protocols, API contracts, and Technical Decision Records (TDRs).

### Key Audiences & Objectives:
- **Engineers & Contributors**: Frictionless local setup, onboarding guides, multi-repo synchronization instructions, and contribution guidelines.
- **System Architects & Security Auditors**: High-fidelity architectural diagrams, threat models (OWASP Mobile & API Top 10), and Row Level Security (RLS) data isolation verification matrices.
- **DevOps & Infrastructure**: Deployment runbooks, CI/CD configuration guidelines, secrets management policies, and database migration checklists.
- **Capstone Evaluators & Technical Interviewers**: Rigorous academic and enterprise documentation demonstrating end-to-end technical excellence and architectural rationale.

---

## 2. Repository Structure & Living Documentation Matrix

```
docs/
├── architecture/
│   ├── c4_system_context.md          # Level 1: System Context Diagram & Actors
│   ├── c4_containers.md              # Level 2: Multi-repo Container Architecture (Expo, FastAPI, Gemini, Postgres)
│   ├── c4_components_backend.md      # Level 3: Backend Clean Architecture Component Map
│   └── data_flow_lifecycles.md       # Sequence diagrams: Receipt Scan -> AI Review -> Pantry Sync
│
├── database/
│   ├── erd_diagram.md                # Entity Relationship Diagram (Mermaid & DBML)
│   ├── ddl_reference.sql             # Full reference PostgreSQL DDL with indices & triggers
│   └── rls_security_matrix.md        # Supabase RLS policies & tenant isolation proof
│
├── api-contracts/
│   ├── core_backend_openapi.json     # Frozen OpenAPI 3.1 contract for core backend
│   ├── ai_service_contract.json      # Inter-service REST contract between Backend & AI
│   └── error_codes_dictionary.md     # Standardized RFC 7807 error codes across services
│
├── mobile/
│   ├── expo_router_navigation_map.md # Complete Expo Router v3 screen and modal hierarchy
│   ├── atomic_design_catalog.md      # Specification of Atoms, Molecules, and Organisms
│   └── offline_sync_strategy.md      # TanStack Query v5 + MMKV cache persistence guide
│
├── technical-decision-records/        # Architectural Decision Records (ADRs / TDRs)
│   ├── TDR-001-multi-repo-architecture.md
│   ├── TDR-002-supabase-rls-tenant-isolation.md
│   ├── TDR-003-tanstack-query-mmkv-offline.md
│   ├── TDR-004-gemini-structured-vision-vs-yolo.md
│   └── TDR-005-expo-push-notification-relay.md
│
├── devops-and-runbooks/
│   ├── local_development_setup.md    # One-command docker compose and local environment setup
│   ├── secrets_management_policy.md  # Rules for Doppler, GitHub Secrets, and zero-key commits
│   └── app_store_deployment_guide.md # Fastlane, EAS, and Google Play / App Store submission
│
├── FINAL_STATE.md                    # Target repository state & purpose (this document)
└── README.md                         # Public repository landing page and sitemap
```

---

## 3. Core Architectural Artifacts Maintained Here

### A. The C4 Architecture Blueprint
Maps how the React Native client interacts through the API gateway to the Core FastAPI backend, which enforces Row Level Security over PostgreSQL and asynchronously delegates multimodal vision tasks to the AI microservice.

### B. The Supabase RLS Verification Matrix
Maintains the mathematical and test-backed proof that tenant isolation cannot be compromised even if an application bug omitted a `WHERE household_id = ...` clause.

### C. Technical Decision Records (TDRs)
Living records establishing why key decisions were made (e.g., choosing `react-native-mmkv` over SQLite for synchronous sub-millisecond cache access, and adopting Google Gemini 1.5 Flash structured outputs over fragile regex-parsed OCR engines).

## Current inventory API documentation

- [Issue #44: household inventory updates](inventory-44.md) — editing, consumption, discard, filters, and batch operations.
- [Backend OpenAPI snapshot](openapi.json) — generated API reference.

## Shopping list API

- [Shared shopping list API (#71)](shopping-list-71.md) — household CRUD, check/uncheck, and clearing purchased items.

## Backend container runtime

- [Docker setup and health probes (#48)](backend-docker-48.md) — build, runtime configuration, and troubleshooting.

## AI scan reliability

- [AI timeout and recovery behavior (#47)](ai-resilience-47.md).

## Browser access configuration

- [CORS origins (#74)](cors-origins-74.md) — Expo web, tunnels, and production origin lists.

## Demo data

- [Local demo database seeding (#60)](demo-seeder-60.md).

## Inventory item editing

- [Complete partial item updates (#70)](item-edit-70.md).
<<<<<<< Updated upstream
=======

## Storage zones

- [Creation defaults, filtering and scan suggestions (#73)](storage-zones-73.md).

## Inventory status

- [Consumed/discarded actions and history (#72)](item-status-72.md).

## Launching the app

- [Starting Mealventory — Mac and Windows](starting-the-project.md).
>>>>>>> Stashed changes
