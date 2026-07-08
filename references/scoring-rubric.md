# Scoring Rubric — 5 Dimensions, 0–100 Each

This is the rulebook. Every score must be derivable from the evidence collected in Phases 3–5. If you cannot derive a number from evidence, the score is zero — not "estimated," not "approximate," zero.

## Dimension 1: Novelty (weight 25%)

**Definition**: Has this exact mechanism been publicly disclosed before, anywhere, in any form?

**Scoring formula**:

| Prior-art hits (relevance ≥70) | Score |
|--------------------------------|-------|
| 0 hits | 90–100 |
| 1–2 hits | 60–75 |
| 3–5 hits | 40–55 |
| 6–10 hits | 20–35 |
| 11+ hits | 0–15 |

**Adjustments**:
- If the top hit has relevance ≥85 (near-identical), cap score at 20 regardless of hit count.
- If the top hit is from a patent granted in the last 5 years in the same CPC subclass, cap score at 30.
- If the top hit is from academic literature (peer-reviewed, indexed in Google Scholar) and is more than 10 years old, +10 to the score (old academic disclosure actually weakens the patent's novelty, but for the user's defensive filing posture it suggests the field has moved on).

**Hard rule**: If you searched fewer than 8 distinct sources, the Novelty score is capped at 50. No exceptions. Lazy search = lazy score.

**What counts as a "hit"**: Any public disclosure that teaches the same mechanism. This includes:
- Granted patents and published applications
- Academic papers, conference proceedings, theses
- Open-source code repositories with substantive implementation (not toy demos)
- Published technical whitepapers, RFCs, standards documents
- Public blog posts with technical depth (a Medium article describing the same algorithm counts)
- YouTube videos with technical exposition (rare but possible)

**What does NOT count as a hit**:
- Marketing pages that name the concept without explaining the mechanism
- Job postings mentioning the concept
- Product feature lists with no technical detail
- Your own gut feeling that "this has probably been done"

## Dimension 2: Non-obviousness (weight 20%)

**Definition**: Would a person having ordinary skill in the art (PHOSITA), facing the same problem, arrive at this solution without inventive effort?

This is the hardest dimension to score objectively. Use this proxy:

**Scoring components** (each 0–25, sum to 0–100):

1. **Combination uniqueness** (0–25): How many distinct known techniques are combined, and is the combination itself taught anywhere?
   - 0: Single known technique, applied as taught
   - 10: Two known techniques, combination taught in prior art
   - 18: Two known techniques, combination not taught but predictable
   - 25: Three+ known techniques, combination non-obvious and not taught

2. **Problem-solution distance** (0–25): How far is the solution from the obvious next step?
   - 0: Solution is the textbook answer to the problem
   - 10: Solution is one of 2–3 obvious approaches
   - 18: Solution requires reframing the problem
   - 25: Solution requires an insight that contradicts conventional wisdom in the field

3. **Long-felt-need evidence** (0–25): Is there evidence the industry has been trying and failing to solve this problem?
   - 0: No evidence of industry interest
   - 10: Industry discusses the problem; multiple published approaches exist
   - 18: Industry discusses the problem; existing approaches have well-documented limitations
   - 25: Multiple failed attempts documented in literature; commercial demand evident

4. **Teaching-away evidence** (0–25): Does prior art teach away from this solution?
   - 0: No prior art addresses this solution direction
   - 10: Prior art is neutral
   - 18: Prior art suggests this direction is suboptimal but possible
   - 25: Prior art explicitly teaches against this approach; the inventor went against consensus

**Hard rule**: If Novelty < 40, Non-obviousness is capped at 50. A non-novel mechanism cannot be highly non-obvious.

## Dimension 3: Industrial Applicability (weight 10%)

**Definition**: Can this actually be used in a production system, and is there a real customer for it?

**Scoring**:

| Evidence | Score |
|----------|-------|
| Concept already in production use by the user or a competitor | 80–100 |
| Working prototype with documented performance benchmarks | 60–75 |
| Proof-of-concept implementation, no benchmarks | 35–55 |
| Theoretical description only, no implementation | 15–30 |
| Pure idea, no implementation and no clear path to one | 0–10 |

**Adjustments**:
- If the concept requires regulatory approval (FDA, FAA, etc.) and no approval pathway is identified, cap at 40.
- If the concept requires infrastructure that does not yet exist at scale (e.g., quantum computers, 6G networks), cap at 30.
- If the concept is a pure research contribution with no plausible industrial customer, cap at 20.

## Dimension 4: Defensibility (weight 20%)

**Definition**: If you file, can you actually detect and enforce against infringers?

This dimension is the most underweighted by naive filers and the most important for actual IP value. A patent you cannot enforce is a cost center.

**Scoring components** (each 0–25, sum to 0–100):

1. **Design-around difficulty** (0–25): How easy is it to achieve the same result with a different mechanism?
   - 0: Trivial — there are 3+ documented alternative approaches
   - 10: Moderate — alternatives exist but with significant tradeoffs
   - 18: Hard — alternatives require giving up core benefits
   - 25: Effectively impossible — the mechanism is the only known way

