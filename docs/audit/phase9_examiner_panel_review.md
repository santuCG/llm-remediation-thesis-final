# PHASE 9 — INDEPENDENT EXAMINER PANEL REVIEW

**Date:** 2026-08-02
**Repository state reviewed:** `main` @ `9da897ce` (latest commit at review time)
**Mode:** Read-only. No code, evidence, or documentation was modified during this review.

## Method and safeguard

Four examiners, each applying a distinct evaluation lens, followed by a Chair who forces exactly one verdict. This is one reviewer (an AI) deliberately adopting four different priorities — **not four independent humans** — so the findings are only as good as the primary evidence they cite.

**Governing safeguard:** `docs/audit/` was treated as *unverified claims*, never as evidence. Every "fixed/verified/resolved" statement in prior audit reports was re-checked against primary sources (the actual files under `results/`, `git cat-file`, real CI run IDs, the workflow YAML). Findings below cite primary evidence only.

Findings are classified **Blocker** (undermines validity/reproducibility/integrity — must stop) / **Major** (needs fixing; freezable only after) / **Minor** (documentation/disclosure only) / **Observation** (future work).

---

## Examiner A — Research Methodology

*Mandatory question: Are there any conclusions in the thesis that go beyond what the evidence actually demonstrates?*

**Yes — one headline claim is contradicted by the repository's own evidence.**

### [MAJOR] A1 — The "0% deterministic success rate" claim is false as stated
- **Claim:** `docs/01-overview.md:100` states, as an observed research result: *"basic version bumps that frequently fail (resulting in the 0% deterministic success rate observed in the baseline of this research)."* This is contradicted by the repository's own deterministic-baseline evidence.
- **Primary evidence:** `results/reproducibility_verification/AF-01/rescan.json` (deterministic Grype-recommendation baseline, produced by `grype-baseline.yml`) — the target `CVE-2026-8838` is **absent** from the post-fix rescan and `metrics.json` shows `build_success: true`. Same for `results/reproducibility_verification/AF-03/` (`CVE-2023-50782` removed, build succeeded). The repo's own draft table `results/THESIS_DRAFT.md:94-95` independently records AF-01 and AF-02 deterministic baseline as **"Success."** The deterministic success rate is therefore **not 0%** — it is 0% *only on the npm/transitive (JS) scenarios*, where `ERESOLVE`/dependency-shadowing defeats naive bumps. For the pip (AF) scenarios, a direct version bump frequently succeeds without any LLM.
- **Why it matters:** The RQ itself (`docs/01-overview.md:60`) is correctly scoped ("*where basic deterministic package upgrade strategies do not achieve the intended remediation objective*"), but this motivational sentence overstates the scoped result into a blanket falsehood. An examiner cross-checking the evidence would treat a stated-as-observed result that the evidence contradicts as an integrity concern, not a wording nit.

### [MAJOR] A2 — The central comparative result is not synthesised anywhere trustworthy in the repo
- **Claim:** The thesis's affirmative answer requires showing scenarios where the deterministic baseline fails to remove the CVE *and* the LLM succeeds. The only artifact in the repo that attempts this comparison, `results/THESIS_DRAFT.md:84-98`, is self-flagged as unreliable (`results/THESIS_DRAFT.md:2`: *"Do not use this table as a source of current results"*), conflates build-compilation failure with remediation failure (records JS-01 LLM as *"Failed (TS2531)"* even though `results/execution_evidence/JS-01/metrics.json` shows `rescan_success: true` / `dependency_verified: true`), and lists AF-06/JS-06 under pre-registered identities that don't match the executed evidence.
- **Primary evidence:** `results/THESIS_DRAFT.md:2,84-98`; contrasted with `results/execution_evidence/JS-01/metrics.json` (`rescan_success: true`). Also: `docs/audit/phase3_workflow_validation.md` "Missing Steps #1" confirms no programmatic baseline-vs-remediated comparison script exists (`docs/06-reproducibility.md` Step 11 documents one that was never implemented).
- **Why it matters:** `docs/05-results-and-discussion.md` presents only 2 of 18 scenarios and defers the aggregate to "the accompanying thesis." That division is defensible for an evidence-repo *if* the repo doesn't also contain a contradictory results table. As it stands, the most results-like artifact in the repo (`THESIS_DRAFT.md`) records the LLM as failing on ~13/18 — the opposite of the thesis's claim.

