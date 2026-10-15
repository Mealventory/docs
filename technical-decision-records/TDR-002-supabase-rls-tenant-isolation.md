# TDR-002: Supabase PostgreSQL Row-Level Security (RLS) Tenant Isolation (DOCS-02)

- **Status**: Accepted
- **Deciders**: Mealventory Architecture Team
- **Date**: 2026-10-15
- **Technical Domain**: Data Security & Multi-Tenancy

---

## 1. Context & Problem Statement

Mealventory is designed around **shared household pantries**. Multiple users (roommates, family members) belong to a household, but must never view, modify, or delete another household's grocery inventory, shopping lists, or private receipts.

We needed an architectural pattern to enforce strict multi-tenant isolation that guarantees zero cross-tenant data leakage, even if an application endpoint omits a query filter.

---

## 2. Decision Drivers

- **Zero-Trust Defense-in-Depth**: Application code errors (e.g., forgetting `WHERE household_id = X`) must not result in security incidents.
- **Auditable Security**: Tenant boundaries should be inspectable and verifiable directly in the database engine.
- **Compatibility with Direct Client Queries**: Future direct mobile Supabase subscriptions (e.g., real-time shopping list updates) must be secure by default.

---

## 3. Decision

We adopted **PostgreSQL Row-Level Security (RLS)** as the authoritative boundary for tenant isolation.

Every table containing tenant-scoped data (`inventory_items`, `households`, `household_members`, `recipes`, `shopping_list_items`) enables RLS:
```sql
ALTER TABLE inventory_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access items belonging to their households"
ON inventory_items
FOR ALL
USING (
  household_id IN (
    SELECT hm.household_id
    FROM household_members hm
    WHERE hm.user_id = auth.uid()
  )
);
```

The FastAPI backend executes requests within the user's authenticated context using Supabase JWT tokens, ensuring database-level enforcement.

---

## 4. Alternatives Considered

### Alternative A: Application-Only Filtering (`WHERE household_id = :id`)
- **Evaluation**: Relying entirely on FastAPI repository methods and ORM queries to filter records by `household_id`.
- **Rejection Rationale**: Human error risk. In a multi-developer team, a single overlooked query in an inventory join or search endpoint could leak private grocery and location data across households.

### Alternative B: Separate Database Schema per Household
- **Evaluation**: Creating dynamic PostgreSQL schemas (`household_abc123.inventory_items`).
- **Rejection Rationale**: Extreme migration complexity. Running Alembic migrations across thousands of dynamic schemas introduces connection pool bloat and maintenance overhead.

---

## 5. Consequences & Tradeoffs

### Positive Consequences
- **Absolute Boundary Guarantee**: Accidental omission of `WHERE` clauses in application queries still returns only the caller's household data.
- **Real-Time Readiness**: Supabase Realtime WebSocket subscriptions inherit RLS policies automatically.
- **Clear Audit Trail**: Security evaluators can verify multi-tenant isolation from SQL DDL alone.

### Negative Consequences & Mitigation
- **Query Overhead**: Recursive subqueries evaluating `household_members` can impact performance on large queries.
  - *Mitigation*: Compound indexes on `household_members(user_id, household_id)` and `inventory_items(household_id, status)`.
- **Bypass for Background Cron Jobs**: Daily expiry push notification jobs require reading across all households.
  - *Mitigation*: Dedicated service role database connections with explicit `SECURITY DEFINER` procedures used exclusively by trusted background tasks.
