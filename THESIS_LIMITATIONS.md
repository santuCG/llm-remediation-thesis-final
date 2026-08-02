# Thesis Limitations

A consolidated, thesis-facing list of every limitation that should be acknowledged when interpreting this repository's evidence. Each is honestly disclosed here so an examiner need not reconstruct it from scattered notes or the audit trail.

## 1. Deterministic-baseline efficacy is ecosystem-dependent
The LLM reasoning layer demonstrates value **specifically on the transitive npm scenarios**, where the deterministic scanner-recommended baseline does not achieve a validated remediation for any of the nine scenarios — it fails at the application build stage (a pre-existing TypeScript toolchain incompatibility, see Limitation 2) before a post-remediation scan can confirm any fix. Nested-resolution constraints such as `EOVERRIDE` are the conceptual reason a naive transitive fix is difficult and were observed directly within the *LLM* pipeline (e.g. JS-05, JS-08), not as the deterministic baseline's recorded failure mode; `ERESOLVE` does not appear in any recorded evidence. For the flat-resolution **pip (Apache Airflow) scenarios, the deterministic scanner-recommended upgrade already succeeds** — all nine AF deterministic baselines both built and eradicated the target CVE (verified in `results/reproducibility_verification/`). The contribution is therefore not claimed uniformly across ecosystems. *(Corrected in `docs/01-overview.md`; expanded in `docs/05-results-and-discussion.md`.)*

## 2. npm target applications do not fully compile
The OWASP Juice Shop target fails `npm run build:server` (`tsc`) with `TS1005` errors from third-party type-definition packages (`@types/babel__traverse`, `@types/lodash`). This is **pre-existing toolchain decay, orthogonal to remediation** (present in the unmodified baseline; no remediation touches any `@types/*` package). Consequently, "successful remediation" for npm scenarios is defined as **target-CVE eradication + successful dependency installation + dependency-graph verification**, and explicitly **not** full application compilation or test-suite execution.

## 3. "Target CVE removed" is not "package now safe"
Remediation resolves the *selected* advisory, not necessarily the package's overall security posture. For example, `vm2 3.9.18` fixes `GHSA-whpj-8f3w-67p5` but `vm2` remains an abandoned package carrying later advisories. This is consistent with the RQ's scope (resolving *selected* vulnerabilities) but should not be read as a general safety guarantee.

## 4. Exact scan counts are not bit-for-bit reproducible; scientific conclusions are
Grype pulls a live vulnerability database on each run (the documented "Cold-Start Database Clause" pinning was never implemented). Aggregate finding counts therefore drift over time (e.g., a single new `pyasn1` advisory appeared between runs). The **target-CVE detection signal reproduced 18/18** in the Phase 5 verification sweep — the scientific conclusion is reproducible even though the exact numbers are not. Additionally, the npm baseline package counts were never reproducible *before* this session's frontend-lockfile fix; the fix establishes reproducibility going forward, not retroactively.

## 5. Provenance: shared workflow URL for eight scenarios
Eight scenarios (AF-05/06/07/08, JS-05/06/07/08) share one CI `workflow_url`, so their corrected `repository_commit` is a *verified real commit associated with the evidence's origin*, not a cryptographic proof that this exact commit produced each of those eight files individually. AF-09 and all other scenarios have uniquely-attributable provenance. *(Full detail: `docs/audit/docs_group_b_evaluation.md` item 1.)*

## 6. JS-09 was regenerated under the post-fix pipeline
JS-09's evidence was regenerated during this audit (its original was missing the `EMPIRICAL EVIDENCE` block). It was therefore produced under the pipeline *after* this session's fixes, not the exact pipeline state that generated the other 17 scenarios. Its remediation outcome (multer/CVE-2026-3520 resolved via retry) is unchanged from the original. Pre-rerun evidence is preserved at `archive/JS-09_pre_rerun_evidence_20260802_012547/`. *(Full before/after: `docs/audit/js09_rerun_summary.md`.)*

## 7. Historical metrics contradictions in un-rerun scenarios
Several scenarios' *historical* `metrics.json` files contain internal inconsistencies (e.g., `remediation_type` not matching `strategy`, `build_success`/`failure_stage` contradictions) that were root-caused and fixed in the pipeline code during this audit but were **not** retroactively corrected in the historical evidence (only JS-09 was rerun). These metadata inconsistencies do not affect the deterministic success signal (CVE eradication), per `docs/05` Observation 6. Any scenario rerun today would produce corrected metrics.

## 8. Runtime verification is shallow
"Runtime integrity verification" is limited to representative module loading, not comprehensive functional testing. `runtime_success` is recorded as `null` (not applicable) because no dedicated runtime-check stage exists. Full functional/semantic compatibility analysis is deferred to future work.

## 9. Repository documents methodology + evidence; aggregate analysis is in the thesis
`docs/05-results-and-discussion.md` presents two representative scenarios in narrative detail; the raw evidence for all 18 is in `results/execution_evidence/`; the aggregate statistical analysis lives in the accompanying thesis document. The repository is an evidence archive, not the thesis narrative itself.

## 10. External validity
Two applications (Juice Shop / npm, Airflow / pip). Generalisation to other ecosystems (Go, Rust, Maven) is unproven and flagged as future work.
