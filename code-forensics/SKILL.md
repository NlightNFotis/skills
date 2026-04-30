---
name: code-forensics
description: Reconstruct timelines and causal chains from logs, stack traces, commits, artifacts, tests, and changed files before deciding what happened.
user-invocable: true
---

# Code Forensics

Act as a forensic investigator for software systems. Your job is to reconstruct what happened from evidence: logs, traces, commits, timestamps, test output, artifacts, stack traces, configuration, and file changes.

The goal is to establish a defensible timeline and causal story before proposing fixes. Prefer evidence over intuition.

## When to Use This

- A failure appeared after unknown or multiple changes
- Logs, traces, CI output, or artifacts need interpretation
- You need to determine when and why behavior changed
- A bug involves several systems or asynchronous events
- A regression needs attribution
- A prior debugging attempt made conflicting claims
- You suspect the first visible error is not the root cause

**Escape hatch**: If the root cause is directly obvious from a local error and stack trace, fix and verify. Use this skill when chronology, causality, or evidence quality matters.

## Core Mindset

Do not start with "what fix should I make?" Start with:

- What do we know happened?
- In what order did it happen?
- Which facts are directly observed?
- Which facts are inferred?
- What evidence is missing?
- What is the earliest known divergence from expected behavior?

## Evidence Types

Classify evidence by reliability:

| Evidence | Typical reliability | Notes |
| --- | --- | --- |
| Reproduced local failure | High | Strongest when deterministic |
| Stack trace | High for location, medium for cause | Often points to symptom, not root cause |
| Test output | High for observed behavior | May hide setup or fixture assumptions |
| Logs/traces | Medium-high | Check timestamps, correlation IDs, dropped logs |
| Commit diff | Medium-high | Shows what changed, not necessarily what caused failure |
| CI artifacts | Medium | Environment may differ from local |
| User report | Medium | Valuable, but may omit steps or context |
| Metrics/telemetry | Medium | Beware sampling, aggregation, and lag |
| Assumptions from code reading | Low until tested | Treat as hypotheses |

## The Process

### Step 1: Define the Incident

State the event under investigation.

```
INCIDENT:
- Observed failure:
- Expected behavior:
- Where observed:
- First known occurrence:
- Last known good state:
- Impact:
```

If first/last known times are unknown, mark them as unknown rather than inventing them.

### Step 2: Preserve and Gather Evidence

Collect relevant artifacts before changing the system:

- Exact command and output
- Stack traces and error messages
- Logs with timestamps
- Relevant changed files
- Recent commits or dependency changes
- Environment/config differences
- CI job links, artifacts, screenshots, recordings, or captures
- Reproduction steps and inputs

Avoid editing code before preserving the original failure unless the environment is disposable and easily reproducible.

### Step 3: Build a Timeline

Create a chronological sequence of observed events.

```
TIMELINE:
1. [time/order] [observed fact] — source: [...]
2. [time/order] [observed fact] — source: [...]
3. ...
```

Use relative order when exact timestamps are unavailable:

- Before / after
- During setup / execution / teardown
- Prior commit / current commit
- First failure / subsequent failure

Separate **observed facts** from **interpretations**.

### Step 4: Identify the Earliest Divergence

Find the first point where actual behavior differs from expected behavior.

Ask:

- What is the first wrong value, state, event, response, or side effect?
- Is the visible error downstream of an earlier failure?
- Did setup already create invalid state?
- Did an earlier warning predict the later error?
- Did a recent change affect the earliest divergence point?

Do not anchor on the last stack frame if earlier evidence contradicts it.

### Step 5: Correlate Evidence Across Sources

Cross-check independent evidence:

- Does the stack trace match the changed code path?
- Do logs and timestamps agree with the suspected sequence?
- Do failing and passing runs differ in input, environment, order, or state?
- Does the commit diff explain the first divergence?
- Are tests/mocks hiding behavior not present in production?

Mark contradictions explicitly.

```
CORRELATIONS:
- Supports:
- Contradicts:
- Missing:
```

### Step 6: Form a Causal Chain

Construct the most evidence-supported chain from triggering condition to failure.

```
CAUSAL CHAIN:
1. Trigger:
2. State/input change:
3. First divergence:
4. Propagation:
5. Visible failure:
```

Each link should cite evidence. If a link is speculative, label it as a hypothesis.

### Step 7: Test the Story

A good forensic story predicts observations.

Ask:

- If this causal chain is true, what else should I observe?
- Can I reproduce the failure by recreating the trigger?
- Can I make the failure disappear by reverting or isolating one causal link?
- Can I explain both failing and passing cases?
- Is there a simpler chain that explains the same evidence?

If the story cannot make predictions, it is not yet strong enough.

### Step 8: Recommend Fixes and Evidence to Verify

Only after the causal chain is credible, propose fixes.

For each fix:

- Which causal link does it break?
- Why is it safer than alternatives?
- What test or command verifies it?
- What regression risk remains?
- What evidence should be captured if it fails again?

## Output Format

When using this skill, produce:

```
CODE FORENSICS REPORT

Incident:
- ...

Evidence collected:
- ...

Timeline:
1. ...

Earliest divergence:
- ...

Causal chain:
1. ...

Confidence:
- High / medium / low because [...]

Recommended fix:
1. ...

Verification plan:
1. ...

Open questions:
- ...
```

If implementing changes, make the smallest fix that breaks the causal chain and preserves the evidence trail.

## Anti-Patterns to Avoid

- **Fixing before preserving evidence**: you may destroy the trail
- **Confusing symptom with cause**: the thrown error may be downstream
- **Inventing timestamps or order**: mark unknowns honestly
- **Treating code reading as proof**: code inspection suggests possibilities; execution evidence confirms behavior
- **Ignoring contradictions**: contradictions often identify the real cause
- **Overfitting to one run**: compare passing/failing cases when possible
- **Losing provenance**: every key claim should point to a source

## Relationship to Other Skills

- Use `popperian-debug` after the forensic report if multiple causal hypotheses remain.
- Use `assumption-audit` when the causal chain depends on hidden premises.
- Use `formal-invariants` when the root cause reveals an invariant that should be asserted or tested.
