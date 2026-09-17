# Issue #71: shared shopping list API

The backend persists shopping items in the existing `shopping_list_items` table. All household members can use these endpoints. Requests require a Supabase bearer access token and `X-Household-ID` containing the selected household UUID. The household and membership are verified server-side; payloads cannot supply ownership.

| Method | Path | Response |
| --- | --- | --- |
| GET | `/api/v1/shopping` | 200, all unchecked and checked items |
| POST | `/api/v1/shopping` | 201, created item |
| PATCH | `/api/v1/shopping/{item_id}` | 200, updated item |
| DELETE | `/api/v1/shopping/{item_id}` | 204, empty body |
| POST | `/api/v1/shopping/clear-checked` | 200, `{"deleted_count": 2}` |

## Create and edit

Create example:

```json
{"name":"Milk","quantity":2,"unit":"bottles"}
```

`food_id` is an optional UUID referencing the shared food catalogue. Omit it for free-text items. New items start unchecked. Names and units are trimmed; blank values are rejected. Quantity must be positive and fit numeric(12,3). Defaults are quantity 1 and unit `units`.

Patch example:

```json
{"checked":true,"quantity":3,"unit":"bottles"}
```

The only editable fields are `checked`, `quantity`, and `unit`. At least one must be supplied; nulls and unknown fields are rejected with 422. Omitted fields remain unchanged. Send an explicit boolean, not a toggle instruction, so repeating a check/uncheck request keeps the same state.

Responses contain `id`, `household_id`, nullable `food_id`, `name`, `quantity`, `unit`, `checked`, `created_at`, and `updated_at`. Quantities serialize as decimal strings. List results put unchecked items first, then order by creation time and ID.

A request without authentication returns 401; missing or malformed household context returns 400; a nonmember receives 403. Unknown items and items from another household return 404. An unknown food ID returns 404; a food/household reference that disappears during creation returns 409. Delete and clear operations permanently remove the selected shopping rows. Clearing checked items is scoped to the selected household and returns zero when no checked items remain.

## Schema and rollout

No migration is required. The checked state maps to the actual DDL column `is_checked`. Issue #71's description mentions `checked` and `added_by` database columns, but the checked-in DDL has `is_checked` and no `added_by`. This implementation follows that DDL and does not invent an attribution column or return a fabricated creator. PostgreSQL retains the existing foreign keys and updated_at trigger.

Restart the backend after pulling the feature. The shopping tab must be wired to these endpoints separately (frontend #10). Refresh or refetch after writes and when returning to the screen; other phones see committed changes on their next fetch. This issue does not add push updates, automatic replenishment, or moving purchased items into inventory.

## Verification

From the backend repository with development dependencies installed:

```sh
python -m pytest tests/ -q
RUN_POSTGRES_TESTS=1 python -m pytest tests/test_shopping_postgres.py -q
```

The PostgreSQL test requires Docker and creates a disposable PostgreSQL 16 database, never the application's configured database. Tests cover member CRUD, household isolation, checked-state updates, clear-checked isolation, validation, authentication, optional food links, persistence across sessions, and timestamp updates.

For manual testing in Swagger, authorize with your Supabase access token, use the same household UUID for each request, create Milk, patch `checked` to true, and call clear-checked. GET should then omit Milk. A second household's items must remain unchanged.
