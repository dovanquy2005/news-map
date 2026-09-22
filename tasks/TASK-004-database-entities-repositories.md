# TASK-004 — Base Database Entity Models & Repositories

## Status
DONE

## Priority
P0

## Phase
Phase 0 — Foundation

## Depends On
- TASK-003

## Objective
Define the core relational and geospatial database schema models, relationships, spatial indices, constraints, and base repository patterns matching the entity definitions in `docs/04-data-architecture.md` and `prd.md`.

## Source of Truth
- `docs/04-data-architecture.md` (Core entities, Relationships, Required indexes, Geospatial)
- `docs/15-dev-conventions.md` (Naming, IDs, Time)
- `prd.md` (Section 20: Suggested Data Model)
- `adr/002-postgres-postgis.md`

## Scope

### MUST
- Implement database entity models for:
  - `Source`: `id`, `name`, `domain`, `source_type`, `rss_url`, `active`, `priority`, `last_success_at`, `last_error_at`, `created_at`, `updated_at`
  - `Article`: `id`, `source_id`, `url`, `canonical_url`, `title`, `summary_raw`, `content_excerpt`, `published_at`, `updated_at`, `fetched_at`, `content_hash`, `language`, `raw_metadata`
  - `Location`: `id`, `raw_text`, `normalized_text`, `province`, `district`, `ward`, `address`, `latitude`, `longitude`, `provider`, `confidence`, `geom` (PostGIS `GEOMETRY(Point, 4326)`)
  - `Event`: `id`, `title`, `normalized_title`, `category`, `summary`, `latitude`, `longitude`, `location_label`, `location_confidence`, `geom` (PostGIS `GEOMETRY(Point, 4326)`), `occurred_at`, `first_reported_at`, `last_updated_at`, `status`, `confidence_score`, `article_count`, `source_count`, `created_at`, `updated_at`
  - `EventArticle`: `event_id`, `article_id`, `match_score`, `match_reason`, `created_at` (composite primary/unique key)
  - `EventFact`: `id`, `event_id`, `fact_key`, `fact_value`, `fact_confidence`, `supporting_article_count`, `created_at`, `updated_at`
  - `EventTimeline`: `id`, `event_id`, `timestamp`, `timeline_type`, `text`, `source_article_id`, `created_at`
  - `HistoricalSnapshot`: `id`, `event_id`, `captured_at`, `article_count`, `source_count`, `last_seen_at`
  - `ProcessingJob`: `id`, `job_type`, `entity_id`, `status`, `attempt`, `max_attempts`, `error_message`, `scheduled_at`, `created_at`, `updated_at`
- Create database migration script generating tables, primary keys, foreign keys with appropriate cascade rules, and check constraints.
- Create required indices:
  - `articles`: unique on `canonical_url`, index on `content_hash`, index on `published_at`, composite index on `(source_id, published_at)`
  - `events`: index on `occurred_at`, `last_updated_at`, `category`, `status`, and PostGIS GiST spatial index on `geom`
  - `event_articles`: unique `(event_id, article_id)`, index on `event_id`, index on `article_id`
  - `locations`: spatial GiST index on `geom`, index on `province`
  - `historical_snapshots`: index on `(event_id, captured_at)`
  - `processing_jobs`: index on `(job_type, status, scheduled_at)`

### MUST NOT
- Use naive sequential auto-increment integer IDs for public-facing entities (`Event`, `Article`); use UUIDv7 or stable opaque IDs to prevent enumeration.
- Permit unindexed spatial queries on map-related tables.
- Mix article published time with event occurred time in a single timestamp column.

## Architecture Constraints
- Conforms strictly to `docs/04-data-architecture.md` entity and relationship definitions.
- All timestamps must be stored as timezone-aware UTC (`TIMESTAMP WITH TIME ZONE`).

## Implementation Requirements
- Use ORM or query builder (SQLAlchemy / Prisma / SQLModel) with strict type hints.
- Base repository layer providing CRUD helpers with transaction support and soft-delete/status-filter guards where applicable.
- Geometry columns mapped using GeoAlchemy2 / PostGIS geometry primitives SRID 4326 (WGS 84).

## Security Requirements
- Parameterized queries must be enforced across all repository operations; zero raw SQL string concatenation from user inputs.
- Stable opaque UUIDs generated to prevent ID enumeration attacks.

## Performance Requirements
- PostGIS GiST spatial indexing must enable bounding box queries (`ST_MakeEnvelope`) in < 20ms over 50,000 records.
- Foreign keys properly indexed to prevent table scans on joins.

## Testing Requirements
- Database migration integration tests:
  - Migration applies cleanly and creates all tables, foreign keys, and indices.
  - Rollback drops all objects without dangling constraints.
  - Insert, update, and query tests for all core entities verifying relationships (e.g. cascading deletes, composite uniqueness on `EventArticle`).
  - Spatial query test verifying `ST_DWithin` and `ST_Contains` on indexed `geom` column.

## Expected Files / Modules
- `backend/app/common/db/models/`
  - `source.py`
  - `article.py`
  - `location.py`
  - `event.py`
  - `event_article.py`
  - `event_fact.py`
  - `event_timeline.py`
  - `historical_snapshot.py`
  - `processing_job.py`
- `backend/app/common/db/repositories/base.py`
- `backend/migrations/versions/0002_core_entity_schema.py`
- `tests/integration/test_entity_schema.py`

## Acceptance Criteria
- [x] All 9 core entities from `docs/04-data-architecture.md` are defined with typed models and migrations.
- [x] Unique constraints and indexes (especially GiST on `geom`) are verified in the database schema.
- [x] Database test verifies creating an event with attached articles, facts, and timeline items in a single transaction.
- [x] All timestamps use `TIMESTAMPTZ` and default to UTC.

## Completion Report
When completed, report:
1. List of entity models created.
2. Migration version generated and applied.
3. List of created indexes and constraints.
4. Test results for schema validation and spatial querying.

## Follow-up Tasks
- TASK-006 (Backend Modular Monolith Foundation)
- TASK-013 (Source Management Domain)
- TASK-017 (Article Normalization Domain)
- TASK-028 (Clustering Worker & Provenance)
- TASK-042 (Historical Snapshot Worker)
