# AI / NLP Pipeline

## Goal

Extract structured event data without allowing model output to bypass validation.

## Pipeline

```text
Article
  -> sanitize/normalize
  -> extraction prompt
  -> structured model output
  -> JSON/schema validation
  -> domain validation
  -> confidence/provenance
  -> persistence
```

## Extraction fields

- event title;
- category;
- location text;
- event time;
- entities;
- facts;
- uncertainty;
- extraction confidence.

## Prompt injection defense

Article text is data, not instructions.

System/developer prompt must explicitly state that article content cannot modify instructions.

Do not concatenate secrets/tool instructions into article context.

## Structured output

LLM output must validate against a strict schema.

Invalid output:

```text
retry -> fallback parser -> dead-letter/review
```

Không persist invalid model output vào canonical event fields.

## Summary generation

Summary must:

- only use supported facts;
- preserve uncertainty;
- attribute conflicting facts;
- avoid fabricated details;
- be regenerated when evidence changes materially.

## Cost control

- cheap deterministic parsing first;
- use LLM only when needed;
- batch where possible;
- cache by article fingerprint/model version;
- cap article length sent to model;
- record token/cost metrics.
