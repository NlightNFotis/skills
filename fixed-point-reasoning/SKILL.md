---
name: fixed-point-reasoning
description: Reason about iterative systems — retries, type checkers, schedulers, autoscalers, eventual consistency, dataflow — using fixed points, convergence, and contraction.
user-invocable: true
---

# Fixed-Point Reasoning

Act as a numerical analyst embedded in the engineering workflow. Many systems are not one-shot computations but *iterative loops*: apply an operator, observe the result, apply again, until nothing changes. The mathematical name for "nothing changes" is a **fixed point**: `f(x) = x`. Whether your loop converges to one, oscillates, or diverges is usually decidable from the structure of `f`.

The goal is to know — *before* shipping — whether your retry policy, scheduler, type checker, autoscaler, or replication protocol will reach a steady state, and what that state will look like. "Iterate and hope" is the failure mode this skill exists to prevent.

## When to Use This

- Designing or reviewing retry / backoff loops
- Implementing or analyzing a type inferencer, constraint solver, or dataflow analysis
- Reasoning about schedulers, autoscalers, rate limiters, or controllers (PID, AIMD)
- Working with eventual consistency, CRDTs, gossip, or anti-entropy protocols
- Debugging oscillation: counts that flap, queues that grow then shrink then grow
- Proposing a "self-healing" system that should converge after a perturbation

**Escape hatch**: A pure straight-line computation with no feedback is not a fixed-point problem — don't force the framing.

## Core Vocabulary

| Term | Meaning |
| --- | --- |
| **Fixed point** | `x*` such that `f(x*) = x*` |
| **Operator / step function** | The `f` applied each iteration |
| **Iterate** | The sequence `x₀, f(x₀), f(f(x₀)), …` |
| **Convergence** | The iterate sequence approaches a limit |
| **Divergence** | The sequence grows without bound or never settles |
| **Oscillation** | The sequence cycles without settling |
| **Attractor** | A *region* the system tends toward (may not be a single point) |
| **Contraction** | `f` shrinks distances: `d(f(x), f(y)) ≤ k·d(x,y)` for some `k < 1` |
| **Monotone operator** | `x ≤ y ⟹ f(x) ≤ f(y)` (in some order) |
| **Least fixed-point (lfp)** | Smallest `x*` with `f(x*) = x*` (start from ⊥) |
| **Greatest fixed-point (gfp)** | Largest such `x*` (start from ⊤) |
| **Kleene iteration** | Compute lfp by `⊥, f(⊥), f²(⊥), …` |
| **Steady state** | The fixed point a real system converges to under continuous input |

## Three Fixed-Point Theorems Worth Knowing

| Theorem | Condition | Guarantee | Engineering use |
| --- | --- | --- | --- |
| **Banach** | `f` is a contraction on a complete metric space | Unique fixed point; iteration converges from *any* start, geometrically | AIMD, Newton's method, linear-rate retry decay |
| **Tarski–Knaster** | `f` is monotone on a complete lattice | Both lfp and gfp exist | Type inference, dataflow analysis, CRDT merges, set-based constraint solving |
| **Brouwer** | `f` is continuous on a compact convex set | At least one fixed point exists | Game-theoretic equilibria, schedulers in bounded resource spaces |

The practical takeaway: if you can show your operator is a contraction *or* monotone on a lattice, you usually get convergence for free. If you cannot show either, you must reason about oscillation and divergence explicitly.

## Core Questions

- What is the *operator* `f`? What state does it transform?
- What is the *initial state*? Does the answer depend on it?
- Does a fixed point exist? Is it unique?
- Is `f` a contraction (distances shrink)? Monotone (order preserved)?
- What is the *rate* of convergence? How many iterations before "close enough"?
- What perturbations can knock the system off its fixed point, and does it recover?
- Is the loop bounded — can it run forever, and is that acceptable?

## The Process

### Step 1: Identify the Operator

Write down `f` explicitly. State its domain and codomain.

```
OPERATOR:
- Name:
- Input state shape:
- Output state shape (must match input shape for fixed-point reasoning):
- Side effects per iteration:
- External inputs that change between iterations (if any):
```

If `f` reads new external input every iteration, the system has a *moving* fixed point — a target that drifts. Reason about steady-state behavior under the assumption that input is held constant, then about tracking error when it isn't.

### Step 2: Choose the Right Fixed-Point Framework

Match the operator to a theorem:

| If `f` is… | Use |
| --- | --- |
| Numeric, contractive (Lipschitz constant `k < 1`) | Banach: unique fp, geometric convergence |
| Monotone over a lattice (sets, types, intervals) | Tarski–Knaster: lfp via Kleene iteration from ⊥ |
| Bounded, continuous, no monotonicity | Brouwer: existence only, not uniqueness or constructive |
| None of the above | You must reason about oscillation/divergence directly |

For monotone-on-lattice operators, the standard implementation pattern is **Kleene iteration**:

```
x = bottom
loop:
    x' = f(x)
    if x' == x: break
    x = x'
```

