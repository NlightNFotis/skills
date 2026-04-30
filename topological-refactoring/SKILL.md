---
name: topological-refactoring
description: Reason about refactoring as continuous deformation that preserves observable behavior — what is essential structure, what is accidental, and which tests must keep passing.
user-invocable: true
---

# Topological Refactoring

Act as a topologist embedded in the engineering workflow. A refactor is a *continuous deformation* of code: the syntactic shape changes, but the observable behavior — the "topology" — must be preserved. Two implementations are *equivalent* not because their source matches but because no observer can distinguish them.

The classic image: a coffee cup and a donut are topologically equivalent because you can deform one into the other without cutting or gluing — they have the same number of holes (one). A refactor that cuts (changes a contract) or glues (merges things that should stay separate) is no longer a refactor; it is a behavioral change in disguise.

The goal is to know — for any proposed change — whether it is a true refactor (preserves shape), a behavior change (cuts or glues), or worse, an accidental shape change masquerading as cleanup.

## When to Use This

- Reviewing a "pure refactor" PR — verifying it really is one
- Restructuring a module without breaking callers
- Migrating from one API to another while preserving semantics
- Deciding what tests *must* keep passing after a change
- Distinguishing essential complexity (real holes) from accidental complexity (wrinkles)
- Estimating blast radius: which observers can see this change?

**Escape hatch**: If the goal is explicitly to change behavior, this skill is the wrong frame — use `failure-mode-effects-analysis` or `formal-invariants` instead. This skill is for changes that *should not* change behavior.

## Core Mindset

A refactor preserves the **observable shape** of a system. To use the topological lens, decide:

1. Who are the **observers**? (Callers, tests, users, downstream services, persistent storage)
2. What can they **observe**? (Return values, errors, side effects, performance characteristics, log lines that other systems parse)
3. Is the proposed change a **continuous deformation** with respect to that observation set?

If yes: it's a refactor. If no: it's a behavior change, and should be reviewed accordingly.

## Core Vocabulary

| Term | Engineering meaning |
| --- | --- |
| **Homeomorphism** | A behavior-preserving bijection between implementations |
| **Continuous deformation** | A change that can be done in small steps with no observer ever seeing a "broken" state |
| **Neighborhood** | The set of code that depends on a given symbol/contract |
| **Connectedness** | Whether a module's responsibilities form a single cohesive unit or several disjoint pieces |
| **Compactness** | Whether the surface area of a contract is bounded and finite |
| **Hole (essential)** | A genuine indirection or abstraction the design *must* have |
| **Hole (accidental)** | A wrinkle introduced by historical accident; can be smoothed away |
| **Boundary** | The contract surface — types, signatures, protocols, persisted formats |
| **Observational equivalence** | Two implementations no observer in scope can distinguish |
| **Semantic preservation** | The change leaves all specified behavior unchanged |

## Equivalence Hierarchy

Two pieces of code can be "the same" at different strengths. Pick the strongest level your refactor needs to preserve.

| Level | Preserves | Example refactor |
| --- | --- | --- |
| **Syntactic equivalence** | Source text (modulo whitespace) | Rename a local variable |
| **α-equivalence** | Up to bound name renaming | Rename a parameter |
| **β-equivalence** | Up to inlining/extracting | Extract a helper function |
| **Observational equivalence** | All observable outputs and effects | Replace bubble sort with quicksort |
| **Contextual equivalence** | Behaves the same in *every* program context | Replace one Map implementation with another |
| **Bisimulation** | Step-by-step matching of state transitions | Refactor a state machine |

A refactor that preserves observational equivalence may still break a caller that does pointer-equality checks, depends on iteration order, or parses a log line. *Define the observers first.*

## The Process

### Step 1: Map the Boundary

Identify the surface across which observation can occur.

```
BOUNDARY:
- Public API (functions, methods, types):
- Errors thrown / returned:
- Side effects (filesystem, network, DB, env):
- Persisted formats (DB schema, file format, wire protocol):
- Log lines / events that other systems consume:
- Performance characteristics callers depend on (latency, memory):
- Concurrency guarantees (thread-safety, ordering):
```

Anything on this list is part of the topology. Anything off this list is interior — free to deform.

### Step 2: Identify the Observers

Different observers see different surfaces.

| Observer | Sees |
| --- | --- |
| Direct callers in this repo | Public types, signatures, exceptions |
| Downstream services | Wire protocol, error codes, latency tail |
| End users | UX, perceived performance, error messages |
| Operators | Logs, metrics, alerts |
| Tests | Whatever the test asserts (often *too much*) |
| Storage | Persisted format; cannot be migrated atomically |

A change is a refactor *with respect to a set of observers*. Be explicit about that set.

### Step 3: Classify Holes

For each abstraction layer (interface, indirection, factory, adapter), ask: is this hole *essential* or *accidental*?

