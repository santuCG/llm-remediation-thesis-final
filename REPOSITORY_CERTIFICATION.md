# Repository Certification

**Repository:** `llm-remediation-thesis-final`
**Basis:** Publication-level consistency sweep (2026-08-02), Phases A-F — see `docs/audit/publication_consistency_sweep_2026-08-02.md` (full findings) and `docs/audit/publication_readiness_checklist_2026-08-02.md` (10-question checklist).
**Scope note:** This certification evaluates documentation/evidence/methodology consistency. It does not re-run or redesign any experiment (no-scope-creep constraint, honored throughout this sweep — no code, evidence, or methodology file was modified in Phases A-F).

---

## Dimension-by-dimension verdict

### 1. Repository implementation — PASS
The pipeline code (`.github/workflows/*.yml`, `scripts/**`) was read as ground truth and found internally consistent: the retry mechanism, metrics semantics, and LLM configuration all behave as the corrected documentation now describes them. No code was modified during this sweep (verified: every commit in this pass touched only `.md` files and `.agents/AGENTS.md`).

### 2. Documentation synchronization — PASS
55 in-scope files checked; 14 findings corrected across 9 commits (`docs/audit/publication_consistency_sweep_2026-08-02.md`). One caveat: `preregistration/AIRFLOW_PREREGISTRATION.md`, `JUICESHOP_PREREGISTRATION.md`, `protocol.md`, `scenario_selection_log.md`, and `tool_versions.md` received a targeted pattern check rather than a full line-by-line read (locked, non-narrative supporting files; nothing surfaced from the patterns checked).

### 3. Methodology consistency — PASS
The 4-phase/12-stage pipeline description is identical and accurate across `docs/01`, `docs/02`, `docs/04`, and all three thesis drafts. Historical documents (`docs/07`, `docs/08`, `methodology_evolution_record.md`) are correctly scoped as historical and do not claim to describe current behavior.

