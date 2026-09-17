# ADR-002: PostgreSQL + PostGIS as Primary Data Store

Status: Accepted

## Context

The product requires relational provenance, event/article relationships, filtering, timestamps and geospatial queries.

## Decision

Use PostgreSQL as primary database and PostGIS for spatial operations. Use pgvector only if semantic similarity needs database-native vector search.

## Consequences

- strong relational consistency;
- mature indexing/querying;
- spatial filtering without introducing a separate spatial database;
- operational simplicity for MVP.
