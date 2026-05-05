# Skill Evaluation Harness — Sketch

Pilots on `popperian-debug` but the schema is skill-agnostic so it scales.

## Directory layout

```
skill-eval/
├── skills.yaml                          # which skills are under test
├── arms.yaml                            # arm definitions (baseline, skill, placebo)
├── tasks/
│   └── popperian-debug/
│       ├── T-ON-1/
│       │   ├── task.yaml                # prompt, trigger class, model config
│       │   ├── fixtures/                # repo snapshot the agent operates on
│       │   ├── repro.sh                 # produces the failing symptom
│       │   └── solution.md              # judge-only: root cause + acceptable fixes
│       ├── T-ON-2/...
│       └── ...
├── rubrics/
│   └── popperian-debug.yaml             # the rubric from rubric.md, machine-readable
├── judge/
│   ├── prompt.tmpl                      # judge system prompt (rubric-aware, blind)
│   └── schema.json                      # expected JSON output shape
├── runs/                                # one JSONL per (skill, run-id), append-only
│   └── popperian-debug/2026-05-05_run-001.jsonl
├── scores/                              # one JSONL per (skill, run-id)
│   └── popperian-debug/2026-05-05_run-001.jsonl
├── runner.py                            # executes (task × arm × seed) → runs JSONL
├── scorer.py                            # reads runs JSONL → calls judge → scores JSONL
└── analyze.sql                          # DuckDB queries over runs+scores
```

Append-only JSONL means you can re-score without re-running, re-run without losing scores, and diff across days cheaply.

## Schemas

### `task.yaml`

```yaml
id: T-ON-1
skill: popperian-debug
trigger: on            # on | off | adversarial
prompt: |
  test_window_sum is flaky on CI — passes locally most of the time...
fixture_dir: fixtures/
repro_cmd: ./repro.sh
expected_repro_exit: 1
notes: |
  Distractor: time.sleep in helper. True cause: off-by-one + hash seed ordering.
```

### `arms.yaml`

```yaml
- id: A_baseline
  description: No skill mentioned, no system prompt change.
  injection: none

- id: B_skill
  description: Explicit /popperian-debug invocation prepended to the user prompt.
  injection: prepend
  text: "/popperian-debug\n\n"

- id: C_placebo
  description: Invoke an unrelated procedural skill (recipe-rescue) — controls for
    "any skill invocation increases structure".
  injection: prepend
  text: "/recipe-rescue\n\n"

# Optional fourth arm — controls for "anything that slows the agent down helps"
- id: D_slowdown
  description: Plain instruction to think step by step before acting.
  injection: prepend
  text: "Before acting, think carefully and write out your reasoning step by step.\n\n"
```

### Run record (one JSONL row per execution)

```json
{
  "run_id": "2026-05-05_001",
  "task_id": "T-ON-1",
  "skill": "popperian-debug",
  "arm": "B_skill",
  "seed": 3,
  "model": "claude-opus-4.7",
  "started_at": "2026-05-05T12:30:00Z",
  "ended_at":   "2026-05-05T12:34:11Z",
  "transcript": "<full agent transcript, including tool calls and outputs>",
  "tool_calls": 17,
  "tokens_in":  4321,
  "tokens_out": 2890,
  "agent_final_answer": "<just the agent's last message>",
  "agent_proposed_fix": "<extracted patch, if any>",
  "repro_after_fix_exit": 0,
  "harness_version": "0.1.0"
}
```

### Score record

```json
{
  "run_id": "2026-05-05_001",
  "task_id": "T-ON-1",
  "arm": "B_skill",
  "seed": 3,
  "judge_model": "claude-opus-4.7",
  "judge_seed": 1,
  "axis_a": {"A1":1,"A2":1,"A3":1,"A4":1,"A5":1,"A6":1,"A7":0,"A8":1},
  "axis_b": {"B1":1,"B2":1,"B3":1,"B4":1,"B5":1,"B6":1,"B7":1},
  "axis_c": {"C1":1,"C2":1},
  "process_score":   0.875,
  "reasoning_score": 1.0,
  "outcome_score":   1.0,
  "judge_rationale": "<judge's per-item justification, free text>",
  "scorer_version": "0.1.0"
}
```

## Runner pseudocode

```python
def run_eval(skill, tasks, arms, seeds, model):
    for task in tasks:
        for arm in arms:
            for seed in seeds:
                env = checkout_fixture(task.fixture_dir)
                prompt = apply_arm(arm, task.prompt)
                transcript = invoke_agent(
                    model=model, seed=seed, cwd=env,
                    initial_message=prompt,
                    max_tool_calls=50, timeout_s=600,
                )
                fix_applied = extract_and_apply_fix(transcript, env)
                repro_exit = run(task.repro_cmd, cwd=env) if fix_applied else None
                append_jsonl(runs_path(skill), run_record(...))
```

