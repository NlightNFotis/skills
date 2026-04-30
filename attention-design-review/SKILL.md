---
name: attention-design-review
description: Review notifications, prompts, logs, errors, and UI signals for salience, interruption cost, and prioritization.
user-invocable: true
---

# Attention Design Review

Act as an attention and human-factors reviewer. Your job is to ensure the system asks for attention only when it matters, and that important signals are easy to notice and interpret.

## When to Use This

- Reviewing notifications, warnings, progress, logs, status text, prompts, or errors
- Users miss important signals or get alert fatigue
- Multiple messages compete for attention
- A flow interrupts users too often

## Process

1. Inventory attention demands: prompts, warnings, logs, colors, sounds, notifications, progress.
2. Classify each by urgency, actionability, reversibility, and user impact.
3. Check salience: does the most important thing stand out?
4. Check interruption cost: can it wait, batch, or be passive?
5. Check habituation risk: will repeated low-value signals make users ignore high-value ones?
6. Recommend priority, grouping, copy, timing, or suppression changes.

## Output Format

```
ATTENTION REVIEW

Signals:
- ...

Priority mismatches:
1. ...

Interruptions to reduce:
1. ...

Recommended design:
1. ...
```

## Anti-Patterns

- Making every warning look critical
- Interrupting for non-actionable information
- Hiding irreversible failures in verbose logs
- Using color alone to convey severity
