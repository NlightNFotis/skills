---
name: system-ecosystem-analysis
description: Analyze dependency ecosystems, cascading failures, resource competition, and emergent behavior.
user-invocable: true
---

# System Ecosystem Analysis

Act as an ecologist studying a software ecosystem. Analyze dependencies, niches, resource competition, cascading effects, and adaptation over time.

## When to Use This

- Many services, packages, tools, teams, or agents interact
- A change affects distant components
- Dependencies compete for shared resources
- System health depends on ecosystem balance

## Process

1. Identify species: services, modules, teams, dependencies, users, bots, queues.
2. Map relationships: dependency, competition, mutualism, predation, parasitism, succession.
3. Identify shared resources: CPU, memory, tokens, attention, review capacity, API quotas, disk, network.
4. Look for cascading failures and invasive dependencies.
5. Recommend isolation, diversity, redundancy, limits, observability, and dependency hygiene.

## Output Format

```
ECOSYSTEM ANALYSIS

Actors/species:
- ...

Relationships:
- ...

Shared resources:
- ...

Cascading risks:
1. ...

Interventions:
1. ...
```

## Anti-Patterns

- Treating dependencies as passive
- Ignoring resource competition
- Assuming monocultures are resilient
- Missing indirect effects
