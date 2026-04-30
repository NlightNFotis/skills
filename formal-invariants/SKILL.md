---
name: formal-invariants
description: Discover system invariants and mathematical properties, then design logical rules that can be verified with assertions, contracts, or tests.
user-invocable: true
---

# Formal Invariant Discovery

Act as a mathematician and formal methodist embedded in the engineering workflow. Your job is to understand the system as a collection of states, transitions, constraints, and guarantees; then express the important truths as verifiable rules.

The goal is not to make the code academic. The goal is to find invariants that prevent bugs, clarify assumptions, and make invalid states harder to represent or easier to catch.

## When to Use This

- Designing or reviewing complex business logic
- Debugging state corruption or impossible states
- Refactoring code where behavior must be preserved
- Adding assertions, validation, contracts, or property-based tests
- Understanding protocols, state machines, queues, caches, schedulers, permissions, or parsers
- Looking for hidden assumptions before changing a critical subsystem

**Escape hatch**: If the code is simple data plumbing or already has a clear local bug, do not over-formalize it. Use this skill where invariants would materially improve correctness or understanding.

## Core Mindset

Prefer precise statements over vague confidence.

Ask:

- What must always be true?
- What must never be true?
- What is true before and after each operation?
- Which states are valid, invalid, transitional, or impossible?
- Which quantities are conserved, monotonic, bounded, unique, or ordered?
- Which assumptions are currently implicit but should be explicit?

## The Process

### Step 1: Define the System Boundary

Identify the smallest meaningful system to reason about.

```
SYSTEM:
- Component/module:
- Inputs:
- Outputs:
- Persistent state:
- External dependencies:
- Operations/transitions:
```

Avoid reasoning about the entire application unless the invariant genuinely crosses subsystem boundaries.

### Step 2: Inventory State and Transitions

List the relevant state variables and the operations that can change them.

For each state variable, capture:

- Type or domain
- Valid range or allowed values
- Ownership and mutation points
- Whether it is derived or authoritative
- Whether it persists across calls, turns, sessions, or process restarts

For each transition, capture:

- Preconditions: what must be true before it runs?
- Postconditions: what must be true after it completes?
- Failure behavior: what remains true if it throws, rejects, or partially completes?

### Step 3: Discover Candidate Invariants

Generate candidate invariants from multiple mathematical lenses. Look for properties that are specific enough to verify.

#### Shape and Domain

- Values are non-null only after initialization
- IDs match a required format
- Arrays contain only valid elements
- Optional fields have required companions
- Invalid combinations are unrepresentable or rejected

#### Cardinality and Uniqueness

- IDs are unique within a collection
- There is at most one active item of a given kind
- Every child has exactly one parent
- Counts match the number of stored items

#### Ordering and Monotonicity

- Sequence numbers only increase
- Timestamps never move backward within a session
- Queues preserve insertion order unless explicitly prioritized
- A lifecycle state can only move along allowed edges

#### Conservation and Correspondence

- Every enqueue has a matching dequeue or cancellation
- Every acquired resource is released
- Every emitted event corresponds to a state transition
- Derived indexes match the authoritative collection

#### Security and Authorization

- Untrusted input is validated before use
- Permission checks happen before side effects
- Sensitive values are never logged in unrestricted channels
- User-controlled paths stay within allowed roots

#### Temporal and Concurrency

- A callback cannot run after disposal
- A promise settles at most once
- Cancellation prevents later side effects
- Concurrent operations cannot observe partially updated state

### Step 4: Classify Each Invariant

Not every true statement deserves an assertion. Classify each candidate:

```
INVARIANT:
- Statement:
- Scope: local / module / subsystem / global
- Type: precondition / postcondition / representation invariant / temporal invariant
- Importance: correctness / security / performance / maintainability
- Enforceability: type system / assertion / runtime validation / test / documentation
- Cost of checking:
- Risk of false positives:
```

Prefer invariants that are:

- Cheap to check
- High impact when violated
- Stable across expected product evolution
- Close to the code that can violate them

### Step 5: Make the Rule Precise

Rewrite informal properties into logical, falsifiable statements.

Weak:

> The queue should be consistent.

Strong:

> For every item in `pendingById`, exactly one queue contains that same item ID, unless the item is currently executing.

Weak:

> Users should not access private data.

Strong:

> Before returning a resource with visibility `private`, the caller must have an explicit allow decision for that resource owner.

Use quantifiers when useful:

- **For all** items...
- **There exists exactly one**...
- **If** condition A holds, **then** condition B must hold...
- **Before** operation X, condition P must hold...
- **After** operation X succeeds, condition Q must hold...

### Step 6: Choose the Verification Mechanism

Use the least expensive mechanism that reliably catches violations.

| Mechanism | Use when |
| --- | --- |
| Type system | Invalid states can be made unrepresentable |
| Runtime assertion | Violation indicates an internal bug |
| Input validation | External or user-controlled data may be invalid |
| Unit test | A specific transition or edge case needs coverage |
| Property-based test | Many generated inputs should satisfy the same rule |
| Integration/E2E test | The invariant depends on multiple components |
| Documentation | The rule matters but cannot be cheaply checked |

Do not use assertions for normal user errors or expected external failures. Validate those and return clear errors instead.

### Step 7: Place Assertions at the Right Boundary

Prefer assertion points that maximize signal and minimize noise:

- Immediately after constructing or mutating internal state
- At module boundaries before returning derived results
- Before irreversible side effects
- After parsing, normalization, or deserialization
- In debug/test-only paths if production cost is too high

Avoid scattering duplicate assertions everywhere. If many call sites need the same check, extract a single validation or invariant-checking helper.

### Step 8: Test the Invariant Itself

For each important invariant, verify that the check can fail for the right reason.

Ask:

- Can I construct a minimal invalid state that violates this?
- Does the assertion/test fail with a useful message?
- Does valid behavior still pass?
- Could this assertion reject legitimate future behavior?
- Does this reveal a better type or data model?

If an invariant is hard to test, it may be too vague, too global, or placed at the wrong boundary.

## Output Format

When using this skill, produce a concise invariant report:

```
FORMAL INVARIANT REPORT

System boundary:
- ...

State model:
- ...

Candidate invariants:
1. [Precise statement]
   - Scope:
   - Why it matters:
   - Verification:
   - Suggested assertion/test location:

Recommended implementation:
1. ...

Risks / non-goals:
- ...
```

If implementing changes, make the smallest code change that enforces the highest-value invariant first. Prefer one invariant per edit/test cycle when debugging a subtle issue.

## Anti-Patterns to Avoid

- **Vague invariants**: "state is valid" is not useful unless validity is defined
- **Over-asserting**: too many low-value checks create noise and maintenance burden
- **Asserting user errors**: assertions are for programmer mistakes; validate external input
- **Global reasoning too early**: start with a small boundary and expand only when necessary
- **Ignoring failure paths**: invariants must also hold after errors, cancellation, and cleanup
- **Encoding current bugs as rules**: distinguish intended behavior from accidental behavior
- **Unstable rules**: avoid assertions that are likely to block legitimate product changes

## Useful Mathematical Vocabulary

Use these terms when they clarify reasoning:

- **Invariant**: property preserved across allowed transitions
- **Precondition**: property required before an operation
- **Postcondition**: property guaranteed after an operation
- **Representation invariant**: internal consistency rule for a data structure
- **Monotonicity**: value can move in only one direction
- **Bijection**: one-to-one correspondence between two sets
- **Conservation**: total quantity is preserved across transitions
- **Idempotence**: repeated operation has the same effect as one operation
- **Commutativity**: operation order does not affect the result
- **Totality**: function handles every value in its domain
- **Soundness**: everything accepted is valid
- **Completeness**: everything valid is accepted
