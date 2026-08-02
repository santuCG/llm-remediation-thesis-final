# Thesis Improvement Assessment (Phase 9.5)

**Date:** 2026-08-02 · **Mode:** Read-only assessment. No code implemented in this phase.

This document classifies every remaining improvement idea surfaced across the audit into four categories, and — critically — distinguishes improvements **intentionally deferred to preserve the integrity and comparability of the completed 18-scenario evaluation**. The guiding rule: anything that changes what the LLM sees, produces, or how success is measured would make new evidence non-comparable to the frozen dataset, and is therefore *not* an engineering tweak but a methodology change.

For each item: **motivation · scientific benefit · effort · methodology impact · evidence impact · rerun required · recommendation.**

---

## Category 1 — Engineering improvements suitable before freeze

*(Robustness/provenance/reproducibility improvements that do NOT change the experiment. All of these were already implemented and validated during this session — listed here for completeness of the classification.)*

| Improvement | Effort | Methodology impact | Evidence impact | Rerun | Status |
|---|---|---|---|---|---|
| Pin frontend npm deps (deterministic JS baseline) | Done | None | Additive (new lockfile) | No | ✅ Implemented (`b9d98fb1`) |
| Exclude `**/bin` from Syft (scanner self-contamination) | Done | None | None (fixes future scans) | No | ✅ Implemented (`cbdd1de1`) |
| Preserve `llm-response-full.json`, dependency graph, Grype DB metadata | Done | None | Additive only | No | ✅ Implemented (`30843e65`) |
| Fix `build_success` regression + null metric semantics | Done | None (measurement fidelity) | None (historical evidence untouched) | No | ✅ Implemented (`f856b891`) |
| Replace 9 fabricated `repository_commit` hashes | Done | None | Metadata field only | No | ✅ Implemented (`d0748e0a`) |

**No further Category-1 engineering work is outstanding.** Anything remaining is deliberately *not* Category 1 (see below).

---

## Category 2 — Thesis presentation / documentation improvements (no experiment change)

| Improvement | Motivation | Scientific benefit | Effort | Methodology impact | Evidence impact | Rerun | Recommendation |
|---|---|---|---|---|---|---|---|
| **Publication-quality JS-01 case study** (original vuln → baseline Grype → candidate ranking → LLM prompt/response → manifest diff → resolution → build/test → rescan → final metrics → interpretation) | An examiner grasps the pipeline far faster from one end-to-end narrative than from raw evidence folders | Improves comprehensibility and defensibility; changes nothing measured | Low–Medium | None | Uses existing frozen evidence only | No | **Do after freeze** (user already flagged this) |
| **Evidence-derived 18-scenario outcome table** (target CVE eradicated? install? build? per scenario, strictly from `metrics.json`) | Gives a reader the aggregate picture without the contradictory old draft | Presents the real result honestly | Low | None | Read-only derivation | No | **Recommended** — belongs in the thesis narrative; can be added post-freeze as a docs artifact |
| **Consolidated `THESIS_LIMITATIONS.md`** | Scattered limitations are hard for an examiner to audit | Integrity/transparency | Low | None | None | No | **Being produced now as a freeze artifact** |
| Folder-level READMEs for `results/execution_evidence/` navigation | First-time navigability | Presentation | Low | None | None | No | Optional, post-freeze |

---

## Category 3 — Methodology extensions that would require rerunning experiments

*(These change the independent variable or the success definition. Implementing any of them makes new results **non-comparable** to the frozen 18-scenario dataset — this is the core reason they are deferred, not effort.)*

| Extension | Motivation | Scientific benefit | Effort | Methodology impact | Evidence impact | Rerun | Recommendation |
|---|---|---|---|---|---|---|---|
| **Retry prompt fed with failure logs** | Second attempt could self-correct from diagnostics | Higher retry success | Medium | **High** — changes what the LLM sees on retry | Invalidates comparability for any retried scenario | **Yes (≥ retried scenarios)** | Deferred — Future Work |
| **LLM confidence scoring** | Enables confidence↔correctness calibration study | New analysis axis | Medium | **High** — changes the response schema/what LLM produces | All 18 for comparability | **Yes (all 18)** | Deferred — Future Work |
| **Improved prompt engineering** | Prompt structure may lift success rate | Potentially stronger result | Med–High | **High** — the prompt *is* the methodology | All 18 | **Yes (all 18)** | Deferred — Future Work |
| **Remove the fixed-version hint from the prompt** | Tests whether the LLM can find the fix unaided (harder, more scientifically interesting) | Stronger claim of LLM reasoning | Medium | **High** — changes the task given to the LLM | All 18 | **Yes (all 18)** | Deferred — Future Work |
| **Multiple retries until success** | Measures ceiling of iterative repair | Different research question | Medium | **High** — violates the pre-registered strict one-retry rule (AGENTS.md rule 5) | All 18 | **Yes (all 18)** | Deferred — Future Work |
| **Semantic / functional compatibility analysis** (does the app still *work* after remediation, beyond compilation) | Addresses the build-compilation limitation directly | Would let "success" include functional correctness | High | **High** — redefines the success criterion | All 18 | **Yes (all 18)** | Deferred — Future Work |
| **Grype DB pinning (Cold-Start clause)** | Exact numerical reproducibility of scan counts | Removes DB-timing drift | Medium | Moderate — changes the reproducibility protocol, not the LLM task | Would shift baseline counts | **Yes (all 18 baselines)** | Deferred — Future Work (documented but unimplemented) |

**Why deferred (explicit):** every Category-3 item alters either the LLM's input/output contract or the definition of experimental success. Introducing any of them now would mean the 18 frozen scenarios were evaluated under one methodology while new scenarios use another — destroying the internal comparability that the pre-registration and version-pinning were designed to guarantee. They are deferred **to protect the completed evaluation's integrity**, not because they are hard.

---

## Category 4 — Future research directions beyond MSc scope

| Direction | Motivation | Research question enabled | Rerun | Recommendation |
|---|---|---|---|---|
| Internet-enabled / tool-using LLM reasoning | Live advisory lookup could improve recommendations | Does live retrieval beat a frozen snapshot for remediation quality? | New study | PhD / journal |
| Multi-agent reasoning (proposer + critic) | Adversarial self-review of remediations | Does a critic agent reduce false-success remediations? | New study | PhD |
| Retrieval-Augmented Generation over advisory corpora | Ground recommendations in retrieved advisories | Does RAG reduce hallucinated versions? | New study | Journal / PhD |
| Model comparison (Gemini vs others) | Isolate model-specific effects | How much of the result is model-dependent? | New study | Journal |
| Additional ecosystems (Go, Rust, Maven) | External validity | Does the transitive-remediation finding generalise? | New study | MSc extension / journal |

---

## Bottom line

- **Category 1 is exhausted** — no engineering improvement remains that could be done without changing the experiment.
- **Category 2** is where genuine pre/post-freeze value lives (case study, honest aggregate table, consolidated limitations) — none of it touches the experiment.
- **Categories 3 and 4 are deferred by design.** `docs/FUTURE_WORK.md` and the freeze artifact `THESIS_FUTURE_WORK.md` carry them forward. Deferring them is the correct choice for a *completed, internally comparable* MSc evaluation — implementing them would start a new experiment, not finish this one.