- **Essential**: it exists because the system genuinely has multiple implementations, swap points, or test seams. Removing it would force a behavior change or destroy testability.
- **Accidental**: it exists because someone added it "in case we need it", or it congealed from a sequence of smaller changes. Nobody implements the interface twice. Removing it loses no behavior.

A topological refactor either preserves essential holes exactly or cleanly fills accidental ones. It never silently changes which holes exist.

### Step 4: Choose a Continuous Deformation Path

Prefer changes that can be applied in small steps where every intermediate state compiles and passes tests. This is the engineering analogue of continuity.

Good deformation patterns:

- **Parallel change** (expand → migrate → contract): add the new shape, migrate callers, remove the old shape
- **Branch by abstraction**: introduce an interface, swap implementations, then optionally remove the interface
- **Extract → inline elsewhere**: never have the system in a "half-extracted" broken state
- **Strangler fig**: route progressively more traffic through the new path

Bad (discontinuous) patterns:

- "Big bang" rewrites that leave the system non-compiling between commits
- Renames that change *both* the symbol and its semantics in one step
- Deleting an old code path before all callers are migrated

### Step 5: Apply the "Cut or Glue?" Test

Topology forbids cutting or gluing. In code:

- **Cutting**: introducing a new failure mode, error, or distinction the observer didn't have before. Example: an operation that used to be infallible now returns an error.
- **Gluing**: collapsing a distinction the observer relied on. Example: two error codes that now both map to one; two iteration orders that now coincide; two callers that now share state they didn't share.

For each diff hunk, ask: *is this a cut, a glue, or a stretch?* Only stretches are refactors.

### Step 6: Identify the "Tests That Must Keep Passing"

Refactors are validated by the tests that pin down observable behavior. List them explicitly:

```
INVARIANT TESTS:
- [test name] — pins [behavior]
- [contract test] — pins [boundary]
- [property test] — pins [law]
```

If no test pins a behavior the refactor must preserve, **add the test before refactoring**. This is "characterization testing" — capture current behavior, then deform.

A refactor that requires *changing* a test is not a refactor; the test reveals the behavior change.

### Step 7: Check Implicit Observers

The most dangerous observers are the ones nobody listed:

- Reflection / introspection (class names, method names, field order)
- Serialization (struct layout, JSON key order, default values)
- Hash codes and equality (identity vs structural equality)
- Iteration order of "unordered" collections (downstream code may depend on it)
- Log strings parsed by other tools (operational observers)
- Stack trace contents (test frameworks, error reporters)
- Timing (a much faster or slower implementation may break consumers tuned to the old timing)

Ask: *if I changed nothing visible in the API but reordered fields / changed a hash / sped this up 100x, who breaks?*

### Step 8: Verify Equivalence

For non-trivial refactors:

- Run the existing test suite (necessary, rarely sufficient)
- Add property-based tests asserting old(input) == new(input) over generated inputs
- For wire-format-preserving changes, do a round-trip diff between old and new output
- For performance-relevant code, add a benchmark gate
- Consider running both implementations in parallel ("shadow") and diffing in production

## Output Format

```
TOPOLOGICAL REFACTORING REPORT

Boundary:
- ...

Observers in scope:
- ...
Observers explicitly out of scope:
- ...

Hole inventory:
- Essential: ...
- Accidental: ...

Proposed deformation:
- Steps (each preserves boundary):
  1. ...
  2. ...

Cut / glue check:
- No cuts (no new failure modes / distinctions)
- No glues (no collapsed distinctions)

Invariant tests (must keep passing):
- ...
Tests that change (FLAG: reveals behavior change):
- ...

Implicit-observer risks:
- ...

Verification plan:
- ...
```

## Anti-Patterns to Avoid

- **"Pure refactor" PRs that change a test**: the test change reveals the behavior change
- **Removing an "unused" abstraction without listing observers**: the observer may be a downstream parser, a reflection user, or a future port
- **Big-bang restructuring**: every commit should compile and pass tests
- **Bundling refactor + behavior change**: review and test them separately
- **Trusting "no public API changed"**: implicit observers (logs, ordering, perf) are still observers
- **Deleting before migrating callers**: discontinuous and recoverable only by revert
- **Filling an essential hole**: looks like cleanup, removes a swap point, breaks tests in three sprints
- **Preserving an accidental hole "just in case"**: ossifies the wrinkle

## Relationship to Other Skills

- Use `formal-invariants` to identify the *exact* invariants the refactor must preserve.
- Use `assumption-audit` to surface implicit observers nobody documented.
- Use `code-narrative-review` for the readability side: this skill handles correctness preservation, that one handles clarity gain.
- Use `failure-mode-effects-analysis` if the refactor has any chance of being a behavior change in disguise.
- Use `cognitive-load-review` to weigh whether removing an accidental hole is worth the diff.
