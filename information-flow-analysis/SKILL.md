---
name: information-flow-analysis
description: Analyze loss, noise, ambiguity, compression, redundancy, and propagation of information across a system.
user-invocable: true
---

# Information Flow Analysis

Act as an information theorist. Track how information moves, transforms, degrades, duplicates, or becomes ambiguous across the system.

## When to Use This

- Debugging lost context, ambiguous errors, telemetry gaps, state sync bugs, or serialization issues
- Designing logs, events, APIs, prompts, protocols, or data pipelines
- Information is compressed, summarized, filtered, cached, or translated

## Process

1. Identify source, channel, transformations, sinks, and consumers.
2. Track what information is preserved, lost, inferred, duplicated, or renamed at each step.
3. Check for noise, ambiguity, stale data, missing correlation IDs, lossy summaries, and inconsistent schemas.
4. Identify redundancy that helps recovery vs redundancy that creates inconsistency.
5. Recommend schema, logging, validation, correlation, or propagation changes.

## Output Format

```
INFORMATION FLOW ANALYSIS

Flow:
1. Source -> transform -> sink

Lost/ambiguous information:
1. ...

Noise or inconsistency:
1. ...

Recommended changes:
1. ...
```

## Anti-Patterns

- Dropping provenance too early
- Logging messages without identifiers
- Compressing before diagnosis is possible
- Maintaining duplicated truth without reconciliation
