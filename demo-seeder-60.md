# Demo database seeding (#60)

The seeder creates two households (`Demo Family` / `DEMO01`, `Single Student` / `STUD02`), four external identity references, eight storage locations, 16 catalogue foods, at least 50 inventory items, and 10 recipes with 30 ingredient mappings. Inventory includes active, consumed and discarded examples and dates relative to the run date: -5, 0, 2, 7 and 30 days. These are UI fixtures, not food-safety recommendations.

## Target safety and setup

Use a dedicated **local PostgreSQL 16** database named with a `_demo` or `_test` suffix, initialized once using `backend/scripts/init_db.sql`. The initialization script is for a clean database only. No automatic schema changes or authentication changes occur during seeding.

The CLI reads only `SEED_DATABASE_URL` from the shell. It does not load `.env` or use `DATABASE_URL`. Remote hosts, non-PostgreSQL targets, unexpected database names, URL query overrides, and PostgreSQL host/service environment overrides are rejected. These safeguards reduce mistakes; a forwarded local port must still point to a disposable database, never production.

From the backend repository with its Python environment active:

macOS:

```sh
export SEED_DATABASE_URL='postgresql://YOUR_LOCAL_USER:YOUR_LOCAL_PASSWORD@127.0.0.1:5432/mealventory_demo'
python -m app.scripts.seed_db --reset --items=50
```

Windows PowerShell:

```powershell
$env:SEED_DATABASE_URL='postgresql://YOUR_LOCAL_USER:YOUR_LOCAL_PASSWORD@127.0.0.1:5432/mealventory_demo'
python -m app.scripts.seed_db --reset --items=50
```

Use the local database's actual port and credentials. `--items` accepts 50–10000 total inventory items across both households.

## Repeat runs and reset

Normal runs insert missing fixture rows using deterministic IDs and leave existing values untouched. They do not advance existing expiry dates. Increasing `--items` adds new inventory fixtures.

`--reset` removes only inventory IDs reserved for this seeder, rebuilds the requested item count, and refreshes fixture values for catalogue foods, locations, recipes, ingredients and seeded memberships. Unrelated inventory—even within demo households—remains. It does not truncate tables or delete households, shopping lists, auth users or unrelated recipes. Concurrent seed runs are serialized; the complete operation is one transaction. A failure rolls everything back. Reserved invite-code collisions abort instead of modifying another household.

## Identities and app sign-in

The current DDL has external user UUIDs, not an auth-user table. The four default identities are fixtures, **not sign-in accounts**. This is an explicit difference from the ticket's request for four auth users. The seeder does not access Supabase Admin APIs, create passwords or bypass authentication.

To use the demo with real sign-in, first create four accounts in your development Supabase project and supply their UUIDs on the first run:

```sh
python -m app.scripts.seed_db --user-ids UUID1 UUID2 UUID3 UUID4
```

The first account owns Demo Family, the next two are members, and the fourth owns Single Student. Use the same mapping on repeat runs. A different existing demo owner mapping is rejected. Configure your local backend to use this demo database and the test Supabase authentication project. Alternatively, an authenticated test user can join `DEMO01` through the normal household API. Changing the backend database is a deliberate developer step; the seeder does not change your app configuration.

Cloud-hosted Supabase databases are intentionally rejected as seed targets. Supporting remote development targets or automatic auth provisioning needs a separately designed workflow.

## Verification

From the backend repository:

```sh
python -m pytest tests/test_seed_db.py -q
RUN_POSTGRES_TESTS=1 python -m pytest tests/test_seed_db_postgres.py -q
```

For PowerShell, set `$env:RUN_POSTGRES_TESTS='1'` before running the second pytest command. Docker must be running and on PATH. PostgreSQL tests create their own disposable container and verify counts, expiry coverage, repeat-run stability, scoped reset, rollback and invite enrollment. They never use the application's configured database.
