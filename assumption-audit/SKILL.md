---
name: assumption-audit
description: Surface hidden assumptions in code, specs, designs, and debugging plans; classify which are guaranteed, validated, trusted, inherited, or unsafe.
user-invocable: true
---

# Assumption Audit

Act as an epistemologist embedded in the engineering workflow. Your job is to identify what the current code, design, plan, or debugging theory assumes to be true; then decide whether those assumptions are justified, validated, risky, or false.

The goal is to prevent bugs caused by invisible premises. Make assumptions explicit, testable, and located at the right boundary.

## When to Use This

- Before implementing a feature with unclear requirements
- Before refactoring code with implicit behavior
- During design review or API review
- When debugging has stalled or keeps circling the same theory
- When code depends on external systems, user input, environment state, timing, ordering, permissions, or data shape
- When a proposed fix sounds plausible but rests on unstated beliefs

**Escape hatch**: Do not audit every trivial line of code. Use this skill when hidden premises could affect correctness, security, UX, reliability, or maintainability.

## Core Questions

Ask:

- What must be true for this code/design/plan to work?
- How do we know that is true?
- Where is it enforced?
- What happens if it is false?
- Who or what is trusted to keep it true?
- Is this assumption stable, or likely to change?
- Should this be encoded in types, validation, assertions, tests, docs, or product decisions?

## Assumption Categories

Classify each assumption into one of these categories:

| Category | Meaning |
| --- | --- |
| **Guaranteed** | Enforced by the type system, data model, protocol, or a stronger upstream invariant |
| **Validated** | Checked at runtime before use |
| **Asserted** | Treated as an internal invariant; violation means programmer error |
| **Tested** | Covered by tests but not enforced at runtime |
| **Documented** | Written down but not mechanically enforced |
| **Trusted** | Assumed because another component, user, service, or process is expected to behave |
| **Inherited** | Assumed because existing code already relies on it |
| **Unsafe** | Important but not guaranteed, validated, tested, or documented |
| **False** | Evidence contradicts it |

## The Process

### Step 1: Define the Audit Target

Set a clear boundary. Avoid auditing the whole world.

```
AUDIT TARGET:
- Code/design/plan under review:
- Intended behavior:
- Inputs:
- Outputs:
- State touched:
- External dependencies:
- Main risk if wrong:
```

### Step 2: Extract Explicit and Hidden Assumptions

Look for assumptions in:

- Function parameters and return values
- Object shapes, optional fields, IDs, paths, timestamps, and status values
- Ordering, timing, concurrency, cancellation, and retries
- Permissions, authentication, authorization, and trust boundaries
- Environment variables, filesystem state, OS behavior, network state, and dependencies
- User intent, UX expectations, defaults, and migration behavior
- Tests, mocks, fixtures, and generated data
- Error handling and cleanup paths

Use this prompt:

> For this to be correct, what must already be true?

### Step 3: Classify Each Assumption

Use a compact table:

```
ASSUMPTIONS:
1. [Assumption statement]
   - Category:
   - Evidence:
   - Enforcement location:
   - If false:
   - Risk:
```

Be precise. Replace vague statements with falsifiable ones.

Weak:

> The input is valid.

Strong:

> `request.repository` is non-empty and has the form `owner/name` before it is passed to repository resolution.

Weak:

> The operation happens in order.

Strong:

> A cancellation event cannot be processed after the session has emitted its final shutdown event.

### Step 4: Rank by Risk

Prioritize assumptions by:

- Severity if false
- Likelihood of being false
- Distance from enforcement point to use point
- Whether user input or external systems are involved
- Whether failure is silent, confusing, or security-sensitive
- Whether the assumption is likely to change

```
RISK RANKING:
1. [Highest-risk assumption] — because [...]
2. ...
```

### Step 5: Decide What to Do

For each high-risk assumption, choose the cheapest appropriate treatment:

| Treatment | Use when |
| --- | --- |
| Make invalid state unrepresentable | The type/data model can encode the rule cleanly |
| Validate input | Data comes from users, files, network, env vars, CLI args, or external systems |
| Assert invariant | Violation means an internal bug and should be caught early |
| Add a test | The assumption is behavioral and can regress |
| Add telemetry/logging | The assumption may fail in production but should not crash |
| Document contract | The rule matters to maintainers or callers but is not cheap to enforce |
| Ask for clarification | The assumption is a product or requirements decision |
| Reject the approach | The plan relies on an assumption that is false or too fragile |

Do not turn normal user errors into assertions. Validate them and return clear errors.

### Step 6: Trace Assumption Chains

Important assumptions often depend on earlier assumptions. Trace the chain until you reach enforcement or uncertainty.

Example:

```
Assumption: This path is safe to write.
Depends on:
1. The path was normalized.
2. The normalized path remains inside the workspace root.
3. Symlinks cannot escape the workspace root.
4. The workspace root itself is trusted.
```

If any link is unsafe, the whole chain is unsafe.

### Step 7: Convert Risky Assumptions into Action

Produce concrete next steps. Prefer changes close to the boundary where the assumption first becomes knowable.

Good actions:

- Add a parser/validator at the input boundary
- Refine a type or introduce a discriminated union
- Add an assertion after a state transition
- Add a regression test for a violated assumption
- Rename a variable/API to clarify the contract
- Document a non-obvious invariant near the code that relies on it
- Ask the user/product owner to decide an ambiguous behavior

Avoid vague actions like "be careful" or "handle edge cases better."

## Output Format

When using this skill, produce:

```
ASSUMPTION AUDIT

Audit target:
- ...

Key assumptions:
1. ...

Highest-risk assumptions:
1. ...

Recommended actions:
1. ...

Clarifications needed:
- ...

Non-goals:
- ...
```

If implementing changes, start with the highest-risk unsafe or false assumption. Make the smallest change that enforces, validates, tests, or documents it.

## Anti-Patterns to Avoid

- **Treating assumptions as facts**: mark how you know something, not just what you believe
- **Auditing too broadly**: narrow the boundary until the analysis is actionable
- **Over-validating internal state**: use types or assertions for internal invariants where appropriate
- **Trusting mocks too much**: mocks often encode assumptions that real dependencies violate
- **Ignoring failure paths**: assumptions also matter after errors, cancellation, cleanup, and partial work
- **Assuming existing behavior is intended**: inherited assumptions may be accidental
- **Leaving unsafe assumptions unnamed**: if you decide to accept risk, say so explicitly

## Relationship to Other Skills

- Use `formal-invariants` when an assumption should become a durable invariant.
- Use `popperian-debug` when an assumption is part of a debugging hypothesis and needs to be falsified.
- Use future adversarial/security review skills when assumptions cross trust boundaries.
