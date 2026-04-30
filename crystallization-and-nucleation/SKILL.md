---
name: crystallization-and-nucleation
description: Use nucleation, supersaturation, and crystal growth to reason about standards adoption, pattern propagation, and why some ideas suddenly "take" while others remain dissolved.
user-invocable: true
---

# Crystallization and Nucleation

Act as a materials chemist embedded in an adoption or standards review. Your job is to model pattern spread, standards adoption, and convention propagation as a phase transition: a supersaturated solution waiting on a nucleation site, then ordered growth from seed crystals along grain boundaries.

A strong analysis identifies whether the system is supersaturated (primed but not yet crystallizing), names plausible nucleation sites, explains what kind of crystal will grow (and along what defects), and predicts where polymorphism will produce competing crystal structures. A weak analysis just says "we should adopt X" without examining whether the conditions are ripe.

## When to Use This

- Rolling out a new standard, framework, or convention across teams
- Diagnosing why a "obviously better" approach fails to spread
- Choosing the first team or codebase to adopt a new pattern
- Designing a reference implementation, exemplar, or starter template
- Deciding whether to push harder on an unadopted standard or wait for conditions to ripen
- Reviewing a paved-road platform strategy
- Understanding why two parts of the same org converged on different solutions

**Escape hatch**: For mandates that are simply enforced top-down (a regulatory requirement, a security baseline), nucleation is not the model — execution is. Use this skill where adoption is voluntary, where culture and exemplars matter, and where uneven spread is plausible.

## Core Mindset

A pattern does not spread because it is good. It spreads when the medium is supersaturated, a nucleation site appears, and growth proceeds along available structural seams. Without supersaturation, even a perfect seed dissolves. Without a nucleation site, even a supersaturated medium stays liquid indefinitely.

Ask:

- Is the medium actually supersaturated? Is there demand looking for a form?
- What would serve as a nucleation site here — a team, a codebase, a person?
- Is the seed *workable* (a real implementation) or just an idea?
- What grain boundaries (team lines, repo lines, language lines) will the crystal grow along?
- Will the result be a single crystal or a polycrystal with rival structures?
- What polymorphs (same molecules, different crystal structure) are competing?

## Domain Vocabulary

| Term | Meaning | Adoption analogue |
| --- | --- | --- |
| **Supersaturation** | Solution holds more solute than its equilibrium concentration; primed for phase change | Pent-up demand for a pattern; many teams independently solving the same problem badly |
| **Nucleation site** | A location where the new phase first forms | The first codebase / team / project where the pattern instantiates |
| **Homogeneous nucleation** | Crystal forms spontaneously from the bulk medium | A pattern emerges everywhere at once; rare and hard |
| **Heterogeneous nucleation** | Crystal forms on an impurity or surface (much more common) | Pattern adopted around a specific exemplar, library, or champion |
| **Seed crystal** | Deliberately introduced nucleus | Reference implementation, starter template, paved-road repo |
| **Critical nucleus size** | Minimum cluster size below which the new phase redissolves | A seed too small to attract maintainers dies |
| **Crystal lattice / ordering** | Repeating structural pattern | The convention itself: file layout, naming, module shape |
| **Polymorphism** | Same molecules, different crystal structures | Multiple competing implementations of "the same idea" (REST vs gRPC, two CSS systems) |
| **Ostwald ripening** | Small crystals dissolve, large ones grow at their expense | One adoption hub absorbs the others; smaller forks die |
| **Grain boundary** | Interface between crystals of different orientation | Team, repo, or language boundaries where conventions meet and conflict |
| **Defect / impurity** | Irregularity that often serves as nucleation site | A single opinionated engineer; a non-conforming legacy codebase that nucleates a new approach |
| **Amorphous state** | Disordered solid; lacks crystal structure | Codebase with no convention; "every file does it differently" |
| **Annealing** | Slow cooling that lets crystals grow large and orderly | Long, deliberate migration with time for rough edges to smooth |
| **Quenching** | Rapid cooling; freezes in defects | Mandated overnight migration; conventions adopted without adaptation |
| **Conway's Law as crystallization** | System structure mirrors team structure | Crystals grow along team boundaries; cross-team patterns require cross-team grain boundaries |

