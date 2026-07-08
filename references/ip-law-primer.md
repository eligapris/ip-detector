# IP Law Primer — Patent / Copyright / Trademark / Trade Secret

This primer governs Phase 2 (IP type triage). It is a decision tree, not a treatise. Use it to classify the concept, then move on.

## Important caveat

This primer is a research aid, not legal advice. The dossier always ends with: "This dossier is a research artifact, not legal advice. Consult a registered patent attorney before any filing decision." Do not omit this disclaimer.

## The four regimes at a glance

| Regime | Protects | Against | Duration | Cost to obtain | Cost to enforce |
|--------|----------|---------|----------|----------------|-----------------|
| Patent (utility) | Inventions — processes, machines, manufactures, compositions | Independent invention + copying | 20 years from filing | $30k–$150k+ | $3M–$5M per case |
| Patent (design) | Ornamental designs | Copying of ornamental features | 15 years from grant (US) | $5k–$15k | $500k–$2M per case |
| Copyright | Original expression (code, text, art, music) | Copying (not independent invention) | Life + 70 years (US) | $0–$1k registration | $500k–$2M per case |
| Trademark | Brand identifiers — words, logos, sounds | Use of confusingly similar marks in commerce | Perpetual while in use + renewed | $1k–$5k per class | $500k–$2M per case |
| Trade secret | Information with independent economic value from secrecy | Misappropriation (not independent invention or reverse engineering) | Perpetual while secret | $5k–$20k/year maintenance | $1M–$5M per case |

## Decision tree

### Step 1: Is the concept an invention, an expression, a brand, or secret information?

- **Invention** (a new way of doing something technical) → consider Patent (Step 2)
- **Expression** (specific code, specific text, specific artwork) → Copyright (Step 6)
- **Brand identifier** (word/logo used to identify source in commerce) → Trademark (Step 7)
- **Secret information** (formula, process, customer list, algorithm kept confidential) → Trade Secret (Step 8)
- **Combination** → classify the primary regime first, then check secondary regimes

### Step 2: Is the invention patentable subject matter?

This is where most software concepts fail in the US post-Alice (2014) and in EU under the technical-effect test.

**US (Alice / Mayo framework)**:
1. Is the claim directed to a patent-ineligible concept (abstract idea, natural phenomenon, law of nature)?
   - Abstract ideas include: mathematical algorithms, business methods, basic economic practices, organizational structures
2. If yes, does the claim contain an "inventive concept" sufficient to transform the abstract idea into a patent-eligible application?
   - Means: does the claim recite specific, non-conventional technical implementation, or just "do X with a computer"?

Examples:
- ✅ Patentable: A method of improving memory allocation in a database using a specific hash-tree indexing technique
- ❌ Not patentable: A method of allocating resources using the abstract idea of "comparing bids" implemented on a generic computer
- ✅ Patentable: A cryptographic protocol that achieves a specific security property (e.g., post-quantum signature scheme)
- ❌ Not patentable: A method of "securely communicating" using conventional cryptography applied to a new business context

**EU (EPO technical-effect test)**:
- The invention must have a "technical character" — it must solve a technical problem using technical means.
- Pure business methods and pure mathematical methods are not patentable.
- Software that solves a technical problem (e.g., reducing memory usage, improving cache hit rate, optimizing a control system) is patentable.

**CN / JP / KR**:
- Generally more permissive for software patents than US/EU, but still require technical character.
- CN in particular has broadened software patent eligibility in recent years.

If the concept fails subject matter eligibility in all major jurisdictions → classify as `DO NOT FILE - patent`, the verdict is forced.

### Step 3: Is the invention novel?

This is what Phase 3 (prior-art search) determines. If Phase 3 surfaces high-relevance prior art, the answer is no.

### Step 4: Is the invention non-obvious?

This is what Phase 6 scoring (Non-obviousness dimension) determines.

### Step 5: Is the invention useful?

Industrial Applicability dimension (Phase 6) determines this. Pure research contributions with no industrial application fail this test.

### Step 6: Copyright analysis

Copyright protects original works of authorship fixed in a tangible medium of expression. For codebases:
- Source code is automatically copyrighted upon fixation (writing it down)
- Registration is recommended but not required (in the US, registration is required to sue for infringement)
- Copyright protects against copying, NOT against independent invention
- Copyright does NOT protect the underlying idea, algorithm, or method — only the specific expression

