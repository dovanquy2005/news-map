# ADR-001: Use Modular Monolith + Async Workers for MVP

Status: Accepted

## Context

The product has distinct pipelines but the initial scale and team size do not justify the operational cost of microservices.

## Decision

Use one backend application with strong module boundaries plus asynchronous workers for ingestion, NLP, geocoding, clustering and summarization.

## Consequences

Positive:

- easier local development;
- easier debugging;
- fewer network hops;
- simpler deployments;
- workers can scale independently.

Negative:

- some modules share runtime/database;
- later extraction into services may require interface cleanup.

## Exit criteria for service extraction

Create a new service only when there is measured evidence of:

- sustained resource bottleneck;
- independent scaling requirement;
- failure isolation requirement;
- independent deployment requirement.
