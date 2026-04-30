---
name: failure-mode-effects-analysis
description: Enumerate failure modes, effects, severity, detectability, and mitigations before risky changes.
user-invocable: true
---

# Failure Mode and Effects Analysis

Act as a reliability engineer. Enumerate how a system can fail, what each failure causes, how detectable it is, and what mitigations reduce risk.

## When to Use This

- Before risky releases, migrations, auth changes, data changes, or operational workflows
- Reviewing critical paths or external dependencies
- Designing rollback, validation, and monitoring

## Process

1. Define the operation or component.
2. Break it into steps or functions.
3. For each step, list failure modes.
4. For each failure mode, record cause, effect, severity, likelihood, detectability, and existing controls.
5. Prioritize high-severity and hard-to-detect failures.
6. Recommend prevention, detection, containment, rollback, or recovery.

## Output Format

```
FMEA

Scope:
- ...

Failure modes:
1. Mode:
   - Cause:
   - Effect:
   - Severity:
   - Detectability:
   - Mitigation:

Top risks:
1. ...
```

## Anti-Patterns

- Listing only obvious crashes
- Ignoring silent data corruption
- Treating detection as mitigation
- Missing rollback and recovery paths
