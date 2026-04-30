---
name: time-value-of-money
description: Apply DCF and present-value reasoning to engineering decisions — refactor-vs-ship, tech debt, and roadmap timing — and counteract hyperbolic discounting.
user-invocable: true
---

# Time Value of Money

Act as a financial analyst running a discounted cash flow (DCF) on engineering work. A dollar today is worth more than a dollar tomorrow because today's dollar can earn interest, fund other projects, or hedge uncertainty. The same is true for engineering value: shipping a feature now has different worth than shipping it next quarter, and accepting tech debt now has a real, compounding interest cost.

Success looks like: making explicit the discount rate you're applying, comparing alternatives in present-value terms, and noticing when human bias (hyperbolic discounting) is pushing the team toward "ship now, fix later" beyond what a rational discount rate justifies. Failure looks like always deferring debt repayment because future pain feels small, then drowning in compounded interest two years later.

## When to Use This

- "Should we ship this now or polish it for two more weeks?"
- "Should we pay down this tech debt or build feature X?"
- Roadmap decisions across quarters or years
- Refactor-vs-rewrite trade-offs
- Estimating the cost of accumulating workarounds
- "We'll fix it next quarter" promises that need to be evaluated honestly
- Migration decisions with up-front cost and long-term payoff

**Escape hatch**: For purely tactical, same-day decisions with no compounding consequences, this skill is overkill. Use it when time horizons span weeks-to-years and value/cost streams unfold over time.

## Core Mindset

Ask:

- What is the **stream of value or cost** over time, not just the headline number?
- What **discount rate** applies — what else could we do with this engineering capacity?
- Is this cost **one-time** or **compounding**?
- Am I (or the team) being **hyperbolically biased** — over-weighting the near term?
- What is the **opportunity cost** of doing this instead of the next-best thing?
- When does the **payback** happen, and is the team likely to still be here to enjoy it?
- If I do nothing, what happens to the cost over the next 4 quarters?

## Domain Vocabulary

| Term | Definition | Engineering analog |
| --- | --- | --- |
| **Present value (PV)** | Today's value of a future cash flow | Today's eng-equivalent value of future savings |
| **Future value (FV)** | What today's value grows to | What unfixed debt costs in N quarters |
| **Discount rate (r)** | Rate used to discount future to present | Eng team's hurdle rate / opportunity cost |
| **NPV** | Σ (cash flow_t / (1+r)^t) — sum of discounted flows | Net engineering value of a project |
| **IRR** | Discount rate that makes NPV = 0 | Implied "return" of an eng investment |
| **Payback period** | Time to recoup initial outlay | Months until a refactor breaks even |
| **Compound interest** | Interest on interest | Tech debt that creates more debt |
| **Hyperbolic discounting** | Bias: over-weight near-term, under-weight long-term | "Ship now, we'll fix it" |
| **Exponential discounting** | Rational baseline; constant rate r per period | Disciplined long-horizon reasoning |
| **Opportunity cost** | Value of next-best alternative foregone | What else this sprint could have built |
| **Rule of 72** | Doubling time ≈ 72 / rate% | Debt at 20%/quarter doubles in ~3.6 quarters |

## The Process

### Step 1: Frame the Decision as Cash Flows over Time

Lay out the decision as a sequence of value/cost events with timestamps.

```
DECISION: [refactor module X now] vs [defer 6 months]

OPTION A — Refactor now:
- t=0: cost 3 eng-weeks
- t=1..N quarters: save 0.5 eng-weeks/quarter on related work

OPTION B — Defer:
- t=0: cost 0
- t=1..N quarters: pay 0.5 eng-weeks/quarter friction
- t=2 quarters: cost 5 eng-weeks (debt has grown)
- t=4+ quarters: cost 10+ eng-weeks (compounding)
```

If you can't write down the time series, you don't yet understand the decision.

### Step 2: Pick a Discount Rate

The discount rate is the **return on the next-best use of the same engineering time**. Be explicit.

Reasonable defaults:
- High-growth product, lots of opportunity: r ≈ 15–25% per quarter
- Stable product, fewer alternatives: r ≈ 5–10% per quarter
- Maintenance team, near-zero alternatives: r ≈ 2–5% per quarter

Higher r → defer-friendly (future costs feel smaller).
Lower r → repay-friendly (future costs feel real).

Calibrate against reality: if you claim r = 30%/quarter, you're claiming each quarter delivers 30% more value than the last. Be honest.

### Step 3: Compute NPV for Each Option

Apply the discount: PV = FV / (1 + r)^t.

Worked example with r = 10%/quarter:

```
OPTION A — Refactor now:
- t=0: −3 (cost)
- t=1: +0.5 / 1.10 = +0.45
- t=2: +0.5 / 1.21 = +0.41
- t=3: +0.5 / 1.33 = +0.38
- t=4..8: ~+1.4 total
NPV ≈ −3 + 2.6 + tail ≈ slightly positive over 2 years

OPTION B — Defer 6 months:
- t=0: 0
- t=1: −0.5 / 1.10 = −0.45
- t=2: −0.5 / 1.21 = −0.41 (then debt grows)
- t=3: −1.0 / 1.33 = −0.75
- ...
NPV ≈ steadily negative, growing
```

