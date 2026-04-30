---
name: order-and-lattice-thinking
description: Reason about partial orders, joins, meets, and monotonicity to design type lattices, CRDTs, version compatibility, permission models, and dataflow analyses.
user-invocable: true
---

# Order and Lattice Thinking

Act as an order theorist embedded in the engineering workflow. Many systems are not "equal or unequal" but **partially ordered**: one version is *compatible with* another, one permission *implies* another, one type *is a subtype of* another, one CRDT state *subsumes* another. The right primitive for these systems is a **lattice**: a set with a `≤` relation plus operations to combine elements (join, meet) that respect that order.

The goal is to recognize when "boolean" or "totally ordered" thinking is too crude — when the right answer is "these two states are *incomparable*" — and to use lattice machinery to merge, compare, and reason about state without losing information or asserting false orderings.

## When to Use This

- Designing or reviewing a type system, especially with subtyping, generics, or variance
- Implementing CRDTs, eventual consistency, or any merge-of-state operation
- Modeling permissions, capabilities, roles, or trust levels
- Reasoning about version/compat ranges (semver, protocol versions, schema evolution)
- Building a dataflow / abstract interpretation analysis
- Debugging "merge produced wrong result" or "version compatibility check is wrong"
- Hitting a case where two values are neither equal nor unequal — they're *incomparable*

**Escape hatch**: If your domain is genuinely a *total order* (sortable numbers, timestamps, linear stages), don't import lattice machinery — just use `<`. This skill earns its keep when the domain is *partial*.

## Core Vocabulary

| Term | Definition |
| --- | --- |
| **Poset (partially ordered set)** | Set with `≤` that is reflexive, antisymmetric, transitive |
| **Total order** | Poset where every pair is comparable: `x ≤ y ∨ y ≤ x` |
| **Comparable** | `x ≤ y` or `y ≤ x` holds |
| **Incomparable** | Neither holds (write `x ‖ y`) — *not* the same as "equal" or "unequal" |
| **Chain** | Totally ordered subset |
| **Antichain** | Subset where every pair is incomparable |
| **Upper bound** of S | An `x` with `s ≤ x` for all `s ∈ S` |
| **Least upper bound (sup, join, ⊔)** | Smallest upper bound |
| **Lower bound / inf / meet (⊓)** | Dual |
| **Lattice** | Poset where every pair has both a join and a meet |
| **Semilattice** | Has only joins (or only meets) |
| **Complete lattice** | *Every* subset has a join and meet (including ⊥ = ⊔∅ and ⊤ = ⊓∅) |
| **Bottom (⊥)** | Least element |
| **Top (⊤)** | Greatest element |
| **Monotone function** | `x ≤ y ⟹ f(x) ≤ f(y)` |
| **Ascending chain condition (ACC)** | Every increasing chain stabilizes — guarantees iteration terminates |

## Common Engineering Lattices

| Domain | Order | Join (⊔) | Bottom | Top |
| --- | --- | --- | --- | --- |
| Subtyping | "is a subtype of" | least common supertype | `Never` / `Bottom` | `Any` / `Object` |
| Powerset of a set | `⊆` | `∪` | `∅` | full set |
| Boolean lattice | implication | OR | `false` | `true` |
| Interval analysis | `[a,b] ≤ [c,d]` iff `c ≤ a ∧ b ≤ d` | enclosing interval | `[+∞,−∞]` | `[−∞,+∞]` |
| Permission set (capability) | "implies" | union of capabilities | no permissions | superuser |
| Version compat | "is compatible with" | most permissive compat | impossible / no version | universal |
| CRDT G-Counter | per-replica componentwise ≤ | componentwise max | all zero | none (unbounded) |
| CRDT G-Set | `⊆` | `∪` | `∅` | none (unbounded) |
| Vector clocks | componentwise ≤ | componentwise max | all zero | none |
| Optional / Maybe | `None ≤ Some(x)` | `Some` if defined | `None` | (per-value) |

If your domain doesn't fit any of these, the question to ask is *what's the join?* — given two states, what is the least state that subsumes both?

## Core Questions

- Is the relation truly a *partial* order, or am I forcing a total order onto an inherently incomparable domain?
- For two given elements, is there a join? A meet? Are they unique?
- What are ⊥ and ⊤? Do they exist in this domain?
- Is the function I'm computing monotone with respect to the order? If not, why?
- Could two updates be incomparable, and what should "merge" do then?
- Does the lattice have finite height (ACC), or do I need a widening operator?

## The Process

### Step 1: Identify the Order

Write down the relation `≤` and verify the three poset laws:

- **Reflexive**: `x ≤ x`
- **Antisymmetric**: `x ≤ y ∧ y ≤ x ⟹ x = y`
- **Transitive**: `x ≤ y ∧ y ≤ z ⟹ x ≤ z`

If antisymmetry fails, you have a *preorder*, not a poset — equivalence classes may be hidden. If transitivity fails, you don't have an order at all.

### Step 2: Find Incomparable Pairs

This is the diagnostic that distinguishes partial from total order. Construct two elements that are neither `≤` nor `≥` each other.

Examples:

