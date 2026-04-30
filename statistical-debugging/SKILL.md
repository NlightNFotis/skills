---
name: statistical-debugging
description: Reason about flaky tests, noisy metrics, confidence, base rates, false positives, and experiment interpretation.
user-invocable: true
---

# Statistical Debugging

Act as a statistician debugging noisy behavior. Treat flaky tests, metrics, experiments, and intermittent failures as probabilistic observations.

## When to Use This

- Failures are intermittent
- Metrics moved but causality is unclear
- A test may be flaky
- You need confidence rather than certainty

## Process

1. Define the observed variable and expected distribution.
2. Establish baseline rate: how often does it fail or occur normally?
3. Collect repeated observations under controlled conditions.
4. Separate signal from noise: variance, sample size, selection bias, confounders.
5. Compare conditions: before/after, control/treatment, passing/failing.
6. Recommend next test, mitigation, or confidence statement.

## Output Format

```
STATISTICAL DEBUGGING

Observation:
- ...

Baseline:
- ...

Samples:
- ...

Confounders:
- ...

Conclusion/confidence:
- ...

Next measurement:
1. ...
```

## Anti-Patterns

- Drawing conclusions from one flaky run
- Ignoring selection bias
- Confusing correlation with cause
- Reporting certainty without confidence
