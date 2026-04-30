---
name: evolutionary-pressure
description: Apply natural selection thinking to API and codebase evolution — what is being selected for, what drifts, what persists vestigially, and where the system sits on its fitness landscape.
user-invocable: true
---

# Evolutionary Pressure

Act as an evolutionary biologist embedded in the engineering workflow. Your job is to ask what selection pressures are actually operating on this code, who or what is doing the selecting, what variation is available, and what the resulting fitness landscape looks like.

A strong analysis distinguishes selection (directed by pressure) from drift (random change in the absence of pressure), explains why some old features persist as vestiges, and predicts where the codebase will and will not adapt. A weak analysis just says "this code is old" or "this API needs to evolve" without naming the mechanism.

## When to Use This

- Deciding what to deprecate, prune, or invest in across a large API surface
- Explaining why some legacy code persists despite no one defending it
- Diagnosing why a "better" framework keeps losing to an "inferior" incumbent
- Reviewing a fork or competing internal project for likely trajectory
- Planning a rewrite and asking what the new system will be selected for
- Understanding why two teams' code diverges even when starting from the same template
- Choosing between local optimization (refining current design) and structural change

**Escape hatch**: For one-off scripts, single-team tools, or short-lived prototypes, selection pressure is too weak to model. Use this skill where there is a real population of users, callers, or contributors exerting differential pressure over time.

## Core Mindset

Darwin's three requirements for evolution by natural selection:

1. **Variation** — different versions exist
2. **Inheritance** — versions persist across generations (releases, forks, copies)
3. **Differential reproduction** — some versions are kept and propagated more than others

If any of the three is missing, you are not seeing evolution — you are seeing engineering by decree, drift, or stasis. Diagnose which.

Ask:

- What is being selected *for*? What is the actual fitness function?
- Who or what is the *selector* — users, CI, reviewers, an SRE on call, a benchmark?
- What variation exists, and how does new variation enter the system?
- What is inherited across releases, forks, copies, or refactors?
- Is the current state due to selection, drift, or founder effects?
- Where is the system on its fitness landscape — local peak, slope, or valley?
- What would a small change cost vs. a structural jump?

## Domain Vocabulary

| Term | Meaning | Code analogue |
| --- | --- | --- |
| **Selection pressure** | Force that makes some variants reproduce more than others | Customer adoption, on-call pain, perf budget, review standards |
| **Fitness function** | What "more reproductive success" actually measures | Latency, ergonomics, lines deleted, paying customers retained |
| **Fitness landscape** | Topology of fitness across the space of designs | Smooth = tunable; rugged = many local optima; flat = drift dominates |
| **Neutral drift (Kimura)** | Change with no fitness effect, propagated by chance | Naming churn, formatting reshuffles, no-op refactors |
| **Genetic drift** | Random allele loss, strongest in small populations | Idioms that vanish because the one engineer who used them left |
| **Founder effect** | Small starting population fixes traits regardless of fitness | Original team's stack choices outlast their reasons |
| **Punctuated equilibrium (Eldredge–Gould)** | Long stasis broken by rapid change | Years of patches, then a major version rewrite |
| **Vestigial feature** | Once-functional structure now unused but retained | Flags, code paths, columns no one calls but no one removes |
| **Exaptation** | Feature co-opted for a use it didn't evolve for | A debug endpoint that became a load-bearing integration |
| **Red Queen dynamics** | Must keep changing just to maintain relative fitness | Security patches, browser quirks, dep upgrades, API parity races |
| **Arms race** | Coevolving pressure between two parties | Ad-blockers vs. trackers, scrapers vs. anti-bot, attacker vs. WAF |
| **Local optimum** | Best in neighborhood, worse than distant alternatives | "Best-in-class monolith" stuck because no incremental path out |
| **Adaptive radiation** | Rapid diversification into open niches | Plugin ecosystem after a stable extension API ships |
| **Bottleneck** | Population crash that erases variation | Layoff, fork, migration that collapses code variety to one |
| **Selective sweep** | One variant rapidly displaces alternatives | A formatter or lint rule fixed across the org |

## The Process

### Step 1: Identify the Population

Selection acts on populations, not individuals. Name yours.

```
POPULATION:
- Unit of selection: (functions, modules, services, repos, plugins, forks)
- Generation event: (release, deploy, PR merge, fork, copy-paste)
- Population size: (10 plugins? 10,000 callers? 3 services?)
- Timescale: (days, releases, years)
```

Small populations drift; large populations track selection. A 4-service architecture is dominated by founder effects and drift, not natural selection.

### Step 2: Name the Selector and the Fitness Function

The single most common error is assuming you know the fitness function. Make it explicit and *operational*.

Weak:

> The API is selected for being good.

Strong:

> The public SDK is selected by paying customers' integration time-to-first-success. Methods that show up in onboarding tutorials within 14 days are kept and stabilized; methods that don't get tutorial coverage drift, get deprecated, or are silently removed at major versions.

Common selectors and what they actually reward:

- **Users in production** → backward compatibility, error messages, perf at p99
- **Internal callers** → ergonomics for the *most frequent* call pattern, not the cleanest
- **Reviewers** → readability of diffs, not of resulting code
- **CI** → tests passing, not behavior being correct
- **On-call engineers** → debuggability and rollback safety
- **Benchmarks** → whatever the benchmark measures, including pathological cases

### Step 3: Inventory Variation

What variants currently exist or could exist?

- Multiple implementations of the same concern (3 HTTP clients, 2 logging libs)
- Forks, branches, copy-pasted utilities
- Feature flags creating live A/B variants
- Plugins or extensions implementing the same hook differently

If variation is low, evolution is slow regardless of selection strength. If you want adaptation, you must allow variation to exist long enough to be tested.

### Step 4: Distinguish Selection from Drift

For each notable feature of the current code, ask: was this *selected* (because it works better) or did it *drift* (because nothing pushed back)?

| Pattern | Likely selection | Likely drift |
| --- | --- | --- |
| Used hourly by SDK customers | ✓ | |
| Last touched 4 years ago, no callers in repo search | | ✓ |
| Survived 3 rewrites with the same shape | ✓ | |
| Two modules do the same thing slightly differently | | ✓ |
| Removed in a fork and the fork is healthy | (vestigial) | |
| Defended fiercely in code review when changed | ✓ | |

Vestigial code is real. The test is: can you remove it and nothing breaks across the population that exerts selection? If yes, it's vestigial regardless of how old or "load-bearing-looking" it is.

### Step 5: Map the Fitness Landscape

Sketch the topology around the current design.

- **Smooth landscape**: small changes → small fitness changes → safe to optimize incrementally. (E.g., tuning a cache size.)
- **Rugged landscape**: small changes can collapse fitness; you're on a peak surrounded by valleys. (E.g., changing a serialization format.)
- **Flat landscape**: changes don't matter to the selector. Drift dominates. (E.g., bikeshedding internal helper names.)

Position matters:

- **On a local peak**: any direct change makes things worse. Real improvement requires a bridge — a parallel implementation, a migration phase, or accepting a temporary fitness drop.
- **On a slope**: hill-climbing works.
- **In a valley after a recent change**: you may be mid-adaptation; give it time before reverting.

### Step 6: Look for Exaptation and Red Queen Traps

- **Exaptation**: which features are now load-bearing for a purpose they weren't designed for? (Debug logs scraped by dashboards. An internal field used as an external ID. A retry mechanism doing flow control.) These are fragile when "cleaned up."
- **Red Queen**: where are you running just to stay in place? (Browser compat, dep upgrades, security patches.) Red Queen costs are real fitness costs and must be budgeted; they don't produce visible progress but their absence produces visible decay.

### Step 7: Recommend Interventions That Match the Mechanism

Match the intervention to the diagnosis:

| Diagnosis | Intervention |
| --- | --- |
| Drift, no selector | Don't add ceremony; either accept drift or introduce a selector (lint, owner, SLO) |
| Strong selector, low variation | Allow controlled variation (flags, parallel impls, plugin API) |
| Vestigial | Delete and observe; restore only if the population complains |
| Local optimum | Build a bridge (compat layer, dual-run period); do not jump |
| Red Queen | Budget it as ongoing maintenance, not as one-time work |
| Founder effect surviving its reason | Re-justify or replace; don't preserve by default |
| Exaptation | Document the second use before refactoring the first |

## Output Format

```
EVOLUTIONARY ANALYSIS

Population and generation:
- ...

Selector(s) and fitness function(s):
- ...

Variation present:
- ...

Selection vs. drift inventory:
- Selected for: ...
- Drifting: ...
- Vestigial: ...
- Exaptations: ...

Landscape position:
- Smooth / rugged / flat — ...
- On peak / slope / valley — ...

Red Queen costs to budget:
- ...

Recommended interventions:
1. ...
```

## Anti-Patterns to Avoid

- **Assuming the fitness function**: "good code" is not operational; name the actual selector
- **Confusing age with fitness**: old code may be selected, drifting, or vestigial — the test is removal, not date
- **Treating drift as design**: small-team idioms often look like decisions but are founder effects
- **Pruning exaptations**: removing a "useless" feature that quietly props up something else
- **Hill-climbing into a cliff**: applying incremental optimization on a rugged landscape
- **Ignoring Red Queen**: counting maintenance work as failure rather than as the cost of staying alive
- **Forcing variation that has no selector**: producing 3 implementations when nothing chooses between them just multiplies drift

## Relationship to Other Skills

- Use `system-ecosystem-analysis` for *system-wide* ecology, cascades, and resource competition; this skill is narrower — it is about the *mechanism of change* in a single population.
- Use `entropy-and-code-rot` for thermodynamic decay framing; evolutionary pressure asks instead *what is selecting against the rot*.
- Use `apoptosis-and-cell-death` when the recommended intervention is deliberate deletion of vestigial features.
- Use `incentive-analysis` to identify *who* is exerting selection pressure and why.
- Use `constraint-analysis` when the fitness function is dominated by a single bottleneck.
