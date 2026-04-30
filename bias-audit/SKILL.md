---
name: bias-audit
description: Check reasoning for anchoring, confirmation bias, availability bias, sunk-cost fallacy, and premature closure.
user-invocable: true
---

# Bias Audit

Act as a cognitive debiasing reviewer for an engineering decision, debugging plan, design argument, or code review. Humans (and LLMs) reason under predictable cognitive biases. Your job is to inspect the *reasoning process* — not the conclusion — and identify where bias is doing the work that evidence should be doing.

Success looks like: at least one named bias is concretely identified (or convincingly ruled out), at least one alternative hypothesis is raised, and a single cheap "decision-changing" observation is proposed. Failure looks like vague hand-waving ("watch out for confirmation bias!") with no specific instance and no actionable counter-move.

## When to Use This

- Debugging has fixated on one theory for hours without progress
- A proposed solution feels obvious but the supporting evidence is thin
- A team is preserving an expensive prior decision (architecture, vendor, refactor)
- A review or plan lists no alternatives
- A recent dramatic incident is shaping a design choice
- Confidence in the conclusion exceeds the quality of evidence
- The reasoning sounds like "obviously" or "everyone knows" without citation

**Escape hatch**: Don't audit trivial decisions or routine code. Use this when the cost of a biased decision is meaningful: production incidents, architectural commitments, security calls, prioritization, hiring, or stuck debugging sessions.

## Core Questions

- What conclusion is being defended, and how was it first reached?
- What evidence is being weighted heavily, and why is *that* evidence available?
- What evidence would change the conclusion — and has anyone looked for it?
- What alternative would I generate if I had never heard the current proposal?
- Would I make this decision the same way if the prior investment were zero?
- Am I attributing this to a person/team when a system explanation fits equally well?
- If I'm wrong, when and how will I find out?

## Bias Catalog

Each entry: what it is, how it shows up in engineering, and a concrete debiasing move.

| Bias | Engineering signature | Debiasing move |
| --- | --- | --- |
| **Anchoring** | First-mentioned cause/number dominates later estimates | Generate 2–3 alternatives *before* discussing the first; compare on equal footing |
| **Confirmation bias** | Searching for evidence that supports the favored theory | Write the falsification test: "what observation would *disprove* this?" |
| **Availability heuristic** | Recent/vivid incidents weighted as likely | Check base rates: how often does this *actually* happen across the history? |
| **Premature closure** | Investigation stops at the first plausible cause | Require ruling out N alternatives before declaring root cause |
| **Sunk-cost fallacy** | "We've already invested too much to change direction" | Ask: would we start this today, knowing what we know now? |
| **Fundamental attribution error** | Blaming a person for behavior a system makes likely | Ask: would a competent stranger have done the same thing here? Fix the system. |
| **Hindsight bias** | "It was obvious this would fail" — after it failed | Recover the actual information available *before* the event |
| **Planning fallacy** | Estimates ignore the distribution of similar past projects | Use reference-class forecasting: how long did the last 5 similar tasks take? |
| **Dunning–Kruger** | Confidence highest where competence is lowest | Test a concrete prediction; calibrate against it |
| **In-group bias** | Trusting code/teams/tools "we" own more than "they" do | Apply identical standards to internal and external components |
| **Status-quo bias** | Defaulting to the existing design without comparison | Force a written comparison against one credible alternative |
| **Authority bias** | Senior person's opinion carries weight beyond their evidence | Separate "what they observed" from "what they concluded" |
| **Bandwagon / social proof** | "Everyone is doing X" replaces argument | Ask for the load-bearing reason, not the count of adopters |
| **Loss aversion** | Avoiding a small certain cost over a larger expected gain | Symmetrize the framing: phrase it as gain *and* loss |
| **Framing effect** | Same facts, different conclusion based on wording | Re-state the question in opposite framing; check if the answer changes |
| **Survivorship bias** | Learning only from successful systems/PRs/tests | Look at the failures and abandoned attempts too |
| **Recency bias** | Latest data point dominates the trend | Plot the longer window |
| **Optimism bias** | Default schedule and risk estimates skew rosy | Have a "red team" generate the failure case |
| **Bikeshedding** | Disproportionate attention to easy/visible items | Time-budget topics by their actual impact |

## The Process

### Step 1: Identify the Reasoning Under Audit

Be specific about what claim or decision you are auditing. "The codebase" is too broad; "the proposal to roll back commit X to fix the latency regression" is auditable.

