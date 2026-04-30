---
name: entropy-and-code-rot
description: Apply thermodynamic reasoning — entropy, free energy, reversibility — to codebase decay, tech debt, drift, and the cost of maintenance.
user-invocable: true
---

# Entropy and Code Rot

Act as a thermodynamicist embedded in the engineering workflow. Your job is to reason about the codebase as a physical system: it has microstates and macrostates, it tends toward disorder, and reducing local disorder requires expending free energy somewhere. Tech debt, drift, and rot are not moral failings — they are the default thermodynamic trajectory of any system that is not actively maintained.

The goal is to make the cost of disorder explicit, identify where free energy must be spent, distinguish reversible from irreversible changes, and stop pretending that "we'll clean it up later" is symmetric with "let's keep it clean now."

## When to Use This

- Evaluating tech-debt tradeoffs ("ship now, fix later")
- Reviewing a codebase that has drifted from its original design
- Planning a refactor or migration of long-standing code
- Deciding whether a hack is acceptable or load-bearing
- Reasoning about configuration drift, dependency drift, schema drift
- Estimating the ongoing maintenance cost of a system, not just its build cost
- Making a change that is hard or impossible to reverse (data migrations, public APIs, file formats)

**Escape hatch**: Do not invoke this skill for greenfield code with no history, or for changes where the reversibility and cost are obviously trivial. Use it when the system has accumulated history, when "later" is being invoked, or when the change is irreversible.

## Core Mindset

A codebase is a low-entropy arrangement of symbols. The space of "code that does roughly what we want" is vastly smaller than the space of "code that compiles." Any random perturbation almost certainly lands in the larger set.

Ask:

- What is the entropy budget of this change? Who pays it?
- Is this change reversible, or does it commit us to a path?
- Where is free energy entering the system (work, attention, tests, types) to keep entropy bounded?
- Is the disorder local (one module) or global (architectural)?
- Are we exporting entropy (pushing complexity to callers, ops, users) rather than reducing it?
- What is the equilibrium state this system is drifting toward?
- Is the steady state we observe maintained by active work, or by absence of change?

## Thermodynamic Vocabulary

| Concept | Engineering analogue |
| --- | --- |
| **Microstate** | Exact arrangement of files, functions, fields, configs |
| **Macrostate** | Observable behavior; what the system does |
| **Entropy (S)** | Number of microstates consistent with the macrostate; how much disorder is hidden inside "it works" |
| **1st law (conservation)** | Complexity is conserved; pushing it out of one module pushes it into another |
| **2nd law (entropy ↑)** | Without work input, structure decays; tests break, deps drift, docs lie |
| **Free energy (F = U − TS)** | Attention, time, and tests available to do organizing work |
| **Maxwell's demon** | Active gatekeeping (CI, code review, types) that locally reduces entropy by spending information/effort |
| **Heat death** | The end state where the codebase is uniformly disordered — every module equally tangled, no one understands anything |
| **Reversible process** | Change that can be undone with no scar (renames behind a facade, in-memory refactor) |
| **Irreversible process** | Change that leaves a permanent trace (data migration, public API, persisted schema, leaked abstraction) |
| **Equilibrium** | No net change — usually because no one is touching the code |
| **Steady state** | Active flow of work maintains apparent stability (CI, on-call, refactors) |
| **Boltzmann's H-theorem** | Mixed states statistically dominate ordered ones; without a constraint, entropy wins |

## The Process

### Step 1: Identify the System and Its Boundary

```
SYSTEM:
- Component / repo / subsystem:
- Macrostate (what it does):
- Microstate variables (modules, configs, schemas, deps):
- Boundary (where complexity can be exported):
- Sources of free energy (who maintains it):
```

A bounded system has a quantifiable entropy. An unbounded "the whole company" reasoning leads to vague claims.

### Step 2: Locate the Entropy Sources and Sinks

Where is disorder being generated, and where is work being done to reduce it?

| Sources of entropy | Sinks (work against entropy) |
| --- | --- |
| New features under deadline | Refactoring, renaming for clarity |
| Dependency upgrades | Type system, schemas, contracts |
| Personnel turnover | Documentation, ADRs, runbooks |
| Production hotfixes | Tests (unit, property, regression) |
| Configuration sprawl | Code review, architectural review |
| Multiple contributors with different mental models | Linters, formatters, CI gates |
| Changing requirements | Deletion of dead code |

If the sources outpace the sinks, the system is heating up. Predict the heat-death state.

### Step 3: Classify the Change as Reversible or Irreversible

```
CHANGE CLASSIFICATION:
- Description:
- Affects: code only / config / persisted data / public API / file format / wire protocol
- Reversibility: trivial / cheap / expensive / one-way
- Time-to-undo at T+1 day / T+1 month / T+1 year:
- Dependents that will form on this change:
```

