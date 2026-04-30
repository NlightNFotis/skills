---
name: mental-model-alignment
description: Compare the system model, developer model, and user model; identify mismatches that cause bugs or UX confusion.
user-invocable: true
---

# Mental Model Alignment

Act as a cognitive science and HCI reviewer. Don Norman observed that every system has three models: the **design model** (how the designer thinks it works), the **system image** (what the system actually exposes through its interface, naming, errors, and behavior), and the **user's model** (what the user infers from that exposure). When these three drift apart, you get bugs that aren't bugs, UX disasters that pass QA, and "user error" that is really design error.

Success looks like: the three models are written down, the load-bearing mismatches are named, and each mismatch has a concrete intervention (change behavior, change interface, or change docs — in that priority). Failure looks like blaming users for reasonable inferences from a misleading interface, or documenting around a mismatch instead of fixing it.

## When to Use This

- Users repeatedly misuse a feature in the same way
- A CLI/API behaves "correctly" but support tickets keep coming
- Documentation contradicts the code, or both contradict the UI
- Bug reports describe the system doing what the user "didn't expect"
- Internal teams have different beliefs about who owns or controls a piece of state
- A migration changes behavior; users don't notice until something breaks
- You're designing a new affordance and want to predict how users will read it
- "Power user" workarounds reveal the system has hidden state the user is tracking themselves

**Escape hatch**: Don't apply this to mechanical or internal-only code paths with no human users (or where the "user" is another system whose contract is fully specified). Use this where humans interpret behavior — even other developers count as users of an API.

## Core Frameworks

### Norman's Three Models

- **Design model**: the mental model the designer/engineer holds
- **System image**: everything the user can actually observe — UI, names, errors, defaults, latency, sounds, sequences
- **User's model**: what the user *infers* from the system image

Critical insight: the designer never communicates with the user directly. They communicate **only through the system image**. If the image is inconsistent, the user's model will be wrong even if the design model is perfect.

### Norman's Two Gulfs

- **Gulf of execution**: the gap between what the user wants to do and what the system makes possible/discoverable. Symptom: "I don't know how to do X."
- **Gulf of evaluation**: the gap between what happened and what the user can perceive happened. Symptom: "I don't know if it worked."

Most "this is unintuitive" complaints map to one of these gulfs.

### Surface vs Deep Model

- **Surface model**: what the user needs to know to operate the system day-to-day
- **Deep model**: how the system actually works internally

A healthy system lets users succeed with the surface model and only forces them into the deep model when something goes wrong. **Model debt** accumulates when users have to learn deep-model details to perform routine surface-model tasks.

### Conceptual vs Implementation Model

The conceptual model is the *story* a user tells themselves about objects, actions, and consequences. The implementation model is the engineering reality. UIs that expose implementation directly ("DB rows", "kubernetes pods", "merge conflicts") force the user to translate.

## Core Questions

- What story does the user tell themselves about what happened? Where does it diverge from reality?
- What signals does the system give to update the user's model — and are they timely, perceivable, attributable?
- Where does the interface expose **implementation concepts** that users have to learn?
- Which "user errors" are really violated affordances?
- What hidden state does the system have that the user must track externally to succeed?
- Are similar things named/displayed similarly, and different things differently? (mapping principle)
- When something fails, can the user form an accurate causal story from what they see?

## Mismatch Catalog

| Mismatch type | Example | Fix priority |
| --- | --- | --- |
| **Hidden state** | A flag changes behavior but is never shown | Surface the state |
| **Invisible action** | An action succeeds with no feedback | Add evaluation feedback |
| **False affordance** | Looks clickable, isn't | Remove the visual cue or make it work |
| **Hidden affordance** | The action exists but isn't discoverable | Make it visible, document, or tutorialize |
| **Mode error** | Same action, different meaning depending on hidden mode | Make the mode visible; or eliminate modes |
| **Naming drift** | UI/CLI/docs/code use different terms for the same thing | Pick one; rename the others |
| **Ownership ambiguity** | User unsure who/what controls a value (their config? the server? cached?) | Make ownership explicit in UI/docs |
| **Temporal mismatch** | "Saved" appears before durable persistence completes | Distinguish optimistic from confirmed |
| **Failure invisibility** | A background job failed; user sees stale UI | Emit failure into the user's view |
| **Implementation leakage** | Error says "ECONNREFUSED on port 5432" to an end user | Translate to user-domain concept |
| **Asymmetric model** | Create flow exposes 3 fields; edit flow exposes 7 | Symmetrize the model presented |
| **Default tyranny** | Default behavior is the dangerous one | Reverse default; require opt-in for danger |
| **Magic** | System acts on its own with no visible cause | Surface the trigger; allow inspection |
| **Two pointers, one name** | "Project" means org-project to admin, user-project to member | Disambiguate |

## The Process

### Step 1: Pick a User Journey

Define a concrete journey, not "the system." The unit of analysis is *one task one user performs.*

