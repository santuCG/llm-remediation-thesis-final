# Publication-Readiness Checklist (Phase F, 2026-08-02)

Each item answered only from evidence verified during this sweep (`docs/audit/publication_consistency_sweep_2026-08-02.md`), not asserted.

**1. Can an examiner read any document without finding outdated methodology?**
Yes, for the 55 in-scope files checked. `docs/03` (the highest-risk document — LLM configuration) was fully rewritten and verified against both code and evidence. All propagated staleness found by the Phase C.5 chain-of-custody check (the future-work item repeated in three thesis drafts) was corrected. Files explicitly marked historical (`docs/07`, `docs/08`, `methodology_evolution_record.md`) are scoped correctly and not expected to match current state.

**2. Are all pipeline diagrams correct?**
Yes. The 4-phase/12-stage diagrams in `docs/01`, `docs/02`, `docs/04` and the repository-layout diagram in `docs/06` were checked stage-by-stage / directory-by-directory against the actual workflow YAML and filesystem, and matched (the layout diagram had already been corrected in an earlier pass and was re-verified here, not re-fixed).

**3. Are all workflow stages correct?**
Yes. Verified directly against `.github/workflows/generic-remediation.yml` and `grype-baseline.yml` line-by-line (Phase A ground truth); the retry-prompt-augmentation mechanism, previously undocumented, is now described in `docs/03`.

**4. Are all tool versions correct?**
Yes, with one clarification applied: Syft 1.44.0 and Grype 0.112.0 are genuinely pinned (verified in workflow YAML); the CI runner (`ubuntu-latest`) is a floating label, not a strict pin, and `docs/02` now states this precisely rather than implying a fixed OS version.

**5. Are all repository paths correct?**
Yes, after this sweep. Two were wrong before it: `README.md`'s `audit_reports/` (fixed to `docs/audit/`) and `docs/08`'s workflow path (fixed to note the archived location).

**6. Are all scenario references correct?**
Yes. `SCENARIOS_LIST.md` cross-checked line-by-line against `preregistration/PRE_REGISTRATION_AMENDMENT.md`'s amended scenario tables — all 18 CVE/package/CVSS/upgrade-type values match. The one known scenario-identity issue (AF-06/JS-06 executed evidence vs. locked targets) was already disclosed before this sweep and remains an open item for the repository owner, not silently hidden.

**7. Are all quantitative claims supported?**
Yes, after this sweep. `docs/05`'s headline results table (182→181) did not match any evidence file and was corrected to the verified 383→187 (336→183 unique ids), consistent with the JS-01 case study. No other headline quantitative claim was found unsupported during the checks performed (see the sweep report's "not yet independently re-verified" section for the narrower-scope items).

**8. Are all limitations consistent?**
Yes, after this sweep. `THESIS_LIMITATIONS.md` Item 1 carried a stale ERESOLVE/EOVERRIDE mis-attribution that contradicted the already-corrected `docs/01`; now consistent. The Grype DB live-database limitation is now consistently disclosed in `docs/06`, `THESIS_LIMITATIONS.md`, and the pre-registration amendment.

**9. Are all future work statements consistent?**
Yes, after this sweep. A classification error (failure-log retry prompt listed as undone future work when it was already implemented) was present in five files (`docs/FUTURE_WORK.md`, `THESIS_FUTURE_WORK.md`, `docs/THESIS_IMPROVEMENTS.md`, and all three thesis drafts' Chapter 5) and corrected in all of them.

**10. Can the repository now be considered publication-ready?**
Conditionally yes — see Phase G certification (`REPOSITORY_CERTIFICATION.md`) for the full dimension-by-dimension verdict and the specific open items that qualify this answer.
