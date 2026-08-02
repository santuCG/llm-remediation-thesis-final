# Thesis Future Work

Every enhancement deliberately deferred to preserve the integrity and comparability of the completed 18-scenario evaluation. Each would change what the LLM sees, what it produces, or how experimental success is defined — implementing any of them would begin a *new* experiment rather than complete this one. Consolidates and supersedes `docs/FUTURE_WORK.md`. Detailed per-item evaluation: `docs/THESIS_IMPROVEMENTS.md` (Categories 3 and 4).

## Methodology extensions (would require rerunning experiments)

**Correction (added during documentation synchronisation, 2026-08-02):** item 1 below, "Failure-log-informed retry prompt," was originally listed here as undone future work. That was a classification error: the mechanism was implemented on 2026-07-24 (`scripts/remediation/retry_remediation.py`, `scripts/remediation/llm_reasoner.py`), before this document was written, and is directly evidenced in the frozen dataset (`results/execution_evidence/JS-05/llm-request.json`, `JS-08/llm-request.json` — both contain the "Previous Attempt Failure Logs" section). It is documented as current methodology in `docs/03-llm-configuration.md` and `docs/04-experimental-methodology.md`. It has been removed from the numbered list below; the remaining items are renumbered accordingly.

| # | Direction | Research question enabled | Rerun scope | Best venue |
|---|---|---|---|---|
| 1 | **LLM confidence scoring** | Is an LLM's self-reported confidence predictive of remediation correctness (calibration)? | All 18 | MSc extension / journal |
| 2 | **Prompt-engineering ablation** | Does prompt structure materially affect remediation success independent of model? | All 18 | Journal |
| 3 | **Remove the fixed-version hint** | Can the LLM identify the correct fixed version unaided (a harder, stronger test of reasoning)? | All 18 | MSc extension / journal |
| 4 | **Multiple retries until success** | What is the ceiling of iterative LLM repair? (violates the current pre-registered one-retry rule) | All 18 | Journal |
| 5 | **Semantic / functional compatibility analysis** | Does the application still *function* (not merely compile) after remediation? | All 18 | Journal / PhD |
| 6 | **Grype DB pinning (Cold-Start clause)** | Enables bit-for-bit reproducible scan counts | All 18 baselines | Engineering pre-req for any of the above |

## Future research directions (beyond MSc scope)

| # | Direction | Research question enabled | Best venue |
|---|---|---|---|
| 7 | **Internet-enabled / tool-using LLM** | Does live advisory retrieval beat a frozen snapshot for remediation quality? | PhD / journal |
| 8 | **Multi-agent reasoning (proposer + critic)** | Does an adversarial critic agent reduce false-success remediations? | PhD |
| 9 | **Retrieval-Augmented Generation over advisory corpora** | Does RAG reduce hallucinated version recommendations? | Journal / PhD |
| 10 | **Model comparison** (Gemini vs. others) | How model-dependent is the observed result? | Journal |
| 11 | **Additional ecosystems** (Go, Rust, Maven) | Does the transitive-remediation finding generalise beyond npm/pip? | MSc extension / journal |

## Why these are deferred, not omitted

The completed evaluation's strength rests on **internal comparability**: 18 scenarios run under one pre-registered methodology, version-pinned tooling, and a fixed prompt/model contract. Every item above breaks that contract in some way. Deferring them is the disciplined choice that keeps the frozen dataset a valid, self-consistent whole; each is a well-defined next study with its own clean baseline.
