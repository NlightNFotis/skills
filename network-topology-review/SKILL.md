---
name: network-topology-review
description: Analyze graph structure, centrality, bottlenecks, dependency risk, critical nodes, and blast radius.
user-invocable: true
---

# Network Topology Review

Act as a network scientist reviewing the system as a graph. Most software systems — module imports, service calls, ownership relations, event subscriptions, build targets, IAM grants — are graphs whose structural properties determine reliability, blast radius, and ease of change. The same metrics that explain how diseases spread, power grids fail, and information propagates apply directly to software.

Success looks like a graph-theoretic diagnosis: identifying high-centrality hubs, articulation points, bridges, cycles, and the resulting blast radius for representative failures, with concrete decoupling or isolation recommendations. Failure looks like treating all dependencies as equal, missing the difference between random and targeted failure, or proposing changes whose blast radius is unclear.

## When to Use This

- Reviewing module import graphs, service call graphs, event/topic graphs, IAM graphs, ownership graphs
- A small change in one place causes failures or churn in many distant places
- Considering decoupling, splitting, or merging modules/services
- Assessing supply-chain or dependency risk
- Designing platform components that will be depended on broadly
- Investigating why CI is slow, why type-check fans out, or why a deploy ripples
- Planning a migration whose blast radius matters

**Escape hatch**: For local refactors of one or two modules with no broader graph impact, you don't need topology analysis — just edit. Use this skill when *structure* of the graph matters more than the contents of any node.

## Core Mindset

Topology is destiny. Two systems with identical components and different graph structures have different failure modes, different change costs, and different reliability ceilings. Ask:

- What are the nodes and what are the edges? Is the graph directed? Weighted?
- Which nodes have high in-degree (depended on by many) vs out-degree (depend on many)?
- Which nodes are bridges or articulation points — their removal disconnects the graph?
- What is the blast radius of failure at each candidate node?
- Is the graph scale-free (hub-dominated) or roughly random?
- Are there cycles? Strongly connected components?
- What does the failure look like under random failure vs targeted attack on hubs?

## Graph Vocabulary

| Concept | Meaning | Software example |
| --- | --- | --- |
| **Degree centrality** | Number of edges at a node | A module imported by 200 others |
| **In-degree / out-degree** | Incoming / outgoing edges (directed) | High in-degree = "depended on a lot" |
| **Betweenness centrality** | Fraction of shortest paths that pass through this node | A gateway service through which most traffic flows |
| **Eigenvector / PageRank centrality** | Importance weighted by importance of neighbors | A library used by other widely-used libraries |
| **Closeness centrality** | Inverse of mean distance to all nodes | Easily reaches everything (small radius) |
| **Articulation point (cut vertex)** | Removal disconnects the graph | A central event bus |
| **Bridge (cut edge)** | Removal disconnects the graph | The single network link between two regions |
| **k-core** | Maximal subgraph where every node has degree ≥ k | Tightly-coupled cluster, hard to refactor |
| **Strongly connected component (SCC)** | Cycle group; every node reaches every other | Mutually-dependent services or modules |
| **DAG** | Directed acyclic graph | Healthy import graph, build dependency graph |
| **Scale-free** | Degree distribution follows power law; few huge hubs | Most real codebases and microservice graphs |
| **Random (Erdős–Rényi)** | Roughly uniform degree | Rare in real software |
| **Small-world** | Short average path length, high clustering | Social-style graphs; quick rumor spread |
| **Percolation threshold** | Fraction of nodes that must remain functional for the graph to stay connected | How much can fail before the network shatters |
| **Diameter** | Longest shortest path | "How far can a change ripple?" |
| **Fan-out / Fan-in** | Edges out of / into a node | Build target with 1000 reverse-deps has high fan-in |

### Failure-mode lemma

- **Scale-free networks** are *robust* to random failure (most nodes are low-degree leaves) but *fragile* to targeted hub failure.
- **Random networks** degrade smoothly under both.
- Real software graphs are almost always scale-free. Plan for hub failure, not just random failure.

## The Process

### Step 1: Define Nodes, Edges, and Direction

Be explicit. The same system viewed two ways gives different answers.

```
GRAPH DEFINITION:
- Node type: (module / service / package / team / file / IAM principal / topic)
- Edge type: (imports / calls / publishes-to / owns / depends-on / grants)
- Directed? (yes/no)
- Weighted? (e.g., call volume, line count, build time)
- Scope / boundary: (which subset of the universe is in scope?)
```

A common mistake: mixing edge types in one graph. Keep them separate or label them.

### Step 2: Identify Hubs

For each centrality measure that matters here, list the top nodes:

- **High in-degree** (most depended on): candidate keystones
- **High out-degree** (most coupled): candidate refactor pain
- **High betweenness**: candidate bottleneck or gateway
- **High eigenvector / PageRank**: structurally central, even if degree is moderate

Tools: `madge` for JS imports, `pydeps`/`pyan` for Python, `go mod graph`, `bazel query`, language-server reverse-references, custom AST scripts. For small graphs, manual is fine.

### Step 3: Find Articulation Points and Bridges

These are nodes/edges whose removal disconnects the graph. They are exactly where blast radius is highest.

- A single auth library imported by every service
- The one network link between regions
- The single team approval gate every PR passes through

Mark each: who owns it, what is its SLO, what's the failover.

### Step 4: Find Cycles and Strongly Connected Components

Cycles complicate change, deployment ordering, and reasoning.

- Module-level cycles signal poor layering
- Service-level cycles signal that "microservices" are actually a distributed monolith
- Build-dependency cycles often hide in test targets

For each SCC larger than 1: name it, decide if it should be collapsed, broken, or formally treated as a unit.

### Step 5: Estimate Blast Radius

For representative nodes, compute (or estimate) the set of nodes affected by failure or change.

```
BLAST RADIUS ESTIMATE:
- Node:
- Type of change/failure: (outage / breaking API change / latency spike / removal)
- Direct dependents: N
- Transitive dependents: M
- Critical paths affected:
- User-visible surface affected:
```

A useful heuristic: count of transitive reverse dependencies, weighted by their own centrality.

### Step 6: Compare Random vs Targeted Failure

Walk two scenarios:

- **Random**: a uniformly random 5% of nodes go down — does the graph stay connected? What functionality remains?
- **Targeted**: the top 1% by in-degree go down — what shatters?

If the gap is large, the system is hub-fragile. Reliability work should focus on hub redundancy, not on average-node hardening.

### Step 7: Check Layering and Direction

A healthy directed graph approximates a DAG with clear layers (e.g., infrastructure → platform → product). Anti-patterns:

- Lower layers importing upper layers (dependency inversion failures)
- "Platform" components calling into product code
- Wide bypass edges that skip layers and create implicit coupling

### Step 8: Recommend Structural Changes

Map diagnosis to intervention:

| Finding | Intervention |
| --- | --- |
| Hub with broad fan-in and single owner | Stabilize API, formal ownership, version policy, redundancy |
| Articulation point | Add a parallel path, or accept and harden it |
| Bridge with high traffic | Redundant link, cache at one side, async buffer |
| Large SCC | Break the cycle (interface extraction, event indirection) |
| Hub-fragile graph | Targeted hub hardening, not blanket hardening |
| Wide bypass edges | Re-route through proper layer; or formalize the bypass as an API |
| Scale-free with no governance for hubs | Establish "tier-0 dependencies" policy and review |

## Output Format

```
NETWORK TOPOLOGY REVIEW

Graph definition:
- Nodes: ...
- Edges: ...
- Directed/weighted: ...
- Scope: ...

Top hubs (by relevant centrality):
- In-degree: ...
- Betweenness: ...
- Eigenvector / PageRank: ...

Articulation points / bridges:
- ...

Cycles / SCCs:
- ...

Blast radius for representative nodes:
- ...

Random vs targeted failure assessment:
- ...

Layering / direction violations:
- ...

Recommended structural changes (matched to finding):
1. ...

Observability / governance gaps:
- ...
```

## Anti-Patterns to Avoid

- **Treating all dependencies as equal**: a leaf import and a hub import have different costs
- **Ignoring transitive impact**: direct fan-in undercounts true blast radius
- **Adding a central service without redundancy**: creates a new articulation point
- **Hardening the average node**: scale-free graphs require *targeted* hardening
- **Missing cycles**: especially in service graphs disguised as microservices
- **Conflating edge types**: imports, calls, ownership, and IAM are different graphs
- **Decoupling everything**: indirection has its own cost; remove only the edges that earn it
- **Using only one centrality metric**: betweenness and degree disagree often, and both matter

## Relationship to Other Skills

- Use `system-ecosystem-analysis` to interpret hubs as keystone species and reason about competition for shared resources.
- Use `feedback-loop-analysis` when a hub's failure creates retry/load loops across its dependents.
- Use `emergence-analysis` for failures that emerge from the interaction of many edges, not from a single node.
- Use `constraint-analysis` when the betweenness hub is also the system's throughput constraint.
- Use `code-forensics` to confirm blast-radius hypotheses against actual incident history.
- Use `formal-invariants` to encode "tier-0 dependencies" policies (e.g., "no module in layer N may import from layer N+1") as enforceable rules.
