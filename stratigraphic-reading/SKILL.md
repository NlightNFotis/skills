---
name: stratigraphic-reading
description: Read a codebase as geological strata — date layers by idiom, find unconformities where rewrites stopped, identify load-bearing bedrock vs surface sediment. Use before refactoring legacy code so you cut into the right layer.
user-invocable: true
---

# Stratigraphic Reading

Act as a field geologist mapping an outcrop. Geology reads landscapes by recognising that what you see is *layered* — laid down at different times under different conditions, sometimes deformed, sometimes interrupted by an unconformity where deposition stopped or erosion removed everything in between. Codebases are the same. The class you're editing was deposited in 2014 under one paradigm; the function it calls was rewritten in 2021 under another; the helper underneath them dates to the original commit and has never been disturbed because everything depends on it. Cutting into a stratum without knowing its age and what overlies it is how rewrites bury live wires.

`code-forensics` reconstructs a *timeline of an event*. Stratigraphic reading reconstructs the *layered history of a place* — the file, module, or subsystem you're about to change.

Success looks like a labelled cross-section of the area you intend to modify, with each stratum dated, characterised, and assessed for what it supports. Failure looks like "I refactored the helper" without realising the helper was bedrock and three other strata rest on its current shape.

## When to Use This

- Before a non-trivial refactor of legacy code
- Inheriting a module from another team, vendor, or departed author
- A bug whose fix "should be one line" keeps growing
- Pre-rewrite assessment: replace, refactor in place, or wrap?
- Understanding why two parts of the same file look like they were written by different people (they were, decades apart)
- Auditing a critical path where you suspect old, untouched code is doing more work than its surface suggests
- Onboarding into a long-lived codebase

**Escape hatch**: For greenfield code, recently-written code with one author, or code you're about to delete entirely, the layering question is moot. Use this when the code has *history* — when `git log` shows multiple eras.

## Core Questions

- How many distinct strata can I identify in this area?
- What is the age order? Where are the unconformities?
- Which stratum is bedrock — supporting everything above it?
- Which stratum is surface sediment — recently deposited, easy to brush off?
- Where has deformation (later edits) bent earlier layers out of shape?
- What erosion has happened — code removed, leaving a gap others fill awkwardly?
- If I cut here, which strata do I disturb?

## Domain Vocabulary

| Term | Definition | Code analogue |
| --- | --- | --- |
| **Stratum** | A layer deposited under specific conditions | Code written under one paradigm/era/author |
| **Bedrock** | The deepest, oldest, load-bearing layer | Original abstractions everything else depends on |
| **Sediment** | Recent, loose, surface deposits | New code, easy to change, holds little |
| **Unconformity** | A surface where deposition stopped — time gap | A rewrite that didn't finish; a paradigm shift mid-module |
| **Angular unconformity** | New layers laid at an angle on tilted old layers | New idiom bolted onto code with a different shape |
| **Disconformity** | Time gap with no angular change | Code abandoned then resumed in same style years later |
| **Intrusion** | Younger material forced into older layers | A modern feature flag/instrumentation threaded through legacy code |
| **Deformation** | Folding/faulting from later stress | Hot-fix scars, "if (legacy) { ... }" branches |
| **Erosion** | Material removed | Deleted code whose absence shapes what remains |
| **Index fossil** | A characteristic feature that dates a layer | An idiom (e.g., callback style, naming convention, lib version) that pins an era |
| **Cross-section** | Vertical slice showing the layer order | Annotated file or call graph with eras labelled |
| **Principle of superposition** | Lower layers are older (absent intrusion) | In an untouched file, older lines tend to be near the top of the call chain or at the bottom of the dependency graph |
| **Walther's law** | Adjacent facies were once adjacent in time | Code styles that coexist now were once contemporary; sudden style boundary = unconformity |
| **Outcrop** | Where bedrock is visible at the surface | A function in legacy code that's still called directly from the entry point |

### Index fossils for dating code strata

| Fossil | Likely era / paradigm |
| --- | --- |
| Callback hell, no Promises | Pre-2015 JS |
| jQuery selectors | Pre-React UI era |
| `var` everywhere, IIFEs | Pre-ES6 |
| `setState` callbacks, no hooks | React pre-16.8 |
| Threadpool with `synchronized` blocks | Pre-async/await Java |
| Hand-rolled DI containers | Pre-Spring/Guice adoption point |
| Comments referencing JIRA tickets | Era of that tracker |
| Particular ORM patterns | Date of that ORM's dominance |
| Logging style (printf vs structured) | Observability maturity era |
| Magic numbers that match old config defaults | Era of that config schema |

## The Process

### Step 1: Choose Your Outcrop

You can't stratigraph the whole codebase. Pick the file, module, or subsystem you intend to change. Expand the boundary just far enough to include direct callers and direct callees. This is your outcrop.

### Step 2: Date the Strata Using Index Fossils

Walk the code looking for idioms that pin an era. Don't open `git log` first — let the *style* tell you. Then confirm with `git blame` and dates.

```
STRATA INVENTORY:
- Stratum A (oldest): lines ... — fossils: ... — estimated era: ...
- Stratum B: ...
- Stratum C (youngest): ...
```

Weak:

> This file is old.

Strong:

> Top half uses async/await and structured logging (Stratum C, ~2022). Middle uses raw Promises and `console.log` (Stratum B, ~2018). Bottom helpers use callbacks and a custom event emitter (Stratum A, original commit, 2014). Three strata, two unconformities.

### Step 3: Confirm with `git blame` and Build a Cross-Section

Now reach for git. Annotate the file with first-touched dates. Validate or correct your stratigraphy. Produce a cross-section:

