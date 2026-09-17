# Backend Architecture

## Style

Modular monolith, module boundaries rõ ràng.

```text
backend/
  app/
    api/
    modules/
      sources/
      articles/
      events/
      locations/
      clustering/
      search/
      analytics/
      admin/
    common/
      auth/
      errors/
      logging/
      security/
      db/
      cache/
      queue/
  workers/
    ingestion/
    extraction/
    geocoding/
    clustering/
    summarization/
```

## Module ownership

### sources
Quản lý source config, health, enable/disable.

### articles
Ingestion, canonicalization, dedup, provenance.

### events
Event lifecycle, summaries, source links, timeline.

### locations
Location normalization, geocoding, confidence.

### clustering
Candidate retrieval, similarity, same-event decision.

### search
Full-text + geo filters.

### analytics
Historical snapshots, metrics, future trend inputs.

### admin
Source monitor, processing monitor, review queue.

## Layering

```text
API/Controller
   -> Application Service
      -> Domain rules
         -> Repository / external adapter
```

Không để controller chứa business logic nặng.

## Transaction rules

- DB transaction chỉ bao quanh state change cần atomic.
- Không giữ transaction trong lúc gọi external API/LLM.
- Job phải idempotent.

## Idempotency

Một source item hoặc job có thể chạy lại mà không tạo duplicate.

Dùng deterministic keys như:

- canonical_url hash;
- source_id + external_id;
- content fingerprint;
- job idempotency key.

## Error handling

Phân loại:

- validation error;
- authentication/authorization error;
- resource not found;
- rate limit;
- external provider failure;
- internal failure.

API không trả stack trace production.
