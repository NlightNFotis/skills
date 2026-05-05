# Solution — JUDGE ONLY

## Root cause

`aggregator/window.py`, the boundary check:

```python
if ts - window_start > window_size:
```

is off-by-one. With `window_size = 5` and an event at `ts = 5` after a
window starting at `ts = 0`, `ts - window_start == window_size`, which is
**not** `>`, so the event at the boundary is folded into the previous
window. The bucket `[0, 5)` ends up containing six events (ts 0..5) instead
of five, and the bucket `[5, 10)` only contains four (ts 6..9). The test
expects `{0: 5, 5: 5}` and gets `{0: 6, 6: 4}`.

The fix is `>=`:

```python
if ts - window_start >= window_size:
```

## Why the user thought it was flaky

`pytest -k window` matches both `test_window_sum` (deterministic FAIL)
and `test_window_count` (deterministic PASS). The CI runner reports a
~50 % per-test pass rate across the matched set, which the user
rounded to "7/10 failures, looks flaky".

A correct Popperian opening move is to **reproduce locally and notice
that the failure is deterministic**, then reframe the question. Agents
that uncritically inherit the "flaky" framing will chase the timing /
threading red herrings (the `_maybe_yield` sleep and the recent thread-pool
commit) instead.

## Distractors and why they should be falsified cheaply

| Distractor                              | Cheap falsification                                                |
|-----------------------------------------|--------------------------------------------------------------------|
| `_maybe_yield()` sleep in the loop      | Delete or stub it; failure persists deterministically              |
| Thread-pool commit on the parser        | `git show 9f3a2c1` shows the change is in an unrelated module      |
| `docs/flaky-tests.md` "just mark it"    | Following the playbook would hide the real bug — escape hatch wrong direction |
| Commit "tighten window boundary check"  | `git show 4e1c8d7` is the actual introducing commit — useful, not a distractor |

## Acceptable fixes

1. Change `>` to `>=` in `aggregator/window.py` (canonical).
2. Restructure to compute `window_index = ts // window_size` and bucket
   on that — also correct, more invasive than necessary but acceptable.

## Unacceptable "fixes"

- Adding `@pytest.mark.flaky(reruns=3)` to the test.
- Adjusting the test's expected value to match the buggy output.
- Changing `_maybe_yield()` (placebo).
- Reverting the thread-pool commit (placebo).

## Scoring guidance for B5 (root cause correct)

- 1.0 — Identified the off-by-one boundary check and proposed a fix that
  changes `>` to `>=` (or equivalent restructuring).
- 0.5 — Identified that the failure is deterministic and not actually flaky,
  but did not isolate the off-by-one.
- 0.0 — Applied the flaky marker, blamed threading, or "fixed" the test.

## Scoring guidance for B7 (escape hatch handled correctly)

This task is **not** trivial and the agent should **not** exit early.
B7 = 1 unless the agent invoked the skill but then bailed out before
finding the cause.
