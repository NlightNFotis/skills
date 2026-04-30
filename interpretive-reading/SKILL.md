---
name: interpretive-reading
description: Hermeneutics for code, specs, PRs, and error messages — the disciplined practice of charitable interpretation, the hermeneutic circle, and distinguishing reading-out from reading-in.
user-invocable: true
---

# Interpretive Reading

Act as a hermeneut — a disciplined interpreter of texts. Hermeneutics is the philosophy of how meaning is reconstructed from a text by a reader separated from its author by time, context, and assumptions. Software engineers are constant interpreters: of unfamiliar code, of an RFC written in 1998, of a PR by a colleague in another timezone, of an error message whose author left the company. The quality of your interpretations governs the quality of your changes. Misread the author's intent and you fix the wrong bug; misread the spec and you ship a subtle violation; misread the PR and your review misses the real risk.

Success looks like: an interpretation that the original author would recognize as fair, that explains all the textual evidence (not just the convenient parts), and that distinguishes what the text *says* from what you *want* it to say. Failure looks like: confidently fixing what you think the code "really meant" while breaking what it actually meant; eisegesis (reading your assumptions into the text) presented as exegesis (reading meaning out of it).

## When to Use This

- Reviewing a PR or design doc whose intent is not immediately obvious
- Reading legacy code without an available author
- Interpreting a spec, RFC, protocol, or contract whose wording is ambiguous
- Debugging an error message you didn't write and can't easily test
- Onboarding to an unfamiliar module
- When you find yourself saying "this code is wrong" before understanding why it's there
- Mediating disagreements about what a comment, doc, or commit message "really means"

**Escape hatch**: For text whose meaning is unambiguous and whose author is reachable, just ask. Use this skill when the author is gone, the text resists single readings, or stakes are high enough that a wrong interpretation is costly.

## Core Mindset

Two foundational ideas:

1. **The hermeneutic circle.** You cannot understand the parts of a text without grasping the whole; you cannot understand the whole without working through the parts. Interpretation is iterative — you form a tentative whole-picture, refine it as parts surprise you, then re-read parts in light of the new whole. *There is no first reading that gets it right.*
2. **The principle of charity.** Assume the author was reasonable, informed about their context, and writing for a purpose. If your reading makes the author look foolish, suspect your reading first. Stupid-author readings are usually reader laziness.

Ask:

- What could this mean, before I decide what it does mean?
- What context did the author have that I lack?
- What problem was this solving when it was written?
- Does my reading explain *all* the evidence, or only the parts I noticed?
- Am I reading meaning *out* of the text, or *into* it?
- What would the author say if they saw my interpretation?
- Where is real ambiguity, vs ambiguity I've manufactured by skimming?

## Hermeneutic Vocabulary

| Term | Meaning | Software application |
| --- | --- | --- |
| **Exegesis** | Drawing meaning *out* of a text | Letting the code, comments, tests, history tell you what it does |
| **Eisegesis** | Reading meaning *into* a text | Projecting your current task's assumptions onto unrelated code |
| **Hermeneutic circle** | Whole↔part dialectic | Iterating between module-level mental model and line-level reading |
| **Principle of charity** | Assume the author was rational | "Why would a competent engineer have written this?" |
| **Fusion of horizons** (Gadamer) | Your context meets the text's context | Acknowledging your modern assumptions vs the code's original era |
| **Authorial intent** | What the author meant | Recoverable via commit message, PR, design doc, history |
| **Textual meaning** | What the text says, independent of author | The semantics the code actually has, which may exceed intent |
| **Surface reading** | Take it at face value | Read the code as if the names and comments are accurate |
| **Symptomatic reading** | Read against the grain for what the text suppresses | Notice what the code *avoids* doing or names misleadingly |
| **Sensus literalis** | The plain literal sense | The straightforward semantics of the construct |
| **Sensus plenior** | The fuller sense, beyond what the author may have foreseen | Emergent properties when used in contexts the author didn't envision |
| **Aporia** | Genuine, irreducible interpretive difficulty | A real ambiguity the text cannot resolve on its own |
| **Polysemy** | Multiple legitimate meanings | Overloaded names, dual-purpose functions |
| **Marginalia** | Notes around the text | Comments, commit messages, code review threads |

## The Process

### Step 1: Establish the Text and the Horizon

Define what you are interpreting and what you bring to it.

```
TEXT:
- What I'm reading: [code, spec, PR, error]
- Boundary: [what counts as "the text"; what is context]
- Author/source if known:
- Approximate era / version:

MY HORIZON:
- Why I am reading this:
- Assumptions I bring:
- Outcomes I want it to support:  ← danger: this biases reading
```

Naming your own horizon is the first defense against eisegesis.

### Step 2: Surface Reading First

Read the text at face value. Names mean what they say. Comments are honest. Structure is intentional. This is the *charitable starting point*.

```
SURFACE READING:
- The function appears to: ...
- The comment claims: ...
- The structure suggests: ...
```

Do not skip this in favor of "I bet this is wrong because…" — premature suspicion is a leading cause of misreading.

### Step 3: Identify Surprises and Ambiguities

Where does the text resist a clean reading?

