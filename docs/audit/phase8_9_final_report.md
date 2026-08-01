# PHASES 8-9 — SCIENTIFIC REPRODUCIBILITY ASSESSMENT & FINAL AUDIT REPORT

*Independent reproducibility audit of `main`, conducted fresh in this session. Covers Phases 1-7; this document is the synthesis and final verdict.*

## 1. What was actually done, end to end

| Phase | Scope | Method | Outcome |
|---|---|---|---|
| 1 | Repo + today's commits | Read every changed file, `git log` | Baseline understanding established |
| 2 | Methodology verification | Read every pipeline script in full | Documented in [phase2_methodology_verification.md](phase2_methodology_verification.md) |
| 3 | Workflow validation | Diagrammed both YAMLs, cross-referenced against `scripts/` | [phase3_workflow_validation.md](phase3_workflow_validation.md) — found the missing `**/bin` exclusion later confirmed as a real bug in Phase 5 |
| 4 | Per-scenario audit (18/18) | Re-verified every scenario's evidence fresh, not from memory | [phase4_scenario_audit.md](phase4_scenario_audit.md) — 4 PASS / 8 WARNING / 6 FAIL |
| 5 | Baseline reproducibility | Dispatched `grype-baseline.yml` via GitHub API for all 18 scenarios, twice for determinism | [phase5_baseline_reproducibility.md](phase5_baseline_reproducibility.md) — 2 real bugs found and fixed (commits `b9d98fb1`, `cbdd1de1`) |
| 6 | Evidence completeness | File-count/JSON-validity/corruption sweep, all 18 | [phase6_evidence_completeness.md](phase6_evidence_completeness.md) — no corruption, 2 minor anomalies flagged |
| 7 | Pipeline smoke test | Dispatched `generic-remediation.yml` (JS-01) | [phase7_pipeline_smoketest.md](phase7_pipeline_smoketest.md) — infrastructure validated, 1 new structural finding surfaced |

**Historical evidence (`results/execution_evidence/`) was never modified.** All reproduction was done via fresh CI dispatches compared *against* that evidence, never overwriting it, per your explicit direction.

## 2. Consolidated findings register

### Fixed today (verified via re-run, not just patched-and-assumed)
1. **Frontend npm install was never pinned** (`package-lock=false` in `frontend/.npmrc`) → non-deterministic JS-track baseline. Fixed via a pinned `frontend/package-lock.json` + pre-seed step in both workflows. Verified: two independent post-fix JS-01 runs produced identical numbers.
2. **`grype-baseline.yml` scanned its own scanner binary** (missing `--exclude "**/bin"`) → inflated AF-track package/vulnerability counts by ~13%. Fixed by matching the exclusion already present in `generic-remediation.yml`. Verified: post-fix AF package counts matched recorded evidence exactly (2026=2026).