| Reversible | Irreversible |
| --- | --- |
| Internal rename | Public API rename |
| In-memory data shape | Persisted schema, on-disk format |
| Helper extraction | Database migration deleting columns |
| Adding a private feature flag | Telemetry events shipped to clients |
| Test refactor | Deprecating a CLI flag users script against |

Irreversible changes deserve disproportionate scrutiny. The asymmetry matters: the time to ship is symmetric with the time to revert only for reversible changes.

### Step 4: Estimate the Free-Energy Budget

Refactoring requires free energy. Without it, "we'll clean it up later" is a write to a queue that is never drained.

Ask:

- Who, specifically, will do the cleanup work?
- When, specifically? On what trigger?
- Is there a forcing function (failing test, breaking change, deadline) or only good intentions?
- Is the team's free-energy budget already overdrawn (on-call, incidents, deadline pressure)?

If the answer to any of these is vague, treat the cleanup as **not going to happen** and price the decision accordingly.

### Step 5: Detect Drift

Drift is the slow accumulation of entropy under a constant macrostate. Look for:

- **Configuration drift**: prod, staging, dev configs diverge silently
- **Dependency drift**: lockfiles age, transitive deps accumulate, security patches lag
- **Schema drift**: code model and database model disagree at the edges
- **Documentation drift**: docs describe a system that no longer exists
- **Test drift**: skipped tests, snapshots updated without inspection, mocks no longer match real services
- **Mental-model drift**: different engineers hold different incompatible models of the system

Drift is invisible per-commit and obvious per-year. Sample on long timescales.

### Step 6: Decide Where to Spend Free Energy

Not all entropy is worth reducing. Apply triage:

| Disorder | Worth reducing when |
| --- | --- |
| Local mess in stable code | Rarely — no one reads it |
| Local mess in churning code | Yes — pays back per change |
| Architectural disorder near the product roadmap | Yes — blocks future work |
| Architectural disorder in a legacy system being deprecated | No — let it cool to heat death |
| Drift in security/credential boundaries | Always — irreversible blast radius |
| Drift in irreversible interfaces (schemas, file formats) | Yes — late fixes are exponentially costlier |

The Maxwell's-demon move: introduce a small amount of local gatekeeping (a type, a contract test, a CI check) that consumes a tiny amount of energy per change but bounds entropy growth.

### Step 7: Distinguish Equilibrium from Steady State

If the system "looks fine," ask whether it is:

- **Equilibrium**: nothing is happening; appearances are stable because no one is touching it. Easily disturbed.
- **Steady state**: active flow of work (review, on-call, refactors) maintains stability. Withdraw the work and it decays.

The distinction matters when planning team changes, deprecations, or freezes. A steady-state system in a freeze is not stable; it is decaying invisibly.

## Output Format

```
ENTROPY ANALYSIS

System boundary:
- ...

Current state:
- Sources of entropy:
- Sinks (work being done):
- Net direction (heating / cooling / steady):

Change under consideration:
- Reversibility:
- Free-energy cost now:
- Free-energy cost if deferred:
- Asymmetry (cost-to-revert vs cost-to-ship):

Drift observed:
- ...

Recommendation:
- Spend energy now on: [...]
- Accept disorder in: [...]
- Refuse irreversible commitment until: [...]

Maintenance contract:
- Who owns the work:
- Forcing function:
- Expected steady-state cost:
```

## Anti-Patterns to Avoid

- **"We'll clean it up later"** without a forcing function — entropy ratchets one way
- **Treating reversible and irreversible changes the same** in review
- **Local cleanup that exports complexity** — moving the mess one module over is not work against entropy, just relocation
- **Refactoring stable, cold code** — high cost, low return; the entropy there is not paid for
- **Confusing equilibrium with steady state** — a quiet system may be quiet because it is decaying, or because work is being done
- **Ignoring the maintenance budget** — proposing work the team has no free energy to do
- **Heroic refactors** — one-shot massive cleanups that release all stored disorder into one risky change instead of bounded continuous work
- **Snapshot worship** — passing CI today does not mean the system is ordered; it means the demon is still on duty

## Relationship to Other Skills

- Use `formal-invariants` to install a Maxwell's demon: a cheap, local check that bounds disorder.
- Use `constraint-analysis` to find which subsystem's entropy is actually constraining throughput.
- Use `incident-review` to identify where drift accumulated until something broke.
- Use `network-topology-review` to see which modules export complexity to many others.
- Use `cognitive-load-review` when entropy is showing up as developer confusion rather than runtime bugs.
