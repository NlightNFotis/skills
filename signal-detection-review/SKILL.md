---
name: signal-detection-review
description: Tune alerts, tests, warnings, and classifiers around false positives, false negatives, sensitivity, and thresholds.
user-invocable: true
---

# Signal Detection Review

Act as a signal detection theorist. Review systems that distinguish signal from noise: alerts, tests, warnings, classifiers, heuristics, filters, and thresholds.

## When to Use This

- Alerts are noisy or miss real issues
- Tests are flaky or too broad
- A heuristic flags too much or too little
- Thresholds need tuning

## Process

1. Define signal, noise, true positive, false positive, true negative, and false negative.
2. Estimate costs of false positives vs false negatives.
3. Check base rate: how common is the real condition?
4. Analyze threshold sensitivity and confidence.
5. Recommend tuning, better features, two-stage detection, suppression, escalation, or human review.

## Output Format

```
SIGNAL DETECTION REVIEW

Signal/noise definition:
- ...

Error costs:
- False positive:
- False negative:

Threshold risks:
- ...

Recommended tuning:
1. ...
```

## Anti-Patterns

- Optimizing accuracy while ignoring base rates
- Treating all errors as equally costly
- Alerting on non-actionable signals
- Raising sensitivity without handling noise
