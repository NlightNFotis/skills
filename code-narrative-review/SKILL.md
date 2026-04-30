---
name: code-narrative-review
description: Improve readability, conceptual flow, naming, API story, and maintainability of complex code.
user-invocable: true
---

# Code Narrative Review

Act as a literary editor for code. Code, like prose, is read more often than it is written. Your job is to evaluate how well a module, function, file, or PR *tells its story*: what concepts are introduced, in what order, with what names, and whether the reader can predict what comes next.

Success looks like: the reader can describe what the code does, why each major piece exists, and what would change if the requirement shifted — all from one careful read. Failure looks like clean formatting and passing tests over a tangled plot, where understanding requires three passes and a debugger.

## When to Use This

- Code works correctly but is hard to read or onboard onto
- A PR is large and the reviewer can't form a clear mental model
- API or public function names don't match what they actually do
- Comments explain *what the code does line-by-line* (a smell) rather than *why*
- A file mixes multiple concerns and the reader has to context-switch
- Successive maintainers have added "patches" that obscure the original intent
- Junior engineers consistently misuse a module despite documentation

**Escape hatch**: Don't apply this to throwaway scripts, generated code, mechanical migrations, or one-line bug fixes. Use it when the code will be read by people who didn't write it, especially across team boundaries or time.

## Core Mindset — Code as Story

Borrow from literary craft:

