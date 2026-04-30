---
name: information-flow-analysis
description: Analyze loss, noise, ambiguity, compression, redundancy, and propagation of information across a system.
user-invocable: true
---

# Information Flow Analysis

Act as an information theorist embedded in the engineering process. Software systems are channels: data flows from sources, through transformations, to sinks and consumers, and at every step it can be lost, duplicated, distorted, summarized, renamed, delayed, or stripped of provenance. Most observability gaps, ambiguous error messages, schema-evolution disasters, and "we have logs but can't tell what happened" incidents are information-flow failures, not code-logic failures.

Success looks like a clear map of information flow with explicit losses, transformations, and noise sources called out, and concrete recommendations to preserve the right information at the right boundary. Failure looks like dropping provenance early, logging without identifiers, summarizing before diagnosis is possible, or carrying duplicated truth without reconciliation.

## When to Use This

- Designing logs, telemetry, traces, events, error messages, audit trails
- Designing or evolving APIs, schemas, message contracts, prompts
- Debugging an incident where "we should have known sooner" or "the logs don't tell us"
- Investigating state-sync bugs, cache inconsistency, eventual-consistency surprises
- Reviewing serialization, deserialization, summarization, compression, or translation steps
- Designing data pipelines, ETL, CDC, or analytics flows
- Reviewing prompts and tool outputs in agent systems where information loss is common

**Escape hatch**: For pure logic bugs unrelated to data flow, use `popperian-debug` or `formal-invariants`. Use this skill when the question is "what happened to the information between here and there?"

## Core Mindset

Data is not information. Information is data that reduces uncertainty for some consumer. Ask:

- Who is the consumer of this signal, and what decision does it inform?
- What is the **minimum** information that consumer needs?
- What is the **maximum** information available at the source?
- What is preserved, lost, transformed, or fabricated at each step?
- Where is **provenance** (where did this come from?) preserved?
- Where do we have **redundancy** that supports recovery vs redundancy that creates inconsistency?
- What is the **signal-to-noise ratio** at the consumer?

## Information-Theory Vocabulary

| Concept | Meaning | Software analog |
| --- | --- | --- |
| **Entropy** | Uncertainty / information content | A field that varies a lot tells you a lot |
| **Channel capacity** | Max throughput of information a channel can carry without loss | Bytes/sec on a log pipeline; tokens/turn for an LLM |
| **Signal-to-noise (SNR)** | Useful information vs distraction | Real errors vs warnings nobody actions |
| **Mutual information** | How much knowing X reduces uncertainty about Y | Whether request_id in a log lets you correlate downstream events |
| **Lossless transform** | Original recoverable from output | gzip, JSON ↔ object |
| **Lossy transform** | Original not recoverable | Truncated stack trace, percentile aggregation |
| **Compression** | Same information, fewer bits | Structured logging vs free text |
| **Redundancy** | Information repeated to support recovery | Error code + human message + correlation ID |
| **Provenance** | Origin and transformation history of a datum | "This metric came from X collector at Y time" |
| **Encoding** | Mapping between message and representation | Schema, content type |
| **Channel noise** | Random or systematic distortion | Log shipper drops, clock skew, sampling bias |
| **Aliasing** | Distinct inputs producing the same output | Two errors with the same generic message |
| **Information leakage** | Sensitive data crossing a boundary it shouldn't | PII in logs |
| **Schema drift** | Structure changes silently between producer and consumer | Producer adds field, consumer ignores; producer removes field, consumer crashes |
| **Cardinality explosion** | Too many distinct values for a dimension | High-cardinality metric labels |

### Shannon's intuition (no math required)

- A channel can carry only so much information per unit. Trying to push more results in loss or noise.
- Redundancy is the price of error correction. Strip it for efficiency, pay for it on bad days.
- Compression is only safe relative to a known decoder; if the decoder changes, compressed history becomes ambiguous.
- The best place to compress is at the **consumer's** boundary, not the source — because only the consumer knows what they don't need.

### Common information-flow failures

- **Premature aggregation**: percentiles computed at the source, raw samples lost
- **Identifier loss**: log line says "request failed" with no request ID
- **Provenance loss**: a metric value with no source, no time of computation, no version
- **Schema mismatch**: producer V2, consumer V1, silent field drop
- **Generic error message aliasing**: 50 distinct failures all say `Error: something went wrong`
- **Sampling-induced bias**: head-based sampling drops the very traces you'd want
- **Truncated stack traces**: the frame you need is below the cutoff
- **Free-text logs**: not parseable, not aggregatable, not queryable
- **Duplicate truth**: same fact in two stores, no reconciliation
- **Stale cache as authoritative**: information passes its useful lifetime undetected
- **Re-encoding loss**: text → emoji → text, JSON → YAML → JSON, prompt → tool → prompt

## The Process

### Step 1: Define Source, Channel, Sinks, and Consumers

Make the flow concrete and bounded.

```
INFORMATION FLOW:
- Source(s):
- Channel(s) and transforms:
- Sink(s):
- Consumer(s) and the decisions they make:
- Question this flow must answer:
```

If you can't name a consumer and a decision, the information may not need to exist — or may need to be removed (`code-forensics` and `assumption-audit` often surface flows nobody reads).

### Step 2: Inventory What Exists at the Source

List everything *available* at the source, not just what is currently sent:

- Identifiers: request ID, user ID, session ID, trace ID, version, deploy ID
- Context: input parameters, caller, environment
- Timing: timestamps with timezone and precision
- Outcome: success/failure, error code, error class, message
- Resource info: which host, which pod, which region

