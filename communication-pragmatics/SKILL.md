---
name: communication-pragmatics
description: Grice's maxims and speech act theory applied to engineering text — error messages, commit messages, log lines, prompts, and PR descriptions. Distinguishes literal meaning from intended effect.
user-invocable: true
---

# Communication Pragmatics

Act as a pragmatic linguist embedded in the engineering workflow. **Pragmatics** is the branch of linguistics that studies meaning *in context* — what an utterance does, what it implies, what it commits the speaker to, and what the listener will reasonably infer beyond the literal words. Engineers produce text constantly: error messages, log lines, commit messages, PR descriptions, agent prompts, code comments, doc tone, warning vs error labels. Most of these texts fail not because their literal meaning is wrong, but because their *pragmatic* effect — what users actually infer and do — diverges from what was intended.

Success looks like: an error message that produces the right next action; a commit message that lets a reviewer skip what isn't relevant; a log line that means the same thing at 2 a.m. as at 2 p.m.; an agent prompt that doesn't accidentally license behavior the author would reject. Failure looks like: an "error" that users learn to ignore because half are warnings; a "warning" that gets treated as fatal because of its tone; a commit titled "fix bug" that obscures what changed.

## When to Use This

- Writing or reviewing user-facing error messages and warnings
- Drafting commit messages, PR titles, and PR descriptions
- Designing log lines, alert text, and on-call runbooks
- Authoring agent / LLM prompts where unintended licensure is costly
- Reviewing doc tone, README intros, and onboarding text
- Designing CLI output, including success messages, prompts, and confirmations
- When the team is debating *how to phrase* something — usually a sign pragmatics is at stake

**Escape hatch**: For text consumed only by you and only once, don't over-engineer it. Use this skill when the text will be read by people who don't share your context, or when the inference the reader draws determines downstream behavior.

## Core Mindset

> Literal meaning is what your words *say*. Pragmatic meaning is what your reader *takes away and does*. The gap between them is where most communication failures live.

Pragmatic communication is **cooperative**: speaker and listener jointly assume that the speaker is following recognizable norms. Violate the norms (be too long, too short, too tangential, too vague) and the listener will *infer* a reason — often a wrong one. "Why did they include that detail?" "Why didn't they mention X?" "What does it commit them to?"

Ask:

- What will the reader *do* after reading this?
- What will the reader *infer* beyond what I literally said?
- What does saying this *commit me to* (or appear to commit me to)?
- Am I saying enough — or so much that the important part is buried?
- What is the reader's situation when they encounter this text?
- Is the *force* of my utterance (warning, command, suggestion, claim) clear?
- Would a reasonable reader, in this context, draw the inference I want?

## Grice's Cooperative Principle and the Four Maxims

H. P. Grice proposed that speakers are presumed to follow a **Cooperative Principle**: contribute what is required, when it is required, by the accepted purpose of the exchange. From this, four maxims follow. Violating a maxim doesn't always mean failure — sometimes the violation itself communicates (an *implicature*).

| Maxim | Rule | Software failure example | Better |
| --- | --- | --- | --- |
| **Quantity** | Say enough; don't say more than needed | `Error: failed.` (too little) / 8 KB stack trace dumped to user (too much) | `Error: could not connect to database 'orders' at db-prod-3:5432 (timeout after 30s).` |
| **Quality** | Say what you believe true and have evidence for | `This will not affect production.` (when unverified) | `Tested on staging; production behavior verified for the read path; write path untested.` |
| **Relation** | Be relevant | `Build #4382 finished.` (in a PR review) — true but not relevant to the question asked | Address the reviewer's specific question first |
| **Manner** | Be clear, brief, ordered, unambiguous | `If not nonexistent, deactivate.` | `If the user exists, deactivate them.` |

A good engineering text satisfies all four. Most bad ones violate one badly — usually Quantity (dump everything) or Manner (unclear referent).

## Speech Act Theory: What Texts *Do*

J. L. Austin and John Searle showed that utterances perform actions, not just describe states. Five categories:

| Speech act type | What it does | Engineering examples |
| --- | --- | --- |
| **Assertive** | Commits speaker to truth of a proposition | Log line, status report, doc statement |
| **Directive** | Tries to get the hearer to act | Error with required next step, prompt, "Please retry", on-call page |
| **Commissive** | Commits speaker to future action | "I will deploy at 4 PM", SLA, API contract |
| **Expressive** | Conveys a psychological state | "Sorry for the noise", "Heads-up", apologetic warning |
| **Declarative** | Brings about a state by being said | "Closing this issue", "Approved", `git tag v1.0`, "marked as resolved" |

Three further distinctions:

- **Locutionary act**: the literal utterance ("the build is broken")
- **Illocutionary force**: what the speaker is *doing* (warning, blaming, informing, requesting)
- **Perlocutionary effect**: what the utterance *causes* in the hearer (panic, fix, ignore, escalate)

A "warning" log line whose perlocutionary effect is "everyone ignores it" has failed pragmatically even if locutionary content is correct.

## Conversational Implicature

Speakers communicate beyond literal meaning by trusting the listener will reason from the maxims. Examples:

- "The deploy completed." → implicates that nothing else noteworthy happened (Quantity). If an unrelated error occurred, the omission misleads.
- "Some tests pass." → implicates that not all do (Quantity scalar).
- "The migration ran." → implicates success (Manner: would have said "failed" otherwise).
- "Restart the service." → implicates that restarting is sufficient (Quantity / Relation).

Engineers leak implicatures constantly without intending to. A status update of "deploy complete" carries the implicature "and everything is fine"; if it isn't, you've misled even with literally true words.

## Politeness and Face-Threatening Acts

Brown and Levinson's politeness theory: every utterance can threaten the hearer's *face* (their public self-image). Engineering relevant **face-threatening acts**:

- Pointing out a bug in someone's PR (negative face: their autonomy)
- Rejecting a design (positive face: their competence)
- Demanding a fix (negative face: imposing)
- Correcting an error message that another team owns

Mitigation strategies (use sparingly — over-mitigated text becomes unclear):

- **Hedging**: "I might be wrong, but…" (use only when truly uncertain)
- **Indirect**: "Is this intentional?" (vs "this is wrong")
- **Solidarity**: "We saw similar in our code…" (positive face)
- **Bald-on-record**: "Drop the column" (when speed matters more than face)

The pragmatic risk: **over-politeness obscures the directive**. "Maybe consider possibly looking at this?" leaves the reader unsure whether action is required.

## The Process

### Step 1: Identify the Text and Its Audience

```
TEXT:
- What I'm writing:
- Audience:
- Audience's situation when they read it:
- What I want them to do after:
- What I do NOT want them to infer:
```

The "do not want inferred" line is the most underused. Pragmatic failures live there.

### Step 2: Name the Speech Act

What is this text *doing*?

```
SPEECH ACT:
- Type: assertive / directive / commissive / expressive / declarative
- Illocutionary force: warning / informing / requesting / committing / apologizing / declaring
- Desired perlocutionary effect: ...
- Risk: this might be perceived instead as ... (which would cause ...)
```

A "warning" that is functionally a directive ("you must act") should be re-labeled or rephrased to make the directive clear.

### Step 3: Apply the Four Maxims

Walk through Grice:

- **Quantity**: Is anything missing the reader needs? Is anything included that isn't earning its place?
- **Quality**: Is every claim true and supported? Where am I asserting beyond what I know?
- **Relation**: Is this addressing what the reader actually came here for?
- **Manner**: Is the wording unambiguous, ordered, and brief?

For each, rewrite if violated — or *flag the violation as intentional* (e.g., extra detail because the reader is on-call at 2 a.m. and lacks context).

### Step 4: Check the Implicatures

Ask: "What might a reasonable reader *infer* beyond what I said?"

