# Performance & Scalability

## Core principle

Scale by removing expensive work from synchronous requests.

## Read path

```text
Browser
  -> CDN/cache
  -> API
  -> Redis
  -> PostgreSQL/PostGIS
```

## Write/processing path

```text
Source
  -> queue
  -> worker
  -> DB
```

## Public map query

Do not return every event in Vietnam.

Use:

- bbox/viewport;
- time window;
- category;
- max result count;
- clustering.

## Database performance

- spatial indexes;
- indexes matching public filter combinations;
- EXPLAIN ANALYZE for expensive queries;
- avoid SELECT *;
- pagination/cursor where suitable;
- batch writes in workers.

## Cache

Cache:

- popular map viewport responses;
- static source metadata;
- event detail when safe.

Do not cache user-specific/admin-sensitive data in shared public cache.

## Worker scaling

Scale workers independently by queue depth:

```text
ingestion queue
extraction queue
geocoding queue
clustering queue
summary queue
```

A slow LLM provider must not stop ingestion of raw articles.

## Backpressure

When external provider quota is exhausted:

- slow queue consumption;
- retry later;
- preserve raw article;
- do not drop source data unnecessarily.

## Performance targets

Use PRD targets as initial budgets:

- initial map render target < 3s under normal network;
- cached/indexed event API P95 target < 800ms;
- search P95 target < 1s.

Treat them as benchmark goals, not guarantees.

## Capacity tests

Load-test at least:

- map pan/zoom;
- concurrent event detail;
- search spikes;
- ingestion bursts;
- worker backlog.

Measure P50/P95/P99, error rate and queue lag.