- `{a, b}` and `{a, c}` in a powerset (neither contains the other)
- Permission `{read:posts}` and `{read:comments}` (neither implies the other)
- Vector clocks `[2, 0, 1]` and `[1, 1, 0]` from concurrent replicas

If you cannot construct an incomparable pair, your domain is totally ordered and you don't need lattice machinery. If you can, every operation on the domain must explicitly handle incomparability.

### Step 3: Define the Join

The join `x ⊔ y` is the least element that is `≥` both `x` and `y`. For a lattice to be useful, joins must be:

- **Associative**: `(x ⊔ y) ⊔ z = x ⊔ (y ⊔ z)`
- **Commutative**: `x ⊔ y = y ⊔ x`
- **Idempotent**: `x ⊔ x = x`

These three properties together = a **semilattice**. CRDTs are exactly state-based semilattices: any merge order, any duplicate delivery, same answer.

If your "merge" function violates any of the three, replicas will not converge, retries will produce different answers, and `merge(a, b, c)` will depend on grouping.

### Step 4: Check Monotonicity

For each transformation `f`, ask: does `x ≤ y ⟹ f(x) ≤ f(y)`?

Monotone functions over a complete lattice have well-defined least and greatest fixed points (Tarski–Knaster). Non-monotone functions may oscillate, or terminate with wrong answers.

Common monotonicity bugs:

- Permission *removal* in an additive permission lattice (non-monotone)
- A type narrowing that is not consistent with subtyping (non-monotone in the type lattice)
- A version range that *shrinks* as new versions are released (non-monotone in compat)

If a function must be non-monotone (e.g., revocation), that operation must live *outside* the join-merge machinery and be handled specially.

### Step 5: Use ⊥ and ⊤ Deliberately

- ⊥ is the *uninformative* element: "I know nothing." Useful as a starting point for Kleene iteration.
- ⊤ is the *over-approximating* element: "could be anything." Useful as a safe fallback when the join would explode (widening).

A lattice without ⊥ requires an explicit "no info" sentinel. A lattice without ⊤ has no safe fallback — `widen` is then impossible without changing the lattice.

### Step 6: Verify Termination via Chain Conditions

For lattice-based algorithms (type inference, dataflow, CRDT convergence), termination depends on the lattice structure.

| Property | Guarantee |
| --- | --- |
| **Finite lattice** | All algorithms terminate trivially |
| **Ascending chain condition** (every chain stabilizes) | lfp Kleene iteration terminates |
| **Infinite-height lattice** | Need a widening operator, accept over-approximation |

Cross-reference: `fixed-point-reasoning`.

### Step 7: Use Antichains for "Incomparable Concurrent" Sets

When you have a set of states none of which subsumes another, you have an *antichain*. Maintain antichains explicitly when:

- Tracking concurrent CRDT versions for last-write-wins-with-conflict-resolution
- Reporting type errors (don't keep dominated errors)
- Pareto frontiers in optimization problems
- Showing "candidate" versions in a dependency resolver

### Step 8: Compose Lattices

Lattices compose:

- **Product**: `(A × B)` is a lattice with componentwise join (vector clocks!)
- **Function space**: `A → L` for lattice `L` is a lattice with pointwise join (per-key counters)
- **Lifting**: any set becomes a lattice by adding ⊥ and ⊤ (flat lattice)
- **Smash product / lift**: control how nullability composes

If you can express a complex state as a product of simpler lattices, you get the join for free.

## Output Format

```
ORDER & LATTICE ANALYSIS

Domain:
- ...

Order relation ≤:
- Reflexive: ✓/✗
- Antisymmetric: ✓/✗
- Transitive: ✓/✗

Incomparable pair example:
- ...

Join (⊔):
- Definition:
- Associative / commutative / idempotent: ✓/✗

Bottom / Top:
- ⊥:
- ⊤:

Monotonicity of operations:
- f1: monotone / not / N/A
- ...

Chain condition:
- Finite / ACC / infinite-height-with-widening

Risks:
- ...

Recommended changes:
- ...
```

## Anti-Patterns to Avoid

- **Forcing a total order** (a single "is newer than") on inherently concurrent state
- **Non-idempotent merges** — duplicate delivery breaks convergence
- **Non-commutative merges** — replica order matters, network reorder breaks consistency
- **Pretending incomparable means equal** ("they're both `2` in different dimensions")
- **Using ⊥ as a value** — it's a marker for "no information", not a legitimate state
- **Computing lfp of a non-monotone function** — may not exist; iteration may oscillate
- **Permission models with ad-hoc precedence rules** instead of an explicit lattice
- **Semver checks that aren't monotone** in the version order
- **Joining an unbounded number of antichain elements** without a widening or pruning policy

## Relationship to Other Skills

- Use `fixed-point-reasoning` to compute lfp/gfp on monotone operators over lattices.
- Use `formal-invariants` to assert that joins are A-C-I and operations are monotone.
- Use `topological-refactoring` when changing a lattice's order — it changes what observers can compare.
- Use `ledger-consistency` for the special case of a balance lattice (every credit matched by a debit).
- Use `semantic-precision` when the words "compatible" / "subsumes" / "implies" are doing too much work.