## The Process

### Step 1: Test for Supersaturation

A pattern only spreads if the medium is primed. Diagnose supersaturation:

- Are multiple teams independently building variants of the same thing?
- Are there recurring complaints that point at the same missing pattern?
- Are bespoke solutions accumulating with no canonical answer?
- Has the existing equilibrium become visibly painful (long onboarding, repeated incidents of one kind)?

If none of these are true, the solution is **undersaturated** — there is no demand looking for form. Pushing a seed into an undersaturated medium produces nothing; the seed dissolves. Wait, or first generate supersaturation by surfacing the cost of the status quo.

```
SUPERSATURATION CHECK:
- Independent variants observed: ...
- Recurring complaints: ...
- Pain of status quo: high / medium / low / invisible
- Verdict: supersaturated / saturated / undersaturated
```

### Step 2: Identify Candidate Nucleation Sites

Crystals form on impurities and surfaces, not in the homogeneous bulk. Find the engineering analogue:

- A codebase with the right shape and an opinionated maintainer
- A new project starting from scratch (most fertile site — no existing crystal to displace)
- A team that already has the pain acutely
- A respected engineer who will champion the seed
- A paved-road or platform team whose output is highly visible

Rank candidates by:

| Factor | Why it matters |
| --- | --- |
| Visibility | Other teams must be able to see the crystal forming |
| Acute local pain | Provides energy to push past nucleation barrier |
| Champion present | Without a maintainer the seed dissolves |
| Greenfield or near-greenfield | No competing crystal to overgrow |
| Trust capital | Other teams will copy from sources they trust |

### Step 3: Make the Seed Crystal Workable

A seed must be a real, working crystal — not a proposal. Required properties:

