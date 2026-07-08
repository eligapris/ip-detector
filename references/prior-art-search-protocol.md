# Prior-Art Search Protocol

The prior-art search is the single most important phase of the analysis. A weak search produces a falsely high Novelty score, which produces a falsely high Gold Index, which produces a false `FILE` verdict, which costs the user real money. Bias the search toward finding prior art, not toward confirming novelty.

## Mindset

You are not the user's advocate. You are a hostile examiner. Your job is to find the prior art that kills the claim. If you find none, the novelty is real. If you find some, you must report it honestly.

The user will tell you "I searched and found nothing." The user is wrong. The user does not know how to construct a prior-art search. You do.

## Query construction

### Step 1: Extract the keyword set

From the concept's four extractions (Phase 1), pull out:

1. **Mechanism keywords** — the specific technical terms for what the concept does (e.g., "vector clock quorum", "differential privacy mechanism", "transformer attention routing")
2. **Problem keywords** — the problem it solves (e.g., "consensus finality latency", "training data leakage", "context window scaling")
3. **Domain keywords** — the application domain (e.g., "permissioned blockchain", "federated learning", "large language model")
4. **Result keywords** — the measurable outcome (e.g., "sub-second finality", "epsilon-bounded leakage", "infinite context")

For each category, generate 3–5 synonyms and variants. This gives you a 20–40 term keyword pool.

### Step 2: Identify the CPC class

If the concept is patent-eligible software, identify the most likely Cooperative Patent Classification (CPC) class. Common software CPCs:

- G06F 18 (AI / machine learning)
- G06F 21 (security)
- G06F 16 (data management)
- G06N 3 (neural networks)
- G06Q 20 (payment / blockchain)
- G06Q 30 (commerce)
- H04L 9 (cryptography)
- H04L 67 (network protocols)
- G16H (healthcare IT)
- G16B (bioinformatics)

CPC class restricts the patent search and improves precision. Always cite the CPC class in the dossier.

### Step 3: Construct search queries per source

Different sources have different query syntaxes. Construct accordingly.

#### USPTO (PatFT for granted, AppFT for applications)
- URL: https://patft.uspto.gov/
- Query syntax: Boolean with field tags. Example: `((vector AND clock) WITHIN 5 (quorum OR consensus)) AND spec/permissioned`
- Run at least 3 queries: one tight (mechanism keywords), one medium (mechanism + problem), one broad (problem + domain).

#### Google Patents (https://patents.google.com/)
- Supports natural-language queries.
- Filter by CPC class, date range, jurisdiction.
- Sort by relevance and by date (citations descending) — different hits surface.
- Run at least 3 queries.

#### WIPO Patentscope (https://patentscope.wipo.int/)
- PCT applications and many national phase entries.
- Supports structured field queries.
- Run at least 2 queries.

#### EPO Espacenet (https://worldwide.espacenet.com/)
- Global coverage, including non-English patents.
- Run at least 2 queries, including one in the language of the original concept if non-English.

#### Google Scholar (https://scholar.google.com/)
- Academic papers, theses, conference proceedings.
- Run at least 2 queries.
- Sort by date and by relevance — different hits.

#### GitHub search (https://github.com/search)
- Repositories implementing the mechanism.
- Use code search with mechanism keywords.
- Run at least 2 queries.
- Ignore toy/demo repositories (stars < 10) unless the README explains the mechanism in depth.

#### arXiv (https://arxiv.org/)
- Preprints for ML/AI/crypto/distributed-systems concepts.
- Run at least 2 queries if the concept is in these domains.

#### Industry reports and competitor whitepapers
- Web-search for `<competitor> whitepaper <concept>` and `<domain> technical report <mechanism>`.
- Include in the dossier even if not formally "prior art" — they establish industry awareness.

### Step 4: Run the searches

Total minimum: 8 distinct searches across the above sources. More is better. If the concept is cross-domain (e.g., biotech + ML), run searches in both domains.

For each search, record:
- Source
- Query string (exact)
- Number of results
- Top 3 hits with: title, date, URL, one-sentence relevance note
- Relevance score 0–100 for each top hit