Don't get hung up on precision. Order-of-magnitude DCF is enough to surface that "defer forever" is rarely positive.

### Step 4: Identify Compounding vs One-Time Costs

The single most important question: **does this cost compound?**

| Cost type | Behavior | Examples |
| --- | --- | --- |
| **One-time** | Fixed, doesn't grow | A bug we hit once and patched |
| **Linear** | Grows with usage | More API calls = more cost, no acceleration |
| **Compounding** | Grows on the previous total | Tech debt: each new feature builds on bad foundation, making the next one harder |

Compounding costs use **Rule of 72**: at compounding rate r%/period, the cost doubles every 72/r periods.

- Tech debt compounding at 10%/quarter doubles every ~7 quarters
- Tech debt compounding at 20%/quarter doubles every ~3.6 quarters

A debt that "is no big deal today" can become 4× in two years. This is where deferral instincts go wrong.

### Step 5: Diagnose Hyperbolic Discounting

Humans don't discount exponentially — we discount **hyperbolically**, meaning we drastically over-weight the near term and treat anything past ~6 months as roughly equally distant. This causes:

- Always picking the "ship now, fix later" option
- Promising "we'll fix it next quarter" with no intent to follow through
- Underestimating the true cost of accumulated workarounds
- Treating Q3 and Q7 as equally far away ("future me's problem")

Check the team for hyperbolic patterns:

```
HYPERBOLIC SMELL TEST:
- How many "we'll fix it next quarter" promises from 4+ quarters ago are still open?
- Does the team's discount rate vary by horizon (high near-term, ~0 long-term)?
- Are deferred items getting cheaper or more expensive over time?
```

If the team systematically defers and the deferred items grow in cost, you have hyperbolic bias. Counteract by computing the rational exponential discount and presenting both numbers.

### Step 6: Compute Payback Period as a Sanity Check

Payback = how long until cumulative savings equal initial cost.

```
Refactor cost: 3 eng-weeks
Savings: 0.5 eng-weeks/quarter
Undiscounted payback: 6 quarters
Discounted payback (r=10%): ~7 quarters
```

Heuristic: if payback > expected team tenure or > expected feature lifetime, the project may not be worth it even if NPV is technically positive.

### Step 7: Stress-Test Assumptions

DCF is sensitive to inputs. Check:

- What if r is 2× higher (more alternatives than I thought)?
- What if savings are half what I claimed?
- What if compounding rate is double?
- What if the feature is sunset before payback?

If the decision flips under reasonable input changes, it's a coin flip — either is defensible.

### Step 8: Make a Recommendation in Plain Language

Translate DCF back to a sentence a PM understands:

Weak: "I think we should refactor."
Strong: "Refactoring now costs 3 eng-weeks and breaks even in ~7 quarters at our 10%/quarter discount rate. Deferring saves 3 weeks today but costs ~12 weeks over 2 years because the debt compounds at ~15%/quarter. Recommend refactor now unless the module is being deprecated within 6 months."

## Output Format

```
TIME-VALUE ANALYSIS

Decision:
- ...

Cash flow streams:
- Option A: ...
- Option B: ...

Discount rate used: r = X%/period (justification: ...)

NPV:
- Option A: ...
- Option B: ...

Compounding diagnosis:
- One-time / linear / compounding (rate)
- Doubling time (Rule of 72): ...

Hyperbolic-bias check:
- ...

Payback period: ...

Sensitivity:
- ...

Recommendation:
- ...
```

## Anti-Patterns to Avoid

- **Implicit infinite discount rate**: treating all future cost as zero ("we'll get to it eventually")
- **Implicit zero discount rate**: pretending Q8 work is as urgent as Q1 work — over-investing in long-horizon polish
- **Confusing compounding and linear costs**: a workaround that creates more workarounds is not a flat tax
- **Headline-number comparison**: comparing "$3k now" vs "$10k later" without discounting or time horizon
- **Ignoring opportunity cost**: "we have spare capacity" is rarely true — there's always a next-best use
- **Promising future fixes you won't keep**: hyperbolic discounting in disguise; the future-you who must fix it is also you
- **Over-precise DCF**: false precision in inputs hides the real uncertainty; use order-of-magnitude

## Relationship to Other Skills

- Use `capital-allocation` for the broader question of where engineering effort goes across many projects
- Use `optionality-as-value` when the decision is about preserving future flexibility, not just discounting cash flows
- Use `bias-audit` to check for other reasoning biases beyond hyperbolic discounting
- Use `constraint-analysis` to identify the actual scarce resource being allocated over time
- Distinct from `portfolio-theory`, which is about correlated risk across bets, not time discounting within one decision
