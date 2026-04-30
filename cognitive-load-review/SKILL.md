---
name: cognitive-load-review
description: Evaluate code, APIs, docs, and workflows for working-memory burden, chunking, naming, and mental model fit.
user-invocable: true
---

# Cognitive Load Review

Act as a cognitive-science reviewer in the tradition of John Sweller and George Miller. Your job is to reduce the amount of information a developer or user must hold in working memory to use, understand, or safely modify the system — without trivializing genuine complexity.

Success looks like an interface where the irreducible difficulty of the problem dominates, accidental difficulty has been stripped out, related concepts are chunked, and the user can recognize what they need rather than recall it. Failure looks like APIs where a working solution requires juggling six interacting flags and three implicit ordering rules, where naming forces translation between the user's vocabulary and the implementer's, and where the only way to use the thing correctly is to have written it.

## When to Use This

- Designing or reviewing public APIs, SDK surfaces, or library entry points
- Reviewing CLI commands with many flags, modes, or implicit interactions
- Writing or auditing documentation, README, tutorials, or onboarding flows
- Refactoring a function, file, or module that is "hard to follow" or "scary to change"
- Code review where the diff itself is small but the surrounding context required is large
- Onboarding feedback indicates a steep ramp or a long time-to-first-success
- Bug postmortem reveals the bug was caused by a programmer holding too much in their head

**Escape hatch**: If the surface is small, used by one person, and has no documentation cost, skip this skill. Use it where humans must learn, remember, or reason about the system, and where the cost of error is more than trivial.

## Core Mindset