**Positive:** Where the docs make scoped claims, they are unusually disciplined — `docs/05` Observation 6 honestly separates "vulnerability removed" from "metadata consistent," and the RQ statement, README §2, and construct-validity section are all correctly bounded.

---

## Examiner B — Security & Dependency Analysis

*Mandatory question: Did any remediation merely suppress the scanner rather than genuinely remediate the vulnerability?*

**No suppression found in the scenario spot-checked — the remediation is genuine — but a domain caveat is under-disclosed.**

### [OBSERVATION] B1 — JS-01 remediation is genuine, not suppression
- **Claim:** The `vm2` override installs the fixed version rather than hiding the package. Verified directly.
- **Primary evidence:** `results/execution_evidence/JS-01/rescan.json` — the target advisory `GHSA-whpj-8f3w-67p5` is absent post-remediation, and `results/execution_evidence/JS-01/package-after.json` carries the `vm2 → 3.9.18` override (`3.9.18` is the genuine fixed version for this advisory). Confirmed the `@types/*` packages responsible for the build failure are never touched by any scenario's `package-after.json`, so remediation is not achieved by removing/masking a scanned component.

### [MINOR] B2 — "Target CVE removed" ≠ "package now safe" is not disclosed for vm2-class cases
- **Claim:** `vm2 3.9.18` resolves `GHSA-whpj-8f3w-67p5` but `vm2` itself is an abandoned package carrying later advisories (a fresh scan flags `3.9.18` for numerous other GHSAs). The thesis's success definition (target-CVE eradication) is legitimately met, but a security reader should be told the remediation fixes the *selected* advisory, not the package's overall safety.
- **Primary evidence:** `npm warn deprecated vm2@3.9.18: The library contains critical security issues...` appears in `results/execution_evidence/JS-01/build.log`; the RQ scoping (`docs/01-overview.md:60`) restricts to *selected* vulnerabilities, so this is a disclosure gap, not a validity defect.

### [MAJOR] B3 — npm target applications do not fully compile, and the effect on "success" is under-consolidated
- **Claim:** For every JS scenario, `npm run build:server` (`tsc`) fails with `TS1005` errors from `@types/babel__traverse` and `@types/lodash`. This is pre-existing toolchain decay, orthogonal to remediation (the failing `@types` packages are never modified by any remediation — verified). But it means "successful remediation" for JS scenarios = CVE eradicated + install + dependency-graph verification, and explicitly **not** full application compilation. This is disclosed only in scattered notes (`docs/04` Stage 8 note, the `test_success` semantics), never consolidated into a clear statement a reader can't miss.
- **Primary evidence:** `results/execution_evidence/JS-01/build.log` (6× `error TS1005`); orthogonality verified (no `package-after.json` touches `@types/*`).

---

## Examiner C — Reproducibility & Provenance

*Mandatory question: If I cloned this repository tomorrow and followed the documented methodology, could I regenerate evidence that supports the same conclusions?*

**Identical artifacts: mostly no (and honestly disclosed why). Reproducible scientific conclusions: yes for the target-CVE signal. But the documented layout would misdirect a fresh cloner.**

### [OBSERVATION] C1 — Provenance corrections verified against primary source
- **Claim:** The 9 previously-fabricated `repository_commit` hashes and JS-09's new hash resolve to real commits.
- **Primary evidence:** `git cat-file -e 241b549e07430f9520d1a116360ae194d1ba84f6` and `git cat-file -e d0748e0ac94fe75227d3c57303dfc59ffac78692` both succeed; `results/execution_evidence/AF-05/experiment_manifest.json` now carries the former. (Not taken from `docs/audit/` — re-verified here.) **[Superseded 2026-08-03: AF-05's `repository_commit` was subsequently corrected to `796ba575b26a4038bd2393d9f09c6328f06661b1`, its own genuine commit — see `docs/audit/repository_commit_correction_2026-08-03.md`. The commit cited here, while real and git-verified as this review states, was the wrong scenario's commit.]**

### [OBSERVATION] C2 — Baseline reproducibility fix is real
- **Claim:** The JS baseline is now deterministic across runs.
- **Primary evidence:** `results/reproducibility_verification/JS-01/baseline-sbom.json` = 2129 packages, matching the second determinism run documented in `docs/audit/phase5_baseline_reproducibility.md` (independently re-counted here, not trusted from the doc).

