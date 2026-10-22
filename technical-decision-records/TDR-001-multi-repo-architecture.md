# TDR-001: Multi-Repository Architecture (DOCS-02)

- **Status**: Accepted
- **Deciders**: Mealventory Architecture Team
- **Date**: 2026-10-15
- **Technical Domain**: Repository Organization & Source Control

---

## 1. Context & Problem Statement

Mealventory consists of diverse technical domains with distinct toolchains and operational cadences:
1. **Frontend**: React Native 0.74, Expo SDK 51, TypeScript, npm, iOS/Android native compilation.
2. **Backend**: FastAPI (Python 3.11), SQLAlchemy 2.0 Async, Alembic migrations, PostgreSQL database.
3. **AI Services**: Computer Vision, Google Cloud Vision SDK, TensorFlow MobileNetV2, Pillow image processing.
4. **Documentation & Architecture**: Centralized blueprints, contracts, and evaluation runbooks.

The team required a source control strategy that maximized independent feature velocity, prevented dependency pollution (e.g., Python ML packages conflicting with web/node dependencies), and enabled granular permissions and CI runners.

---

## 2. Decision Drivers

- **Heterogeneous Toolchains**: Node/npm vs Python virtual environments vs C++ native vision dependencies.
- **CI/CD Independence**: Building the mobile client with EAS must not trigger heavy AI container test runs or migration checks.
- **Team Specialization**: Separate engineers specialize in mobile UI/UX, database migrations, and vision algorithms.
- **Release Cadence**: Backend and AI microservices can be updated continuously without requiring App Store reviews.

---

## 3. Decision

We chose a **Multi-Repository Architecture** partitioned across four distinct GitHub repositories under the `Mealventory` organization:
- `Mealventory/frontend`
- `Mealventory/backend`
- `Mealventory/ai-services`
- `Mealventory/docs`

Inter-service contracts are defined through versioned OpenAPI specifications (`contracts/openapi.json`), enforced via automated schema validation in PR workflows.

---

## 4. Alternatives Considered

### Alternative A: Unified Monorepo (Turborepo or Nx)
- **Evaluation**: Would allow single atomic commits spanning client and server.
- **Rejection Rationale**: Monorepo tooling for mixed Node.js and Python ecosystems is immature and complex. CI run times would inflate significantly, and heavy machine learning dependencies (TensorFlow, PyTorch) would bloat developer clone times and IDE indexing on mobile workstations.

### Alternative B: Git Submodules
- **Evaluation**: Nesting repositories within a root container repository.
- **Rejection Rationale**: Git submodules introduce detached HEAD traps, complex merge conflict resolution, and synchronization friction across team members.

---

## 5. Consequences & Tradeoffs

### Positive Consequences
- **Clean Dependency Isolation**: Node modules, backend libraries, and heavy computer vision wheels never conflict.
- **Fast, Scoped CI**: Each repository has isolated GitHub Actions workflows executing in < 1 minute.
- **Granular Git Access**: Security tokens and deployment credentials are compartmentalized.

### Negative Consequences & Mitigation
- **Coordinated Releases**: Full-stack changes require synchronized branches across repositories.
  - *Mitigation*: Versioned OpenAPI contracts and cross-repo startup runbooks ([operations/README.md](../operations/README.md)).
- **Duplicate Types**: Shared TypeScript and Pydantic types could drift.
  - *Mitigation*: Automated contract tests (`test_scan_contract.py`) ensuring zero schema drift.
