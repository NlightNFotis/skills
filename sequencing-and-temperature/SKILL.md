---
name: sequencing-and-temperature
description: Cooking sequencing and heat control applied to migrations and deploys — order irreversible steps correctly, pace resource intensity, and reason about residual effects.
user-invocable: true
---

# Sequencing and Temperature

Act as a chef choreographing a multi-course service. Cooking is governed by two intertwined disciplines: **sequencing** (some steps must happen in a specific order because they are irreversible — you cannot unblanch a bean, unsear a steak, unsalt a brine) and **temperature** (heat is a resource you ramp up and down, with carryover effects that continue after the burner is off). Migrations, deploys, and dependency upgrades obey the same physics: certain steps lock in, certain operations have ramp time and residual effects, and the difference between a smooth service and a kitchen fire is choreography.

Success looks like: every irreversible step happens in an order where the next step *could not have* run earlier; intensity ramps match what the system can absorb; you respect carryover and never over-shoot. Failure looks like: dropping a column before traffic is off it, ramping deploy from 0% to 100% in one step because "it worked at 1%", or treating a synchronous index rebuild like an instant operation.

## When to Use This

- Designing or reviewing a multi-step migration (schema, data, infra)
- Choreographing a deploy, especially one that touches multiple services
- Ordering a dependency upgrade with breaking changes
- Planning a traffic shift, rollout, or feature flag ramp
- Sequencing an irreversible data operation (delete, anonymize, archive)
- Coordinating a cutover between two systems
- Whenever someone proposes "do A, then B, then C" and the order matters

**Escape hatch**: If steps are independent and reversible, sequence is decoration. Use this skill when at least one step locks in state, blocks a window, or has thermal-mass behavior the rest of the plan must respect.

## Core Mindset

Two questions sit at the heart of every cook:

1. **What can't be undone?** Sear, blanch, salt, deglaze — these change the dish permanently. Schema drops, data deletes, DNS TTL commits, rotated secrets, published packages. List them first; build the rest of the plan around their constraints.
2. **What's the heat?** Cooking adjusts a knob between low (slow, forgiving, low resource) and high (fast, unforgiving, high resource). Deploys and migrations have the same knob: 1% canary is low heat; 100% cutover is high heat. Higher heat means less margin for error and more carryover after you stop.

Ask:

- Which steps are irreversible? Are they last in the plan? If not, why not?
- Which steps must happen *before* an irreversible step (deglaze before the fond burns)?
- What is the active vs passive time of each step? What runs in the background?
- What is the ramp rate? Can the system absorb the next intensity level?
- What's the carryover — what continues after I stop the action?
- Is there a window (a thermal sweet spot) outside of which the step fails?
- What can I do in parallel without burning something else?

## Domain Vocabulary

| Cooking term | Meaning | Software analogue |
| --- | --- | --- |
| **Mise** | Pre-staged materials | Pre-deploy artifacts, snapshots |
| **Sear** | High-heat surface change; irreversible | DDL drop, secret rotation, package publish |
| **Braise** | Low-heat slow conversion | Background backfill, gradual reindex |
| **Blanch** | Quick boil + ice bath; sets state | Cutover with immediate verification |
| **Deglaze** | Capture fond *immediately* before it burns | Drain queue / capture state before teardown |
| **Sweat** | Coax moisture out at low heat | Slow cache warm, gradual rollout to 1% |
| **Reduce** | Concentrate by evaporation; one-way | Compaction, archival, retention trim |
| **Carryover / residual heat** | Continues cooking after burner off | In-flight requests, queued jobs, async retries |
| **Thermal mass** | Resistance to temperature change | Cache warm-up, JIT warmth, connection pool ramp |
| **Resting** | Let it settle before cutting | Bake-time / soak-time after deploy |
| **Window** | Narrow time band when a step works | DNS TTL window, lease window, off-peak window |
| **Cross-contamination** | Flavors / pathogens move between dishes | Shared state leaking between tenants/services |

## Step Classification

Before sequencing, classify every step:

| Class | Reversible? | Intensity | Examples |
| --- | --- | --- | --- |
| **Additive** | Yes (drop the addition) | Low | Add nullable column, add new endpoint, add feature flag (off) |
| **Switch** | Mostly (flip back) | Medium | Toggle reads to new column, swap traffic to new service |
| **Backfill** | Yes (re-run / no-op) | Low active, long passive | Populate new column, denormalize history |
| **Lock-in** | No | High | Drop column, delete data, publish package, rotate secret |
| **Window-bound** | N/A | N/A | DNS propagation, certificate rotation, lease renewal |

The Cardinal Rule: **lock-in steps go last**, after every switch has happened *and been verified*, and never inside the same change as the switch that depends on them.

## The Process

### Step 1: List Every Step and Classify

Write the operations as discrete, named steps. For each, mark class, reversibility, ramp time, and carryover.

```
STEP INVENTORY:
1. [name] — class: [additive/switch/backfill/lock-in/window], reversible: [Y/N],
   active time: [...], passive time: [...], carryover: [...]
2. ...
```

Weak: "Migrate users table."
Strong:
1. Add `email_verified_at` column nullable (additive, reversible, instant)
2. Backfill existing users (backfill, idempotent, ~6h passive)
3. Deploy code that double-writes (switch, reversible by re-deploy)
4. Deploy code that reads from new column (switch, reversible)
5. Verify zero reads from old column for 7 days (window)
6. Drop old column (lock-in, **irreversible**)

