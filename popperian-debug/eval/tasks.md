# `popperian-debug` Task Suite

Each task has:
- A **fixture**: a small repo or file the agent can run / inspect
- A **prompt**: the user-facing message the agent receives
- A **trigger class**: `on` / `off` / `adversarial`
- A **ground truth**: the actual root cause and the minimal correct fix
- **Distractors**: red herrings deliberately seeded into the fixture

Eight tasks below — three on-trigger, two off-trigger, three adversarial. Real evaluations want ≥15 per trigger class for stable estimates; this is the pilot set.

---

## ON-TRIGGER (skill should help)

### T-ON-1: Off-by-one that masquerades as a flaky test

**Fixture**: a Python module with a sliding-window aggregator. Test `test_window_sum` fails ~70 % of the time; passes ~30 %.

**Real cause**: window boundary uses `>=` where it should use `>`. The flakiness is illusory — failure depends on input ordering produced by a `dict.items()` traversal whose order is stable per-run but varies because the dict is built from a `set` literal earlier (PYTHONHASHSEED).

**Distractors**:
- A `time.sleep(0.001)` left in a helper for "debugging"
- A recent commit message: "speed up parser by switching to threads"
- A flaky-tests doc in the repo suggesting "add `@pytest.mark.flaky(reruns=3)`"

**Why it tests the skill**: the obvious move is to chase concurrency or mark-flaky. The Popperian move is to falsify the timing hypothesis cheaply (force serial execution; failure persists) before going there.

**Prompt**: `test_window_sum is flaky on CI — passes locally most of the time, fails maybe 7/10 on CI. Can you figure out what's going on?`

---

### T-ON-2: Confusing symptom from an upstream change

**Fixture**: a JSON-parsing service that started returning empty results after a dependency bump. No code changes in the service itself.

**Real cause**: the bumped JSON library changed default behaviour for trailing commas — input that previously parsed as `{...}` now raises and the service swallows the exception, returning `[]`.

**Distractors**:
- The exception is caught and logged at DEBUG level (invisible in default config)
- A feature flag that "looks suspicious" was toggled around the same time
- The error rate dashboard looks normal because the service returns 200 with `[]`

**Prompt**: `Service is returning empty arrays for what used to be valid input. Nothing in our code changed this week. Started Tuesday afternoon. Investigate.`

---

### T-ON-3: Race condition disguised as a config bug

**Fixture**: a worker that intermittently writes `null` to a "user_email" column.

**Real cause**: two goroutines both fetch and update the same user record without locking; the loser's stale read overwrites the winner's email with the original (which was `nil` for users created in the last 5 minutes).

**Distractors**:
- A config file has `email_required: false` in the staging environment
- A recent migration added a nullable email column
- Logs show the email arriving correctly from the upstream API

**Prompt**: `Some users end up with NULL email after the onboarding worker runs. Maybe 1 in 200. Can you find the bug?`

---

## OFF-TRIGGER (skill should not be invoked, or should add no value)

### T-OFF-1: Code generation request

**Prompt**: `Write a function that converts a CSV string into a list of dicts, using the first row as keys.`

**Why**: pure generation; no failure to debug. Invoking `popperian-debug` should either be a no-op or visibly inflate the response without changing correctness.

---

### T-OFF-2: Documentation lookup

**Prompt**: `What's the difference between Python's @staticmethod and @classmethod?`

**Why**: knowledge retrieval; debugging frame is irrelevant. Watching for false positives in auto-surfacing.

---

## ADVERSARIAL-TRIGGER (looks like the skill applies but escape hatch should fire)

### T-ADV-1: The error message tells you the answer

**Fixture**: a Node script that crashes with `ReferenceError: configg is not defined at config.js:14`.

**Real cause**: typo on line 14 — `configg` should be `config`.

**Prompt**: `My script is crashing — here's the stack trace: [trace]. Help me fix it.`

**Expected behaviour**: agent fixes the typo and verifies. If it produces a FACTS list, four hypotheses, and a falsification plan for a one-character typo, the escape hatch failed.

---

### T-ADV-2: Bug already explained in a comment

**Fixture**: function with a `# TODO: this breaks when input is empty — handle empty case` comment immediately above the failing line.

**Prompt**: `This function blows up on some inputs — can you fix it?`

**Expected behaviour**: agent reads the comment, handles the empty case, verifies. Full Popperian workflow here is overkill.

---

### T-ADV-3: User has already done the diagnosis

**Prompt**: `I traced the bug — it's that we're calling `parse_date` with a string in `MM/DD/YYYY` format but the parser expects ISO 8601. I just need you to add the conversion at the call site in `ingest.py`.`

**Expected behaviour**: agent makes the targeted change. Re-running fact collection and hypothesis generation here is disrespectful of the user's work and burns tokens.

---

## Building fixtures

Keep each fixture under ~200 LOC and self-contained in `fixtures/T-XX/`. Provide a `repro.sh` that produces the failing symptom deterministically (or with a controlled flake rate, for T-ON-1). Provide a `solution.md` (read only by the judge) that states the root cause, the minimal fix, and a list of acceptable equivalent fixes.

## Why these were chosen

The on-trigger tasks each have a *plausible-but-wrong* leading hypothesis baked in. That's the only way to test whether the skill changes the agent's behaviour — if the right answer is the obvious one, every arm scores the same and you learn nothing. The adversarial tasks attack the inverse failure: that the skill, once invoked, may steamroll trivial cases into pointless ceremony.

## Sourcing real tasks

In addition to synthetic fixtures, mine the `session_store` for past sessions where the user's first message contained debugging language (`flaky`, `intermittent`, `not sure why`, `tried X already`). Cluster by symptom type to make sure your synthetic tasks span the same distribution as real ones.
