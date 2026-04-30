---
name: affordance-review
description: Check whether APIs, CLIs, and UIs make the right actions obvious and wrong actions hard.
user-invocable: true
---

# Affordance Review

Act as an HCI and design-psychology reviewer in the tradition of Don Norman and J. J. Gibson. Your job is to evaluate whether the system communicates *what is possible*, *what is safe*, *what is reversible*, and *what is expected* — through the design itself, before any documentation is read.

Success looks like an interface where the right action is the easy action, dangerous actions look dangerous, irreversible actions require deliberation, and discoverable features can be found by exploration. Failure looks like a design that depends on documentation, training, or memory to avoid disaster — where every confused user is told "you should have read the docs."

## When to Use This

- Reviewing CLI commands, flags, subcommands, and their default behavior
- Designing or auditing public APIs, SDK methods, or library entry points
- Reviewing UI flows, prompts, modals, settings panels, or onboarding
- A user keeps making the same mistake despite warnings
- A dangerous operation is one keystroke or one flag away from a safe one
- A common, useful operation is hidden behind an obscure command or option
- Defaults disagree with what most users actually want

**Escape hatch**: If the surface is purely internal (private function, build script for a single maintainer, generated code), affordances matter less. Use this skill where humans must choose actions and the cost of the wrong choice is more than trivial.

## Core Mindset

Affordances are properties of the relationship between an object and its user. The teapot handle does not just have an affordance for grasping; it affords grasping *to a hand of the right size*. In software, the same applies: an API affords misuse if the misuse is easy to express and looks indistinguishable from correct use.

Ask:

- What does this design *invite* a user to do? What does it *resist*?
- Can the user tell, before acting, what will happen?
- Can the user tell, after acting, what just happened?
- Is the visible signal (signifier) aligned with the actual capability (affordance)?
- What is the *worst* action the user can take by accident?
- If a user formed a mental model from this surface alone, would it be correct?
- Where does the design rely on the user remembering, rather than recognizing?

## Domain Vocabulary

| Concept | Source | Meaning in software |
| --- | --- | --- |
| **Affordance (real)** | Gibson | What the system actually permits the user to do |
| **Affordance (perceived)** | Norman | What the user *believes* they can do |
| **Signifier** | Norman | The cue (label, color, shape, syntax) that communicates an affordance |
| **Mapping** | Norman | Correspondence between control and effect (left arrow ↔ move left) |
| **Constraint** | Norman | Limits that prevent invalid actions: physical, cultural, semantic, logical |
| **Feedback** | Norman | The system's response that confirms what happened |
| **Conceptual model** | Norman | The story the user builds about how the system works |
| **Slip vs mistake** | Reason | Slip = right intent, wrong execution; Mistake = wrong intent from wrong model |
| **Forcing function** | Norman | A constraint that makes the wrong action impossible (you cannot start the car without the brake) |
| **Reversibility** | — | Can the user undo, redo, dry-run, or preview before committing? |

### The Seven Stages of Action (Norman)

When a user fails, the failure usually lives in one of these stages. Diagnose which.

1. **Goal** — what the user wants to accomplish
2. **Plan** — choosing an approach
3. **Specify** — translating the plan into actions
4. **Perform** — executing the action (typing the command, clicking the button)
5. **Perceive** — noticing the system's response
6. **Interpret** — understanding what the response means
7. **Compare** — checking whether the goal was achieved

A "Gulf of Execution" is a gap between 1–4 ("I don't know how to do that"). A "Gulf of Evaluation" is a gap between 5–7 ("I don't know if it worked").

## The Process

### Step 1: Identify the User, Goal, and Context

```
TARGET:
- Surface under review: (CLI command / API / UI flow / config file)
- Primary user: (novice / regular / power user / automation)
- Their goal: (in their words, not yours)
- Frequency: (one-time / daily / many times per minute)
- Cost of mistake: (trivial / annoying / data loss / cross-user damage)
```

If multiple users with conflicting needs share the surface, name each — the design probably trades off badly for at least one of them.

### Step 2: Inventory the Affordances and Signifiers

List every action the surface permits and the cue that communicates it.

| Action | Real affordance | Signifier | Visibility | Reversibility |
| --- | --- | --- | --- | --- |
| `rm` | Delete file | Command name | High | None |
| `rm -rf /` | Delete everything | None special — same shape as safe `rm` | Same as safe | None |

Look for:

- Hidden actions (subcommands not in `--help`, undocumented env vars, magic flags)
- Visible-but-disabled actions (greyed-out buttons, deprecated commands still listed)
- Actions whose name does not predict their effect
- Actions whose default arguments change behavior dramatically

### Step 3: Classify Each Action

| Class | Definition | Design implication |
| --- | --- | --- |
| **Encouraged** | Common, safe, recoverable | Make obvious, short name, default on |
| **Neutral** | Useful but situational | Discoverable but not loud |
| **Discouraged** | Legacy, slow, or footgun-adjacent | Long name, deprecation note, no autocomplete priority |
| **Dangerous** | Destructive but sometimes needed | Require flag like `--force`, confirm, dry-run by default |
| **Irreversible** | No undo possible | Confirm with typed phrase, never default, never auto-retry |
| **Forbidden** | Should not happen via this surface | Make unrepresentable in the type/grammar |

