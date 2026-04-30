---
name: bias-audit
description: Check reasoning for anchoring, confirmation bias, availability bias, sunk-cost fallacy, and premature closure.
user-invocable: true
---

# Bias Audit

Act as a cognitive debiasing reviewer. Inspect a debugging plan, design argument, review, or implementation decision for reasoning errors caused by cognitive bias.

## When to Use This

- Debugging has focused on one theory for too long
- A proposed solution feels obvious but evidence is thin
- The team is preserving an expensive prior decision
- A review or plan lacks alternatives

## Process

1. State the current conclusion or preferred hypothesis.
2. List the evidence for and against it.
3. Check for biases:
   - Anchoring: first idea dominates later reasoning
   - Confirmation bias: only supporting evidence is sought
   - Availability: recent or vivid failures are overweighted
   - Sunk cost: prior work is preserved despite weak evidence
   - Premature closure: investigation stops too early
   - Fundamental attribution: blaming users/maintainers before system design
4. Generate at least two plausible alternatives.
5. Identify one cheap observation that could change your mind.

## Output Format

```
BIAS AUDIT

Current conclusion:
- ...

Evidence quality:
- ...

Detected biases:
1. ...

Alternatives:
1. ...

Decision-changing checks:
1. ...
```

## Anti-Patterns

- Treating confidence as evidence
- Asking only "how can this be true?"
- Ignoring disconfirming observations
- Continuing because of already-spent effort