### [MINOR] C3 — "Identical artifacts" are not reproducible, but this is disclosed
- **Claim:** A fresh clone cannot reproduce the *exact* recorded numbers — Grype pulls a live DB each run (documented Cold-Start-DB clause never implemented) and the pre-fix baseline numbers were never reproducible. The target-CVE detection *is* reproducible (18/18 in the Phase 5 sweep). This is honestly disclosed in `docs/05` Reproducibility section and the audit reports.
- **Primary evidence:** `results/execution_evidence/JS-01/grype-db-metadata.json` shows a live DB build date; `docs/audit/phase5_baseline_reproducibility.md` documents the +1 `pyasn1` DB-timing drift.

### [MINOR] C4 — Documented repository layout does not match the actual repository
- **Claim:** `docs/06-reproducibility.md:163-180` shows a "recommended repository layout" with `experiment/`, `analysis/`, and `manual-validation-docs/` directories that do not exist; the real evidence lives under `results/`. A fresh cloner following the doc would look in the wrong place.
- **Primary evidence:** `docs/06-reproducibility.md:168` (`experiment/`) vs. actual top-level `results/` (no `experiment/` directory exists).

---

## Examiner D — Presentation & Documentation

*Would a first-time reader understand this repo? Are limitations honestly disclosed in thesis-facing docs? Is anything missing that would frustrate an examiner?*

### [OBSERVATION] D1 — Strong navigational entry point
- **Primary evidence:** `README.md` is a clean navigation hub with correctly-scoped research framing (§2) and direct links to methodology, results, and evidence.

### [MAJOR] D2 — A contradictory draft sits inside `results/`
- **Claim:** `results/THESIS_DRAFT.md` is a superseded draft whose results table contradicts the actual evidence, yet it lives in the authoritative `results/` directory. Its disclaimer helps, but a first-time examiner should not have to be told a file in `results/` is untrustworthy — it should be archived or clearly marked superseded and moved out of the evidence path.
- **Primary evidence:** `results/THESIS_DRAFT.md:2` (self-disclaimer) and `:84-98` (the contradictory table).

### [MINOR] D3 — No consolidated, thesis-facing limitations section
- **Claim:** Limitations are real and mostly disclosed, but scattered across `docs/05`, `docs/04` notes, and `docs/audit/`. There is no single thesis-facing limitations document a reader can consult. (This is precisely what the planned `THESIS_LIMITATIONS.md` freeze artifact would resolve.)
- **Primary evidence:** limitations appear in `docs/05-results-and-discussion.md:224-240` but omit the build-compilation point (B3) and the deterministic-baseline-per-ecosystem point (A1).

---

## CHAIR — Synthesis and Verdict

### Rubric

| Area | Rating | Basis |
|---|---|---|
| Scientific validity | **Adequate** | Per-scenario evidence is sound; but one headline claim (A1) is contradicted by the repo's own evidence and the central comparative result is not trustworthily synthesised (A2). |
| Methodology | **Good** | The deterministic-validation design is rigorous and honestly separates recommendation from verification; implementation matches the documented stages. |
| Reproducibility | **Good** | Target-CVE signal reproduces 18/18; determinism fixes verified; honestly disclosed where exact numbers can't reproduce. Docked for the layout mismatch (C4). |
| Evidence | **Good** | Complete per-scenario artifacts, now with genuine provenance; the gap is synthesis, not raw evidence. |
| Provenance | **Good** | Fabricated hashes corrected and re-verified against `git`; residual shared-URL caveat honestly disclosed. |
| Documentation | **Adequate** | Strong README and methodology docs, undercut by the contradictory `THESIS_DRAFT.md` in `results/` (D2) and the false overview claim (A1). |

### Verdict: **MAJOR REVISIONS REQUIRED**

Not a Blocker — no experiment is invalid, no evidence is corrupt, and the correctly-scoped research question is genuinely supported by the per-scenario metrics. But it is more than minor revision, because two issues are factual/integrity matters that cannot be discharged by a limitations paragraph alone:

- **A1** — a stated-as-observed quantitative result ("0% deterministic success rate") that the repository's own evidence contradicts. Correcting a false stated result is not "clarification."
- **A2 / D2** — the repository's most results-like artifact (`THESIS_DRAFT.md`) contradicts the thesis's affirmative answer and is only saved by a "don't trust this" banner.

Everything else (B2, B3, C3, C4, D3) is genuinely Minor/Observation and would be dischargeable via the freeze's disclosure artifacts.

