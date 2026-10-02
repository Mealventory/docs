# Mealventory documentation

Team guides for running, testing and maintaining Mealventory. Application code lives in the [frontend](https://github.com/Mealventory/frontend), [backend](https://github.com/Mealventory/backend) and [AI services](https://github.com/Mealventory/ai-services) repositories.

## Start here

1. [Launch the app on Mac or Windows](getting-started/starting-the-project.md).
2. [Connect authentication and households](getting-started/live-households.md).
3. [Test account flows](getting-started/auth-testing.md).
4. [Verify shared inventory on two phones](features/shared-inventory.md).

## Guides by topic

| Folder | Contents |
| --- | --- |
| [Getting started](getting-started/README.md) | Startup, networking and account checks |
| [Features](features/README.md) | Household, pantry, scanner, expiry, recipes and shopping |
| [API](api/README.md) | Authentication and the retained OpenAPI snapshot |
| [Database](database/README.md) | Initial schema and row-level security |
| [Operations](operations/README.md) | Containers, CORS, demo data and AI failures |
| [Architecture](architecture/README.md) | Authentication session storage |
| [Archive](archive/README.md) | Historical proposals and superseded task lists |

The archive preserves context; it is not the current backlog. Check the relevant GitHub issue and assignee before taking a task. A feature guide may record tests from its implementation, not a guarantee that a deployed environment has been verified.

## Maintaining these docs

- Update the existing topic guide instead of appending another section to this index.
- Use relative links and add new guides to their folder index.
- State which code repository commands run in. Use placeholders for machine paths and environment values. Never include credentials or temporary team tunnel URLs.
- Separate implemented behaviour from proposals, and identify the repository when citing issue numbers.
- Keep the launch guide as the single source for startup instructions.
- Before a PR, check links and conflict markers with `python3 scripts/check_docs.py` (Windows: `py scripts/check_docs.py`).

See [moved documents](MOVED.md) for previous filenames.
