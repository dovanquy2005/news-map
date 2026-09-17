# Admin & Operations

## Source monitor

For each source:

- active/inactive;
- last success;
- last failure;
- article count;
- freshness lag.

## Processing monitor

Show queues:

- pending;
- processing;
- success;
- retry;
- dead-letter.

## Review queue

Prioritize:

- low location confidence;
- low clustering confidence;
- conflicting facts;
- suspicious duplicate;
- extraction errors.

## Admin capabilities MVP

- enable/disable source;
- view source health;
- inspect failed jobs;
- inspect event provenance;
- mark event for reprocessing;
- review location/confidence;
- audit admin action.

## Audit log

Record:

```text
actor
action
resource_type
resource_id
result
timestamp
request_id
```

Never store secrets in audit logs.