```
LINE RANGE   STRATUM   FIRST AUTHOR   FIRST DATE   LAST TOUCHED   FOSSIL
1–40         C         alice          2022-03      2024-01        async/await
41–120       B         bob            2018-09      2019-02        Promise.then
121–end      A         carol          2014-06      2014-08        callbacks
```

Lines whose `last_touched` is much newer than `first_seen` are **deformed bedrock** — old code with hot-fix scars; treat with extra care.

### Step 4: Identify Unconformities

The boundary between strata is where the interesting failures live. Two flavours:

- **Disconformity**: same style resumes after a gap. Usually safe; the abandoned period left no scar.
- **Angular unconformity**: new style bolted onto old, often via an adapter, shim, or `if`-branch. The shim *is the seam*; bugs cluster there.

For each boundary, name what bridges it:

```
UNCONFORMITY between B and A:
- Bridge code: `legacyAdapter()` lines 118–125
- Type translation, error handling shim, or naming reconciliation:
- Risk class: high (style boundary + active translation)
```

### Step 5: Identify Bedrock

Find the stratum the rest *rests on*. Heuristics:

- Imported by everything above; imports nothing in the outcrop
- Touched least often (low blame churn)
- No tests of its own; tested transitively
- Its function names appear in error messages elsewhere
- Removing it would require changes in N other places where N is large

Bedrock is what you must *not* casually change. If your refactor target is bedrock, plan accordingly: characterisation tests first, change in place rarely, more often wrap-and-replace.

### Step 6: Identify Intrusions and Deformation

Look for code that doesn't belong to any stratum's era — modern feature flags threaded through 2014 code, observability calls inside legacy loops, an `if (experimental)` branch in bedrock. These are **intrusions**: younger material pushed down into older layers.

```
INTRUSIONS:
- `flagService.isEnabled('x')` injected into Stratum A function `processOrder` — line 142
- Risk: removing the flag will leave a scar; the function was not designed to branch here
```

Deformation: lines blamed to recent commits in an otherwise-old stratum. Usually hot-fixes. Read the commit message; the fix is often a clue to load-bearing behaviour the original didn't intend.

### Step 7: Write the Cut Plan

Now decide where to cut. Each option has different consequences:

| Cut location | Disturbs | When appropriate |
| --- | --- | --- |
| Surface sediment only | Just Stratum C | Adding a feature, no behavioural change to lower layers |
| Across one unconformity | C and B, plus the bridge | Replacing the bridge or unifying styles |
| Into bedrock | All strata | Rare; requires characterisation tests, broader review, often a wrap-and-replace |
| Add new stratum on top | None existing | Safest; defer the rewrite |

State the chosen cut, the disturbed strata, the bridges that will need re-pouring, and the tests required to pin behaviour at each disturbed layer.

### Step 8: Preserve What You Disturb

Before cutting into older strata, capture their behaviour with characterisation tests. Older code is older for a reason — it has survived selection pressure you do not yet understand. The first test you write is the one that catches the behaviour you didn't know was load-bearing.

After the cut, leave a marker: a comment, an ADR, or a CHANGELOG entry that records "in YYYY-MM, Stratum X was disturbed by Y" so the next geologist can re-date the layer correctly.

## Output Format

```
STRATIGRAPHIC SURVEY

Outcrop: [file/module/subsystem]
Boundary justification:

Strata (oldest → youngest):
- Stratum A — lines/files — era — index fossils — primary author(s)
- Stratum B — ...
- Stratum C — ...

Cross-section (annotated):
- [file: line ranges → stratum]

Unconformities:
- Between A/B: bridge code = ..., type, risk
- Between B/C: ...

Bedrock:
- Identified as: ...
- Evidence (incoming deps, low churn, error message presence):
- Tests covering it: present / absent

Intrusions and deformation:
- Modern code threaded into older strata:
- Hot-fix scars in older strata:

Proposed cut:
- Location:
- Strata disturbed:
- Bridges to rebuild:
- Characterisation tests required before cut:
- Marker to leave after cut:
```

## Anti-Patterns to Avoid

- **Treating the file as one age**: blaming "the legacy code" as a monolith and missing that the bug lives in the 2021 shim, not the 2014 helper.
- **Refactoring bedrock first**: starting with the deepest stratum because it "looks worst" — you'll break everything above before you understand why it survived.
- **Removing intrusions blindly**: that flag is ugly because it's load-bearing in a way the original code wasn't built for; deleting it without replacing the behaviour breaks callers.
- **Trusting current style as evidence of age**: heavily-reformatted code may be old; recently-touched lines in old code are *deformation*, not new strata.
- **Ignoring the bridge**: the unconformity adapter is where bugs cluster; "I left it alone" is not safety — it's avoidance.
- **No marker after disturbance**: future geologists re-date the layer wrongly because you didn't say what you did.
- **Mistaking erosion for absence**: missing functionality that *used to be there* shapes the surrounding code; reading without checking deletion history misses the load.

## Relationship to Other Skills

- Use `code-forensics` for the timeline of a *specific incident*; this skill maps the *durable layered history* of an area.
- Use `entropy-and-code-rot` for the thermodynamic framing of decay; stratigraphy gives you the structural framing of layered deposition.
- Use `evolutionary-pressure` to understand *why* a stratum has the shape it does (what selection pressure preserved it).
- Use `reverse-engineering` once you've identified bedrock with no spec — disciplined inference from observation.
- Use `topological-refactoring` to ensure the cut preserves the essential shape of the layer being modified.
- Use `reversibility-principle` (art conservation) to plan the cut so it can be undone if the disturbed strata reveal hidden coupling.