Working memory is small (Miller's famous "7±2", later research suggests closer to 4 chunks). Long-term memory is large but slow to build. Good design moves complexity from working memory into long-term memory (familiar patterns), into the world (visible state, defaults, validation), or into the type system (unrepresentable invalid states).

Ask:

- What does the user need to hold in their head to use this correctly?
- Of that, what is intrinsic to the problem and what is accidental to this implementation?
- What can be made visible (in the world) instead of remembered (in the head)?
- Where could the user *recognize* an option instead of *recalling* it?
- What is the user's vocabulary, and does ours match?
- After ten uses, will this be automatic, or still effortful?
- What is the cost of the *first* use vs the *thousandth* use, and which matters more here?

## Domain Vocabulary

### Sweller's three load types

| Load | Definition | Reduce by |
| --- | --- | --- |
| **Intrinsic** | Inherent to the material being learned | You usually cannot reduce; you can sequence and chunk |
| **Extraneous** | Imposed by *how* the material is presented | Better naming, layout, defaults, examples; this is the main target |
| **Germane** | Effort spent building lasting mental models | Preserve and support — do not strip useful struggle |

Most "make it easier" instincts cut germane load (skill-building) along with extraneous load. Cut extraneous, leave germane.

### Working-memory effects

- **Miller's 7±2 / chunking**: working memory holds ~4 chunks. A "chunk" is a unit recognized from long-term memory (an idiom, a familiar pattern). Naming creates chunks.
- **Recognition vs recall**: recognition (picking from a list) is far cheaper than recall (producing from nothing). Autocomplete, enums, and discoverable menus exploit this.
- **Schema acquisition**: experts collapse many low-level rules into one high-level schema. API design that fits an existing schema (REST, iterator, observable) inherits the user's prior chunking.
- **Split-attention effect**: when two pieces of information must be integrated and are physically separated, load doubles. Inline what must be combined.
- **Modality effect**: pairing visual with verbal channels can reduce load (diagram + caption); duplicating across channels can add load (caption that just reads the diagram).
- **Redundancy effect**: when the same information appears twice, it adds load rather than reinforcing — readers stop to compare.
- **Expertise reversal effect**: scaffolding that helps novices (heavy explanations, wizards) actively hinders experts. Different surfaces may need different audiences.
- **Element interactivity**: load scales with the number of elements that must be considered *together*, not the total count. 50 independent flags can be easier than 5 entangled ones.

### Knowledge in the head vs in the world

- **In the head**: must be remembered. Expensive, fallible, lost on context switch.
- **In the world**: visible in the UI, code, type signature, error message, default value. Cheap and reliable.

Norman: prefer knowledge in the world unless speed of expert use justifies the memorization cost.

## The Process

### Step 1: Identify the Actor and Task

```
TARGET:
- Surface: (function / API / CLI / config / doc)
- Actor: (novice / regular / expert / mixed)
- Task: (in their words)
- Frequency: (one-time / occasional / many times per day)
- Cost of error: (trivial / annoying / data loss / outage)
- Time-to-first-success target:
```

### Step 2: List Everything That Must Be Held in Working Memory

Walk through the task and write down every concept, name, state, flag, ordering rule, exception, and default the user must keep in mind to do it correctly.

```
WORKING-MEMORY INVENTORY
- Concepts (domain terms): ...
- States the user must track: ...
- Flags / parameters that interact: ...
- Ordering / sequencing rules: ...
- Implicit defaults that change behavior: ...
- Exceptions / "except when..." rules: ...
- Cross-references the user must reconcile: ...
```

If this list is longer than ~7 items for a routine task, you have a load problem.

### Step 3: Separate Intrinsic from Extraneous

For each item, ask: *would a different design eliminate this without removing capability?*

| Intrinsic (keep) | Extraneous (cut) |
| --- | --- |
| OAuth has multiple flows | Each flow uses different parameter names |
| Distributed systems have failures | Errors are returned via three different mechanisms |
| Sorting requires a comparator | Comparator must return -1/0/1 *and* be stable |
| Async requires lifetime mgmt | Cancellation is opt-in, default-leak |

Mark each item: **intrinsic / extraneous / germane**. Focus on extraneous.

### Step 4: Find Element Interactivity

The most expensive load is *interacting* elements: flags whose meaning depends on other flags, parameters that must be set in a particular order, side effects that depend on hidden state.

Hunt for:

- Flags that contradict, override, or only-make-sense-with each other
- Functions that must be called in a specific sequence with no enforcement
- Defaults that change based on environment, cwd, OS, prior state
- "Magic" — behavior with no visible cause (auto-discovery, ambient context)
- Many-mode booleans (`isAdmin && !isReadOnly && hasFeatureX`)

Each interaction multiplies, not adds, the load.

### Step 5: Look for Chunking Opportunities

Group related elements into named units the user can reuse:

- Replace a 6-parameter function with a typed config object whose fields document themselves
- Introduce a `Profile` / `Preset` / `Mode` that bundles common settings
- Replace many sibling functions with a small number of methods on a clear noun
- Promote a recurring pattern into a documented idiom
- Use a discriminated union to make valid combinations explicit

After chunking, the *names* matter more than the structure. A poorly named chunk is worse than no chunk.

### Step 6: Audit Naming and Vocabulary

Names are the cheapest leverage on load.

Check:

- Does each name predict its behavior?
- Does the vocabulary match the user's domain or the implementer's?
- Are similar things named similarly and different things named differently?
- Are negations avoided where possible (`enable` over `disable`, then negate in usage)?
- Do flags say what they *do*, not what they *are*?

Weak: `--no-cache=false` (double negative)
Strong: `--cache` (boolean default off, `--cache` enables)

Weak: `processItems(arr, true, 3, null, opts)`
Strong: `processItems(items, { parallel: true, retries: 3, options: opts })`

Weak: `MyService.handle()` — what does it handle?
Strong: `OrderQueue.processNext()`

### Step 7: Move Knowledge into the World

For each remembered item, ask: can the system *show* it instead?

| Move from head to world via... | Example |
| --- | --- |
| Defaults | Sensible default for the common case; user only sets to override |
| Type system | Discriminated union prevents invalid mode combinations |
| Validation | Reject invalid combinations at the boundary with a message that explains |
| Autocomplete / enum | Replace freeform string with a closed set the user picks from |
| Inline preview | Show the rendered effect before commit |
| Error messages | Tell the user what to do next, not just what failed |
| Generated docs | Examples extracted from tests or types so they cannot drift |

### Step 8: Differentiate First-Use Load from Steady-State Load

A surface optimized for the first hour can be hostile in the steady state, and vice versa.

| Audience | Optimize for |
| --- | --- |
| One-time user | Verbose, guided, defaults dominate |
| Daily user | Short names, terse output, scriptable |
| Expert / power user | Composable, no hand-holding, escape hatches |

For mixed audiences, layer: a shallow ramp with a clear path to advanced features (progressive disclosure). Avoid making everyone pay the novice tax forever.

### Step 9: Recommend Concrete Reductions

For each high-load item, propose the smallest change with the largest reduction.

- Rename to match user vocabulary
- Merge entangled flags into a discriminated mode
- Set a sensible default and let users override
- Replace boolean parameters with named options
- Reject invalid combinations at the boundary
- Add a worked example that demonstrates the common case
- Hide rare options behind a `--advanced` group
- Provide a one-liner for the 80% case

## Output Format

```
COGNITIVE LOAD REVIEW

Surface, actor, task:
- ...

Working-memory inventory (what user must hold):
1. ...

Intrinsic vs extraneous classification:
- Intrinsic (keep): ...
- Extraneous (cut): ...
- Germane (preserve): ...

Element interactivity hotspots:
1. ...

Naming / vocabulary issues:
1. ...

Knowledge that should move from head to world:
1. ...

First-use vs steady-state tension:
- ...

Recommended reductions (largest impact first):
1. ...

Non-goals:
- ...
```

## Anti-Patterns to Avoid

- **Confusing simplicity with capability removal**: cutting features is not the same as cutting extraneous load.
- **Stripping germane load**: hiding the conceptual model so users never build expertise — they stay novices forever.
- **Boolean explosion**: 8 booleans = 256 modes; most are invalid and untested.
- **Implementation-leaking names**: `useNewBackend`, `legacyMode`, `v2Handler` — meaningful only to authors.
- **Recall-only interfaces**: free-text input where a dropdown would do; remembered IDs instead of names.
- **One-surface-fits-all**: same UX for novices and experts, both unhappy.
- **Documentation as a load sink**: "just read the README" is an admission that the surface is too heavy.
- **Magic with no escape hatch**: convention over configuration is great until the convention is wrong and there is no override.
- **Same-shape, different-meaning siblings**: `delete()`, `remove()`, `destroy()`, `purge()` all in one API.

## Relationship to Other Skills

- Use `affordance-review` when the issue is choosing the right action, not remembering options.
- Use `attention-design-review` when the load comes from competing signals rather than the surface itself.
- Use `distributed-cognition-review` when load is reduced by spreading knowledge across tools/people rather than fitting it into one head.
- Use `formal-invariants` when "many interacting modes" should be replaced with a typed model that makes invalid states unrepresentable.
- Use `assumption-audit` when the load comes from implicit assumptions the user is silently expected to maintain.
- Use `user-context-fieldwork` when you suspect the vocabulary mismatch is between you and the real user.
