---
name: bubble-dynamics
description: Behavioral finance applied to tech adoption — recognize hype cycles, herding, FOMO, and Minsky moments before deciding to chase the next framework, paradigm, or migration.
user-invocable: true
---

# Bubble Dynamics

Act as a behavioral economist watching the tech ecosystem. Technology adoption rarely follows the rational, evidence-driven path the original engineers imagine. It follows the same patterns financial markets do: hype peaks, herding, "this time is different," greater-fool dynamics, asymmetric information, and eventual disillusionment. Some bubbles deliver the promised value years later (the internet); others leave nothing but sunk capital and rewritten codebases (the second microservices migration most teams didn't need).

Success looks like: making adoption decisions based on where in the cycle a technology actually is, with a clear estimate of what *future-you* will think of this choice in 3 years. Failure looks like rewriting in $HYPE_FRAMEWORK at peak hype, then maintaining the rewrite during the trough while the team that didn't migrate ships features.

## When to Use This

- "We should rewrite in [new framework]"
- Microservices / monolith / serverless / event-sourcing migration decisions
- AI / LLM / agent adoption choices in a hype-saturated environment
- Evaluating "industry standard" or "everyone is doing it" arguments
- When a technology is being heavily marketed and adoption is accelerating
- Considering whether to wait, adopt early, or skip a wave
- Postmortems on past technology choices that didn't pan out

**Escape hatch**: For mature technologies with stable adoption and well-understood trade-offs (Postgres, nginx, Linux), this lens adds little. Apply it when the technology is contested, novel, or socially loaded.

## Core Mindset

Ask:

- Where in the **hype cycle** is this technology right now?
- What part of the argument is **evidence** and what part is **social proof**?
- Who **benefits** from the hype (vendors, conference speakers, consultants)?
- What is the **information asymmetry** — what do early adopters know that we don't, or vice versa?
- Are we hearing from **survivors** of past adoptions, or also from the casualties?
- What would **future-me** in 3 years think about this decision?
- What is the **opportunity cost** of chasing this vs the boring path?

## Vocabulary

| Term | Finance meaning | Engineering analog |
| --- | --- | --- |
| **Bubble** | Asset price disconnected from fundamentals | Tech adoption disconnected from actual problem fit |
| **Rational bubble** | Price rises because others will pay more (greater-fool) | "Adopt early to get ahead of the curve" |
| **Irrational bubble** | Price rises on belief alone, no fundamentals | "We must rewrite in X because X is the future" |
| **Herding** | Following others' actions over own analysis | "Everyone's switching to Y, we should too" |
| **FOMO** | Fear of missing out | The driver behind most premature adoption |
| **Minsky moment** | Sudden collapse after long stability | Vendor disappears, paradigm dies, project abandoned |
| **Greater-fool theory** | Profit by selling to a more enthusiastic buyer | "We'll be ahead when everyone else adopts" |
| **Asymmetric information** | One side knows more than the other | Vendor knows the limitations; you don't yet |
| **Survivorship bias** | Seeing only the winners' stories | Only successful migrations get blog posts |
| **"This time is different"** | The 4 most expensive words in finance | "Past framework wars don't apply to X" |
| **Chasm** (Moore) | Gap between early adopters and pragmatist majority | Many techs die in the chasm; few cross |

## The Gartner Hype Cycle

Most technologies move through five phases. Knowing which one applies is half the analysis.

| Phase | Signals | Adopter recommendation |
| --- | --- | --- |
| **Innovation Trigger** | Few users, paper or demo, no real production scars | Watch; experiment cheaply; don't bet the company |
| **Peak of Inflated Expectations** | Conference keynotes, vendor blitz, "everyone's doing it," success stories everywhere | **Most dangerous phase to adopt**; skepticism is socially costly but financially correct |
| **Trough of Disillusionment** | Backlash posts ("$TECH considered harmful"), early-adopter regret blogs, vendor consolidation | **Often the right time to evaluate seriously** — the survivors are visible and the limits are documented |
| **Slope of Enlightenment** | Realistic best-practices, tooling matures, hiring pool grows | Safe adoption; risk-adjusted return is good |
| **Plateau of Productivity** | Boring; "obvious" choice; stable | Default choice unless you have a specific reason to deviate |

Critically: **adopting at the trough often beats adopting at the peak** — the technology is the same, but you have realistic information and community-tested patterns.

## The Process

### Step 1: Identify What's Actually Being Proposed

Strip the proposal down to its concrete change.

```
PROPOSAL:
- What technology / paradigm: ...
- What current technology / paradigm it replaces: ...
- What concrete problem it solves: ...
- What new problems it introduces: ...
- Migration cost (eng-weeks): ...
- Switching cost back (if it doesn't work): ...
```

If the proposal can't pass this without reaching for hype words ("modern," "cloud-native," "future-proof," "scalable"), it's not yet a real proposal — it's a vibe.

### Step 2: Locate on the Hype Cycle

Use external evidence, not internal enthusiasm.

```
HYPE CYCLE INDICATORS:
- Conference talk count this year vs last:
- Backlash post count ("X considered harmful"):
- Number of high-profile case studies:
- Number of high-profile *migrations away from it*:
- Job postings asking for it:
- Mature, stable ecosystem libraries vs alpha-quality libraries:
- Vendor consolidation (good sign; means winners are emerging):
```

Be honest. If your evidence is "I read 5 hyped blog posts," you're at the peak.

### Step 3: Diagnose Your Own Decision Drivers

Hardest step — examine motives.

```
WHY DO WE WANT THIS?
- [ ] We have a specific, named problem the current tech can't solve
- [ ] The benchmarks/POC show meaningful win on our actual workload
- [ ] Strong recruiting / retention pressure (engineers want to use it)
- [ ] FOMO (everyone is doing it; we'll look behind)
- [ ] Resume-driven development
- [ ] Boredom with current stack
- [ ] Vendor / consultant push
- [ ] Leadership wants a "modernization" narrative
```

Multiple legitimate reasons can coexist. The diagnostic is whether reasons in the **first two** are sufficient on their own. If everything below the first two were absent, would you still adopt? If no, FOMO is doing the work.

### Step 4: Stress-Test "This Time Is Different"

Almost every bubble argument includes a "this time is different" claim. Test it.

```
"THIS TIME IS DIFFERENT" CHECK:
- What past wave does this most resemble? (NoSQL, microservices, blockchain, etc.)
- What's claimed to be different now?
- Is that difference supported by evidence or by enthusiasm?
- What was the failure mode of the prior wave, and is it actually addressed?
```

Common patterns: "this time we have better tooling," "this time the hardware can handle it," "this time we won't make the same architectural mistakes." Sometimes these are true. Often they are not.

### Step 5: Correct for Survivorship Bias

You're seeing the success stories. The teams that quietly suffered or quietly migrated back rarely write blog posts.

```
SURVIVORSHIP CHECK:
- Find 2-3 teams that adopted this 2+ years ago and ask how it went
- Search for "migrating away from X" and "X considered harmful" — sample the casualties
- For every "we love X" story, ask: how big is the team, what's their domain, do they look like us?
- What's the survival rate of teams that adopted in the same phase you're in now?
```

The denominator matters. "10 famous companies use X" tells you nothing without "and 1000 tried and gave up."

### Step 6: Estimate Information Asymmetry

The vendor / framework author knows things you don't:
- The roadmap (and what's quietly being deprioritized)
- The financial runway (will the company still exist in 3 years?)
- Known unfixable architectural limitations
- Which "best practices" are workarounds for unfixed bugs

You may know things they don't:
- Your actual workload, data shape, team skills
- Your reliability and compliance constraints
- Your real migration cost

Adopt when **your private information favorably resolves their hidden risks** — e.g., your workload is small enough that the scaling limitations they're hiding don't matter to you.

### Step 7: Apply the 3-Year Test

Imagine yourself 3 years from now, looking back at this decision.

```
3-YEAR TEST:
- If this was a great choice, what will future-me say?
- If this was a bad choice, what will future-me say?
- What's the probability of each, honestly?
- What is the cost of being wrong (migration back, abandoned codebase, eng turnover)?
- Is the upside worth the downside, given the probabilities?
```

Many adoption decisions look great on day 1 and terrible on year 2. The 3-year frame is far enough out to see past launch glow but close enough to be relevant.

### Step 8: Choose Adoption Posture

Not all adoption is binary. Stage it:

| Posture | When | Risk |
| --- | --- | --- |
| **Skip** | Hype cycle peak with no clear fit | Miss out if it actually delivers |
| **Watch** | Innovation trigger; let others find the limits | Lag adoption by ~12-24 months |
| **Pilot** | One non-critical workload; reversible | Pilot becomes accidental production |
| **Adopt for new work** | Trough/slope; mature enough; clear fit | Maintain two stacks during transition |
| **Migrate existing** | Plateau; established; clear win | Highest cost; only if benefits are large and durable |

A staged posture (skip → watch → pilot → adopt) lets you ride the cycle without being a peak buyer.

## Output Format

```
BUBBLE DYNAMICS REVIEW

Proposal:
- Tech under consideration: ...
- Concrete problem solved: ...
- Migration cost: ...

Hype cycle phase: ...
- Evidence: ...

Decision drivers (honest):
- Specific problem fit: ...
- FOMO / herding signal: ...
- Resume / hiring pressure: ...
- Vendor pressure: ...

"This time is different" claims:
- Claim: ...
- Past analog: ...
- Verdict: holds / weak / no

Survivorship correction:
- Casualty data found: ...

3-year test:
- Best case: ...
- Worst case: ...
- Probability of each: ...

Recommended posture:
- Skip / Watch / Pilot / Adopt-new / Migrate-existing
- Re-evaluation trigger: ...
```

## Anti-Patterns to Avoid

- **Adopting at the peak**: hype-driven adoption when realistic data is unavailable
- **Permanent skepticism**: refusing to adopt anything new; eventually obsolete
- **"Everyone is doing it"**: weak signal; wait until you can name *who* and *why* and verify they look like you
- **Conference-driven architecture**: technology choices made because the talks were exciting
- **Ignoring casualty stories**: only reading success cases and treating them as the base rate
- **Greater-fool reasoning**: "we'll adopt now and be ahead when everyone else does" — works only if everyone else actually does
- **"This time is different" without evidence**: claim every wave makes; almost always wrong
- **Sunk-cost migration**: continuing a hype-driven migration that's clearly failing because you've already invested
- **Mistaking trough backlash for failure**: tech in the trough is often the best time to evaluate seriously

## Relationship to Other Skills

- Use `bias-audit` to find the FOMO, anchoring, and confirmation bias driving the proposal
- Use `time-value-of-money` to actually price the migration cost vs delayed value
- Use `optionality-as-value` to evaluate whether deferring (preserving the option to adopt later) is cheaper than committing now
- Use `capital-allocation` to compare the migration against the other things the team would otherwise do
- Use `incentive-analysis` to identify who benefits from the hype (vendors, consultants, internal champions) — distinct from this skill, which is about cycle dynamics
- Distinct from `adoption-strategy` (encouraging others to adopt) — this skill is about whether *we* should adopt
