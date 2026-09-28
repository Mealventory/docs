# Consumed and discarded inventory (#72)

## Behavior

POST /api/v1/items/{id}/consume and /discard transition an active item to consumed or discarded. The entire quantity is finalized. Rows remain in PostgreSQL for history; the updated_at trigger records the change. Rejected transitions do not alter timestamps.

Both endpoints require bearer authentication and X-Household-ID. Nonmembers get 403; missing or other-household items get 404. Any already-finalized item returns 400 with detail "Item is not active", including a repeat of the same action. This replaces the previous idempotent 200 / conflicting 409 behavior for these two POST endpoints. PATCH behavior is unchanged.

GET /api/v1/items defaults to active. Use ?status=consumed or ?status=discarded for history. Existing hard-delete remains a separate action.

The issue title mentions expired, but its scope and existing database enum define only active, consumed and discarded. Expiry dates remain a separate property; no automatic expiry transition or analytics endpoint is introduced.

## App

Both item-detail screens offer Mark as consumed and Mark as discarded. Actions are disabled while saving. Successful actions remove the item from the active view; failures remain visible. The existing foreground five-second refresh and app-resume refresh propagate changes to other phones. This is polling, not realtime subscriptions.

Demo mode changes only local sample state.

## Manual verification

1. Start the backend and Expo with these changes.
2. On phone A, open an item and choose Mark as consumed.
3. On phone B in the same household, refresh or wait for the foreground poll; the item should leave active inventory.
4. In Swagger, GET /api/v1/items?status=consumed must include the same ID.
5. Repeat with discard and ?status=discarded.
6. Repeat either POST against a finalized item: expect 400 and no timestamp change.
7. Disconnect the backend and attempt an action: an error should appear without pretending the item was saved.

Physical phone verification remains outstanding. Automated coverage includes tenant isolation, history visibility across sessions, concurrent conflicting transitions, timestamp behavior, authenticated frontend requests and error handling.

## Branch dependencies

Backend feat/item-status-72 builds on feat/storage-zones-73.
Frontend feat/item-status-72 and docs/item-status-72 also retain the previously uncommitted #73 changes. Review/publish those together or separate the commits before opening PRs.
