# `popperian-debug` Evaluation Rubric

Each output is scored on **two independent axes**, then on a **terminal-outcome** check. The split exists so we can detect "vocabulary parroting without behaviour change" — the dominant failure mode of skill evaluation.

All items are binary (0/1) unless marked. The judge sees the task, the agent's full transcript, and the rubric — but does **not** see which arm produced the output.

---

## Axis A — Process adherence (structural / "did it follow the shape?")

Max 8.

| # | Item | Pass criterion |
|---|------|----------------|
| A1 | Reproduction established | Agent ran or explicitly confirmed the failing repro before hypothesising |
| A2 | Facts collected explicitly | A discrete fact list (or equivalent) appears before any hypothesis |
| A3 | ≥2 materially distinct hypotheses | At least 2 hypotheses from *different* categories (logic / state / timing / env / upstream / assumption). Trivial paraphrases of one hypothesis = 0 |
| A4 | Hypotheses ranked with reasoning | Ranking is stated and each rank is justified against the facts |
| A5 | Falsification framing | For ≥1 hypothesis, agent states what it would expect to see *if the hypothesis were wrong*, not just what would confirm it |
| A6 | One change at a time | When testing or fixing, the agent does not bundle multiple speculative changes |
| A7 | Verdict explicit | Each tested hypothesis ends in DISPROVED / NOT DISPROVED / INCONCLUSIVE (or clear equivalent) |
| A8 | Fix verified against original repro | Agent re-runs the original failing case after the fix |

## Axis B — Reasoning quality (substantive / "did the thinking actually change?")

Max 7. Score 0 if the corresponding process step was skipped.

| # | Item | Pass criterion |
|---|------|----------------|
| B1 | Hypothesis diversity is real, not cosmetic | The hypotheses would, if true, lead to *different* fixes. Judge writes one sentence on the fix each implies; if two collapse to the same fix, deduct |
| B2 | Ranking reflects evidence, not salience | The top hypothesis is consistent with **all** stated facts, not just the most recent or most dramatic one |
| B3 | A genuinely disconfirming test was attempted | The test could have produced a result that killed the hypothesis (not a tautological "I read the code and it looked right") |
| B4 | Updated beliefs on new evidence | If a test produced a surprise, the fact list / hypothesis ranking changes accordingly |
| B5 | Identified the actual root cause | Matches the known root cause for this task. (Partial credit 0.5 if a contributing factor is found but not the root cause.) |
| B6 | Avoided named anti-patterns | No confirmation bias, anchoring, stacked fixes, unfalsifiable hypotheses (judge must cite specific evidence to deduct) |
| B7 | Escape hatch handled correctly | If the task is trivially obvious, agent exits the workflow early; if non-trivial, agent does not exit prematurely |

## Axis C — Terminal outcome (ground truth)

Single check, weighted heavily in aggregate analysis.

| # | Item | Pass criterion |
|---|------|----------------|
| C1 | Root cause correct | Agent's stated root cause matches the synthesised bug's known root cause |
| C2 | Fix correct | Proposed fix would resolve the failing repro without obvious regressions (judge applies a 30-second sanity read; for high-stakes runs, actually patch and re-run the test) |

---

## Scoring & aggregation

For each (task, arm, seed) run, record:

```
process_score  = sum(A1..A8) / 8        # in [0,1]
reasoning_score= sum(B1..B7) / 7         # in [0,1]
outcome_score  = (C1 + C2) / 2           # in [0,1]
length_tokens  = transcript token count  # confounder
tool_calls     = count of tool invocations
```

**Headline metric: outcome_score.** That's the one that matters.
**Diagnostic metrics: process_score and reasoning_score.** They tell you *why* outcome moved.

The interesting cases:

| process | reasoning | outcome | Interpretation |
|---------|-----------|---------|----------------|
| high    | high      | high    | Skill working as intended |
| high    | low       | low     | **Parroting** — using the template but not the thinking. Skill needs sharper anti-patterns or worked examples |
| low     | high      | high    | Agent solved it without the structure — skill not adding value here |
| high    | high      | low     | Reasoning was sound but rubric/task is mis-calibrated, **or** root cause was genuinely beyond the skill's reach |
| any     | any       | high on baseline = high on skill | Task too easy — discard |

## Pre-registration

Before running: commit the rubric, the task set, and the judge prompt to the repo. Don't tweak the rubric after seeing results — that's how you p-hack a skill into looking good.

## Inter-rater reliability check

For ~10 % of runs, have a second judge (different model, or human) score blind. Compute Cohen's κ per axis. If κ < 0.6 on Axis B (the substantive one), the rubric items are too vague — rewrite before trusting any aggregate numbers.