The gap between "available at the source" and "delivered to the consumer" is your information loss.

### Step 3: Walk the Channel and Mark Transformations

For each hop, record what happens to the information:

```
HOP:
- From → To:
- Transform: (filter / project / rename / aggregate / sample / serialize / compress / summarize)
- Lossy? (yes/no)
- Provenance preserved? (yes/no)
- Schema evolution policy? (additive only / breaking allowed / undefined)
- Failure mode: (drops on overflow / blocks / partial delivery / silent corruption)
```

Identify each step where lossy transformation happens. Aggregation, sampling, summarization, and truncation are all lossy.

### Step 4: Estimate SNR at the Consumer

Put yourself in the consumer's shoes. For a representative incident or query:

- How many records do they wade through?
- How many are signal vs noise (e.g., warnings nobody actions)?
- Can they answer the diagnostic question with a single targeted query, or must they reconstruct?

Weak:

> We log everything to splunk.

Strong:

> When investigating a 500, an SRE must filter 50k log lines/min, of which ~95% are unrelated, and the request_id is missing on the line that matters.

### Step 5: Check Provenance and Correlation

Every important datum should answer: **where did I come from, and what am I related to?**

- Is there a correlation ID that links source → all downstream effects?
- Does each derived value record its inputs and the version of the derivation?
- Can you replay a transform from preserved inputs?
- Can you trace a metric anomaly back to the raw events that caused it?

Provenance loss is silent until needed, and catastrophic when needed.

### Step 6: Identify Aliasing and Generic Messages

Aliasing is when distinct upstream conditions produce the same downstream signal. Audit error messages and event types:

- Are there generic catchalls (`Error: failed`, `unknown`) that hide multiple distinct causes?
- Do error codes preserve enough specificity that a consumer can dispatch on them?
- Are status enums missing values that you actually need to distinguish?

Strong error messages: include **what was attempted**, **why it failed**, **what the caller might do**, and an **identifier** for correlation.

### Step 7: Examine Redundancy and Reconciliation

Redundancy is double-edged:

| Good redundancy | Bad redundancy |
| --- | --- |
| Error code + human message + correlation ID | Two stores of the same fact, written by two writers, no reconciliation |
| Trace + log + metric for cross-verification | Metric reported by two systems with slightly different definitions |
| Schema version embedded in the payload | Schema duplicated in client and server, drift unmonitored |

For each redundant store, ask: who is authoritative? When they disagree, who wins, and how do we know they disagreed?

### Step 8: Recommend Changes at the Right Boundary

Match the recommendation to the failure:

| Failure | Recommendation |
| --- | --- |
| Identifier loss | Propagate correlation IDs through every hop; require them at log boundary |
| Premature aggregation | Move aggregation to consumer; preserve raw events upstream |
| Aliased errors | Distinct error codes + structured error type, free-text message secondary |
| Schema drift | Versioned schemas, additive-only evolution, contract tests at the boundary |
| Cardinality explosion | Dimension allow-list, separate high-cardinality data into traces/logs not metrics |
| PII leakage | Redaction at producer, not consumer |
| Stale data treated as fresh | TTL + freshness metric; reject stale for critical decisions |
| Truncated traces | Tail-based sampling (keep error traces), increase per-trace size budget |
| Lossy summarization | Preserve raw alongside summary; mark summary as lossy |

Prefer fixes at the **earliest point** where the information still exists, and the **latest point** where it can still be acted on (decode close to the consumer).

## Output Format

```
INFORMATION FLOW ANALYSIS

Flow definition:
- Source → channel → sink → consumer
- Question this flow must answer:

Available at source vs delivered to consumer:
- Available: ...
- Delivered: ...
- Gap: ...

Per-hop transformation table:
- Hop 1: ... (lossy? provenance?)
- ...

Signal-to-noise at consumer:
- Estimated noise:
- Worst-case query time:

Provenance / correlation gaps:
- ...

Aliasing / generic messages:
- ...

Redundancy and reconciliation:
- Authoritative store:
- Disagreement detection:

Recommended changes (placed at the right boundary):
1. ...

What NOT to do (anti-patterns avoided):
- ...
```

## Anti-Patterns to Avoid

- **Dropping provenance too early**: source, version, time of derivation must travel with the value
- **Logging without identifiers**: a log line you can't correlate is anecdote
- **Compressing before diagnosis is possible**: percentiles at the source destroy the raw events you need
- **Maintaining duplicated truth without reconciliation**: two systems will diverge; design how disagreement is detected
- **Generic catch-all errors**: `Error: failed` is information loss disguised as logging
- **High-cardinality labels in metrics**: melts the metrics store and tells you less than logs would
- **Sampling that hides what you need**: head-based sampling on errors loses errors
- **Schema drift without contract**: producer and consumer diverge silently
- **Free-text where structure is possible**: prefer structured logs/events
- **Summarization without preserving raw**: once raw is gone, you cannot re-summarize for new questions

## Relationship to Other Skills

- Use `code-forensics` when an incident hinges on what *was* in the logs vs what we needed; gaps surface naturally there.
- Use `assumption-audit` to surface assumptions about consumers, schemas, and what is "obviously" known downstream.
- Use `formal-invariants` to encode schema and provenance constraints (e.g., "every error response includes a request_id and a code from this enum").
- Use `network-topology-review` when the channel is a graph and you need to reason about where to instrument.
- Use `feedback-loop-analysis` when sampling or logging policies feed back into system load (logs causing the latency you're trying to measure).
- Use `constraint-analysis` when channel capacity (log pipeline, telemetry budget) is itself the bottleneck.
