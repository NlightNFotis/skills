---
name: proof-tactics
description: Apply mathematical proof techniques — induction, contradiction, contrapositive, cases, construction — to argue about loop invariants, recursion termination, exhaustiveness, and edge cases.
user-invocable: true
---

# Proof Tactics

Act as a working mathematician embedded in the engineering workflow. When code involves a loop, a recursive function, a state machine, or a claim about *all* inputs, "I tested it on three cases and it worked" is not an argument — it's a sample. This skill brings the standard proof tactics (induction, contradiction, contrapositive, exhaustive cases, construction) to bear on the engineering question: *do you actually have a reason to believe this code is correct?*

The goal is not formal proof in Coq. The goal is to know which tactic the situation calls for, write the argument in plain English with enough rigor that holes are visible, and use counterexamples to kill claims that don't survive scrutiny.

## When to Use This

- Adding or reviewing a loop with a non-obvious invariant
- Writing or reviewing recursion — does it terminate, is it correct?
- Claiming "this handles all cases" — is the case analysis exhaustive?
- A design doc claims a property "always holds" without justification
- A subtle edge case (empty input, single element, max value, negative, zero) keeps biting
- Reviewing a "convince me this terminates" or "prove this can't happen" argument
- Trying to demonstrate that a refactor preserves behavior

**Escape hatch**: For straightforward, well-tested code with no claims of universal correctness, formal argument is overkill. Use this skill when correctness depends on *all* inputs, *all* paths, or *all* iterations.

## The Proof-Tactic Toolbox

| Tactic | Form | Use when |
| --- | --- | --- |
| **Direct proof** | Assume P, derive Q | Most "if-then" claims |
| **Contrapositive** | Prove `¬Q ⟹ ¬P` instead of `P ⟹ Q` | The negation is easier to reason about |
| **Contradiction** | Assume `P ∧ ¬Q`, derive ⊥ | Existence-of-counterexample feels easier than direct |
| **Cases** | Partition into exhaustive cases, prove each | Behavior depends on input shape |
| **Counterexample** | Exhibit a single case where the claim fails | Disprove a universal claim |
| **Weak induction** | Base + `P(n) ⟹ P(n+1)` | Properties indexed by ℕ |
| **Strong induction** | Base + `(∀k<n. P(k)) ⟹ P(n)` | Recursive calls on smaller-but-not-just-`n−1` |
| **Structural induction** | One case per data constructor | Trees, lists, ASTs, recursive types |
| **Well-founded induction** | Induction over any well-founded relation | Termination of recursion on non-numeric measures |
| **Construction** | Build the witness explicitly | Existence claims |
| **WLOG** ("without loss of generality") | Reduce by symmetry | Argument is identical under swap/relabel |
| **Vacuous truth** | `P ⟹ Q` is true if P never holds | Empty-input cases |

## Core Questions

- Is this a claim about *one* input or *all* inputs?
- If "all", over what set? Is the set finite, countable, well-founded?
- What's the right induction principle for this set?
- What is the *invariant* maintained across iterations / recursive calls?
- What is the *measure* that strictly decreases (proves termination)?
- Have I covered all cases, or am I implicitly assuming a default?
- If I cannot prove it, can I find a counterexample? (Often the faster route.)

## The Process

### Step 1: State the Claim Precisely

A claim that can't be precisely stated can't be proved or disproved.

Weak:

> The function works correctly on lists.

Strong:

> For every finite list `xs` of integers, `sort(xs)` returns a permutation of `xs` whose elements are non-decreasing.

A precise claim has:

- A clear domain (`every finite list of integers`)
- A clear conclusion (`returns a permutation of xs whose elements are non-decreasing`)
- No hidden quantifiers ("usually", "typically" → not provable)

### Step 2: Choose the Tactic

Match the claim shape to a tactic:

| Claim shape | Tactic |
| --- | --- |
| `∀x. P(x) ⟹ Q(x)` | Direct or contrapositive |
| `∀n ∈ ℕ. P(n)` | Induction (weak/strong) |
| `∀ tree t. P(t)` | Structural induction |
| `recursive call f(small) terminates` | Well-founded induction |
| `∃x. P(x)` | Construction (exhibit x) |
| `¬∃x. P(x)` (i.e. `∀x. ¬P(x)`) | Direct or contradiction |
| `at least one of A, B, C` | Cases |
| `the universal claim X is false` | Counterexample |

### Step 3: For Loops — Write the Loop Invariant

A loop is a tiny induction. Document:

```
LOOP INVARIANT: at the top of each iteration, _____ holds.
```

Three obligations:

1. **Initialization**: invariant holds before the first iteration.
2. **Maintenance**: if invariant holds at the top of an iteration *and* the loop body executes, invariant holds at the top of the next iteration.
3. **Termination**: when the loop exits, invariant + ¬(loop condition) ⟹ the desired postcondition.

Example — binary search:

```
INVARIANT: if `target` is in `arr`, it is in `arr[lo..hi]`.
INIT: lo=0, hi=len(arr) — true trivially.
MAINTAIN: each iteration narrows lo or hi while preserving the invariant.
TERMINATE: when lo > hi, target is not in any subrange ⟹ not in arr.
```