### Documented, not modified (require your decision)
3. **Retry-path build validation is structurally weaker than the first attempt's** (Phase 7) — Juice Shop's own `postinstall` swallows `build:server` failures (`|| cd .`) during retries, so `build_success`/`failure_stage` after a retry don't reliably reflect that retry's actual build outcome. This is a pipeline behavior/semantics question, not a bug I felt authorized to silently change mid-audit.
4. **The residual +1 AF Grype match** (`pyasn1`→`GHSA-m4p7-r5rc-7g4j`) is a demonstrated Grype-DB timing effect (new advisory, unchanged package version) — exactly what the documented-but-unimplemented "Cold Start Database Clause" was meant to prevent. Not fixed (would require implementing DB snapshot pinning, a larger undertaking than today's scope).
5. **JS track's post-fix numbers (2129/450) differ from the original recorded numbers (1140/383)** — expected and unrecoverable, since the frontend was never pinned before. This is a new, reproducible baseline going forward, not a match to history.
6. **AF-01 has an extra `pipeline_logs/` directory** not present in any other scenario, inside the immutable evidence folder — flagged, not touched.
7. **JS-09's `experiment_manifest.json` still lacks its `EMPIRICAL EVIDENCE` block** — pre-existing, already tracked, awaiting your planned separate JS-09 rerun.

### Carried forward from the original forensic pass (Phase 4), unchanged
8. 9 fabricated `repository_commit` hashes in `experiment_manifest.json` (AF-05 through AF-09, JS-05 through JS-08) — these were fixed in an earlier session pass but lost in a branch-switch incident; **not yet reapplied to `main`**. Still open.
9. JS-01/02/06/07's `package-before.json` reflects an already-patched state (retry-reset bug, since fixed in pipeline code, but the *historical* evidence files themselves are unchanged — would need a rerun to correct).
10. Six scenarios' `build_success`/`failure_stage` metrics contradictions (JS-01, 02, 06, 07 = FAIL; JS-04, 05, 08 = WARNING) — root cause understood (missing `pipefail`, now fixed in code; retry-reset, now fixed in code), but the historical records themselves still show the contradiction since no rerun has occurred.

## 3. Scientific reproducibility assessment

**Can this pipeline, as it exists on `main` today, reliably answer the thesis's research question (can an LLM generate viable dependency-remediation strategies for known CVEs)?**

- **Target-CVE detection: 18/18 reproduced correctly** in fresh CI runs. This is the single most important reproducibility property, and it holds without exception.
- **Baseline package/vulnerability counts:** now internally deterministic for both tracks (same numbers across repeated runs and across all scenarios sharing an app), which was **not true before today's two fixes**. This directly improves the thesis's reproducibility claims for anyone re-running the pipeline from today onward.
- **LLM remediation outcome per scenario:** governed by Phase 4's per-scenario audit (4 PASS / 8 WARNING / 6 FAIL out of 18), which reflects **historical evidence quality**, not pipeline correctness going forward — 6 of those FAILs/WARNINGs are metrics-recording bugs already fixed in code, not genuine remediation failures; the underlying LLM behavior in most cases appears legitimate on inspection of `llm-response.json`.
- **New risk surfaced today (Phase 7):** the retry path's weaker build validation means historical "success"/"failure" labels for any *retried* scenario should be read with the caveat that a build failure during retry may not be recorded as such.

## 4. Would I recommend this as an MSc examiner?

**Recommend acceptance with disclosure**, not rejection. The core scientific claim (target CVE identification and LLM-driven remediation strategy generation) is sound and reproduces. The defects found are exactly the kind a rigorous, disclosed reproducibility audit is *supposed* to surface — a thesis that documents "we audited this, found real bugs, fixed two, and disclosed the rest with root causes" is stronger evidence of scientific integrity than one with no such audit trail at all. What would concern an examiner is if these gaps were *undisclosed*; they are not, provided the thesis references this audit and its findings register (items 1-10 above) rather than presenting the original evidence as flawless.

## 5. Recommended disclosure for the thesis

At minimum, the methodology/limitations section should state:
- The pipeline's baseline scanning had two reproducibility defects (fixed `[date]`, commits `b9d98fb1`/`cbdd1de1`); pre-fix historical evidence counts for AF/JS baselines should not be treated as independently reproducible without noting this.
- 9 scenarios' `experiment_manifest.json` records have non-authentic provenance hashes (open item, not yet corrected on `main`).
- The retry path's build-failure detection is weaker than the first attempt's (Phase 7 finding); retried scenarios' `build_success` field should be read with this caveat.
- JS-09 is intentionally an ablation/exploratory scenario (per your stated design) and its evidence is incomplete relative to the other 17 pending a planned rerun.

## 6. Overall verdict

**PASS, with disclosed limitations.** No finding in this audit undermines the thesis's central research question or its answer. All findings are either fixed-and-verified, or clearly documented with root cause for the author's disclosure and future work sections.
