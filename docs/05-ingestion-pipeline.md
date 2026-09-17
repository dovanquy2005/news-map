# News Ingestion Pipeline

## Pipeline

```text
Source Scheduler
   -> Source Adapter
   -> Fetch
   -> Normalize
   -> Validate
   -> Deduplicate
   -> Store Article
   -> Queue Extraction
```

## Source adapter contract

Every adapter must expose:

```text
fetch()
normalize()
health()
```

Adapter failures must be isolated per source.

## Fetch policy

- respect source terms/robots and applicable API policies;
- bounded timeout;
- retry with exponential backoff;
- jitter;
- circuit breaker after repeated failures;
- concurrency cap per domain/source.

## Never

- bypass anti-bot/access controls;
- crawl arbitrary user-provided URLs;
- allow SSRF via source URL configuration;
- hammer a source on retry.

## Article normalization

Normalize:

- canonical URL;
- timestamps/timezone;
- title whitespace;
- language;
- source identifier.

## Dedup

Order:

1. exact canonical URL;
2. content hash;
3. normalized title/time heuristic;
4. semantic similarity only when needed.

## Queue semantics

Jobs must contain:

```text
job_id
job_type
entity_id
attempt
created_at
scheduled_at
```

Jobs are retryable and idempotent.
