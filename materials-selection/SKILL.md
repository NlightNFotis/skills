---
name: materials-selection
description: Choose tech stack, libraries, and tools by property fit using required-vs-desirable specs, weighted decision matrices, Ashby-style trade-off plots, and lifecycle cost — not hype.
user-invocable: true
---

# Materials Selection

Act as a materials engineer specifying the right material for a load-bearing part. Your job is to translate the system's requirements into a property profile, then select the language, framework, database, message broker, library, or tool that *fits* — not the one that is most fashionable, most familiar, or most general.

The goal is to make selection a defensible engineering decision: properties enumerated *before* shopping, required versus desirable separated, trade-offs visible on a chart, and lifecycle cost (not just acquisition cost) accounted for. A successful selection produces a written justification a successor can audit. A failed selection is "we picked X because everyone uses X" and a future migration nobody budgeted for.

## When to Use This

- Choosing a programming language for a new service
- Choosing a database, queue, cache, or message broker
- Choosing a library among several plausible alternatives
- Choosing a UI framework, build tool, or runtime
- Replacing an existing component because constraints have changed
- Justifying a non-default choice in a design review
- Auditing a stack that "just grew" to identify mismatches between component property and actual load

**Escape hatch**: For trivial libraries (a left-pad-equivalent in a hobby project), this is overkill. Use this skill when the choice is load-bearing, hard to reverse, or contested.

## Core Questions

Ask:

- What load is this component carrying — what are the *required* properties?
- What is *desirable* but negotiable?
- What would have to be true for the popular default to be the wrong answer here?
- What does this cost over its lifetime, not just to install?
- What happens when constraints change — is this material substitutable?
- Am I selecting by fit, by hype, by familiarity, or by habit?
- Would two of these candidates plotted against each other reveal a clear winner, or am I forcing a choice between near-equivalents?

## Property Categories

A property profile spans these categories. Not all matter for every choice; pick the relevant ones.

| Category | Engineering analogue | Software examples |
| --- | --- | --- |
| **Performance / strength** | Yield strength, modulus | Throughput, latency p50/p99, memory footprint |
| **Density / weight** | Mass per volume | Binary size, container size, cold-start time |
| **Temperature / environment range** | Operating temp range | Supported OSes, runtime versions, CPU architectures |
| **Corrosion resistance** | Tolerance to environment | Robustness to malformed input, network flakiness |
| **Fatigue resistance** | Behavior under cyclic load | Behavior under sustained QPS, long-running stability |
| **Machinability / formability** | Ease of fabrication | Developer ergonomics, debuggability, build speed |
| **Sustainability / recyclability** | End-of-life | Migration path off, exportability of data |
| **Cost (acquisition + lifecycle)** | Material + processing | License, hosting, training, maintenance, migration |
| **Availability / standards** | Off-the-shelf? Standard grades? | Maturity, ecosystem, community, hiring pool |
| **Compliance** | Regulatory grade | License (GPL/MIT/proprietary), data residency, audit |

## Domain Vocabulary

| Term | Meaning |
| --- | --- |
| **Property matrix** | Table: candidates × properties, with values |
| **Required property** | Hard constraint; failure to meet eliminates the candidate |
| **Desirable property** | Soft preference; weighted in scoring |
| **Performance index** | Property combination relevant to a use case (e.g., specific strength = strength/density) |
| **Ashby chart** | Plot of two properties; candidates fall in regions; efficient frontier visible |
| **Weighted decision matrix** | Scored property values × weights, summed per candidate |
| **Over-specification** | Choosing a material that exceeds requirements at extra cost |
| **Substitution analysis** | Re-running selection when a constraint changes (e.g., switch from steel to aluminum because weight became binding) |
| **Lifecycle cost** | Acquisition + operation + training + migration + disposal |
| **Fit-to-purpose vs general-purpose** | Specialized component fits one load tightly; general one fits many loads loosely |

## The Process

### Step 1: Write the Requirement Spec Before Shopping

This is the discipline. Do it *before* you look at candidates, or you will retrofit the spec to your favorite.

```
COMPONENT ROLE:
- What this component does in the system:
- Loads it must carry:
  - Functional:
  - Non-functional (latency, throughput, durability, consistency):
  - Operational (deploy targets, observability, scaling model):
  - Compliance (license, data residency, audit):
- Expected lifetime:
- Reversibility (how hard to swap later):
```

If you cannot write this without naming a candidate, stop and try again.

### Step 2: Separate Required from Desirable

Two columns. Be ruthless about what is truly required.

```
| Property | Required value | Desirable value | Weight (if desirable) |
```

Examples of *required*:

- "Must run on customer's air-gapped Linux ARM64 machines" (eliminates anything Windows-only or x86-only)
- "Must support exactly-once semantics for financial events"
- "License must be permissive (Apache/MIT/BSD) — no copyleft"

Examples of *desirable* (weighted):

- "Lower p99 latency is better" (weight 3)
- "Larger ecosystem of plugins is better" (weight 1)
- "Familiarity to current team is better" (weight 2)

A property labeled "required" that is actually negotiable corrupts the entire selection. Be honest.

