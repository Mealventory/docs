# Storage zones (#73)

New household items support `storage_zone`: `pantry`, `fridge`, `freezer`, or `spicerack`.

## API

Send a bearer token and `X-Household-ID` to all inventory endpoints.

```json
{"name":"Milk","category":"Dairy","quantity":1,"unit":"bottle","storage_zone":"fridge"}
```

- POST /api/v1/items and POST /api/v1/items/batch accept the zone. Omission defaults to pantry, regardless of category.
- A supplied storage_location_id takes precedence over the implicit pantry default. It must belong to the selected household; otherwise 404.
- Explicit zone plus non-null location is ambiguous and returns 422.
- Locations named Default pantry/fridge/freezer/spicerack are created within the item transaction and reused, including concurrent requests. A conflicting existing location name with a different zone returns 409.
- GET /api/v1/items?zone=fridge filters by the actual location's zone.
- PATCH /api/v1/items/{id} accepts storage_zone to move an active item.
- Item responses include storage_location_id and storage_zone.
- Invalid zone values return 400 (changed from the earlier 422 enum validation response). Other schema validation remains 422. PATCH null zone remains 422; null location can clear the location.
- Existing unlocated items remain readable with null zone, and are excluded from zone-specific lists. No backfill or migration is required.
- Batch failures roll back both new items and automatically created locations.

Storage location CRUD is optional in this issue and is not added.

## Frontend

Manual entry has a zone selector, initially pantry. Both sample scan review flows pass the selected zone through household inventory and retain it when loading responses.

Scan suggestions use category defaults: dairy/meat/seafood → fridge, frozen/frozen foods → freezer, spices → spicerack, unknown/other → pantry. Users can override the suggestion before saving. Save failures remain visible rather than navigating away as if successful.

Live scanning is documented in the [scanner guide](scanner-recognition.md). The separate legacy per-user scan persistence API is not the household review flow.

## Verification

- Backend suite: 195 passed; 68 optional tests skipped.
- Disposable PostgreSQL 16 inventory tests: 4 passed, including concurrent creates sharing a location.
- Frontend tests: 19 passed; TypeScript check passed.
- Physical phone testing still required.

Manual check:
1. Restart the backend and Expo with these branches.
2. Add an item through Manual Entry with freezer selected.
3. Refresh the household on another phone; verify the item's saved storageZone or query GET /api/v1/items?zone=freezer in Swagger.
4. Open sample scan review, override its suggested zone, and save. Confirm the returned item retains that zone.
5. Verify old items with no location still load.