For a codebase analysis:
- The specific source code: copyrightable (always)
- The algorithm embodied in the code: not copyrightable (only patentable or trade secret)
- The architecture / API design: arguably copyrightable in some jurisdictions (Oracle v. Google, 2021 — but the Supreme Court held Google's use was fair use)
- The variable names, comments, specific implementation choices: copyrightable

**For the IP detector's purposes**: A concept extracted from a codebase is usually an algorithm or mechanism, not the specific source code expression. Therefore copyright is usually a SECONDARY regime, not the primary. The primary regime is usually patent or trade secret.

Copyright becomes primary when:
- The concept is the specific code itself (e.g., a library the user wants to publish and protect against copying)
- The concept is a creative work (text, art, music) and not a technical mechanism
- The user explicitly wants to publish the code as open source with attribution requirements (e.g., GPL enforcement)

### Step 7: Trademark analysis

Trademark protects brand identifiers used in commerce. For a codebase / technical concept, trademark is almost never the primary IP regime. It becomes relevant when:
- The user has a product name, company name, or logo associated with the concept
- The user wants to prevent others from using a confusingly similar name in the same market

For IP detector purposes, mention trademark as a secondary consideration if the concept has an associated brand identifier. Do not score trademark separately — it is not the focus of this skill.

### Step 8: Trade secret analysis

Trade secret protects information that:
1. Derives independent economic value from not being generally known
2. Is subject to reasonable efforts to maintain its secrecy

Trade secret is the OPPOSITE of patent — you protect it by NOT disclosing it. Once you file a patent, the mechanism is public and the trade secret is destroyed.

**Decision**: Patent vs trade secret is often an either/or choice. Factors favoring trade secret:
- The mechanism is difficult to reverse-engineer (e.g., a server-side algorithm users never see)
- The mechanism is likely to be obsolete in <5 years (shorter than patent prosecution timeline)
- Detection of infringement is impossible (you can't tell if someone is using it)
- The user has strong internal secrecy practices (NDAs, access controls)

Factors favoring patent:
- The mechanism is observable in shipped products (so trade secret protection is weak)
- The user wants to license to others (patents are licensable; trade secrets are not, generally)
- The mechanism is likely to remain valuable for >10 years
- Independent invention is likely (patent protects against independent invention; trade secret does not)

**For IP detector purposes**: If trade secret is the recommended regime, the dossier's verdict is `DO NOT FILE - PATENT` and the recommendation is "Maintain as trade secret with the following secrecy measures: ...". The Gold Index still computes (for the patent route) but is reported alongside a trade-secret recommendation.

## Composite IP strategies

A sophisticated IP strategy often combines regimes. For example:
- Patent the core mechanism (public, defensible for 20 years)
- Trade secret the implementation details (training data, hyperparameters, internal optimizations)
- Copyright the source code (against direct copying)
- Trademark the product name (against brand confusion)

The dossier's Phase 2 output should declare:
- **Primary regime**: the one with the highest expected value
- **Secondary regimes**: those that add incremental protection at low cost
- **Incompatible regimes**: those that cannot coexist (e.g., patent + trade secret on the same mechanism — once you patent, the trade secret is gone)

## Common classification errors

1. **Classifying an algorithm as copyrightable.** Algorithms are ideas / methods, not expression. Copyright protects only the specific code, not the algorithm. Use patent or trade secret.

2. **Classifying a UI layout as patentable.** UI layouts are typically design patents or trade dress, not utility patents. Utility patents on UI require a specific technical effect (e.g., reducing user error rates by a measurable amount).

3. **Classifying a brand name as a patent.** Brand names are trademarks. If the user is asking about a name, the answer is trademark search, not patent analysis.

4. **Filing a patent on something that should be a trade secret.** Server-side algorithms with no observable output should usually be trade secrets. Filing a patent discloses the mechanism to competitors for limited protection.

5. **Assuming software is unpatentable.** Post-Alice, software is harder to patent in the US, but technical-effect software (optimization, security, performance) remains patentable. Don't dismiss software patents categorically.

6. **Assuming trade secret is "free."** Trade secret requires ongoing secrecy investment (NDAs, access controls, training). If the user cannot maintain secrecy, trade secret is not a viable regime.

## Output of Phase 2

The dossier's "IP Classification" section must include:
- Primary regime (one of: utility patent / design patent / copyright / trademark / trade secret / none)
- Secondary regimes (list)
- Subject matter eligibility analysis (if patent route): does the concept pass Alice / technical-effect tests?
- Recommended regime with one-sentence justification
- If patent + trade secret are both viable, the recommendation explicitly states which the user should choose and why