- Names that don't match behavior
- Comments contradicted by code
- Branches with no obvious trigger
- Defensive checks for cases that look impossible
- Dead-looking code that's never been removed
- Wording in a spec that admits multiple parses

Flag each surprise; don't yet resolve it.

```
SURPRISES:
1. [observation] — possible meanings: a) [...] b) [...]
```

### Step 4: Apply the Principle of Charity

For each surprise, ask: **what context would make a competent author write this?**

| Surprise | Charitable hypothesis |
| --- | --- |
| Defensive check for "impossible" case | The case was once possible; or upstream is less trusted than you assume |
| Misnamed variable | The name is from an earlier design; the rename was deferred |
| Dead-looking branch | Triggered by a config / environment you haven't seen |
| Awkward wording in a spec | Negotiated language balancing two stakeholders |
| Apparently redundant code | Defends against a race / retry / partial state |
| "Magic" constant | Empirically tuned; comment lost over time |

Generate at least one charitable hypothesis before any "this is wrong" hypothesis. Often the charitable reading is correct.

### Step 5: Walk the Hermeneutic Circle

Iterate between whole and part:

1. **Whole**: What is this module / spec / PR *for*? Form a tentative purpose.
2. **Part**: Read individual functions / sentences. Note what fits and what doesn't.
3. **Refine the whole**: Update your purpose-hypothesis based on parts that surprised you.
4. **Re-read the parts**: With the refined whole in mind, do the surprising parts now fit?
5. **Repeat** until either: parts are coherent under the whole, OR a genuine *aporia* (irresolvable difficulty) is identified.

The circle is not a vice. It is the method. Two passes beat one careful pass.

### Step 6: Distinguish Authorial Intent from Textual Meaning

A common error: collapsing what the author *meant* into what the text *does*.

- A function may be **correct relative to intent** (the author got what they meant) but **wrong relative to current callers** (callers rely on more than was promised).
- A spec may **mean** what its author thought, but **say** something narrower or wider.

Ask:
- What did the author intend? (recoverable from PR, commit, design doc)
- What does the text actually license? (what behavior is consistent with the words)
- Where do these diverge? — that gap is often where bugs live.

When fixing or extending, decide which you are honoring: intent or text.

### Step 7: Check Your Interpretation Against Evidence

A good interpretation is **falsifiable** and **explanatory**.

- Does my reading explain why these *specific* checks exist?
- Does my reading explain why this *specific* test exists?
- Does my reading explain the *commit history*? (a history of reverts and re-introductions tells a story)
- Does my reading explain the *naming choices*?
- Is there evidence I am ignoring because it doesn't fit?

If your interpretation requires you to dismiss multiple pieces of evidence as "weird" or "leftover", suspect the interpretation.

### Step 8: Mark Aporias Explicitly

Some texts are genuinely ambiguous — the author is gone, the spec is silent, and the code admits two readings equally. Name these:

```
APORIA: This function may be intended as [reading A] or [reading B].
- Evidence for A: ...
- Evidence for B: ...
- Cost of choosing wrong: ...
- Resolution: [reach out to original author / propose explicit clarification / write a test that pins one reading]
```

Pretending an aporia is resolved when it is not is the most expensive interpretive failure.

## Output Format

```
INTERPRETIVE READING

Text under interpretation:
- Boundary:
- Era / source:

Reader horizon:
- Why I'm reading:
- Assumptions I bring:

Surface reading:
- ...

Surprises:
1. ...

Charitable hypotheses:
1. For surprise X: a competent author might have written this because ...

Refined whole-picture:
- Purpose:
- How parts fit:

Authorial intent vs textual meaning:
- Intent (evidence: ...): ...
- Text licenses: ...
- Gap: ...

Aporias (genuine ambiguities):
- ...

Recommended action:
- ...
```

## Anti-Patterns to Avoid

- **Eisegesis**: projecting your current task onto unrelated code
- **Stupid-author reading**: concluding the author was incompetent before exhausting charitable readings
- **Single-pass reading**: stopping at the first interpretation that fits half the evidence
- **Cherry-picked evidence**: ignoring tests, comments, or commits that contradict your reading
- **Confusing intent and text**: fixing what you think was meant while breaking what was promised
- **Dissolving real ambiguity**: forcing a single reading on a genuine aporia
- **Manufacturing ambiguity**: treating clear text as ambiguous to license your preferred change
- **Horizon blindness**: pretending you bring no assumptions to the reading
- **Skipping marginalia**: ignoring commit messages, PR threads, and comments where intent is most recoverable

## Relationship to Other Skills

- `semantic-precision` clarifies what individual *terms* mean; interpretive-reading clarifies what whole *texts* mean.
- `assumption-audit` surfaces hidden assumptions in the reader's interpretation, not just the text's.
- `code-forensics` reconstructs the historical context that interpretation depends on (commits, timelines, changes).
- `mental-model-alignment` compares the system's actual behavior against the developer's and user's mental models — interpretive-reading is how you build the developer's model from the text.
- `bias-audit` checks that your interpretation isn't anchored, motivated, or confirmation-seeking.
- `communication-pragmatics` complements this skill from the *writer's* side: how to produce text that survives interpretation.
