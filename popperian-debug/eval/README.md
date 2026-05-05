# `popperian-debug` evaluation suite

Pilot harness for measuring whether invoking `popperian-debug` actually
changes agent behaviour for the better, vs. the skill being structural
window-dressing on top of unchanged reasoning.

This directory is **co-located with `SKILL.md` for discoverability**. The
CLI's skill loader reads `SKILL.md` only; this `eval/` subtree is inert
from the loader's perspective. If a future loader change makes that
assumption wrong, move this whole tree to `<repo>/evals/popperian-debug/`.

## Layout

```
eval/
├── README.md               this file
├── rubric.md               human-readable scoring rubric
├── tasks.md                catalogue of the 8 pilot tasks
├── harness.md              runner/scorer/analysis design (not yet implemented)
├── rubrics/
│   └── popperian-debug.yaml    machine-readable rubric (judge consumes this)
├── judge/
│   ├── prompt.tmpl             blind, rubric-aware judge prompt
│   └── schema.json             JSON schema the judge must emit
└── tasks/
    └── T-ON-1/                 one fully-built task (off-by-one as "flaky")
        ├── task.yaml
        ├── solution.md         JUDGE-ONLY ground truth — never shown to agent
        └── fixtures/
            ├── repro.sh
            ├── aggregator/window.py
            ├── tests/test_window.py
            ├── docs/flaky-tests.md
            └── git_log.txt
```

## Quick checks you can do today

Verify the T-ON-1 fixture still triggers the bug deterministically:

```sh
cd tasks/T-ON-1/fixtures
./repro.sh                  # expect exit 1, "1 failed, 1 passed"
```

Verify the canonical fix resolves it:

```sh
sed -i.bak 's/ts - window_start > window_size/ts - window_start >= window_size/' \
    aggregator/window.py
./repro.sh                  # expect exit 0, "2 passed"
mv aggregator/window.py.bak aggregator/window.py
```

## Status

| Component                      | Status        |
|--------------------------------|---------------|
| Rubric (human + machine)       | done          |
| Judge prompt + schema          | done          |
| Task catalogue (8 tasks)       | drafted in tasks.md |
| T-ON-1 fixture                 | built, verified |
| T-ON-2, T-ON-3, T-ADV-{1,2,3}, T-OFF-{1,2} | not yet built |
| `runner.py`                    | sketched in harness.md, not implemented |
| `scorer.py`                    | sketched in harness.md, not implemented |
| `analyze.sql`                  | sketched in harness.md, not implemented |

## Design highlights worth re-reading before extending

- **Three independent axes.** Process (A), Reasoning (B), Outcome (C).
  Never collapse them — the whole point is to detect "high A, low B"
  parroting.
- **Four arms, including a placebo skill and a slowdown control.**
  Without these you cannot distinguish "this skill helps" from "any
  structured prompt helps".
- **Judge is blind to which arm produced a transcript.** Enforced by
  the runner; do not relax this.
- **`solution.md` is judge-only.** Never include it in the agent's
  context or in the harness invocation prompt.

See `harness.md` for the full design discussion.

## What this harness deliberately does NOT measure

- Multi-session memory effects.
- Skill–skill interactions (each skill is evaluated in isolation).
- Whether the skill's *description* frontmatter triggers correctly under
  the auto-surfacing logic — that's a separate retrieval-quality eval.