### 4. Research consistency — PASS
Chain-of-custody verified end-to-end in all three thesis drafts: Research Question → Hypothesis → Results (§4.7) → Discussion (§4.8) → Conclusion (§5.1) → Contributions (§5.2) → Future Work (§5.5). One drift was found (a stale future-work item repeated in each draft's Chapter 5, contradicting a correction just made to the source future-work files) and fixed in all three.

### 5. Evidence consistency — PASS (external reproducibility limitation, fully investigated)
Two of eighteen scenarios' executed evidence do not match their locked pre-registered targets. `AF-06`'s recorded evidence is `werkzeug`/CVE-2024-34069 (identical to AF-09's target) rather than the pre-registered `jinja2`/CVE-2024-56326; `JS-06`'s recorded evidence is `lodash`/CVE-2021-23337 rather than the pre-registered `flatted`/CVE-2026-33228. This was investigated to completion (`docs/audit/af06_js06_rerun_attempt_2026-08-02.md`), and the investigation establishes that the repository is not internally inconsistent here — it encountered an external dependency-ecosystem drift:
- **Pre-registration, scenario definitions, and package/version targets are all confirmed correct.** `results/scenarios/final_18_scenarios.json` already matches the original pre-registration exactly; jinja2/flatted at the pre-registered versions remain available and installable today.
- **Root cause of the original mismatch confirmed:** a scenario-profile copy-paste error at initial creation time in an earlier, since-replaced per-scenario-workflow architecture — `profiles/AF-06.yaml` was byte-identical to `profiles/AF-09.yaml`. Not a later pipeline defect.
- **A real rerun was attempted** against the correct, locked pre-registered targets (CI runs 30756155220, 30756158221), per the repository owner's explicit feasibility-first instruction.
- **Confirmed currently infeasible, and confirmed why:** both reruns reproduced the same off-target selection, because Grype's live, unpinned vulnerability database has changed since the 2026-07-08 pre-registration snapshot — jinja2's advisory now scores below the pipeline's severity filter, and flatted's advisory is no longer detected at all. This is an external reproducibility limitation, not a design or implementation flaw.
- **No historical evidence was modified** at any point; the rerun output was not merged in since it did not correct the mismatch.
- **The pre-registration is intentionally left unamended.** AF-06 and JS-06 remain defined by their original, correct targets, because that is what the experimental design intended to test; the executed `werkzeug`/`lodash` identities are not adopted as replacements.

This investigation is complete, not open. All other evidence-consistency checks also passed: 9 fabricated provenance hashes were corrected pre-freeze against real `git`-verified commits; JS-09's regeneration is fully disclosed with before/after comparison; the shared-`workflow_url` caveat for eight scenarios is disclosed as a scoped limitation, not hidden.

### 6. Reproducibility consistency — PASS
Target-CVE detection reproduces 18/18 (`results/reproducibility_verification/`). Exact scanner-finding counts do not reproduce bit-for-bit, because Grype's vulnerability database is live and was never pinned as originally pre-registered — this is now consistently disclosed in `docs/06`, `THESIS_LIMITATIONS.md`, and the pre-registration amendment (previously it was inconsistently disclosed: the workflow's actual behavior contradicted an audit report's claim that this was already handled).

### 7. Publication readiness — PASS
The documentation now accurately and consistently reflects the frozen pipeline and evidence, which was this sweep's objective. All items that previously qualified this dimension are now resolved:
- The AF-06/JS-06 evidence-identity question (dimension 5) is a closed investigation with a confirmed external reproducibility limitation, not an open decision; the pre-registration remains correctly unamended.
- Root-level working files (`audit_progress.md`, `findings_classification.md`, `remediation_log.md`, `27-07-2026/Thesis_Update.md`) archived to `archive/session_working_notes/`.
- The thesis draft files (`THESIS.md`, `THESIS_DRAFT_V2.md`, `THESIS_DRAFT_V3.md`) were briefly committed by mistake alongside an unrelated content fix, then untracked per the repository owner's explicit direction that they remain working-directory-only files.

The only remaining action is the new post-sync tag itself (Phase G, below), which is administrative housekeeping rather than a qualification on this verdict.

---

## Recommendation

**If this repository were submitted today alongside the thesis, would you recommend it for examination?**

**YES.**

**Justification.** The core scientific claim — that an LLM reasoning layer adds value specifically for transitive npm dependency remediation, and adds no value where a deterministic upgrade already suffices (flat pip dependencies) — is supported by evidence that was independently re-verified in this sweep at the primary-source level (`results/execution_evidence/`, `results/reproducibility_verification/`, workflow YAML, and pipeline code), not merely asserted by prior documentation. Every discrepancy found between documentation and implementation during this pass was a *documentation* defect, not a defect in the underlying experiment: the pipeline itself behaves as the (now-corrected) documentation describes, and the frozen evidence supports the frozen conclusions. The one substantive evidence issue found (AF-06/JS-06) was investigated to completion rather than left as a guess: the pre-registration, scenario definitions, and package targets are all confirmed correct, the mismatch's root cause is identified (a historical profile copy-paste error), and a real rerun confirmed the exact targets are not currently reproducible for a specific, external reason — Grype's live vulnerability database evolving since 2026-07-08 — not any flaw in the experimental design. It affects two of eighteen scenarios, is honestly and explicitly disclosed rather than hidden, and does not touch the scenarios the primary research-question narrative relies on (JS-01, JS-05, JS-08, JS-09, and the aggregate 9/9-vs-0/9 ecosystem split). This is the same class and severity of issue the repository's own four-examiner panel review already weighed once before, reaching "Accept with minor revisions" — this certification's judgment is consistent with that precedent, not a departure from it.

This is not a claim that the repository is flawless. It is a judgment that its remaining flaws are identified, bounded, and honestly disclosed — which, as this repository's own `FINAL_VERDICT.md` puts it, is the appropriate bar for an MSc evidence archive.

---

*This certification supersedes nothing in `FINAL_VERDICT.md` (which certified the frozen experimental evidence and methodology as of `thesis-freeze-2026-08-02`); it certifies the documentation layer as of the publication-level consistency sweep described above.*
