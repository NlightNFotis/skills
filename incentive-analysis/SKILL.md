---
name: incentive-analysis
description: Predict how users, maintainers, systems, and attackers respond to rules, defaults, metrics, and rewards.
user-invocable: true
---

# Incentive Analysis

Act as an economist. Analyze how defaults, metrics, limits, rewards, costs, and constraints shape behavior.

## When to Use This

- Designing policies, quotas, metrics, defaults, prompts, permissions, pricing, review rules, or workflows
- Users or systems may game the process
- A metric may become a target
- A default could create long-term behavior

## Process

1. Identify actors and what each wants.
2. Identify incentives: rewards, costs, friction, defaults, visibility, penalties.
3. Predict first-order behavior and second-order side effects.
4. Look for gaming, perverse incentives, tragedy of the commons, free riding, and hidden costs.
5. Recommend incentive-compatible designs: align local benefit with system health.

## Output Format

```
INCENTIVE ANALYSIS

Actors:
- ...

Incentives:
- ...

Predicted behavior:
1. ...

Gaming risks:
1. ...

Recommended changes:
1. ...
```

## Anti-Patterns

- Assuming users optimize for your intended goal
- Measuring what is easy instead of what matters
- Ignoring second-order effects
- Punishing honest behavior more than abuse
