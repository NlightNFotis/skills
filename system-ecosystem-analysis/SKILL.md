---
name: system-ecosystem-analysis
description: Analyze dependency ecosystems, cascading failures, resource competition, and emergent behavior.
user-invocable: true
---

# System Ecosystem Analysis

Act as an ecologist studying a software ecosystem. Software systems — composed of services, libraries, package registries, internal platforms, teams, bots, and users — behave like ecosystems. They have keystone species, niches, succession, predator-prey dynamics, mutualisms, parasites, invasive species, monoculture risk, and finite carrying capacity. Treating them as static dependency lists misses the dynamics that produce most long-running incidents.

Success looks like identifying which dependencies are keystone (their failure cascades), where monoculture concentrates risk, where mutualisms quietly hold the system together, and where invasive or parasitic dependencies are extracting more than they contribute. Failure looks like treating the ecosystem as a flat list, ignoring resource competition, or assuming "more dependencies = more capability".

## When to Use This

- Many services, packages, internal tools, teams, or agents interact
- A change in one component produces distant or asymmetric effects
- Dependencies compete for shared finite resources (CPU, tokens, review capacity, on-call attention, build minutes)
- A platform team is overwhelmed and you suspect the dynamic is structural
- Evaluating an "innocuous" new dependency before adoption
- Reviewing dependency sprawl, package monorepos, or supply-chain risk
- A previously stable subsystem has degraded slowly without a single causing change

**Escape hatch**: For a focused two-component coupling problem, use `network-topology-review` directly. Use ecosystem analysis when the question involves *populations* of components, succession over time, or competition over shared resources — not isolated edges.

## Core Mindset

A healthy ecosystem is not the one with the most species, the most connections, or the most activity. It is the one that survives perturbation. Ask:

- Which "species" exist in this ecosystem, and what niche does each occupy?
- Which components are keystone — their removal collapses much more than themselves?
- Where is the monoculture? What single failure would wipe out a whole layer?
- Which relationships are mutualistic, commensal, parasitic, or predatory?
- What is the carrying capacity of shared resources, and how close are we?
- What is the current succession stage — pioneer, growth, climax, decline?
- Where are invasive dependencies displacing healthier alternatives?

## Ecological Vocabulary

| Concept | Software analog |
| --- | --- |
| **Species** | Service, library, internal tool, team, bot, user role |
| **Niche** | The specific role a component fills (auth, caching, observability) |
| **Keystone species** | Component whose removal causes disproportionate collapse (e.g., service registry, central auth) |
| **Foundation species** | Provides habitat for many others (e.g., the build system, package registry) |
| **Mutualism** | Both sides benefit (CI ↔ test framework) |
| **Commensalism** | One benefits, the other is unaffected (a sidecar reading host metrics) |
| **Parasitism** | One benefits at the other's expense (a chatty consumer of a shared API) |
| **Predation** | One consumes another to extinction (a rewrite that kills the original) |
| **Competition** | Two species need the same scarce resource (two teams, one DBA) |
| **Carrying capacity** | Maximum population the environment can sustain |
| **Succession** | Predictable change over time: pioneer → growth → climax → decline |
| **Climax community** | Mature, stable, hard to disrupt — also hard to evolve |
| **Invasive species** | Dependency that spreads aggressively, displacing alternatives (often via convenience) |
| **Monoculture** | One option used everywhere; high efficiency, low resilience |
| **Resource partitioning** | Coexisting species split resources to reduce competition (separate quotas, bulkheads) |
| **Trophic level** | Position in a chain of consumption (raw infra → platform → product → user) |
| **Edge species** | Components living at boundaries; often brittle, often important |

## The Process

### Step 1: Inventory the Ecosystem

List the species and their niches. Be specific.

```
ECOSYSTEM INVENTORY:
- Foundation species (substrate the rest depends on):
- Keystone species (small in number, large in effect):
- Producers (create value from raw resources):
- Consumers (use producer output):
- Decomposers / cleanup (sweepers, GC, retention jobs):
- Edge species (live at boundaries with other ecosystems):
```

If the inventory is more than ~30 entries, group by trophic level rather than enumerating.

### Step 2: Identify Niches and Overlap

For each component, name the niche it occupies. Two species in the same niche are in competition; this is sometimes healthy diversity and sometimes wasteful duplication.

- Three internal HTTP clients → competition or pluralism?
- Two observability stacks → resource partitioning or inevitable consolidation?
- Multiple "platform" teams with overlapping mandates → competition for adoption

### Step 3: Map Relationships by Type

Go beyond "depends on". Classify:

| From → To | Mutualism | Commensalism | Parasitism | Predation | Competition |
| --- | --- | --- | --- | --- | --- |
| Service A → Service B | | | | | |
| Team X → Platform | | | | | |

