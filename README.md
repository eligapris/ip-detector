# IP Detector

**Repository:** [github.com/labKnowledge/ip-detector](https://github.com/labKnowledge/ip-detector)

A Cursor / Claude agent skill that performs **numbers-first intellectual property due diligence** on codebases, algorithms, whitepapers, and technical concepts. It is designed to talk you **out** of filing when the evidence does not support it — and to flag the rare cases where filing is genuinely worth the cost.

The deliverable is a **PDF dossier** with a one-line verdict on page 1:

| Verdict | Meaning |
|---------|---------|
| **FILE** | Gold Index ≥ 70; evidence supports filing |
| **BORDERLINE** | Gold Index 50–69; file only if specific conditions are met |
| **DO NOT FILE** | Gold Index &lt; 50 or hard gates failed |

This is a **research artifact**, not legal advice. Consult a registered patent attorney before any filing decision.

---

## What it does

- Mines a codebase or technical write-up for candidate IP concepts
- Classifies the concept (patent, copyright, trademark, trade secret)
- Runs prior-art research across USPTO, Google Patents, WIPO, EPO, Google Scholar, GitHub, and arXiv
- Projects TAM / SAM / SOM with cited CAGR and 5- / 10-year market size
- Models 10-year filing and maintenance cost across US, EU, CN, JP, and KR
- Scores five dimensions and computes a weighted **Gold Index** (0–100)
- Emits a surgical PDF dossier with cited evidence and a blunt verdict

## What it does not do

- Provide legal advice or draft patent claims
- File applications with USPTO, EPO, or any other office
- Promise enforcement or soften a low score to be polite

---

## Installation

### Recommended — Skills CLI (`npx skills`)

The fastest way to install for Cursor, Codex, and other supported agents:

```bash
npx skills add labKnowledge/ip-detector -g -y
```

| Flag | Purpose |
|------|---------|
| `-g` | Install globally (user-level, all projects) |
| `-y` | Skip confirmation prompts |

**Other useful commands:**

```bash
npx skills find ip patent prior art   # search the registry
npx skills check                      # check for updates
npx skills update                     # update installed skills
```

Browse the ecosystem at [skills.sh](https://skills.sh/).

> **Scripts note:** `npx skills add` installs the agent skill (`SKILL.md`) for chat use. For the Python tooling (`scripts/`, `references/`, `assets/`), clone the full repository (below).

### Full install — git clone (includes scripts)

Use this when you want concept extraction and PDF generation on disk:

**Cursor**

```bash
git clone https://github.com/labKnowledge/ip-detector.git ~/.cursor/skills/ip-detector
# or symlink an existing checkout:
ln -s /path/to/ip-detector ~/.cursor/skills/ip-detector
```

**Claude Code**

```bash
git clone https://github.com/labKnowledge/ip-detector.git ~/.claude/skills/ip-detector
```

**Project-local (team / repo-specific)**

```bash
mkdir -p .cursor/skills
cp -r /path/to/ip-detector .cursor/skills/ip-detector
```

The agent discovers the skill from `SKILL.md` in that folder. No extra registration step is required beyond placing the files in a supported skills path.

### Python dependencies

The concept-extraction script uses only the Python standard library. PDF generation requires **ReportLab**:

```bash
pip install reportlab
```

Python **3.9+** is recommended.

### (Optional) Verify scripts

From the skill root:

```bash
python scripts/extract_concepts.py --help
python scripts/generate_dossier.py --help
```

Generate a sample PDF from the bundled example:

```bash
python scripts/generate_dossier.py \
  --data assets/example_analysis.json \
  --output /tmp/ip_dossier_example.pdf
```

---

## How to use it

### With an AI agent (recommended)

1. Install via `npx skills add` (above) or clone the repository into your skills directory.
2. Invoke the skill in natural language. The agent reads `SKILL.md` and runs the full six-phase workflow.

**Example prompts:**

- “Run IP detector on `~/my-project` — is anything here worth patenting?”
- “Analyze this whitepaper for prior art and give me a FILE / DO NOT FILE verdict.”
- “Should I file a patent on our consensus algorithm before we open-source it?”
- “IP strategy for this codebase — brutal honesty, numbers only.”

**Trigger phrases** the skill listens for: patents, IP, intellectual property, filing, prior art, novelty, trade secrets, defensibility, trademark, monetization of an idea, whether code or an algorithm is worth protecting.

**Inputs the agent accepts:**

| Input | What happens |
|-------|----------------|
| Codebase path | `extract_concepts.py` triages candidates; agent picks the strongest one |
| Whitepaper / abstract / `.md` / `.txt` | Agent extracts novelty, mechanism, application, and search seeds |
| GitHub URL | README + top source files treated as a codebase |

The agent performs **web research** during the run (patent databases, Scholar, market reports). Network access is required for a full analysis.

### Manual script usage

You can run the helper scripts yourself; the agent normally orchestrates them.

**Phase 1 — Extract candidate concepts from a codebase**

```bash
python scripts/extract_concepts.py /path/to/codebase \
  --output /tmp/concepts.json
```

**Phase 6 — Generate the PDF dossier**

After the agent (or you) build a complete analysis JSON (see `assets/example_analysis.json`):

```bash
python scripts/generate_dossier.py \
  --data /path/to/analysis.json \
  --output /path/to/ip_dossier_my_concept.pdf
```

---

## How it works — six phases

```
┌─────────┐   ┌──────────────┐   ┌─────────────┐   ┌──────────┐   ┌──────┐   ┌─────────┐
│ Intake  │ → │ IP type      │ → │ Prior art   │ → │ Market   │ → │ Cost │ → │ Scoring │
│         │   │ triage       │   │ research    │   │ project  │   │ model│   │ verdict │
└─────────┘   └──────────────┘   └─────────────┘   └──────────┘   └──────┘   └─────────┘
                                                                                    │
                                                                                    ▼
                                                                              PDF dossier
```

| Phase | Purpose | Key reference |
|-------|---------|---------------|
| **1. Intake** | Identify the artifact and strongest candidate concept | `scripts/extract_concepts.py` |
| **2. IP type triage** | Patent vs copyright vs trademark vs trade secret | `references/ip-law-primer.md` |
| **3. Prior art** | ≥8 web searches; prior-art matrix with URLs | `references/prior-art-search-protocol.md` |
| **4. Market** | TAM / SAM / SOM, CAGR, 5- and 10-year projections | `references/market-projection-protocol.md` |
| **5. Cost** | 10-year filing + maintenance by jurisdiction | `references/filing-cost-matrix.md` |
| **6. Scoring** | Gold Index and verdict; PDF generation | `references/scoring-rubric.md`, `scripts/generate_dossier.py` |

### Scoring dimensions

| Dimension | Weight | Measures |
|-----------|--------|----------|
| Novelty | 25% | Inverse of prior-art density |
| Non-obviousness | 20% | Would a skilled person find this obvious? |
| Industrial applicability | 10% | Production usefulness |
| Defensibility | 20% | Design-around and independent-invention risk |
| Market value | 25% | 10-year NPV of capture minus cost |

**Hard gates** (override Gold Index):

- Novelty &lt; 30 → **DO NOT FILE**
- Market value &lt; 25 → **DO NOT FILE**
- 10-year cost &gt; projected 10-year capture → **DO NOT FILE**

### Philosophy (why verdicts feel harsh)

1. Default verdict is **DO NOT FILE** until cited evidence earns each point.
2. **No number, no score** — missing CAGR or prior-art counts mean zero, not guesses.
3. **Every claim has a URL** — unsourced claims are dropped.
4. No encouragement padding (“promising,” “interesting approach,” etc.).
5. Bias toward rejection; a successful run often saves $30k–$250k in filing fees on non-defensible ideas.

---

## Project structure

```
ip-detector/
├── SKILL.md                          # Agent instructions (main entry point)
├── skills-lock.json                  # Skills CLI lockfile (npx skills)
├── .agents/skills/ip-detector/       # Skills CLI install target
│   └── SKILL.md
├── README.md                         # This file
├── scripts/
│   ├── extract_concepts.py           # Codebase triage → JSON
│   └── generate_dossier.py           # Analysis JSON → PDF
├── references/
│   ├── ip-law-primer.md
│   ├── prior-art-search-protocol.md
│   ├── market-projection-protocol.md
│   ├── filing-cost-matrix.md
│   └── scoring-rubric.md
└── assets/
    └── example_analysis.json         # Full schema example for PDF generation
```

---

## Output

A typical run produces:

1. **`ip_dossier_<concept_slug>.pdf`** — Cover verdict, executive summary, prior-art matrix, market and cost tables, scoring breakdown, and verdict-specific section (“Why this is a rock, not gold,” “Conditions that would change this to FILE,” or “Filing roadmap”).
2. **`ip_dossier_<concept_slug>.json`** — Raw analysis for re-runs or edits.

Save location is chosen by the agent or you when calling `generate_dossier.py` (`--output`).

---

## Disclaimer

This skill produces a **research document** for due diligence. It is **not** a substitute for advice from a registered patent attorney or IP counsel. Laws, fees, and eligibility rules change by jurisdiction and over time; verify all figures and strategy with qualified professionals before filing.