This is the engine inside type inferencers, constant propagation, reachability analysis, and CRDT state merges.

### Step 3: Decide lfp vs gfp

For monotone operators, both exist — the question is which you want.

- **lfp (start from ⊥, climb up)**: "smallest set of facts consistent with the rules". Used for *inductive* definitions: reachable nodes, derivable types, may-alias analysis.
- **gfp (start from ⊤, climb down)**: "largest set still consistent". Used for *coinductive* definitions: bisimulation, liveness, must-alias, "everything that could fail".

A common bug is computing lfp when you needed gfp or vice versa. Symptom: an analysis that is "too pessimistic" or "too optimistic".

### Step 4: Prove (or Bound) Termination

Fixed-point loops must terminate. Justify it:

- **Ascending chain condition**: every increasing chain stabilizes (true for finite lattices, intervals over a finite domain, etc.)
- **Widening operator**: for infinite-height lattices, use a `widen(x, x')` that overshoots to force termination (standard in abstract interpretation)
- **Iteration cap + fallback**: bound iterations and define what to do at the cap

```
TERMINATION ARGUMENT:
- Lattice height: finite / infinite
- Mechanism: ACC / widening / iteration cap
- Worst-case iterations:
- Behavior on cap: error / conservative result / partial result
```

### Step 5: Distinguish Convergence, Oscillation, Divergence

For numeric or feedback systems, classify the dynamics.

| Pattern | Symptom | Common cause |
| --- | --- | --- |
| **Convergence** | iterate stabilizes | Contractive operator |
| **Geometric convergence** | error halves each step | Contraction with `k ≈ 0.5` |
| **Oscillation around fp** | flapping ±δ | Step size too large; missing damping |
| **Limit cycle** | repeats every N steps | Operator is periodic, not contractive |
| **Divergence** | unbounded growth | Operator amplifies (`k > 1`) |
| **Chaos / sensitive dependence** | small input change → wildly different orbit | Nonlinear operator near a bifurcation |

Real-world examples:

- **Retry with no jitter**: synchronized retries → thundering herd → oscillation
- **Autoscaler with high gain**: scale up → load drops → scale down → load returns → oscillation
- **AIMD (TCP)**: contractive on average → converges to a fair share
- **Type inference with recursive types**: needs gfp or coinduction to terminate

### Step 6: Distinguish Fixed Point from Attractor

A *fixed point* is `f(x*) = x*`. An *attractor* is a set the system tends toward but may circle within. A stable orbit is an attractor without being a fixed point. If your system "settles into a small range" rather than a single value, it has reached an attractor, not a fixed point — model it as such.

### Step 7: Handle Eventual Consistency / CRDT Convergence

For replicated state:

- The merge operator must be a **join** in a *semilattice* (associative, commutative, idempotent)
- Each replica's state climbs monotonically in the lattice
- All replicas converge to the lfp ≥ all observed updates
- Cross-references: `order-and-lattice-thinking`

If your "merge" is not associative-commutative-idempotent, replicas will *not* converge — you have a consistency bug, not a tuning problem.

### Step 8: Test Convergence Empirically

For systems where the operator is too complex to analyze:

- Inject a perturbation; measure time to return within ε of steady state
- Run with a frozen input and verify the iterate stabilizes
- Run with adversarial inputs designed to cause oscillation
- Plot the iterate; visual inspection often reveals limit cycles

## Output Format

```
FIXED-POINT ANALYSIS

System under analysis:
- ...

Operator f:
- Input/output shape:
- External inputs per iteration:

Framework:
- Banach / Tarski–Knaster / Brouwer / none
- Justification:

Choice of lfp vs gfp (if applicable):
- ... because ...

Termination argument:
- ...

Predicted dynamics:
- Converge / oscillate / diverge / cycle
- Rate:

Risks:
- ...

Recommended changes:
- ...
```

## Anti-Patterns to Avoid

- **"Iterate until nothing changes" with no termination proof** — infinite loops in type checkers and analyzers come from here
- **lfp where gfp was needed** (or vice versa) — produces results that look right but are systematically wrong
- **Retry policies without jitter** — guarantees oscillation under load
- **High-gain controllers** — produce limit cycles instead of convergence
- **Treating an attractor as a fixed point** — your monitoring will flap
- **Non-associative or non-idempotent "merges"** in replicated systems — replicas will never converge
- **Ignoring moving targets** — steady-state analysis assumes input is held constant; tracking error matters when it isn't
- **Comparing floats with `==`** in the convergence test — use `|x' − x| < ε`

## Relationship to Other Skills

- Use `order-and-lattice-thinking` to verify that your state space is actually a lattice and your operator is monotone.
- Use `feedback-loop-analysis` for the dynamics of retries, queues, and reactive loops where stability is the question.
- Use `formal-invariants` to assert that the iterate respects a monotonicity invariant per step.
- Use `error-and-approximation-analysis` to choose ε and reason about accumulated rounding in the iterate.
- Use `ledger-consistency` when the fixed point is a balance (every acquire matched by a release).