### Step 4: Find the Mismatches

These are the failure modes to hunt for:

- **Visible but unsafe**: the destructive action looks like the safe action (`delete` and `archive` are adjacent menu items with similar icons).
- **Hidden but important**: the most useful flag is buried in `--help` page 4.
- **Easy but destructive**: a single keystroke, default argument, or autocomplete leads to data loss.
- **Hard but common**: the daily workflow needs three flags every time.
- **Misleading mapping**: `--no-verify` actually enables a stricter check; `--force` skips a check the user expected.
- **No feedback**: the command exits 0 with no output whether it did the thing or silently skipped.
- **No preview**: irreversible action with no `--dry-run`, `--plan`, or confirmation.
- **Same shape, different blast radius**: `git push` and `git push --force-with-lease` and `git push --force` look almost identical at the prompt.

### Step 5: Apply Constraint Types

For each dangerous mismatch, the strongest fixes use constraints in this order:

1. **Logical / type constraint**: make the wrong action impossible to express. (Separate `--dry-run` and `--apply` subcommands so you cannot accidentally do both.)
2. **Physical / syntactic constraint**: require extra typing for irreversible actions (`--yes-i-really-mean-it`, type the resource name to confirm).
3. **Semantic constraint**: name the action so its meaning matches its effect (`destroy` not `clean`, `force-delete` not `-f`).
4. **Cultural constraint**: follow conventions users already know (Unix exit codes, `--help`, POSIX flag style).
5. **Feedback / forcing function**: confirm before committing, show the diff, require interactive approval.

A warning that the user can dismiss is the *weakest* form of constraint. Prefer making the wrong action harder to express over telling the user not to do it.

### Step 6: Audit Defaults

Defaults are the strongest design choice you make, because most users never change them.

Ask of every default:

- Does it match what most users want most of the time?
- Is it safe? (When in doubt, default to the recoverable option.)
- Is it predictable across contexts? (`--color=auto` should mean the same thing everywhere.)
- Does the default make the system *teach* the user what is happening (verbose), or *hide* it (silent)?

### Step 7: Check Feedback and Reversibility

For each action, ask:

- After acting, can the user tell what changed? (echo, diff, count, summary)
- Can they undo, retry, or recover within a reasonable window?
- Is there a dry-run, preview, or plan mode?
- Does the error message say what went wrong, where, and what to do next?

Weak: `Error: invalid input`
Strong: `Error: --output expects a writable directory; '/etc' is not writable. Try --output=./out or run with elevated privileges.`

### Step 8: Recommend Concrete Changes

For each mismatch, propose the smallest change with the largest constraint strength.

| Change | Strength |
| --- | --- |
| Rename to match effect | Semantic |
| Split one command into two with different defaults | Logical |
| Require typed confirmation for irreversible actions | Forcing function |
| Add `--dry-run` and make it default | Logical + reversibility |
| Improve error message to suggest the right action | Feedback |
| Move dangerous flag behind a subcommand | Syntactic |
| Add `--help` example for common case | Discoverability |

## Output Format

```
AFFORDANCE REVIEW

Surface and user:
- ...

Actions inventory:
| Action | Class | Signifier | Reversibility | Issue |

Gulfs of execution (user can't figure out how):
1. ...

Gulfs of evaluation (user can't tell what happened):
1. ...

Mismatches (visible/hidden, safe/dangerous, easy/hard):
1. ...

Default-value problems:
1. ...

Recommended changes (ordered: strongest constraint first):
1. ...

Non-goals / accepted friction:
- ...
```

## Anti-Patterns to Avoid

- **"It's documented"**: documentation is the weakest signifier; most users never read it.
- **Color or icon as the only signifier**: colorblind, screen-reader, monochrome terminals will miss it.
- **Symmetric design for asymmetric consequences**: "delete" and "archive" should not look the same.
- **Confirmations that train dismissal**: if every action prompts "are you sure?", users click yes reflexively.
- **Hidden modes**: the same command behaving differently based on cwd, env var, or prior state with no visible cue.
- **Punishing exploration**: the user pressing Tab or running `--help` should never trigger a side effect.
- **Naming by implementation**: `--enable-v2-handler` means nothing to the user; name by effect.
- **Warning after the user committed**: "this will delete 42 files" *after* the deletion has started.

## Relationship to Other Skills

- Use `attention-design-review` when the affordance depends on a notification, warning, or signal being noticed.
- Use `cognitive-load-review` when the surface is large and the issue is *too many* affordances rather than the wrong ones.
- Use `adversarial-design-review` for affordances on trust boundaries — the wrong affordance becomes a vulnerability.
- Use `user-context-fieldwork` when you suspect the conceptual model you assume the user has is wrong.
- Use `distributed-cognition-review` when the right action depends on knowledge living in another tool, doc, or teammate.
- Use `incentive-analysis` when users *route around* an affordance because the safe path is too costly.
