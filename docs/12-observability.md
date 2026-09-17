# Observability

## Three pillars

- logs;
- metrics;
- traces.

## Correlation

Every API request and important background job gets a correlation/request ID.

## Metrics

### Ingestion

- fetch count;
- success/failure;
- latency;
- articles/source;
- freshness lag.

### Processing

- queue depth;
- extraction success;
- geocode success;
- clustering merge/new rate;
- dead-letter count.

### API

- request count;
- P50/P95/P99 latency;
- 4xx/5xx;
- cache hit ratio;
- DB query latency.

### Product/data quality

- incorrect merge review rate;
- duplicate event rate;
- incorrect location rate;
- summary correction rate.

## Alerts

Alert on:

- source stale beyond threshold;
- queue backlog;
- error-rate spike;
- DB connection saturation;
- Redis unavailable;
- provider quota failure;
- abnormal API traffic.

## Admin dashboard

Show source health and processing health separately from public UI.