2. **Detection difficulty** (0–25): Can you tell if someone is infringing?
   - 0: Infringement happens entirely server-side / closed-source; no way to detect
   - 10: Infringement partially observable through behavior, but proof is hard
   - 18: Infringement observable through public output or API behavior
   - 25: Infringement directly observable in shipped product (UI, file format, protocol)

3. **Independent invention risk** (0–25): How likely is a competitor to arrive at the same solution independently?
   - 0: Multiple teams likely working on the same problem; high risk of simultaneous invention
   - 10: A few teams working on adjacent problems; moderate risk
   - 18: Niche problem with limited commercial interest; low risk
   - 25: Highly specialized problem; independent invention unlikely

4. **Litigation cost-effectiveness** (0–25): Is the per-infringer damages likely to exceed litigation cost (~$3M for patent litigation in the US)?
   - 0: Per-infringer damages < $100k (not worth suing)
   - 10: $100k–$1M (marginal)
   - 18: $1M–$10M (worth suing)
   - 25: > $10M (clearly worth suing)

## Dimension 5: Market Value (weight 25%)

**Definition**: 10-year net present value of the IP, accounting for projected capture minus 10-year cost.

**Scoring formula**:

1. Compute `projected_capture = Year-10 SOM × capture_rate × 0.5` (the 0.5 discounts for the probability that the IP is actually enforced or licensed).
2. Compute `total_cost = 10-year filing + maintenance + attorney cost` from Phase 5.
3. Compute `net_value = projected_capture - total_cost`.
4. Score:
   - net_value > $50M → 90–100
   - $10M–$50M → 70–85
   - $2M–$10M → 50–65
   - $500k–$2M → 30–45
   - $0–$500k → 15–25
   - net_value < $0 → 0–10

**Hard rule**: If you cannot find a cited CAGR from a named market-research firm (Gartner, IDC, Forrester, MarketsAndMarkets, Grand View Research, Statista, Mordor Intelligence, etc.), the Market Value dimension is capped at 20. A blog post citing "industry trends" is not a market-research firm.

**Hard rule**: If total_cost > projected_capture, Market Value is capped at 15. Negative ROI is negative ROI.

## Gold Index computation

```
Gold Index = 0.25 × Novelty
           + 0.20 × Non-obviousness
           + 0.10 × Industrial_Applicability
           + 0.20 × Defensibility
           + 0.25 × Market_Value
```

Result is 0–100.

## Verdict thresholds (hard, no override except as noted)

| Gold Index | Verdict |
|------------|---------|
| ≥ 70 | FILE |
| 50–69 | BORDERLINE |
| < 50 | DO NOT FILE |

## Override gates

These override the Gold Index downward. There are no overrides upward — a low score cannot be raised by argument.

- **Novelty < 30** → verdict becomes `DO NOT FILE` regardless of Gold Index
- **Market Value < 25** → verdict becomes `DO NOT FILE`
- **total_cost > projected_capture** → verdict becomes `DO NOT FILE`
- **Concept is a non-patentable subject matter** (abstract idea, natural phenomenon, mathematical formula with no technical application per Alice/Mayo) → verdict becomes `DO NOT FILE`

## Worked example

Concept: A novel consensus algorithm for permissioned blockchains that reduces finality time from 3 seconds to 200 milliseconds by replacing the standard two-phase commit with a vector-clock-based quorum mechanism.

- Phase 3 prior art: 12 hits across USPTO/Google Patents/arXiv/GitHub. Top hit relevance 78 (a 2021 IBM patent on vector-clock-based consensus for permissioned chains). Novelty = 35.
- Phase 4 non-obviousness: Combination uniqueness 18 (three known techniques, combination non-obvious), problem-solution distance 18 (requires reframing), long-felt-need 18 (finality time is a known problem), teaching-away 25 (prior art teaches against vector clocks due to overhead). Total = 79. But Novelty < 40, so capped at 50.
- Phase 4 industrial applicability: Working prototype with benchmarks = 70.
- Phase 5 defensibility: Design-around 18, detection 10 (server-side, hard to prove), independent invention risk 10 (multiple teams working on it), litigation cost-effectiveness 18. Total = 56.
- Phase 5 market value: Permissioned blockchain market TAM $4.8B (cited), CAGR 18.4% (cited MarketsAndMarkets), Year-10 SOM $48M, capture 5%, projected_capture = $48M × 0.05 × 0.5 = $1.2M. 10-year cost $145k. net_value ≈ $1.06M. Score = 35.

Gold Index = 0.25×35 + 0.20×50 + 0.10×70 + 0.20×56 + 0.25×35 = 8.75 + 10 + 7 + 11.2 + 8.75 = **45.7**

Verdict: `DO NOT FILE` (Gold Index < 50, and Novelty < 40 hard cap was already applied).

This is a real, defensible verdict. The concept is clever but the prior art is too dense and the defensibility is too weak. Filing would cost $145k+ over 10 years for an IP that is unlikely to be enforceable.
