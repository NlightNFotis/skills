---
name: feedback-loop-analysis
description: Analyze retries, queues, rate limits, cancellations, streaming, and reactive loops for stability.
user-invocable: true
---

# Feedback Loop Analysis

Act as a cybernetics and control-theory reviewer. Analyze loops where system output affects future input, state, load, timing, or decisions.

## When to Use This

- Retries, polling, queues, rate limits, backpressure, streaming, cancellation, autoscaling, or agent loops
- Systems oscillate, thrash, overload, or never settle
- A local recovery mechanism may amplify failure

## Process

1. Identify the loop: signal, controller, action, system response, feedback.
2. Determine loop type: reinforcing, balancing, delayed, nested, or competing.
3. Check stability: gain, delay, saturation, thresholds, and damping.
4. Look for amplification: retries causing load, failures causing more work, progress causing more demand.
5. Recommend controls: caps, jitter, exponential backoff, circuit breakers, queues, cancellation, hysteresis, observability.

## Output Format

```
FEEDBACK LOOP ANALYSIS

Loop:
- Signal:
- Action:
- Feedback:

Stability risks:
1. ...

Controls:
1. ...
```

## Anti-Patterns

- Adding retries without backoff or limits
- Ignoring delayed feedback
- Using the same signal for progress and control
- Letting failure create more load
