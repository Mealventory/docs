# TDR-003: TanStack Query & MMKV for Offline-Resilient State (DOCS-02)

- **Status**: Accepted
- **Deciders**: Mealventory Frontend Architecture Team
- **Date**: 2026-10-15
- **Technical Domain**: Mobile Client State Management & Offline Caching

---

## 1. Context & Problem Statement

Users frequently check their pantry inventory and shopping lists inside supermarkets or basement parking garages where mobile network connectivity is degraded or nonexistent.

The mobile client required a caching and persistence strategy that:
1. Displays instant pantry inventory on app launch without waiting for network round-trips.
2. Supports smooth optimistic updates when editing or checking items.
3. Operates efficiently without the maintenance burden of client-side relational schema migrations.

---

## 2. Decision Drivers

- **Zero-Latency App Launches**: Render cached pantry dashboard in < 50ms from local storage.
- **Developer Simplicity**: Minimize state management boilerplate (avoid redundant action/reducer code).
- **Network Resilience**: Automatic background revalidation and exponential backoff retry.
- **Lightweight Native Footprint**: High performance on both iOS and Android.

---

## 3. Decision

We chose **TanStack Query v5** paired with **React Native MMKV** as the storage persister.

TanStack Query manages server state lifecycle (fetching, caching, invalidation, optimistic updates), while MMKV provides ultra-fast synchronous key-value serialization to native mobile storage.

In Expo Go or Web environments, the persister gracefully falls back to memory storage.

---

## 4. Alternatives Considered

### Alternative A: Full Offline SQLite Sync (WatermelonDB / expo-sqlite)
- **Evaluation**: Maintaining a full local relational replica of the PostgreSQL database on each phone.
- **Rejection Rationale**: Overkill for Mealventory's current scope. Dual-schema maintenance (Alembic on backend + SQLite migrations on mobile), complex multi-master sync engines, and conflict-resolution algorithms (CRDTs) would add immense maintenance burden with high risk of desynchronization bugs.

### Alternative B: Redux Toolkit + Redux-Persist + AsyncStorage
- **Evaluation**: Classic React Native global store with asynchronous storage.
- **Rejection Rationale**: `AsyncStorage` is bridge-based, slow, and asynchronous, causing visible layout shifts during splash screen hydration. Redux requires significant manual boilerplate for cache invalidation, polling, and deduplication that TanStack Query handles out of the box.

---

## 5. Consequences & Tradeoffs

### Positive Consequences
- **Instantaneous UI Hydration**: Synchronous MMKV reads allow the app to render the complete pantry dashboard before the splash screen hides.
- **Automated Stale-While-Revalidate**: Queries seamlessly refresh in the background when connectivity resumes.
- **Optimistic Updates**: Modifying item quantities or checking shopping list items reflects immediately in the UI.

### Negative Consequences & Mitigation
- **Read-Only Offline Scope**: While existing inventory is fully viewable and searchable offline, creating new items or scanning receipts requires active connectivity.
  - *Mitigation*: The UI clearly indicates offline status and preserves uncommitted scan drafts in memory. Full write queuing is deferred to future roadmap releases.