A parasitic relationship is a strong signal. Examples:

- A consumer that polls every second on a shared DB it doesn't pay for
- A team that ships features that increase on-call load on another team
- A library that pulls 200 transitive deps for one function

### Step 4: Identify Keystone and Foundation Species

Apply the removal test mentally: "If this component vanished tonight, what collapses by morning?"

- **Keystone**: small footprint, broad collapse on removal (DNS, internal auth, central feature flag service)
- **Foundation**: large footprint, broad collapse on removal (the build system, the cluster)
- **Redundant species**: removable with minor disruption — these are healthy slack

Mark keystones explicitly; they need outsized investment in reliability and ownership clarity.

### Step 5: Find Shared Resources and Carrying Capacity

Enumerate finite shared resources and estimate current load vs capacity.

| Resource | Capacity | Current load | Trend | Saturation symptom |
| --- | --- | --- | --- | --- |
| CI minutes | | | | Slow PRs, queue grows |
| On-call attention (hours/wk) | | | | Burnout, missed pages |
| Review capacity | | | | Stale PRs, rubber-stamp reviews |
| Token / API quota | | | | 429s during peak |
| Platform team bandwidth | | | | Tickets aged > 30d |
| Database connections | | | | Connection pool exhaustion |

Approaching carrying capacity is when ecosystem-level dynamics dominate single-actor behavior (see `emergence-analysis`).

### Step 6: Look for Invasive Dependencies and Monocultures

Invasive signs:

- Spreads via convenience (autocomplete, defaults, "just `npm install` it")
- Displaces a previously diverse set of choices
- Hard to remove once adopted (sticky API surface, deep transitives)
- Maintained by no one in your org

Monoculture signs:

- Single version, single vendor, single team across the entire org
- Efficiency wins justified the consolidation
- A single CVE or outage takes down everything

Diversity vs efficiency is a real trade-off. Name it explicitly rather than assuming consolidation is always good.

### Step 7: Identify the Succession Stage

Each subsystem has a life-cycle stage:

- **Pioneer**: experimental, fast-moving, fragile, low expectations
- **Growth**: adoption rising, capacity strained, shape still changing
- **Climax**: stable, depended on, slow to change, expensive to disrupt
- **Decline**: usage falling, owners drifting, but still load-bearing

Interventions that work at one stage fail at others. Stabilizing a pioneer kills it. Moving a climax community fast breaks the ecosystem above it.

### Step 8: Recommend Interventions

Match intervention to ecological diagnosis:

| Diagnosis | Intervention |
| --- | --- |
| Keystone with single owner | Add redundancy, formal ownership, runbooks |
| Carrying capacity exceeded | Quota, bulkhead, capacity investment |
| Parasitic consumer | Charge for usage, rate limit, force migration |
| Invasive dependency | Containment policy, internal alternative, deprecation plan |
| Monoculture risk | Maintain a viable second option, even at cost |
| Climax community blocking change | Strangler-fig migration, parallel ecosystem |
| Missing decomposer | Add cleanup, retention, GC, sunset process |

## Output Format

```
ECOSYSTEM ANALYSIS

Inventory (by trophic level / role):
- ...

Niches and overlap:
- ...

Relationship map (type, not just edge):
- ...

Keystone / foundation species:
- ...

Shared resources and saturation status:
- ...

Invasive dependencies / monocultures detected:
- ...

Succession stage per major subsystem:
- ...

Recommended interventions (matched to diagnosis):
1. ...

Risks and trade-offs explicitly named:
- ...
```

## Anti-Patterns to Avoid

- **Treating dependencies as a flat list**: ignoring the relationship type
- **Assuming more diversity is always healthier**: some monocultures earn their efficiency
- **Assuming monocultures are resilient**: efficiency is not robustness
- **Ignoring resource competition**: shared finite resources behave nonlinearly near saturation
- **Missing indirect effects**: trophic cascades — change at one level reshapes levels above and below
- **Treating climax communities like pioneers**: moving fast on load-bearing infrastructure
- **Adopting invasive dependencies because adoption is cheap**: removal is the real cost
- **Owning everything or nothing**: keystone species need *clear* owners, not committees

## Relationship to Other Skills

- Use `network-topology-review` to formalize the dependency graph and quantify centrality of keystone species.
- Use `constraint-analysis` to identify which shared resource is the binding constraint.
- Use `emergence-analysis` when ecosystem-level behavior appears only at scale or near carrying capacity.
- Use `systems-archetypes` when patterns like Tragedy of the Commons (shared resource depletion) or Success to the Successful (winner-take-all niche) apply.
- Use `feedback-loop-analysis` for the population dynamics (predator-prey style oscillations).
- Use `code-forensics` to confirm cascading failure stories with evidence.