### Required before freeze (Major items only)
1. **A1:** Correct the "0% deterministic success rate" claim in `docs/01-overview.md:100` to reflect the real, ecosystem-split result (0% on npm/transitive scenarios; deterministic bumps succeed for several pip scenarios). This is the author's stated result to correct — not something the reviewer should silently reword.
2. **A2 / D2:** Either move `results/THESIS_DRAFT.md` to `archive/` (superseding it), or replace its table with an honest, evidence-derived per-scenario outcome summary that distinguishes "target CVE eradicated" from "application compiles." A reader must not find a contradictory results table in `results/`.
3. **B3:** Consolidate the npm build-compilation limitation into a clear, thesis-facing statement of what "success" means for JS scenarios (dischargeable via `THESIS_LIMITATIONS.md`).

### Chair's defence of the verdict
*If another examiner initially disagreed, what repository evidence would I cite?*

- If they argued for **Accept** / minor revisions: I would show `docs/01-overview.md:100` ("0% deterministic success rate") side-by-side with `results/reproducibility_verification/AF-01/rescan.json` and `AF-03/rescan.json` (deterministic baseline removed the CVE and built) — a stated result contradicted by the repo's own evidence is, by definition, more than a wording fix.
- If they argued for **Major revisions is too harsh / near-Blocker**: I would show `results/execution_evidence/*/metrics.json` (`rescan_success: true`, genuine provenance, deterministic-signal reproducibility) to demonstrate the underlying science is sound and the defects are correctable documentation/factual issues, not fatal flaws — so it is Major, not Reject.

---

## Decision (per the approved plan)

Verdict is **Major revisions required**, therefore per the agreed decision logic I **stop before the freeze** and present this to the user. Phase 9.5 (`THESIS_IMPROVEMENTS.md`) and the four freeze artifacts are **held**, pending the user's decision on the three Major items above.

---

## RE-REVIEW ADDENDUM (2026-08-02, after the three Major items were fixed)

The user directed that all three Major items be fixed, then re-reviewed. Each was corrected (documentation only — no code, no experimental evidence touched) and re-verified against primary sources:

- **A1 — RESOLVED.** `docs/01-overview.md` no longer claims a blanket "0% deterministic success rate." It now states the ecosystem-split result verified directly from evidence: the deterministic scanner-recommendation baseline **succeeded on all nine pip (Airflow) scenarios** (each `results/reproducibility_verification/AF-0N/rescan.json` shows the target CVE removed with `build_success: true`), and achieves **0% only on the transitive npm scenarios**. Re-verified: `grep "0% deterministic success" docs/ README.md` returns nothing outside this review document.
- **A2 / D2 — RESOLVED.** `results/THESIS_DRAFT.md` was `git mv`'d to `archive/THESIS_DRAFT_superseded_20260802.md` with an updated banner explaining the relocation. No results-like artifact contradicting the evidence remains under `results/`. Confirmed no live navigational link broke (the only references were in historical audit logs, which legitimately describe the prior state). The authoritative outcomes remain in `results/execution_evidence/*/metrics.json`; the aggregate analysis is in the accompanying thesis.
- **B3 — RESOLVED.** `docs/05-results-and-discussion.md` Limitations now contains an explicit, consolidated statement that the npm target does not fully compile (pre-existing `tsc` toolchain failure, orthogonal to remediation) and that "success" for npm scenarios is therefore defined as CVE-eradication + install + graph-verification, not full compilation — plus a companion note that deterministic-baseline efficacy is ecosystem-dependent.
- **C4 (Minor, fixed opportunistically) — RESOLVED.** `docs/06-reproducibility.md`'s repository-layout diagram, which previously showed non-existent `experiment/`, `analysis/`, and `manual-validation-docs/` directories, now reflects the actual layout.

**Residual Minor / Observation items** (B2, C3, D3, and the shared-`workflow_url` provenance caveat) are genuinely disclosure-only and are carried into `THESIS_LIMITATIONS.md` at freeze.

### Revised verdict: **ACCEPT WITH MINOR REVISIONS**

The two integrity issues (a false stated result; a contradictory results table inside `results/`) are resolved. What remains is honest disclosure, which the freeze artifacts discharge. Per the agreed decision logic, this verdict permits proceeding to Phase 9.5 and the freeze.

### Revised rubric

| Area | Rating |
|---|---|
| Scientific validity | Good |
| Methodology | Good |
| Reproducibility | Good |
| Evidence | Good |
| Provenance | Good |
| Documentation | Good |