```
AUDIT TARGET:
- Claim or decision:
- Author/owner:
- Stage (hypothesis / proposal / committed):
- Reversibility (cheap rollback vs one-way door):
- Stakes if wrong:
```

### Step 2: Reconstruct How the Conclusion Was Reached

Walk back through the reasoning trail before evaluating it.

- What was the first hypothesis considered? (anchor candidate)
- What evidence was examined, in what order?
- What alternatives were considered and dismissed — and why?
- Which evidence was searched for? Which evidence would have been visible if it existed?

If you cannot recover the reasoning trail, that itself is a finding.

### Step 3: Score the Evidence

For each piece of supporting evidence, ask:

- Is this **direct** (observed) or **inferred**?
- Is it **independent** of the conclusion, or did the conclusion shape what was collected?
- Could the same evidence support an alternative?
- Is any disconfirming evidence being explained away?

```
EVIDENCE FOR: [item] — direct/inferred — independent? — could also support: [alt]
EVIDENCE AGAINST: [item] — how is it being handled?
```

If the "evidence against" column is empty, that is suspicious by itself — almost no real claim has zero counter-evidence.

### Step 4: Match Symptoms to Specific Biases

Walk the bias catalog, but only flag biases with a **specific instance**. "There might be confirmation bias" is not a finding; "the only logs pulled were from the failing host, never from a healthy one" is.

```
DETECTED BIAS:
- Bias: [named]
- Specific instance: [what was said/done that exhibits it]
- Counter-evidence that was not sought:
- Severity for this decision: low / medium / high
```

### Step 5: Generate Alternatives by Construction

Force at least two materially different alternatives, even if the current conclusion is probably right. Generation defangs anchoring.

Useful generators:

- **Pre-mortem**: assume the decision failed; write the post-mortem
- **Red team**: someone argues the opposite case
- **Outside view**: how have similar situations resolved in this codebase / industry?
- **Inversion**: instead of "how do we make this work?", ask "how would we guarantee it fails?"
- **Steelman**: state the strongest version of the rejected option

### Step 6: Identify One Decision-Changing Observation

The most valuable output of a bias audit is a cheap observation that, if it came back a particular way, would flip the decision.

Weak: "We should consider more data."
Strong: "If the same regression appears on the previous release, the proposed rollback cannot be the fix. Run the perf test on `v1.4.2` for 50 iterations."

If no observation could change the conclusion, the conclusion is unfalsifiable — which is itself a serious finding.

### Step 7: Recommend a Process Adjustment

Bias is rarely fixed by willpower. Prefer process changes:

- Require two named alternatives in any incident postmortem
- Time-box the first hypothesis before committing to it
- Have a designated "disconfirmer" in design review
- Use blind comparison (hide the author/team for first review pass)
- Force a written pre-mortem for one-way-door decisions

## Output Format

```
BIAS AUDIT

Audit target:
- Claim/decision and stakes:

Reasoning trail (as reconstructed):
- ...

Evidence quality:
- For: ...
- Against: ...
- Missing/unsought: ...

Detected biases (with specific instances):
1. [Bias] — instance: [...] — severity: [...]

Steelmanned alternatives:
1. Alt A:
2. Alt B:

Decision-changing observation:
- If [observation] then [conclusion changes to ...]
- Cost to obtain:

Process recommendations:
- ...

Residual risk if conclusion is kept:
- ...
```

## Anti-Patterns to Avoid

- **Bias-name-dropping**: invoking bias terms without pointing at a specific instance
- **Auditing the conclusion, not the reasoning**: the conclusion may be right *and* poorly reasoned
- **Symmetric skepticism theater**: pretending alternatives are equally weighted when they aren't, to look balanced
- **Counter-anchoring**: forcing the *opposite* conclusion to look unbiased
- **Bias for novelty**: treating "we've always done it this way" as inherently biased while ignoring the same critique of "let's try something new"
- **Auditing trivia**: spending bias-audit cost on low-stakes reversible decisions
- **Unfalsifiable findings**: saying "there is bias here" with no observation that would prove there isn't
- **Personal attack framing**: turning a process critique into a critique of the author

## Relationship to Other Skills

- Use `popperian-debug` to convert detected confirmation bias into actual falsification tests.
- Use `assumption-audit` when bias has hidden a load-bearing premise.
- Use `differential-diagnosis-debugging` when premature closure has truncated a differential.
- Use `code-forensics` to recover the actual evidence trail behind hindsight-biased narratives.
- Use `statistical-debugging` when availability bias has overweighted a vivid recent incident over base rates.
