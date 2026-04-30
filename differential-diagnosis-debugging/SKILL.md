---
name: differential-diagnosis-debugging
description: Use differential diagnosis to triage possible causes by likelihood, severity, and test cost.
user-invocable: true
---

# Differential Diagnosis Debugging

Act as a clinician diagnosing a software failure. Build a differential diagnosis, rule out dangerous causes early, and avoid premature closure.

## When to Use This

- A symptom has many plausible causes
- You need triage rather than deep formal proof
- The cost of missing a severe cause is high
- A failure could be code, data, environment, dependency, or user workflow

## Process

1. State the chief complaint: exact symptom and context.
2. Collect vital signs: error, stack, inputs, environment, recent changes, reproducibility.
3. Build a differential: 3-6 plausible diagnoses from different categories.
4. Rank by likelihood, severity if missed, and test cost.
5. Rule out "must not miss" severe causes even if less likely.
6. Run targeted tests, updating the differential after each result.
7. Treat only after diagnosis is sufficiently supported.

## Output Format

```
DIFFERENTIAL DEBUGGING

Chief complaint:
- ...

Vital signs:
- ...

Differential:
1. Diagnosis - likelihood / severity / test

Ruled out:
- ...

Working diagnosis:
- ...

Treatment and verification:
1. ...
```

## Anti-Patterns

- Treating the first plausible cause as final
- Ignoring severe low-probability causes
- Ordering tests by convenience only
- Fixing symptoms without diagnosis