### Step 2: Find the Irreversibles and Pin Them Last

Mark every lock-in step. Each one must be preceded by every step it depends on, *and* a verification step. If a lock-in is anywhere but the end (or end of its phase), justify why.

The cook's principle: **sear before braise**, never the reverse — but **drop after switch**, never the reverse.

### Step 3: Identify Carryover and Bake-Time

For each step, ask: "What continues after I stop?"

- In-flight HTTP requests after a deploy: minutes
- Queued jobs after a worker rolling restart: until queue drains
- DNS cached records after TTL change: TTL × clients' caching behavior
- Connections in a pool after a config change: until churn
- Async retries from upstream: backoff window
- Materialized view refresh: until next refresh tick

Build **rest periods** into the plan after high-carryover steps. A migration that says "switch reads at T, drop column at T+5min" is the equivalent of slicing the roast straight off the fire — you'll lose all the juice and possibly miss in-flight readers.

### Step 4: Sequence the Steps

Apply ordering rules:

1. **Additive first.** Add the new thing alongside the old; nothing yet depends on it.
2. **Backfill before switch.** Don't switch reads to a column that isn't populated.
3. **Double-write before single-read.** Brief overlap means a switch is a flip, not a leap.
4. **Verify between switch and lock-in.** A bake-time window where rollback is still cheap.
5. **Lock-in last.** Drop, delete, publish, rotate.
6. **Deglaze immediately.** If a step has a perishable byproduct (queue contents, in-memory state, cached data), capture it *before* the next step begins.

```
SEQUENCED PLAN:
T0: [additive] Add column
T0+10m: [backfill] Start backfill (passive ~6h)
T+6h: [switch] Deploy double-write (low heat)
T+6h+30m: [verify] Confirm double-write parity
T+7h: [switch] Deploy reads from new (low heat ramp 1%→10%→100%)
T+7h+1d: [verify] 24h soak; zero reads from old
T+8d: [lock-in] Drop old column
```

### Step 5: Set the Heat

Choose intensity per step. Higher heat = faster, but less margin and more carryover.

| Heat | Cook | Software |
| --- | --- | --- |
| **Low** | Sweat onions, slow braise | Canary 1%, slow rollout, off-peak run |
| **Medium** | Sauté, simmer | 10–50% rollout, business-hours non-peak |
| **High** | Sear, deep fry | Full cutover, 100% switch, peak traffic |

Rules of thumb:
- Start low when the system's response is unknown
- Don't ramp from low to high in one step — ramp through medium to detect drift
- Keep the heat low when carryover is high (a 100% deploy with a 30-minute queue drain is a 30-minute high-heat exposure)

### Step 6: Identify Windows and Constraints

Some steps only work in a window:

- DNS changes need TTL × N for propagation
- Cert renewals need overlap with the old cert
- Off-peak windows for expensive operations
- Lease windows for distributed locks
- "Don't deploy on Friday" social windows

For each window, write down: opens at, closes at, what to do if you miss it.

### Step 7: Plan the Parallelism

Some steps can run on adjacent burners. Some compete for the same resource.

- Backfill + normal traffic: usually parallel-safe with rate limiting
- Two schema changes on the same table: serialize
- Deploy + migration: usually serialize (deploy depends on migration)
- Cache warm + traffic ramp: parallel; warm leads ramp by minutes

Mark each parallel pair and the resource they share; if shared resource saturates, the cooks collide.

### Step 8: Define the Off-Ramp at Each Step

After every irreversible step, document: "If this fails, what is the recovery?"

Note: after a true lock-in, recovery is *forward*, not back. "Restore from snapshot" is the off-ramp for a dropped column. If your only recovery is "redeploy and pray", the lock-in is too early.

## Output Format

```
SEQUENCING PLAN

Operation:

Step inventory (with classification):
1. ...

Irreversible steps:
- ...

Sequenced timeline:
T0: ...
T+...: ...

Heat plan:
- Step X: low (1% → 10% → 100% over 30m)
- ...

Windows:
- ...

Carryover / rest periods:
- ...

Parallel tracks:
- ...

Off-ramps:
- After step X: ...
- After lock-in step Y: forward-only recovery via ...

Risks:
- ...
```

## Anti-Patterns to Avoid

- **Searing twice**: doing two irreversible steps in the same change so neither can be rolled back independently
- **Slicing the roast**: no rest period between switch and lock-in; in-flight work gets cut off
- **Cold-to-high in one step**: jumping from 1% canary to 100% with no medium step
- **Forgetting carryover**: treating "deploy done" as "old code gone" while in-flight requests still run it
- **Deglaze later**: assuming you can recapture state after the next step; the fond is already burnt
- **Window roulette**: planning a step that only works in a window without confirming the window is open
- **Optimistic parallelism**: running two burners hot on the same shared resource and being surprised by saturation
- **Drop-then-verify**: putting verification *after* the lock-in step so failure is unrecoverable

## Relationship to Other Skills

- `mise-en-place` stages the materials each step needs; sequencing decides the order they go into the pan.
- `taste-as-you-go` is the verification discipline *between* sequenced steps — especially before each lock-in.
- `recipe-rescue` handles in-flight failures; good sequencing reduces what rescue must do.
- `preflight-checklist` verifies each step's preconditions; sequencing decides which preconditions matter for which step.
- `feedback-loop-analysis` complements heat reasoning — both deal with ramp rates, retries, and saturation.
- `resilience-engineering` designs systems that tolerate aggressive sequencing; without it, every step must be cooked low.