### Step 3: Assemble the Candidate Slate

List 3–7 candidates. Include:

- The current/default choice
- The popular choice (even if you suspect it is wrong here)
- A specialized fit-to-purpose choice
- A "do nothing / build it ourselves" option, if plausible

Fewer than 3 means you have not actually compared; more than 7 means you are not yet serious.

### Step 4: Build the Property Matrix

For each candidate, fill in measured or researched values for each property.

```
| Property        | Required? | Cand A | Cand B | Cand C | Cand D |
| --------------- | --------- | ------ | ------ | ------ | ------ |
| License         | Apache    | Apache | GPL    | MIT    | Proprietary |
| ARM64 support   | Yes       | Yes    | Yes    | No     | Yes    |
| p99 latency     | <10ms     | 4ms    | 6ms    | 2ms    | 12ms   |
| Memory footprint| <500MB    | 200MB  | 400MB  | 1.2GB  | 150MB  |
| Maintainership  | Active    | Active | Active | Stale  | Vendor |
```

Apply required filters first — eliminate candidates that fail any required property. Do not score them and hope they win on aggregate.

### Step 5: Plot the Ashby Trade-off

Pick the two most contested properties (often performance vs cost, or latency vs ergonomics). Plot candidates on those axes.

```
   high
   |          *D
ergo-|   *A
nomics|       *B
   |   *C
   low|________________
       slow  speed   fast
```

The *efficient frontier* is the set of candidates not dominated on both axes by another. Candidates inside the frontier (dominated) can be eliminated. Candidates on the frontier are the real choice.

This is more honest than a single weighted score, because it shows the reader the trade-off they are accepting.

### Step 6: Compute Performance Indices Where Meaningful

Sometimes the right metric is not a single property but a *combination*. In materials engineering, "specific strength" = strength/density. The software analogues:

- Throughput per dollar (req/s per monthly cost)
- Throughput per memory MB
- Features per LOC of integration glue
- Active maintainers per GitHub-issue backlog

These ratios often expose mismatches that absolute numbers hide.

### Step 7: Compute Lifecycle Cost, Not Acquisition Cost

| Cost element | Why it matters |
| --- | --- |
| Acquisition / license | One-time or recurring fee |
| Hosting / runtime | Per-month operational |
| Training / onboarding | Hours to first useful contribution |
| Maintenance / upgrades | Ongoing engineering hours |
| Observability / tooling | Cost of making it visible in production |
| Migration cost out | If we adopt this and later need to leave |
| Deprecation risk | What if upstream stops maintaining it? |

A "free" library with an unmaintainable API and no migration path can be the most expensive choice on the list.

### Step 8: Decide, Document, and Note Substitution Triggers

```
SELECTION:
- Chosen candidate:
- Why it wins on the required filters:
- What we are accepting (its weak properties):
- What was the runner-up, and why not:
- Substitution triggers — if X changes, re-run selection:
```

The substitution trigger is the most underused output. Future maintainers need to know: *under what changed condition would this choice be wrong?* That is what makes the decision auditable later.

## Output Format

```
MATERIALS SELECTION REPORT

Component role:
- ...

Required properties:
- ...

Desirable properties (with weights):
- ...

Candidate slate:
- ...

Property matrix:
[table]

Eliminated by required filters:
- Candidate X — failed property Y

Ashby plot (two contested axes):
- Axes:
- Frontier candidates:
- Dominated candidates:

Lifecycle cost summary:
- ...

Selection:
- Chosen:
- Rationale:
- Accepted weaknesses:
- Substitution triggers:
```

## Anti-Patterns to Avoid

- **Selecting before specifying**: naming a candidate before writing the requirement spec; the spec then gets shaped to fit
- **All requirements, no desirables**: every property marked "required" so nothing can be eliminated and everything is force-ranked
- **Hype-driven selection**: choosing because of conference talks, GitHub stars, or what a competitor uses
- **Familiarity-driven selection**: choosing what the team knows even when load demands otherwise (or refusing what the team knows out of contrarianism)
- **Over-specification**: picking a distributed database for a workload one Postgres instance would carry for a decade
- **Ignoring lifecycle cost**: optimizing acquisition cost while ignoring training, migration, and exit
- **Single-axis comparison**: comparing only on benchmark numbers and ignoring ergonomics, license, maintainership
- **No substitution trigger**: making an irreversible-feeling choice with no documented condition under which to revisit
- **Forcing a choice between near-equivalents**: when candidates cluster on the frontier, the *choice* matters less than the *commitment* — pick by team fit and move on

## Relationship to Other Skills

- Use `portfolio-theory` when the question is *how to spread bets* across uncorrelated technologies (diversification), not which single material fits one load.
- Use `capital-allocation` when the question is *where to invest engineering effort overall*, not which component to choose for a specific role.
- Use `constraint-analysis` to identify *which* property is the binding constraint before weighting candidates against it.
- Use `optionality-as-value` when reversibility (cost to swap later) dominates the decision and a less-optimal but more-substitutable choice is better.
- Use `commissioning-and-decommissioning` after selection: a chosen material still has to be brought into service and eventually retired.
