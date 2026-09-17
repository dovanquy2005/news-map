# API Contracts

## Public read API

Base:

```text
/api/v1
```

## GET /events

Query:

```text
from
-to
province
category
status
minSources
minArticles
bbox
page
limit
```

Required server-side limits:

- maximum date window unless privileged;
- maximum bbox area;
- maximum page size;
- validated enum fields.

## GET /events/{eventId}

Returns:

```text
id
title
category
summary
location
occurredAt
firstReportedAt
lastUpdatedAt
status
confidence
sources
timeline
relatedEvents
```

## GET /events/search

Full-text event search with pagination and filters.

## Admin APIs

Keep admin endpoints under a separate namespace:

```text
/api/v1/admin/*
```

Require authentication + authorization.

## Response rules

- consistent error schema;
- no stack traces;
- no secrets/internal provider credentials;
- timestamps ISO 8601;
- stable IDs;
- pagination metadata.

## Caching

Public GET endpoints may use CDN/Redis cache where response semantics allow.

Cache key must include all relevant filter parameters.

## Versioning

Breaking changes require API version change or compatibility layer.
