# Market Projection Protocol

This protocol governs Phase 4 (market projection). The goal is to produce a defensible 10-year capture estimate grounded in cited market research, not in the user's optimism.

## Why this matters

Most "IP value" calculations fail because the market projection is fantasy. A user says "this is a $50 billion market" and the analyst nods. The $50 billion figure is usually the TAM for a vaguely related category, not the addressable market for the specific mechanism being patented. This protocol forces specificity.

## The four numbers

Every dossier must produce these four numbers, each with a cited source:

1. **TAM (Total Addressable Market)** — the entire worldwide market for the broad category the concept serves. Cited from a market-research firm.
2. **SAM (Serviceable Addressable Market)** — the segment of the TAM that the concept can technically serve. Derived from TAM × segment share, with the segment share cited.
3. **SOM (Serviceable Obtainable Market)** — the realistic revenue an IP holder could capture. Default: SAM × 1% (conservative for a single-patent holder with no commercialization infrastructure).
4. **CAGR (Compound Annual Growth Rate)** — the projected annual growth of the relevant market segment, cited from a market-research firm.

From these four, project:
- Year-5 market size = current × (1+CAGR)^5
- Year-10 market size = current × (1+CAGR)^10 × disruption_discount

The disruption_discount accounts for AI/tooling commoditization. Defaults:
- Pure software algorithm with no hardware dependency: 0.6 (high disruption risk)
- Software + hardware integration: 0.75
- Hardware-only: 0.85
- Regulatory-protected (FDA-approved, certified): 0.9

## Acceptable market-research sources

Tier 1 (highest credibility):
- Gartner
- IDC
- Forrester
- McKinsey (industry reports, not thought-leadership pieces)
- Bain & Company
- BCG
- Deloitte Insights

Tier 2 (acceptable, cite the methodology):
- MarketsAndMarkets
- Grand View Research
- Mordor Intelligence
- Statista (if underlying source is cited)
- ResearchAndMarkets
- Prescient & Strategic Intelligence
- Allied Market Research

Tier 3 (use only if no Tier 1/2 source exists, flag as lower confidence):
- Industry trade association reports (e.g., CompTIA, GSMA)
- Major consulting firm blog posts (with cited numbers)
- Reputable tech journalism with cited numbers (TechCrunch, Wired, etc. — only if they cite a Tier 1/2 source)