### Step 5: Relevance scoring

Score each top hit on this rubric:

| Score | Criterion |
|-------|-----------|
| 90–100 | Teaches the exact same mechanism for the exact same problem; would likely invalidate the claim |
| 70–89 | Teaches the same mechanism for a similar problem, or a very similar mechanism for the same problem |
| 50–69 | Teaches a related mechanism; relevant but not invalidating |
| 30–49 | Tangentially related; mentions the domain or problem but not the mechanism |
| 0–29 | Not relevant |

A hit at ≥70 is a "high-relevance hit" and counts toward the prior-art density for the Novelty score. A hit at 50–69 is "moderate" and should be noted in the dossier but does not count toward the density. A hit at <50 is noise.

### Step 6: Hostile re-query

After your initial 8+ searches, run **one deliberately hostile query** to test whether you missed anything. Examples:
- `"<concept> alternative"` — surfaces prior art positioned as alternatives
- `"<concept> limitations"` — surfaces prior art that critiques the concept
- `"<problem> solved by"` — surfaces prior art that solves the same problem differently
- `"improvement on <concept>"` — surfaces prior art that builds on the concept (implying the concept is known)

If the hostile query surfaces new high-relevance hits, you missed them in your initial search. Re-run with broader queries.

## Source-prioritization rules

Different sources have different reliability for different concept types:

- **Software algorithms**: Google Patents > arXiv > GitHub > USPTO > Scholar
- **Hardware / mechanical**: USPTO > Espacenet > Google Patents > Scholar
- **Business methods**: USPTO (post-Alice) > Google Patents > Scholar
- **AI / ML**: arXiv > Google Patents > GitHub > Scholar
- **Biotech**: USPTO > Espacenet > PubMed > Google Patents
- **Cryptography**: IACR ePrint > Google Patents > arXiv > Scholar
- **Distributed systems**: Google Scholar > arXiv > Google Patents

When in doubt, run all sources. The 8-search minimum is a floor, not a target.

## What to record in the dossier

The dossier's prior-art section must include:

1. The CPC class identified
2. The full keyword pool (all terms generated in Step 1)
3. A table of every search run: source, query, hit count
4. The top 5 hits across all searches, sorted by relevance, with full citation (title, author/assignee, date, URL, one-sentence relevance note, relevance score)
5. The total count of high-relevance hits (≥70)
6. The total count of moderate-relevance hits (50–69)
7. A one-paragraph summary: "Prior art density is [high/moderate/low]. The closest prior art is [X] by [Y], which teaches [Z]. This [does/does not] anticipate the claimed concept because [reason]."

If you cannot write sentence 7 because you have not read the top hit carefully enough, read it again. Do not summarize from the abstract alone — read the claims (for patents) or the methodology section (for papers).

## Common failure modes — avoid these

1. **Searching only in English.** Many software patents are filed in China, Japan, Korea, Germany. Use Espacenet and Patentscope for non-English coverage. Google Patents auto-translates.

2. **Trusting the abstract.** Patent abstracts are notorious for being vague. Read at least claim 1 and the specification's summary. A patent with a generic abstract may still teach the exact mechanism in the claims.

3. **Ignoring non-patent literature.** A single arXiv paper from 2018 teaching the same mechanism will invalidate a 2024 patent application. Academic prior art counts.

4. **Conflating "different vocabulary" with "different mechanism."** The same consensus algorithm may be described as "vector-clock quorum" in one paper and "logical-clock consensus" in another. Search by mechanism, not by name.

5. **Stopping at the first source.** "I searched Google Patents and found nothing" is not a prior-art search. Run all 8+ sources.

6. **Discounting old prior art.** A 1995 patent teaching the same mechanism is just as invalidating as a 2023 patent. Age does not weaken prior art.

7. **Inflating the relevance score.** If a hit teaches the same mechanism for the same problem, it is a 90+, not a 70. Be honest about the score.

8. **Deflating the relevance score to protect the user's feelings.** If you find a 90-relevance hit, score it 90. The user's feelings are not a relevance factor.
