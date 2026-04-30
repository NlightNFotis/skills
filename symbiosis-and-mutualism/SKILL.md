---
name: symbiosis-and-mutualism
description: Characterize pairwise relationships in dependency networks — mutualism, commensalism, parasitism, amensalism — and decide whether each integration is worth its coevolutionary cost.
user-invocable: true
---

# Symbiosis and Mutualism

Act as an ecologist embedded in a dependency or partnership review. Your job is to characterize each pairwise relationship the system has — with libraries, vendors, plugins, partner teams, customers, integrations — by who benefits, who pays, and how tightly coupled the two organisms have become.

A strong analysis names the relationship type for each pairing, distinguishes obligate (cannot survive without) from facultative (could leave) partnerships, and surfaces hidden parasitic loads or endosymbiotic entanglements. A weak analysis just lists dependencies and their versions.

## When to Use This

- Reviewing a new third-party dependency before adoption
- Evaluating an existing vendor or partner relationship
- Designing a plugin or integration API
- Auditing a microservice architecture for coupling character
- Deciding whether to sponsor, fork, or abandon an open-source dependency
- Negotiating a platform-customer or producer-consumer relationship
- Diagnosing why a "simple" library upgrade keeps cascading

**Escape hatch**: For trivial, leaf-level utilities (a single-purpose pure function library you could rewrite in an afternoon), full symbiotic analysis is overkill. Use this skill when the relationship is non-trivial, long-running, and has coevolutionary potential.

## Core Mindset

In ecology, no two species coexist neutrally for long. Every persistent pairwise relationship has a sign for each party: + (benefits), 0 (unaffected), or − (harmed). The full matrix gives the relationship type, and the type predicts long-run behavior far better than intentions or contracts do.

Ask:

- Who benefits from this relationship today, and by how much?
- Who pays the cost, and is the cost visible to the payer?
- Is this obligate or facultative — could either party survive separation?
- Are we coevolving — does our roadmap shift when theirs does?
- Where is this relationship on the parasite ↔ mutualist spectrum, and is it drifting?
- If we deeply integrated (endosymbiosis), can we still extract?

## Domain Vocabulary

| Type | Sign for A | Sign for B | Software example |
| --- | --- | --- | --- |
| **Mutualism** | + | + | Stable open-source dep with reciprocal contribution; healthy platform/builder |
| **Commensalism** | + | 0 | Reading a public API that costs the provider nothing extra |
| **Parasitism** | + | − | Library that consumes maintenance attention without giving back |
| **Amensalism** | 0 | − | Your traffic patterns degrade a shared service without benefiting you |
| **Competition** | − | − | Two internal teams building the same thing, slowing each other |
| **Neutralism** | 0 | 0 | Coexisting libraries that don't interact (rare in practice) |

Other key terms:

| Term | Meaning | Software analogue |
| --- | --- | --- |
| **Obligate symbiont** | Cannot survive without the partner | A service that cannot start without a specific vendor's API |
| **Facultative symbiont** | Benefits from the partner but can survive alone | A library you use but could swap or vendor in a week |
| **Endosymbiosis** | One organism lives *inside* the other; full integration (e.g., mitochondria) | A SaaS deeply embedded — auth, data model, UI all entangled |
| **Host–parasite arms race** | Each adaptation provokes a counter-adaptation | Anti-bot vendor vs. scrapers; client SDK vs. backend changes |
| **Parasitic load** | Cumulative cost of all parasites on a host | Total maintenance tax across all "+/−" dependencies |
| **Cleaner symbiosis** | Partner removes harmful elements (mutualism through service) | Linters, formatters, security scanners as paid integrations |
| **Brood parasitism** | Parasite tricks host into raising its young | Plugins that capture your users into the plugin's ecosystem |
| **Coevolution** | Each party's evolution constrains the other's | API breaking changes that force every caller to adapt in lockstep |
| **Mutualism breakdown** | Once-mutualistic relationship turns parasitic | Dep maintainer abandons; vendor pivots away from your use case |

### Vendor vs. partner — the operational distinction

Often conflated, but ecologically distinct:

- **Vendor**: facultative, transactional. You pay; they deliver. Substitutable in principle. Coevolution is bounded by contract.
- **Partner**: obligate or near-obligate, coevolving. Their roadmap is your roadmap. Substitution is structurally hard.

Most "vendor" relationships drift toward "partner" without anyone noticing. Naming the transition is the point of this skill.

## The Process

### Step 1: Enumerate Pairwise Relationships

Resist listing only direct deps. Include:

- Libraries and frameworks
- SaaS vendors and APIs you call
- Internal services your service depends on
- Internal services that depend on your service
- Plugin / extension authors
- Partner teams (informal contracts)
- Customer segments with non-trivial integration with your roadmap

```
RELATIONSHIPS:
- [name] [kind: lib/vendor/service/team/customer]
```

### Step 2: Score Each Relationship

For each pairing, fill in:

```
RELATIONSHIP: us ↔ X
- Sign for us: + / 0 / −
- Sign for them: + / 0 / −
- Type: mutualism / commensalism / parasitism / amensalism / competition / neutralism
- Obligate or facultative (for us): ...
- Obligate or facultative (for them): ...
- Coevolution rate: low / medium / high
- Specific benefits we receive: ...
- Specific costs we pay: ...
```

Be ruthless about the costs side. Hidden costs include:

