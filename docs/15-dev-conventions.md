# Development Conventions

## Naming

Use domain names consistently:

- `article` means article source item;
- `event` means clustered real-world event;
- `location` means resolved geospatial entity;
- `source` means publisher/source configuration.

Do not call article `news` in code when ambiguity matters.

## IDs

Use stable opaque IDs for public resources.

Do not expose sequential database IDs if they facilitate enumeration of sensitive/admin resources.

## Time

Persist timestamps with timezone awareness. Prefer UTC in storage; convert to Vietnam time in presentation.

## Errors

Use machine-readable error codes plus human-readable messages.

Example:

```json
{
  "error": {
    "code": "INVALID_BBOX",
    "message": "The requested map bounds are invalid."
  }
}
```

## Configuration

Configuration is environment-specific, not hard-coded.

Examples:

```text
DATABASE_URL
REDIS_URL
MAPS_BROWSER_KEY
MAPS_SERVER_KEY
LLM_API_KEY
RATE_LIMIT_*
```

## Git

Commit messages should communicate intent.

Avoid mixing:

- refactor;
- feature;
- formatting;
- dependency upgrades

in one unrelated commit.
