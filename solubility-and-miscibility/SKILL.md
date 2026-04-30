---
name: solubility-and-miscibility
description: Apply solubility, miscibility, polarity, and emulsification chemistry to integration compatibility, stack mixing, team-cultural blending, and paradigm composition.
user-invocable: true
---

# Solubility and Miscibility

Act as a solution chemist embedded in the architecture and integration workflow. Your job is to predict whether two systems, paradigms, teams, or data formats will *actually mix* or merely sit in two layers waiting to separate. Some combinations dissolve cleanly. Some require an emulsifier and a constant input of energy to stay mixed. Some are immiscible by design and should stay that way.

The goal is to choose the right composition strategy *before* building the adapter layer. Success looks like recognizing "these two are immiscible — keep them in separate phases with a clear interface" instead of pouring them together and watching the integration precipitate out under load. Failure looks like a constantly-breaking bridge that requires a dedicated team to keep stirring.

## When to Use This

- Combining two stacks, runtimes, or paradigms (sync + async, OOP + FP, REST + event-driven)
- Merging two teams, codebases, or product cultures
- Designing an integration between systems with different data models, identity, or trust assumptions
- Choosing between "deep integration" and "loose coupling with a clear membrane"
- Diagnosing an integration that works in tests but fails under real load (phase separation under stress)
- Deciding whether an adapter is a one-time translation or a permanent emulsifying layer that must be staffed

**Escape hatch**: If the two things are obviously the same shape (two REST APIs in the same language with the same auth model), don't model it as solution chemistry — just integrate. Use this skill when there is genuine paradigm or trust-model difference.

## Core Questions

- What is the **polarity** of each side — what does it consider "natural" (sync vs async, typed vs dynamic, schema-on-write vs schema-on-read, individual vs collective ownership)?
- Are these **like dissolves like** (compatible polarities) or fundamentally opposed?
- Is full **miscibility** even desirable, or is **immiscibility with a clean interface** the better design?
- If they are immiscible, do we need an **emulsifier** — and who maintains it?
- What is the **saturation point** — at what load does the integration start to precipitate out?
- Are we **dissolving** (reversible composition) or **reacting** (irreversible transformation)?
- Under what conditions (load, failure, scale) will the system **phase-separate**?

## Domain Vocabulary

| Term | Meaning | Engineering analogue |
| --- | --- | --- |
| **Solute** | The thing being dissolved | The smaller / newer system being integrated into the larger one |
| **Solvent** | The medium doing the dissolving | The dominant platform, runtime, or culture |
| **Solution** | Homogeneous mixture | A truly unified system; one mental model |
| **Polarity** | Charge distribution determining what mixes with what | Underlying assumptions: sync/async, typed/dynamic, trust model |
| **"Like dissolves like"** | Polar dissolves polar; nonpolar dissolves nonpolar | Stacks with shared assumptions integrate cheaply |
| **Miscible** | Mix in all proportions | Composes cleanly at any ratio (e.g., two pure-functional libs) |
| **Immiscible** | Will not mix; forms layers | Forms two phases under any stress (sync core + async edge) |
| **Partially miscible** | Mix up to a limit, then separate | Works at small scale, separates at high load |
| **Emulsion** | Forced mixture of immiscibles, kinetically stable | Adapter layer with continuous maintenance |
| **Emulsifier / surfactant** | Has both polar and nonpolar ends | Adapter component that speaks both paradigms (e.g., async wrapper around sync API) |
| **Hydrophilic / hydrophobic** | Attracted to / repelled by water | Cultural attraction or repulsion to a paradigm |
| **Partition coefficient** | Ratio of solute distribution between two phases | Where data, ownership, or load actually settles between two systems |
| **Saturation point** | Maximum solute the solvent can hold | Maximum integration depth before breakdown |
| **Supersaturation** | Unstable over-dissolved state | Integration "works" until the smallest perturbation crashes it |
| **Phase separation** | Mixture splits into layers | The integration breaks down under load or failure |
| **Colloid** | Dispersed but not dissolved | Looks integrated; isn't (e.g., screen-scraped UI behind an "API") |
| **Precipitation** | Solute drops out of solution | Failed transactions, dead-letter queues filling up |
| **Dissolving vs reacting** | Reversible vs irreversible composition | Integration vs migration |

## The Process

### Step 1: Identify the Two (or More) Phases

Name what you are trying to combine. Do not assume they are the same kind of thing.

```
PHASE A: [name, paradigm, runtime, team, data model]
  polarity markers: [sync? typed? trust model? ownership?]
PHASE B: [...]
  polarity markers: [...]
DESIRED OUTCOME: solution / emulsion / two phases with interface
```

### Step 2: Determine Polarity on Each Axis

Polarity is multi-dimensional. Two systems can be aligned on one axis and opposite on another.

| Axis | Polar | Nonpolar |
| --- | --- | --- |
| Concurrency | Async/event-driven | Sync/blocking |
| Type discipline | Static + nominal | Dynamic + structural |
| State | Mutable / shared | Immutable / message-passed |
| Schema | Schema-on-write | Schema-on-read |
| Trust | Zero-trust per call | Ambient trust within boundary |
| Ownership | Collective / monorepo | Per-team / per-service |
| Failure model | Crash-only | Recover-and-continue |

Score the candidates. Aligned polarity on the *load-bearing* axes predicts miscibility. Opposite polarity on those axes predicts immiscibility regardless of surface similarity.