```
JOURNEY:
- User type / role:
- Goal in their own words:
- Trigger that starts the journey:
- Steps they expect to take:
- Success condition (in their language):
```

### Step 2: Write Down All Three Models Explicitly

Don't try to evaluate before you've articulated.

```
DESIGN MODEL (engineer's understanding):
- Objects: ...
- Operations: ...
- States: ...
- Failure modes: ...

SYSTEM IMAGE (what the interface actually exposes):
- Visible UI/CLI elements: ...
- Names exposed in UI/errors/logs: ...
- Feedback signals (success/progress/failure): ...
- Defaults and pre-selected options: ...
- What is *not* visible:

USER MODEL (likely inference from system image):
- What they think the objects are:
- What they think actions do:
- What they think happened after each action:
- Where they would look for state:
```

For the user model, draw from: support tickets, error messages users have quoted back, common misuses, "feature requests" that already exist as features, onboarding questions.

### Step 3: Walk the Journey and Mark Gulfs

For each step:

- **Gulf of execution check**: does the user know what to do? Is the affordance discoverable?
- **Gulf of evaluation check**: after acting, can the user tell if it worked, partly worked, or failed?

```
STEP: [user action]
- Execution gulf: [low/medium/high] — because:
- Evaluation gulf: [low/medium/high] — because:
- Likely user inference if it goes wrong:
```

### Step 4: Map Mismatches to Categories

For each gap, identify which mismatch type from the catalog applies. This guides the fix.

A single confusing screen often combines multiple mismatches (e.g., hidden state + ambiguous naming + asymmetric model). Name them separately.

### Step 5: Choose the Fix Layer

Fix at the highest-leverage layer:

| Layer | When to use | Cost |
| --- | --- | --- |
| **Behavior** | The current behavior is genuinely wrong / dangerous / surprising | Highest, but most durable |
| **System image** (UI, CLI text, errors, names, defaults, ordering) | Behavior is right but invisible/misnamed/misordered | Medium |
| **Documentation** | Behavior and image are right, but the conceptual onboarding is missing | Lowest, but weakest |

**Avoid the documentation reflex.** Documenting around a mismatch leaves the mismatch in place; only users who read the docs benefit, and they are a minority.

### Step 6: Validate the Updated System Image Predicts the Right User Model

After proposing changes, simulate a fresh user:

- Given only what the *new* system image exposes, what model would they form?
- Does that model now match the design model in the load-bearing places?
- Does it remain *simpler* than the implementation model? (surface > deep)

If the projected user model still diverges, iterate.

### Step 7: Identify Model Debt to Track

Some mismatches can't be fixed in this pass. Record them so they don't compound:

- Surface-model leaks where users must learn implementation details
- Naming drift that needs a coordinated rename
- Hidden state that should eventually become visible
- Defaults that should eventually flip

## Output Format

```
MENTAL MODEL ALIGNMENT REPORT

Journey:
- User, goal, trigger, success condition:

Design model (engineer view):
- ...

System image (what is actually exposed):
- ...

User model (likely inference):
- ...

Walked gulfs:
- Step ... — execution gap: [...] / evaluation gap: [...]

Mismatches identified:
1. [Category from catalog] at [step/component] — effect on user:

Recommended fixes (in priority order):
1. Behavior change: ...
2. System-image change (UI/CLI/error/default/name): ...
3. Doc change (only as last resort or supplement): ...

Predicted updated user model:
- ...

Model debt (deferred):
- ...

Open product questions:
- ...
```

## Anti-Patterns to Avoid

- **User-blame**: framing reasonable inferences from a misleading interface as "user error"
- **Documentation reflex**: writing prose to explain confusing behavior rather than fixing it
- **Model imposition**: asserting that users *should* understand the implementation model
- **Hidden mode addition**: introducing modes to add capability without showing the mode in the UI
- **Confirmation theater**: adding "Are you sure?" dialogs as a substitute for fixing the underlying ambiguity
- **Asymmetric flows**: showing different facets of the same object in create vs edit vs list views
- **Implementation leakage in errors**: surfacing internal identifiers, stack traces, or infra terms to end users
- **Power-user workarounds as features**: codifying expert workarounds instead of fixing the affordance
- **Naming drift across surfaces**: tolerating different terms for the same concept across UI, CLI, API, and docs

## Relationship to Other Skills

- Use `semantic-precision` when the mismatch is rooted in a specific term meaning different things to designers vs users.
- Use `code-narrative-review` when the developer-model side is unclear in the code itself.
- Use `assumption-audit` when the design model rests on premises about user behavior that haven't been validated.
- Use `formal-invariants` when "hidden state" should be made into an explicit, checked invariant the UI can render.
- Use `bias-audit` when designers dismiss user confusion as ignorance (curse-of-knowledge / fundamental attribution).
- Use `differential-diagnosis-debugging` when a recurring "bug" turns out to be a model-mismatch class, not a defect.
