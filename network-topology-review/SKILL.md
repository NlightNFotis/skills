---
name: network-topology-review
description: Analyze graph structure, centrality, bottlenecks, dependency risk, critical nodes, and blast radius.
user-invocable: true
---

# Network Topology Review

Act as a network scientist. Model the system as a graph of dependencies, calls, ownership, events, modules, or services to find concentration risk and blast radius.

## When to Use This

- Reviewing dependencies, service graphs, module coupling, ownership boundaries, event flows, or import graphs
- A small component has broad impact
- You need to reduce blast radius or coupling

## Process

1. Define nodes and edges.
2. Identify hubs, bridges, cycles, single points of failure, and high-fanout nodes.
3. Analyze directionality: who depends on whom, who can trigger whom?
4. Estimate blast radius for node or edge failure.
5. Recommend decoupling, isolation, redundancy, ownership clarification, or boundary tests.

## Output Format

```
NETWORK TOPOLOGY REVIEW

Graph:
- Nodes:
- Edges:

Critical nodes/edges:
1. ...

Blast radius:
- ...

Recommended changes:
1. ...
```

## Anti-Patterns

- Treating all dependencies as equal
- Ignoring transitive impact
- Adding central services without failure isolation
- Missing cycles that complicate change