- "Deploy complete" → "and successful and no side effects"
- "All tests pass" → "including the ones I added"
- "Updated docs" → "to match the code change"
- "Reverted" → "to a known-good state"

If any inference is unwarranted, either:

- Strengthen what you said to license the inference, or
- Add a clause that blocks it ("Deploy complete; one unrelated test was skipped")

### Step 5: Audit the Commitments

For commissive and assertive acts, list what you've committed yourself to.

- "We support X" → commits team to handling X bugs
- "This won't affect production" → commits you to that being true
- "Approved" → commits the reviewer to the change being acceptable
- "Deprecated" → commits the team to migration support

If the commitment is larger than you intend, narrow the wording.

### Step 6: Calibrate Force

Match the wording to the action you want.

| You want… | Use | Avoid |
| --- | --- | --- |
| Reader must act | Imperative directive: "Run X." | Hedged suggestion that buries the requirement |
| Reader should consider | Interrogative or hedge: "Consider X" | Imperative that creates false urgency |
| Reader should be alarmed | Strong assertion + severity tag | Buried warning that reads as routine info |
| Reader should not be alarmed | Calm assertive + explicit no-action | Cautious wording that triggers panic |
| Reader should fix on their side | Directive with target identified | Passive voice that obscures who acts |

The pragmatic value of `[ERROR]` vs `[WARN]` vs `[INFO]` collapses if usage doesn't match severity. Audit usage, not just labels.

### Step 7: Reduce Face Threat Where Possible — Without Sacrificing Clarity

For interpersonal text (PR review, async comments):

- Lead with the technical observation, not the judgment
- Distinguish "I don't understand" from "this is wrong"
- Offer the next step concretely
- Reserve bald-on-record for situations where clarity dominates

### Step 8: Test the Text on a Naive Reader

Pragmatic effects are observable. Where possible:

- Read it aloud
- Show it to someone outside the immediate context
- Ask: "What would you do after reading this?" — not "do you understand it?"
- Notice what they *infer* — if it's wrong, your text caused it

## Output Format

```
PRAGMATIC ANALYSIS

Text:
[the text]

Audience & situation:
- ...

Speech act:
- Type: ...
- Illocutionary force: ...
- Desired perlocutionary effect: ...

Maxims check:
- Quantity: ...
- Quality: ...
- Relation: ...
- Manner: ...

Implicatures (intended and unintended):
- Intended: ...
- Unintended (to block): ...

Commitments incurred:
- ...

Face considerations (if interpersonal):
- ...

Suggested rewrite:
[rewrite]

Why the rewrite is better:
- ...
```

## Anti-Patterns to Avoid

- **Maxim violation by accident**: dumping a stack trace at users (Quantity), passive-voice obscuring agent (Manner)
- **Implicature leak**: technically true statement that misleads by what it doesn't say
- **Force-label mismatch**: "[WARN]" used for things that are either fatal or trivial — readers stop trusting the label
- **Over-commitment**: phrasing that promises support / behavior beyond what you can deliver
- **Politeness collapse**: hedging so much that the directive disappears
- **Bald-on-record by default**: every message in imperative mode regardless of stakes
- **Audience erasure**: writing for the writer's mental state, not the reader's situation
- **Tone drift**: a single doc shifting between formal/casual/apologetic without reason; readers infer instability

## Relationship to Other Skills

- `semantic-precision` is about what individual *words* mean; pragmatics is about what the whole *utterance does in context*. Pair them.
- `interpretive-reading` is the *reader's* counterpart — how meaning is reconstructed; pragmatics is how to produce text that survives that reconstruction.
- `attention-design-review` deals with salience and prioritization; pragmatics provides the linguistic tools (force, maxim choice, implicature) for getting attention right.
- `signal-detection-review` complements this skill: pragmatics shapes the *labels* (error/warn/info), signal-detection tunes the *thresholds* behind them.
- `mental-model-alignment` overlaps where the gap between system behavior and user model is created or repaired by text.
- `assumption-audit` is useful when commitments incurred by a text rest on unverified assumptions.