If you cannot state an invariant, the loop's correctness is unjustified — even if it passes tests.

### Step 4: For Recursion — Identify the Measure

Recursion terminates iff *every* recursive call decreases some well-founded measure.

```
MEASURE: a function from arguments to a well-founded set
- Often: input list length, tree depth, n itself, lex pair (a,b)
- The measure must strictly decrease at every recursive call
- The measure must be bounded below (well-founded)
```

Common bugs:

- Recursing on `n−1` but not handling `n = 0` (no base case → infinite recursion on negatives)
- Recursing on a "smaller" subproblem that isn't actually smaller (e.g. reversing then recursing)
- Mutual recursion where each function decreases its own argument but not the joint measure

For mutual recursion, use a *lex measure*: `(which_function, argument)`.

### Step 5: For Exhaustiveness — Enumerate Cases

When the proof splits into cases, the cases must be:

- **Exhaustive**: every input falls into some case
- **Mutually exclusive** (preferred but not required): no overlaps that contradict

Use the type system to enforce exhaustiveness where possible:

- Discriminated unions / sum types with non-exhaustive-match warnings
- Sealed class hierarchies
- Exhaustive `switch` on enums with the compiler enforcing coverage

When the language can't help, write the case list explicitly *in code* and assert at the end:

```ts
function f(x: A | B | C) {
  if (x.kind === "A") return ...;
  if (x.kind === "B") return ...;
  if (x.kind === "C") return ...;
  const _exhaustive: never = x;  // compile error if a case is missed
  throw new Error("unreachable");
}
```

The `never` trick turns case-exhaustiveness into a proof obligation the compiler discharges.

### Step 6: Use Counterexamples Aggressively

A counterexample is the cheapest proof. To disprove `∀x. P(x)`, exhibit one `x` for which `P(x)` is false.

Routine inputs to try:

- Empty (empty string, empty list, empty map, zero-length array)
- Single element
- Two elements, equal vs different
- Maximum / minimum representable value
- Boundary (off-by-one: 0, 1, n, n−1, n+1)
- Negative, zero, positive
- Duplicate / repeated elements
- Already-sorted / reverse-sorted (for sorts)
- NaN, Infinity, ±0 (for floats)
- Unicode boundary cases (combining marks, surrogate pairs, RTL)
- Concurrent: same operation from two threads simultaneously

If you can produce a counterexample, the proof is over. Skip directly to fixing the claim or the code.

### Step 7: Existence vs Uniqueness

"There is one" and "there is exactly one" are different claims and need different proofs.

- **Existence**: construct a witness. (`such an x exists, namely _____`)
- **Uniqueness**: assume two such, prove they're equal. (`if x and x' both satisfy P, then x = x'`)

Common bug: proving existence and assuming uniqueness. Many systems silently assume "there is exactly one" — verify it explicitly.

### Step 8: Distinguish Vacuous from Substantive

`∀x ∈ ∅. P(x)` is *vacuously true*. This often hides bugs:

- "All zero items in the cart sum to total" — true but useless if "the cart can be empty" is the actual error mode
- "All retries succeed" — vacuous if retries are 0
- "Every user with this flag is valid" — vacuous if no user has the flag (and you're surprised)

When a claim feels too easy to prove, check whether you've proved a vacuous version of it.

## Output Format

```
PROOF SKETCH

Claim:
- ∀ ____, ____ ⟹ ____

Tactic chosen:
- [induction / cases / counterexample / construction / ...]
- Justification:

Argument:
- Base case / case 1: ...
- Inductive step / case 2: ...
- ...

For loops: invariant + initialization + maintenance + termination
For recursion: measure + base case + decrease per call

Edge cases checked:
- Empty: ...
- Singleton: ...
- Boundary: ...
- Adversarial: ...

Counterexample search:
- Tried: ...
- None found / FOUND: ...

Confidence:
- High / medium / low because ...
```

## Anti-Patterns to Avoid

- **"It works on the cases I tried"** as a claim of universal correctness
- **Loops without an invariant** — if you can't state one, you don't know what the loop does
- **Recursion without a decreasing measure** — termination is unjustified
- **Implicit "default" branches** — exhaustive case analysis must be checked, not assumed
- **Confusing existence with uniqueness**
- **Vacuous proofs that miss the actual failure mode** (empty inputs)
- **WLOG without checking the symmetry** — reducing cases by claiming symmetry that doesn't hold
- **Skipping the base case** — induction without a base proves nothing
- **Inductive step that uses `P(n+1)` to prove `P(n+1)`** — circular
- **Treating "I can't think of a counterexample" as proof** — try harder

## Relationship to Other Skills

- Use `formal-invariants` to turn the loop invariant or postcondition into an asserted runtime check.
- Use `assumption-audit` to surface preconditions the proof depends on.
- Use `popperian-debug` when the bug *is* a counterexample to a claim you thought was true.
- Use `fixed-point-reasoning` for termination of iterative analyses (well-founded induction over the lattice).
- Use `dimensional-analysis` to verify the measure has consistent units across recursive calls.
