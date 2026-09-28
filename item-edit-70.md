# Inventory item editing (#70)

`PATCH /api/v1/items/{item_id}` accepts partial edits from any authenticated member of the selected household. Send a Supabase bearer token and `X-Household-ID`. The UUID must belong to that household; otherwise the response is 404 with `application/problem+json`. Missing authentication returns 401, nonmembership returns 403.

## Editable fields

```json
{
  "name": "Oat milk",
  "category": "Dairy alternative",
  "quantity": 2.125,
  "unit": "litres",
  "expiry_date": "2026-10-10",
  "storage_zone": "fridge",
  "status": "active"
}
```

Every field is optional, but at least one is required. Omitted fields remain unchanged. `expiry_date: null` clears the date. `storage_location_id: null` clears the location; it remains supported for existing clients. Other fields cannot be null. Names, categories and units are trimmed and cannot be blank. Quantity is positive with at most three decimal places. Unknown fields and invalid enum values return 422.

`storage_zone` accepts `pantry`, `fridge`, `freezer`, or `spicerack`. It resolves to a household-specific location named `Default <zone>`, creating it if necessary. Send either `storage_zone` or `storage_location_id`, never both. A conflicting default-location name with a different zone returns 409. Existing items without locations remain valid and return `storage_zone: null`. Create-time defaults and automatic scan-zone assignment belong to #73.

The response remains the updated ItemOut object, with an additional nullable `storage_zone` field. The existing GET zone filter reflects the new location immediately.

## Status and isolation

Active items can remain active or become consumed/discarded in the same atomic edit. Finalized items cannot be edited or reopened. Repeating a status-only PATCH with the same final status succeeds; conflicting changes return 409. The existing consume/discard endpoints still work. Expired is a date-derived condition, not a valid database status.

Correcting name/category creates a separate food record for that inventory item instead of changing the shared catalogue row. Its existing default unit and shelf-life metadata are retained; the original barcode stays on the original catalogue record because it is unique. Other items, household inventories and recipe ingredient references retain their original food record. A subsequent identical label edit creates no duplicate.

PostgreSQL row locks serialize edits against status transitions. Location resolution, food replacement and item updates commit together, or all roll back. No migration is required; existing updated_at triggers continue to run. This change does not wire frontend buttons or modify the legacy `/api/v1/inventory/` routes.

## Testing

From the backend repository:

```sh
python -m pytest tests/ -q
RUN_POSTGRES_TESTS=1 python -m pytest tests/test_household_inventory_postgres.py -q
```

PowerShell: set `$env:RUN_POSTGRES_TESTS='1'` before the second pytest command. PostgreSQL tests require Docker and use a disposable database, never the application's configured database.

For manual Swagger verification, create an item, copy its UUID, and PATCH only `{"expiry_date":"2026-10-10"}`. Confirm name, quantity and location remain unchanged. Then edit its name and storage zone, and GET with `?zone=fridge`. Confirm another household cannot edit the same UUID. Finish by setting `status` to `consumed` and confirming it no longer appears in the default active list.