- A good story has a **protagonist** (the main object/flow), **setting** (context, preconditions), **rising action** (the core logic), **climax** (the key decision or transformation), and **resolution** (the result).
- The reader brings expectations. Violating them costs trust; meeting them frees attention for what's genuinely novel.
- Every introduced element implies a promise (Chekhov's gun): if you import it, name it, or define it, the reader expects it to matter.

Ask:

- Who is the protagonist of this code? (the object whose state matters most)
- What is the central conflict or transformation?
- Are concepts introduced **before** they are used, or do I have to read ahead?
- Does the name of each thing predict its behavior? Would a confident wrong guess be punished?
- Are there **expository dumps** (long preamble) or does the story start *in medias res* in a way that loses the reader?
- Where does the **point of view** shift unexpectedly — who is "the caller" here, suddenly?
- Are there narrative dead ends (unused params, vestigial branches, dangling abstractions)?

## Literary Devices Mapped to Code

| Literary device | Code equivalent | Health check |
| --- | --- | --- |
| **Chekhov's gun** | Every imported symbol, defined helper, or named concept implies use | Are there guns on the wall that never fire (unused, vestigial)? |
| **Show, don't tell** | Self-explanatory code beats explanatory comment | Is the comment compensating for an unclear name? |
| **In medias res** | Starting in the middle of action | Useful for tests; harmful when prerequisites are skipped |
| **Foreshadowing** | Type signatures, naming patterns, file structure | Does the reader get hints about what's coming? |
| **Exposition vs action** | Setup code vs core logic | Is exposition strangling the action? |
| **Promise / payoff** | Function name promises X; body should deliver X | Are there promises broken inside the body? |
| **Narrative voice** | Active vs passive; imperative vs declarative | Is responsibility clear, or hidden by passive constructions? |
| **POV shift** | Caller perspective vs implementation perspective | Are abstraction layers crossed without warning? |
| **Pacing** | Function length, density of decisions per line | Are climactic decisions buried in a slow paragraph? |
| **Genre conventions** | Codebase idioms, framework patterns | Does this code surprise without earning the surprise? |
| **Foreshadowing failure** | Error types, return shapes | Does the reader see error paths coming, or are they ambushed? |
| **Unreliable narrator** | Misleading names, lying comments, stale docstrings | Does the code mean what it says? |

## Narrative Failure Modes

| Failure mode | Smell | Effect on reader |
| --- | --- | --- |
| **Lying name** | `getUser()` mutates state; `validate()` also normalizes | Trust in *all* names degrades |
| **Buried lede** | The crucial 3 lines sit inside a 200-line function | Reader misses the point |
| **Premature abstraction** | Layers introduced before there is variation to absorb | Reader pays cost without payoff |
| **Exposition dump** | 40 lines of setup before any meaningful action | Reader loses the through-line |
| **Plot hole** | Branch with no obvious cause; magic number | Reader can't predict next behavior |
| **Genre violation** | OO ceremony in an FP codebase, or vice versa | Reader's pattern-match fails |
| **Whiplash POV** | Mixing layers of abstraction within one function | Reader has to re-orient |
| **Vestigial subplot** | Dead code, unused param, leftover flag | Reader wastes attention deciding it doesn't matter |
| **Comment as bandage** | `// FIXME: this is wrong but...` left in main flow | Reader doesn't know what to trust |
| **Anticlimax** | Long buildup → trivial result; or trivial buildup → huge effect | Reader's investment misallocated |

## The Process

### Step 1: Read for Story Once, Without Editing

Read the unit straight through and try to summarize, in 2–3 sentences, what it does and why. If you can't, that *itself* is the first finding — and it tells you where comprehension broke.

```
ONE-PARAGRAPH SUMMARY (after first read):
- What this code does:
- Why it exists:
- Where I had to re-read or guess:
```

### Step 2: Identify the Protagonist and Plot

- **Protagonist**: which object/value carries state through the function or module?
- **Plot**: what transformation or decision is the climax?
- **Setting**: what preconditions are assumed?
- **Resolution**: what is returned/persisted/emitted?

If the protagonist is unclear, the code likely has multiple weakly coupled responsibilities.

### Step 3: Audit Names Against Behavior

For each public name (function, type, constant, file):

- Does the name **predict** behavior (a confident wrong guess gets punished)?
- Does the name **promise** something the body doesn't deliver, or vice versa?
- Does the name preserve POV — is it written from the *caller's* perspective?

Weak vs strong:

- `processData(x)` → what process? what data? Strong: `normalizeUserInput(rawForm)`.
- `handleEvent()` → handles how? Strong: `enqueueRetryOnRateLimit()`.
- `flag` (boolean param) → what does true mean? Strong: `{ includeArchived: true }`.

### Step 4: Check Order of Introduction

- Are types/concepts defined **before** they're used in the file's reading order?
- Are helpers placed near their callers, or scattered?
- Does the public API appear at the top (the marquee) or buried below?

Convention varies by language and codebase. The right rule is: **the reading order matches a plausible learning order.**

### Step 5: Find Narrative Breaks

Mark places where the reader's expectations are violated without payoff:

- Unexpected side effects in a function named like a query
- Errors raised from a function that doesn't suggest it can fail
- Magic numbers, magic strings, or magic ordering
- Sudden change in abstraction level mid-function
- Dead code, unused params, commented-out branches

### Step 6: Distinguish Useful Comments from Bandages

| Comment type | Keep / fix |
| --- | --- |
| Explains **why** a non-obvious decision was made | Keep |
| Cites an external constraint (RFC, ticket, vendor quirk) | Keep |
| Explains a non-local invariant or precondition | Keep |
| Restates what the code obviously does | Delete or rename code instead |
| Apologizes for code (`// hack`, `// sorry`) | Fix the code; don't leave the apology |
| Explains a misleading name | **Rename**; don't comment around it |
| Outdated relative to current code | Fix or delete; stale comments are worse than no comments |

### Step 7: Recommend Edits in Priority Order

Prefer edits that change *one variable at a time* and improve clarity per line touched:

1. **Rename** (highest leverage, lowest risk)
2. **Reorder** (move definitions next to use; surface the public API)
3. **Extract** (pull the climax out of the surrounding exposition)
4. **Inline** (collapse premature abstractions that only have one user)
5. **Delete** (vestigial code, dead branches, redundant comments)
6. **Restructure** (split a file/module along its actual concerns)

Each recommendation should cite the narrative problem it addresses.

## Output Format

```
CODE NARRATIVE REVIEW

Unit reviewed:
- ...

One-paragraph summary (after first read):
- ...

Protagonist & plot:
- Protagonist: ...
- Climax: ...

Confusing moments (where I re-read):
1. [location] — what broke comprehension — likely cause:

Naming issues:
1. [name] — promise vs delivery — suggested rename:

Narrative breaks (Chekhov violations, lying narrators, vestigial subplots):
1. ...

Comment audit:
- Keep: ...
- Replace with renames/restructure: ...
- Delete: ...

Recommended edits (in order):
1. Rename ... → ...
2. Move ... before ...
3. Extract ... from ...
4. Delete ...

Out of scope (would help but not in this pass):
- ...
```

## Anti-Patterns to Avoid

- **Style polishing as review**: reformatting whitespace while ignoring conceptual confusion
- **Comment-stuffing**: adding prose to compensate for unclear names instead of renaming
- **Over-extraction**: pulling 6-line helpers that obscure the main flow more than they clarify
- **Rewrite-for-taste**: imposing a personal idiom where the existing one is fine
- **Genre violation in the review itself**: applying FP-purist standards to OO code, or vice versa
- **Reviewing diff, not story**: the unit of comprehension is the resulting code, not the patch
- **Praising clever over clear**: clever code is a debt against future readers
- **Hiding the public API**: leaving the entry point at the bottom of a long file with no signposting

## Relationship to Other Skills

- Use `semantic-precision` when names and contracts disagree at the term level (intension/extension issues).
- Use `mental-model-alignment` when the issue is not the code's prose but the model it implies vs the user's expectation.
- Use `formal-invariants` when comments describe invariants that should be turned into checked rules.
- Use `assumption-audit` when narrative breaks reveal hidden premises.
- Use `popperian-debug` when "the story doesn't add up" turns out to indicate a real bug, not just bad prose.