Important runner properties:

- **Hermetic fixtures**: each run gets a fresh checkout. The agent can break things and it doesn't poison the next run.
- **Caps**: tool-call cap and wall-clock cap so a runaway agent can't blow your budget. Record whether the cap was hit — that's a result, not a bug.
- **Determinism where possible**: pin model version, set seed, pin fixture commit. Record everything in the run record so post-hoc analysis is honest.
- **Resumable**: keyed on (task, arm, seed); skip rows already in the JSONL.

## Judge prompt template (`judge/prompt.tmpl`)

```
You are scoring an AI agent's debugging transcript against a rubric. You do not
know which "arm" of an experiment produced this output, and you must not guess.

TASK PROMPT THE AGENT RECEIVED:
{{task.prompt}}

GROUND TRUTH (do not reveal in your rationale, but use for B5/C1/C2):
Root cause: {{solution.root_cause}}
Acceptable fixes: {{solution.acceptable_fixes}}

AGENT TRANSCRIPT:
{{run.transcript}}

RUBRIC:
{{rubric_yaml}}

Score each item as 0 or 1 (or 0.5 where the rubric explicitly allows). For each
item, give a one-sentence justification citing specific text from the transcript.
If an item is not applicable because a prerequisite step was skipped, score 0
and note "prerequisite skipped".

Return JSON matching this schema:
{{score_schema_json}}

Be strict. Do not award an item for "the agent kind of did this" — the rubric
items are gatekeepers.
```

Two important judge mitigations:

1. **Blind to arm.** Never include the arm label in the judge prompt.
2. **Score `vocabulary` and `decision` separately.** Axis A (process) is largely
   pattern-matchable; Axis B (reasoning) requires the judge to reason about
   whether the *content* was sound. If you fold them together, parroting will
   masquerade as competence.

## Analysis (`analyze.sql`, DuckDB on the JSONL)

```sql
-- Headline: lift over baseline, per arm, with naive 95% CI
WITH agg AS (
  SELECT
    task_id, arm,
    avg(outcome_score)   AS mean_outcome,
    avg(reasoning_score) AS mean_reasoning,
    avg(process_score)   AS mean_process,
    stddev_samp(outcome_score) / sqrt(count(*)) AS se_outcome,
    count(*) AS n
  FROM read_json_auto('scores/popperian-debug/*.jsonl')
  GROUP BY task_id, arm
)
SELECT
  b.task_id,
  s.arm,
  s.mean_outcome,
  s.mean_outcome - b.mean_outcome AS lift_vs_baseline,
  s.mean_outcome - 1.96 * s.se_outcome AS ci_low,
  s.mean_outcome + 1.96 * s.se_outcome AS ci_high,
  s.n
FROM agg s
JOIN agg b ON b.task_id = s.task_id AND b.arm = 'A_baseline'
WHERE s.arm <> 'A_baseline'
ORDER BY s.task_id, s.arm;
```

Other queries you'll want:

- **Parroting detector**: per-arm correlation between Axis A (process) score and Axis B (reasoning) score. A skill working as intended should show A and B moving together. A parroting failure shows high A, flat B.
- **Trigger sanity**: outcome by `trigger` × `arm`. If `B_skill` beats `A_baseline` on `off`-trigger tasks, the lift is mostly placebo.
- **Length confound**: regress outcome on `tokens_out` within arm, then look at residual lift. If the lift evaporates after controlling for length, the skill is just buying tokens.
- **Cap-hit rate**: fraction of runs hitting the tool/time cap, per arm. Skills that explode complexity show up here.

## Rolling it out

Order of operations for the pilot:

1. Build fixtures + `solution.md` for the 8 tasks. (Highest effort step.)
2. Define `arms.yaml` with the 4 arms above.
3. Wire the runner against your agent execution path; smoke-test on T-ADV-1.
4. Run N=5 seeds × 8 tasks × 4 arms = 160 runs. Budget accordingly.
5. Score with judge; spot-check 16 (10 %) by hand to calibrate.
6. Compute headline, parroting, trigger sanity, length confound.
7. **Decide whether the framework itself is sound** before scaling to other skills. Common pilot-stage findings: rubric items too vague (κ low), tasks too easy (everyone scores 1), tasks too hard (everyone scores 0), judge biased toward longer outputs.
8. Only after 7, fan out to the other ~84 skills, one per week.

## What this harness deliberately does not do

- Doesn't try to evaluate skills that operate across multi-session memory or long-horizon planning. Those need a different harness (sequential evaluation, checkpoint scoring).
- Doesn't model human-in-the-loop interaction. If a skill's value is "asks better clarifying questions," you need a simulated user, which is its own subproject.
- Doesn't detect *negative interactions between skills*. Each skill is evaluated in isolation. Cross-skill conflict deserves its own study after individual lifts are characterised.