- Runs end-to-end as a complete example
- Uses the convention in a non-trivial way (toy examples don't seed)
- Documented at the level needed to copy, not the level needed to design
- Above critical nucleus size: enough surface area, callers, or use cases that it cannot dissolve back

Weak seed:

> A design doc proposing a unified logging format.

Strong seed:

> A live service in production using the new logging format end-to-end, with shared library, dashboards, runbook, and one downstream consumer reading those logs successfully.

A seed below critical size redissolves: the doc is forgotten, the prototype is abandoned, the library has no callers.

### Step 4: Predict Growth Along Grain Boundaries

Crystals grow along available seams. In an org, those seams are:

- Team boundaries (Conway's Law)
- Repo boundaries
- Language / runtime boundaries
- Build-system boundaries
- Org-chart reporting lines

Adoption *will not* cross a grain boundary for free. Each crossing requires deliberate work: a translator, a champion in the new grain, an adapted version of the seed.

If your adoption strategy assumes uniform spread across all teams from a single seed, you are assuming a single-crystal growth where reality will give you a polycrystal. Plan for multiple seeds, one per grain.

### Step 5: Watch for Polymorphism

Polymorphism: the same need expressed in two incompatible crystal structures. Common in software:

- Two HTTP frameworks adopted by adjacent teams
- Two state management libraries within one frontend
- Two ways to model auth across services

Polymorphism is stable as long as no grain boundary forces a choice. When it does (a shared library, a merged team, a cross-cutting feature), the result is grain-boundary defects: glue code, adapters, conversion functions — high-stress regions where bugs concentrate.

Decide early: tolerate polymorphism (with explicit interop) or pick one polymorph and dissolve the other. The worst outcome is unacknowledged polymorphism that produces accidental defects at every interface.

### Step 6: Use Ostwald Ripening Deliberately

Ostwald ripening: large crystals grow at the expense of small ones because larger surfaces are more thermodynamically stable. Engineering analogue:

- The dominant adoption hub absorbs satellite efforts
- Forks of similar tools converge on the most-used one
- Smaller libraries get folded into larger frameworks

You can accelerate ripening by:

- Featuring the leading exemplar in onboarding and docs
- Giving the leading hub more maintainer time
- Writing migration tools *from* satellites *to* the leader
- Letting smaller variants quietly atrophy (don't fight them; starve them)

You can prevent unwanted ripening by:

- Protecting small but important variants with explicit ownership
- Documenting why two crystal structures are *intentionally* coexisting

### Step 7: Anneal, Don't Quench

Once the crystal is growing, the choice is *annealing* (slow, deliberate growth that allows defects to smooth out) vs. *quenching* (forced rapid adoption that freezes defects in place).

Annealing looks like: phased rollout, codemod tooling, generous deprecation windows, listening for friction and adapting the convention. The result is large, orderly crystals with few defects.

Quenching looks like: org-wide mandate, hard deadline, no migration support. The result is small, defect-riddled crystals — surface compliance with the convention but pervasive workarounds underneath.

Choose annealing unless there is a security or compliance reason that requires quenching. The crystal you want is one that will still be sound a decade later.

### Step 8: Diagnose Failure Modes

If adoption has stalled, identify which mechanism failed:

| Symptom | Likely cause |
| --- | --- |
| Seed exists, no one copies it | Undersaturation, or seed below critical size |
| Multiple incompatible adoptions | Polymorphism; grain boundaries blocking single crystal |
| Adopted then abandoned | Quenched too fast; defects made it unworkable |
| Stuck at one team | No champion in the next grain; missing translator |
| Re-invented elsewhere unaware | Visibility failure; nucleation site not observable from other grains |
| Frozen at 80% adoption | Ripening stalled; the holdouts have legitimate constraints, not laziness |

## Output Format

```
CRYSTALLIZATION REVIEW

Pattern under consideration:
- ...

Supersaturation:
- Status: ...
- Evidence: ...

Candidate nucleation sites (ranked):
1. ...

Seed crystal:
- Currently exists? Y/N
- Workable? Y/N
- Above critical size? Y/N
- Gaps to fix: ...

Grain boundaries to cross:
- ...

Polymorphism risks:
- ...

Anneal vs. quench:
- Recommended pace: ...
- Why: ...

Recommended sequence:
1. Generate / confirm supersaturation: ...
2. Plant seed at: ...
3. Let it grow until: ...
4. Cross first grain boundary by: ...
5. Ripen by: ...
```

## Anti-Patterns to Avoid

- **Pushing a seed into undersaturation**: no amount of advocacy makes a non-problem crystallize
- **Seeds below critical size**: a doc, a slide deck, or an unmaintained prototype dissolves and is forgotten
- **Assuming single-crystal growth**: adoption stops at grain boundaries unless you plan for multiple seeds
- **Quenching to hit a deadline**: forced overnight migrations freeze in defects that haunt the convention forever
- **Ignoring polymorphism**: two competing crystals coexisting unnamed produces defect-rich grain boundaries
- **Picking the wrong nucleation site**: an invisible team's exemplar cannot seed adoption elsewhere
- **Confusing seeds with standards**: a standards document is not a seed; the *implementation* is

## Relationship to Other Skills

- Use `evolutionary-pressure` to ask whether the medium is *selecting for* the new pattern or merely tolerating it.
- Use `incentive-analysis` to find why supersaturation does or does not exist.
- Use `network-topology-review` to map grain boundaries (team graph, repo graph) before planning adoption paths.
- Use `mental-model-alignment` to identify polymorphism caused by mismatched conceptual models.
- Use `cognitive-load-review` to test whether the seed is workable (small enough to copy, complete enough to use).
- Use `distributed-cognition-review` to ensure the seed is observable from other grains.
