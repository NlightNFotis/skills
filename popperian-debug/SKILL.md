---
name: popperian-debug
description: Structured debugging methodology based on Popperian falsificationism. Use when stuck on a bug, facing a confusing failure, or when initial debugging attempts haven't worked.
user-invocable: true
---

# Popperian Debugging

A structured debugging methodology based on abductive reasoning and falsificationism. Instead of confirming what you think is wrong, actively try to **disprove** hypotheses to find the true root cause.

## When to Use This

- You've hit a bug or test failure that isn't immediately obvious
- Your first fix attempt didn't work
- You're seeing confusing or contradictory symptoms
- You're going in circles on a debugging problem

**Escape hatch**: If the stack trace or error points to a single local defect with a direct fix (missing import, typo, null access with a clear line, assertion mismatch with obvious cause), skip this workflow — just fix it and verify. If you invoked this skill but the bug turns out to be trivial, exit early.

## The Process

### Step 0: Reproduce and Isolate

Before anything else, establish a reliable reproduction:

1. Run the failing test/command and confirm you see the failure
2. Minimize the repro — what's the smallest input or scenario that triggers it?
3. Classify the failure:
   - **Deterministic**: Fails every time → proceed normally
   - **Intermittent/flaky**: See the [Flaky Failures](#flaky-failures) section below
   - **Environment-specific**: Check config, versions, OS differences

If you **cannot reproduce**, focus on capturing more evidence (logs, traces, state dumps) before generating hypotheses.

### Step 1: Collect Facts

Gather concrete evidence. The quality of your hypotheses depends on the quality of your facts.

- What is the exact error message or unexpected behavior?
- What is the stack trace (if any)?
- When did this start happening? What changed recently?
- What inputs trigger it? What inputs don't?
- Are there relevant logs, warnings, or other signals?

Use the cheapest tool that gets the fact: `view`/`grep` for code inspection, `bash` for running tests/repros, logs or assertions for runtime evidence.

**Write down your facts explicitly** before moving on:

```
FACTS:
1. [exact error/behavior observed]
2. [reproduction conditions]
3. [relevant recent changes]
4. [environmental context]
```

### Step 2: Generate 2–4 Hypotheses

Based on the facts, generate **2–4 materially distinct** hypotheses. Not exhaustive — just enough to avoid anchoring on your first idea.

Use these categories to ensure diversity:
- **Logic error**: Is the code doing the wrong thing?
- **State/data issue**: Is unexpected data flowing through?
- **Timing/ordering**: Race condition or ordering dependency?
- **Environment**: Runtime environment difference?
- **Upstream change**: Did a dependency or input change?
- **Assumption violation**: Is a precondition or invariant broken?

### Step 3: Rank by Likelihood

Order hypotheses considering:
- Consistency with ALL observed facts
- Simplicity (Occam's razor)
- Cost to test (prefer cheap tests first)

```
HYPOTHESES (ranked):
H1: [most likely] — because [reasoning]
H2: ...
H3: ...
```

### Step 4: Disprove the Leading Hypothesis

Starting with H1, design a test that would **disprove** it. Don't look for confirming evidence — look for disconfirming evidence.

Ask: **"If this hypothesis is WRONG, what would I expect to see?"** Then test that prediction.

Concrete ways to falsify:
- Inspect the exact code path (does control flow actually reach the suspected code?)
- Compare passing vs failing input (what's different?)
- Add a targeted assertion or log at the suspected point
- Run a narrowed test that isolates the suspected component
- Check environment/version/config differences
- Bisect recent changes (`git bisect` or manual)
- Force a different ordering or timing to rule out races

**Change one thing at a time.** Do not bundle speculative fixes — you won't know what actually worked.

```
TESTING H1: [hypothesis]
- If wrong, I'd expect: [prediction]
- Test: [what I did]
- Result: [what happened]
- Verdict: DISPROVED / NOT DISPROVED / INCONCLUSIVE
```

Verdicts:
- **DISPROVED**: Evidence directly contradicts the hypothesis. Move to H2.
- **NOT DISPROVED**: You tried to disprove it and couldn't. This is your leading candidate.
- **INCONCLUSIVE**: The test didn't clearly confirm or deny. Try a different test for the same hypothesis.

### Step 5: Converge or Continue

- **Hypothesis NOT DISPROVED with confidence**: Trace the earliest point where expected and actual behavior diverge. Pursue the fix.
- **All hypotheses disproved**: Proceed to Step 6.
- **Hypothesis NOT DISPROVED but uncertain**: Dig deeper — can you find the specific line, condition, or state transition?

### Step 6: Iterate with New Knowledge

If all hypotheses were disproved, you've still made progress — you know more than before.

1. Review what you learned from the disproval tests
2. Check if any test revealed **new facts** not in your original list
3. Update your facts list
4. Generate new hypotheses from the expanded evidence
5. Return to Step 3

**When to change tactics**: After 2–3 cycles without materially new facts, stop the hypothesis loop and switch approaches:
- Are you looking at the right system/component?
- Try `git bisect` to find the introducing commit
- Build a minimal reproduction from scratch
- Check if the bug is in a dependency rather than your code

### Step 7: Fix and Verify

Once you've identified the root cause:

1. Implement the fix (change one thing)
2. Re-run the original reproduction — confirm it passes
3. Run nearby/affected tests — check for regressions
4. Remove any temporary logging or instrumentation you added
5. Verify the fix explains the original symptoms (not just masking them)

The task is done when the root cause is isolated, the fix is verified, and no regressions are introduced.

## Flaky Failures

For intermittent bugs, adapt the process:

- First, **increase observability**: add logging, capture state, record timing
- Control sources of non-determinism if possible (randomness, time, concurrency)
- Compare passing vs failing runs — what differs?
- Prioritize timing, state, and environment hypotheses over logic hypotheses
- Consider running the test in a loop to establish a failure rate

## Anti-Patterns to Avoid

- **Confirmation bias**: Looking for evidence that supports your theory instead of trying to disprove it
- **Anchoring**: Fixating on the first hypothesis without generating alternatives
- **Skipping fact collection**: Jumping to hypotheses without understanding symptoms
- **Unfalsifiable hypotheses**: If you can't design a test to disprove it, make it more specific
- **Stacking fixes**: Changing multiple things at once, then not knowing what worked
- **Infinite loops**: Change tactics if you're not gaining new information
