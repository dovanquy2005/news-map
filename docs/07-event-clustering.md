# Event Clustering

## Objective

Decide whether an article belongs to an existing event or starts a new event.

## Candidate retrieval

Do not compare every article with every event.

Retrieve candidates by:

- temporal window;
- spatial proximity;
- category;
- entity overlap;
- text/embedding similarity.

## Scoring signals

```text
location_similarity
+ time_similarity
+ semantic_similarity
+ entity_overlap
+ fact_overlap
+ category_match
```

Weights are configurable.

## Decision policy

```text
score >= merge_threshold
    -> attach article

score <= new_event_threshold
    -> create event

middle range
    -> review/uncertain state
```

## Safety principle

False merge is more damaging than a temporary duplicate.

Never merge only because two articles mention the same province or street.

## Provenance

Every `event_article` link must retain:

- match score;
- match reason/version;
- timestamp.

## Re-clustering

Support reprocessing when:

- clustering algorithm version changes;
- an event is manually corrected;
- location/time extraction is corrected.