Unacceptable (do not cite, do not use the numbers):
- Random blog posts without citations
- Reddit / HackerNews / Twitter commentary
- Vendor marketing pages (e.g., AWS's blog claiming the AWS-served market is X)
- Press releases with no underlying methodology
- AI-generated content farms

## Search methodology

### Step 1: Identify the relevant market segment

The concept is not "the AI market" or "the cloud market." It is a specific segment. Examples:

- Concept: novel transformer attention routing → Segment: "large language model inference infrastructure" (not "AI market")
- Concept: differential privacy mechanism for federated learning → Segment: "federated learning platforms" (not "privacy software")
- Concept: sub-second consensus for permissioned blockchains → Segment: "permissioned blockchain platforms" (not "blockchain market")

The narrower the segment, the more defensible the number. If you cannot find a report for the narrow segment, use the parent segment and explicitly flag the imprecision in the dossier.

### Step 2: Run the searches

Use the web-search skill. Run at least 4 searches:
- `<segment> market size 2024`
- `<segment> market size CAGR forecast`
- `<segment> market report Gartner OR IDC OR MarketsAndMarkets`
- `<parent segment> market size 2030 forecast`

For each Tier 1/2 hit, record:
- Source (firm name + report title)
- Year of estimate
- TAM value cited
- CAGR cited
- Forecast horizon (e.g., "to 2030")
- URL

### Step 3: Triangulate

If you find 2+ Tier 1/2 sources, take the median of their TAM and CAGR estimates. Use the median, not the average — outliers in market research are common (a vendor-funded report will inflate the number).

If you find only one Tier 1/2 source, use that single source and flag the projection as "single-source" in the dossier (lower confidence).

If you find zero Tier 1/2 sources, the Market Value dimension is capped at 20 per the scoring rubric. This is a hard rule.

### Step 4: Compute SOM

Default SOM = SAM × 1%.

Justify deviations from the default:
- If the IP holder is a major incumbent with commercialization infrastructure, SOM can be SAM × 3–5%.
- If the IP holder is a single-patent inventor with no commercialization plan, SOM = SAM × 0.5%.
- If the IP holder plans to license exclusively (no direct commercialization), SOM = SAM × 1–2% (licensing rate × expected licensee share).

The 1% default is conservative because most patent holders capture far less than they project.

### Step 5: Compute the capture rate

The capture rate is the fraction of SOM the IP can realistically defend or license. Defaults:

- Strong patent with high detection (e.g., protocol-level, observable in shipped product): 10%
- Strong patent with moderate detection: 5%
- Strong patent with low detection (server-side, hard to prove): 2%
- Weak patent / borderline novelty: 1%
- Copyright on source code (requires proof of copying): 2%
- Trade secret (requires the secret to actually stay secret): 5%

These defaults are conservative because enforcement is expensive ($3M+ for US patent litigation) and infringers settle at a fraction of the headline damages.

### Step 6: Compute projected capture

```
projected_capture = Year-10 SOM × capture_rate × enforcement_probability
```

Where `enforcement_probability` defaults to 0.5 (half of all detectable infringement is actually pursued, given the cost of litigation).

### Step 7: Compute net value and score

Per the scoring rubric:
```
net_value = projected_capture - 10_year_total_cost
```

Score per the Market Value dimension table.

## Worked example

Concept: A novel zero-knowledge proof scheme reducing proof generation time by 10x for a specific class of circuits.

- Segment: "zero-knowledge proof software market" (no direct Tier 1/2 report found).
- Parent segment: "cryptography software market" — Tier 2 source (MarketsAndMarkets) cites $5.2B in 2024, CAGR 21.3% to 2030.
- Flag: "Single-source projection from parent segment; precision limited."
- TAM (Year 0) = $5.2B
- SAM = TAM × 10% (ZKP is ~10% of cryptography software per a cited industry estimate) = $520M
- SOM = SAM × 1% = $5.2M
- CAGR = 21.3% (cited)
- Year-5 SOM = $5.2M × (1.213)^5 = $13.6M
- Year-10 SOM = $5.2M × (1.213)^10 × 0.6 (disruption_discount for pure software algorithm with high AI-commoditization risk) = $23.6M
- Capture rate = 5% (strong patent, moderate detection — ZKPs are partially observable on-chain)
- Enforcement probability = 0.5
- Projected capture = $23.6M × 0.05 × 0.5 = $590k

This gives a Market Value score of approximately 20 (net_value in the $0–$500k band, factoring in ~$145k filing+maintenance cost → net ≈ $445k).

If you can find a more specific Tier 1/2 report for "zero-knowledge proof software" specifically, the projection would be more defensible. With only the parent segment, the projection is lower-confidence and the score should reflect that.

## Common failure modes

1. **Citing the parent segment as the addressable market.** "AI market is $1.3T by 2030" does not mean the user's specific ML inference optimization is addressing $1.3T. Use the segment, not the parent.

2. **Using vendor-funded reports without disclosure.** Many "market reports" are funded by vendors with a stake in inflating the number. If the report's sponsor is a vendor in the space, discount by 30–50%.

3. **Projecting 10 years without disruption discount.** A 21% CAGR compounded for 10 years is 6.7x. Almost no software market sustains this — disruption is inevitable. Apply the discount.

4. **Confusing SOM with capture.** SOM is the realistic revenue. Capture is what the IP holder actually gets. These are different by a factor of 10–100.

5. **Citing a CAGR from a blog that cites a market report that doesn't exist.** Trace every CAGR to a real, named report. If you cannot trace it, do not use it.

6. **Inflating capture rate based on user optimism.** The user says "we'll license to 20 companies at $1M each." No, you won't. Default rates exist because they reflect reality.

7. **Ignoring the enforcement cost.** A patent that captures $500k in value but costs $3M to enforce against a single infringer is a net loss. The capture rate already discounts for this; do not double-count, but also do not assume capture without enforcement.