- Maintenance attention (upgrades, security patches, breaking changes)
- Cognitive surface area (the team has to know this exists)
- Coupling tax (your design constrained by their constraints)
- Migration tax-in-advance (the eventual cost of switching, discounted)
- Brand/trust risk (their incidents are your incidents to your users)

### Step 3: Distinguish Obligate from Facultative

The single most important question: *if this partner disappeared tomorrow, what would survive?*

| Test | Facultative | Obligate |
| --- | --- | --- |
| Could replace within a sprint | ✓ | |
| Already have a backup or abstraction layer | ✓ | |
| Their API is in your domain language | ✓ | |
| Your data model is shaped by their schema | | ✓ |
| Their identifiers leak into your URLs | | ✓ |
| Switching requires customer-visible change | | ✓ |
| They can break your system without your code changing | | ✓ |

Obligate is not bad — mitochondria are obligate and we're glad of it. But obligate must be *chosen*, not drifted into.

### Step 4: Detect Endosymbiosis

Endosymbiosis is when integration crosses a boundary of no return — extraction would now require redesigning the host, not just swapping the partner.

Symptoms:

- Their data types appear throughout your domain code
- Their auth model is your auth model
- Their UI components determine your UX patterns
- Their outages are indistinguishable from your outages to your users
- Onboarding new engineers requires teaching them the partner's mental model

Endosymbiosis can be a winning strategy (mitochondria gave us aerobic life) or a trap (dependency on a single vendor's pricing power). The diagnostic question is: *did we get a capability we could not have built, in exchange for the loss of independence?*

### Step 5: Watch for Drift Toward Parasitism

Mutualisms decay. Causes:

- The partner's strategy shifts; what was reciprocal becomes one-sided
- Your usage shrinks below their attention threshold; you become a cost to them
- Their usage of you shrinks; you keep paying maintenance with no traffic
- Maintenance burden grows as both sides accumulate compatibility shims
- The arms race intensifies (security, anti-abuse) and consumes the value

Periodically re-score relationships. A relationship that scored (+, +) two years ago may now be (+, −) or (−, −).

### Step 6: Detect Brood Parasitism in Plugin Ecosystems

If you offer a plugin/extension API, ask whose ecosystem the plugins actually serve. Brood parasitism patterns:

- Plugin captures user data and re-routes it to the plugin's own backend
- Plugin uses your platform as a discovery channel but converts users off it
- Plugin's branding overshadows yours in the user's mental model
- Plugin requests permissions it doesn't need for its stated purpose

The platform's defenses are scoped permissions, transparent data flow, and limits on what plugins can do with user attention.

### Step 7: Recommend Per-Relationship Action

Match action to type and direction:

| Type | Action |
| --- | --- |
| Healthy mutualism | Invest in the relationship; contribute upstream; co-design |
| Commensalism, stable | Leave alone; document the implicit dependency |
| Commensalism drifting toward parasitism | Reduce surface area; contribute or fork |
| Parasitism (you parasitized) | Reduce, vendor in, replace, or fork |
| Parasitism (you parasitizing) | Acknowledge the cost you impose; consider sponsoring or contributing back |
| Amensalism | Add isolation (rate limits, separate infra) |
| Endosymbiosis (chosen) | Lean in; document the decision and its terms |
| Endosymbiosis (drifted) | Build extraction optionality before it becomes existential |

### Step 8: Budget the Coevolutionary Cost

Coevolution is not free. For each high-coevolution relationship, ensure there is named, scheduled work to absorb their changes — version-bump days, breaking-change response runbooks, deprecation watches. If this work is unbudgeted, it will eventually erupt as an incident.

## Output Format

```
SYMBIOSIS REVIEW

Relationships inventoried: N

Per-relationship table:
| Partner | Type | Obligate? | Coevolution | Drift |
| --- | --- | --- | --- | --- |
| ...     | ... | ...       | ...         | ...   |

Endosymbiotic entanglements:
- ...

Parasitic loads (we pay):
- ...

Parasitic loads (we impose):
- ...

Mutualism-breakdown risks:
- ...

Recommended actions:
1. ...

Coevolution budget required:
- ...
```

## Anti-Patterns to Avoid

- **Listing without scoring**: a dependency list with no sign-pair analysis is inventory, not ecology
- **Assuming vendor stays vendor**: relationships drift toward partner without notice; recheck periodically
- **Ignoring the cost we impose**: you may be the parasite in some relationships and should know it
- **Drifting into endosymbiosis**: integration choices made for a quarter become structural for a decade
- **Treating obligate as bad**: chosen obligate partnerships can be enormously productive; only *unchosen* obligation is the failure
- **Counting only direct deps**: customers, plugins, and internal teams are also symbionts
- **Skipping the coevolution budget**: high-coevolution relationships need staffed response capacity, not just a Slack channel

## Relationship to Other Skills

- Use `system-ecosystem-analysis` for the *whole-graph* ecology — cascades, resource competition, trophic structure; this skill is about the *character of specific pairwise edges* in that graph.
- Use `network-topology-review` for structural properties (centrality, blast radius); this skill is about the *biological character* of each link.
- Use `incentive-analysis` to predict how a partner's behavior will change as their incentives shift.
- Use `evolutionary-pressure` to predict drift over time in a coevolving pair.
- Use `apoptosis-and-cell-death` when the recommended action is to terminate a parasitic relationship.
