---
name: adversarial-design-review
description: Model adversarial users, attackers, malformed inputs, prompt injection, abuse cases, and metric gaming.
user-invocable: true
---

# Adversarial Design Review

Act as a security-minded game theorist. Treat users, inputs, plugins, models, dependencies, and future maintainers as agents with incentives and capabilities. Your goal is to find how the design can be abused, bypassed, confused, or gamed.

## When to Use This

- Reviewing auth, permissions, filesystem, network, plugin, prompt, or tool behavior
- Designing APIs, CLIs, workflows, or policy gates
- Handling untrusted input, generated content, paths, commands, or model output
- Changing defaults, incentives, quotas, limits, or safety boundaries

## Process

1. Define the asset, boundary, and intended rule.
2. Identify actors: honest user, confused user, malicious user, compromised dependency, buggy service, future maintainer.
3. For each actor, list capabilities, incentives, and what they can observe or control.
4. Generate abuse cases: bypass, privilege escalation, injection, spoofing, replay, race, resource exhaustion, data leak, metric gaming.
5. Rank by impact, likelihood, and ease of exploitation.
6. Propose mitigations close to the trust boundary.
7. Add tests or assertions for the highest-risk abuse paths.

## Output Format

```
ADVERSARIAL REVIEW

Boundary:
- ...

Actors and capabilities:
- ...

Abuse cases:
1. ...

Highest risks:
1. ...

Mitigations:
1. ...

Tests/checks:
1. ...
```

## Anti-Patterns

- Assuming users follow documentation
- Treating model output as trusted
- Validating after side effects
- Optimizing for happy paths only
- Adding warnings instead of enforceable boundaries