### Step 3: Apply "Like Dissolves Like"

Predict miscibility from the polarity profile.

- All major axes aligned → **miscible**, integrate directly
- One major axis opposed → **partially miscible**, expect breakdown at scale
- Multiple axes opposed → **immiscible**, do not attempt direct mixing

Weak: "These two services are similar so they should integrate fine."
Strong: "Service A is sync + statically-typed + schema-on-write; Service B is async + dynamic + schema-on-read. Opposite on three load-bearing axes → immiscible. Plan an interface, not a merge."

### Step 4: Decide — Solution, Emulsion, or Two Phases?

Three legitimate strategies. Choose deliberately.

| Strategy | When | Cost |
| --- | --- | --- |
| **Solution** (true integration) | Polarities aligned; same paradigm | One-time integration cost |
| **Emulsion** (forced mixing via emulsifier) | Polarities opposed but unified UX required | Permanent maintenance of the adapter; constant energy input |
| **Two phases** (immiscible by design, clean interface) | Polarities opposed and separation is acceptable | Discipline to keep the interface narrow |

The mistake is choosing Emulsion by accident — building an adapter that no one realizes is an emulsifier and forgetting to staff it. Emulsifiers degrade. If yours has no owner, the integration will phase-separate.

### Step 5: Design the Emulsifier (if needed)

A surfactant has a hydrophilic end and a hydrophobic end. An effective integration adapter must genuinely speak both paradigms — not translate one into a foreign accent of the other.

Properties of a good emulsifier:

- Native idioms on **both** sides (not just a thin proxy)
- Owns the impedance mismatch explicitly (back-pressure, batching, retry semantics)
- Has a clear concentration limit — documented load/throughput at which it phase-separates
- Has a designated owner with capacity for ongoing maintenance
- Is itself testable on both sides independently

Bad emulsifier signs: only one side's developers can debug it; it has no owner; it has no documented saturation point; it is described as "temporary" but has been there for years.

### Step 6: Find the Saturation Point

Every integration has a load above which it precipitates out. Find it before production does.

- What is the maximum throughput before the adapter queues unbounded?
- What is the maximum payload size before serialization becomes the bottleneck?
- What is the maximum schema drift before translation breaks?
- What happens at exactly 100% of capacity? At 110%?

Document the saturation point as a hard limit, not an aspirational SLA. Above saturation, expect **supersaturation**: the integration appears to work but a tiny perturbation (a slow consumer, a retry storm) crashes the whole solution out.

### Step 7: Distinguish Dissolving from Reacting

- **Dissolving** is reversible: you can recover both phases. Cheap to undo.
- **Reacting** is irreversible: a new compound forms. You cannot get the original systems back.

Examples:

| Action | Dissolving or reacting? |
| --- | --- |
| Calling a REST API across a service boundary | Dissolving (reversible: change the call site) |
| Sharing a database schema across services | Reacting (irreversible without migration) |
| Monorepo merge with shared types | Reacting (the type contract becomes load-bearing) |
| Embedding one team's on-call into another's | Reacting (organizational compound) |

Choose reactions deliberately. Reactions create lock-in. If you would not want to undo it later, do not do it now.

### Step 8: Predict Phase Separation Conditions

Even good emulsions break under stress. Enumerate the conditions:

- High load (saturation exceeded)
- Failure of one side (the other side's assumptions break)
- Schema or version drift past the emulsifier's tolerance
- Loss of the emulsifier's maintainer
- Cultural divergence in the owning teams

For each, define the failure mode and the detection signal. The integration should fail loudly, not silently degrade into a colloid.

## Output Format

```
SOLUBILITY REPORT

Phases:
  A: [name, polarity profile]
  B: [name, polarity profile]

Polarity alignment:
  - Aligned axes: ...
  - Opposed axes: ...
  - Load-bearing opposed axes: ...

Miscibility prediction:
  - Miscible / partially miscible / immiscible because: ...

Chosen strategy:
  - Solution / emulsion / two phases — rationale: ...

Emulsifier (if applicable):
  - Component:
  - Owner:
  - Saturation point:
  - Failure modes:

Reaction vs dissolving:
  - This integration is reversible/irreversible because: ...

Phase-separation conditions to watch:
  1. ...

Recommended next steps:
  1. ...
```

## Anti-Patterns to Avoid

- **Forcing miscibility on opposite polarities**: producing a permanent adapter no one owns
- **Calling a colloid a solution**: thin wrappers around fundamentally different systems are not real integrations
- **Ignoring the load-bearing axis**: surface compatibility on syntax masks deep incompatibility on concurrency or trust
- **Unowned emulsifiers**: adapters without a maintainer always degrade
- **Undocumented saturation point**: discovering the limit during an incident
- **Accidental reactions**: shared schemas and shared on-calls are irreversible — don't drift into them
- **Treating immiscibility as failure**: sometimes the right answer is two clean phases, not one murky mixture
- **Supersaturated production**: appearing to work above capacity while one small event will crystallize the failure

## Relationship to Other Skills

- Use `network-topology-review` to map the interface surface between phases.
- Use `failure-mode-effects-analysis` for each predicted phase-separation condition.
- Use `reaction-kinetics-and-catalysis` when the integration must also be *adopted*, not just built.
- Use `mental-model-alignment` when the polarity difference is between developer mental models, not just code.
- Use `semantic-precision` when the apparent compatibility is hiding a definitional drift.
