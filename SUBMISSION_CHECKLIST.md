# Submission Checklist

Practical, checkable list of what must be true before this thesis (`THESIS_DRAFT_V3.md`, "Empirical Evaluation of LLM-Assisted Dependency Remediation in SBOM-Driven CI/CD Pipelines", Santosh Nagaraj) can actually be submitted.

Built from the repository's own self-reported gaps (THESIS_DRAFT_V3.md, "Quality Report" and "Items That Still Require Manual Completion By The Author", lines 617–644) plus a direct check of repo state on 2026-08-08/09. This file does not modify any evidence, the thesis file, or any docx/pdf — checklist only.

---

## 0. Output file status (checked directly, not self-reported)

- [ ] **No formatted output file exists yet.** As of this check, there is no `.docx` or `.pdf` for the thesis anywhere in the repo root (globbed `*.docx`, `*.pdf`). The task brief describes a file "likely named `SRH_Thesis_Nagaraj_FINAL.docx`" as already produced — it does not exist in this repository. (A *different*, unrelated file — `100001670_SantoshNagaraj_ThesisProposal.docx`, the thesis *proposal*, not the final thesis — exists in `C:\Users\HP\Downloads\`, outside this repo; do not confuse it with the final deliverable.)
- [ ] Once the docx is generated (tracked separately in this session), confirm its **last-modified time postdates** the last commit to `THESIS_DRAFT_V3.md` (`git log -1 -- THESIS_DRAFT_V3.md`, currently `2026-08-08 18:49:33 +0200`, commit `d8c37539`). If the thesis file is edited again after the docx is generated, regenerate the docx — do not submit a stale conversion.
- [ ] Final PDF generated from the final docx and visually verified (see `SUBMISSION_QA_REPORT.md` once produced, or equivalent QA note from this session).
- [ ] Final docx visually proofed page-by-page (headers, page numbers, table rendering, figure placeholders) — tracked separately in this session; check off here once done.

## 1. Front matter (currently all placeholders — THESIS_DRAFT_V3.md lines 1–12)

- [ ] University name filled in (README.md states "SRH University Berlin" — confirm this is the exact required legal/formatted name for the title page, e.g. whether a merged-institution name applies per `BestätigungFusionSRHHochschulen2024_engl.pdf` in Downloads)
- [ ] Faculty / Department filled in (not stated anywhere in the repo — must be sourced from the author/program administration)
- [ ] Matriculation number filled in (not present in any repo file — check administration records)
- [ ] First Supervisor name filled in
- [ ] Second Supervisor name filled in
- [ ] Submission date filled in
- [ ] Acknowledgements section written (currently absent; listed as outstanding in the "Items That Still Require Manual Completion" list, item 1)
- [ ] Final title confirmed as-is or revised (currently "Empirical Evaluation of LLM-Assisted Dependency Remediation in SBOM-Driven CI/CD Pipelines" — item 1 flags "final title" as still open)

## 2. Length gap (self-reported: ≈11,000 words vs. 32,000–36,000 target)

- [ ] Decide how to close the length gap: expand the remaining ~15 non-deep-dived scenarios (currently only 7 of 18 have full case-study treatment: AF-01, AF-06, JS-01, JS-05, JS-06, JS-07, JS-09) into ~300–500-word analytical vignettes each, per the author's own proposed remediation in item 2
- [ ] Deepen Chapter 2 literature sub-sections with additional verified sources (no fabrication) if pursuing the length target
- [ ] If the length target is knowingly *not* met, get explicit sign-off from supervisor/examiner that ~11,000–16,000 words (raw file word count independently verified at ~15,986 including tables/references/appendices) is acceptable, rather than submitting silently under-length
- [ ] No requirements document in this repo states the 32,000–36,000-word figure independently of THESIS_DRAFT_V3.md itself — confirm this number against the actual SRH program handbook/thesis guidelines (not found in repo; likely external to this repository)

## 3. References (49 numbered entries + 18 scenario CVE records; ~67 sources; item 3)

- [ ] Verify remaining author lists for the ~8 academic entries not yet fully confirmed (Quality Report: "~26 of 34 academic entries have fully verified author lists; the remainder are verified by title/venue/year/DOI with author lists to confirm")
- [ ] Decide whether to expand references toward 80–90 (author's proposed route: add ~15–25 further verified sources on reachability analysis, SSVC in practice, npm production-dependency studies, additional LLM-repair evaluations) or submit with the current ~67 — no fabricated references either way
- [ ] Fill in "Access dates to be finalised by the author" (References section header note, THESIS_DRAFT_V3.md line 477)
- [ ] Confirm final IEEE citation formatting (the repo does not contain a separate style-guide document — IEEE format is asserted only within THESIS_DRAFT_V3.md itself; confirm this is the program's actual required citation style)

## 4. Figures (F1–F16 described but not rendered — item 4)

- [ ] Render F1: twelve-stage LLM pipeline diagram (source: `.github/workflows/generic-remediation.yml`; Mermaid source in `PIPELINE_V2_RELEASE_NOTES.md`)
- [ ] Render F2: deterministic baseline diagram (`.github/workflows/grype-baseline.yml`)
- [ ] Render F3: JS-01 transitive shadowing graph (`results/execution_evidence/JS-01/llm-request.json`)
- [ ] Render F4: baseline vs LLM by ecosystem (Tables 5–6)
- [ ] Render F5: response-schema fields (`results/execution_evidence/AF-01/llm-request.json`)
- [ ] Render F6: prioritisation order (`scripts/remediation/prioritize.py`)
- [ ] Render F7: baseline-vs-rescan counts for the case studies
- [ ] Render F8: evidence-folder structure
- [ ] Render F9: strategy distribution across 18 scenarios (Table 4)
- [ ] Render F10: npm nested vs pip flat resolution
- [ ] Render F11: retry mechanism flow
- [ ] Render F12: provenance/audit timeline
- [ ] Render F13: CVSS/EPSS/KEV prioritisation concept
- [ ] Render F14: SBOM generation-to-scan data flow
- [ ] Render F15: comparison-to-existing-tools map (Table L1)
- [ ] Render F16: two-tree monorepo structure for JS-07's manifest-editing-scope limitation (§4.3c)
- [ ] **Note the count mismatch**: Appendix D (line 552) lists F1–**F16** (16 figures), but the Quality Report's "Approximate metrics" (line 629) states "Figures suggested: **15**." Reconcile this discrepancy — either the count needs correcting or one figure was added after the metrics line was last updated.
- [ ] Insert rendered figures into the docx/PDF at their referenced locations, replacing "(author to render)" in Appendix D

## 5. Evidence archive integrity (existence/count check only — not modified)

- [ ] `results/execution_evidence/` — confirmed present: 19 entries (AF-01–AF-09, JS-01–JS-09, `manual_baselines/`), 318 files total. Spot-check this count is unchanged at final submission time.
- [ ] `results/reproducibility_verification/` — confirmed present: 18 scenario dirs + `README.md`, 109 files total.
- [ ] `results/scenarios/` — confirmed present: 18 per-scenario `.json` files + `final_18_scenarios.json` + `README.md` + `pre_registered/`.
- [ ] `results/execution_evidence_no_hint/` exists (100 files: AF-01, JS-01, JS-05, JS-09, plus a `JS-09-CONTAMINATED` directory, and `EXPERIMENT_MANIFEST.yaml`). This is a separate no-hint experiment tree, not part of the 18 preregistered scenarios reported in THESIS_DRAFT_V3.md — confirm it is intentionally excluded from the submitted thesis body and does not need reconciling with Chapter 4's scenario count. The `-CONTAMINATED` naming in particular should be understood before submission (confirm it is inert/excluded, not an unresolved data-quality issue).
- [ ] Confirm no evidence files were altered by this checklist-writing pass (none were — read-only checks only were performed)

## 6. Repository-state consistency

- [ ] `git status` is clean on the branch used for submission (`research/no-hint-search-grounding` at time of this check — confirm this is the intended branch, given README.md states results correspond to branch `pipeline-v2-phase1` / tag `thesis-submission-v1.0`, not the currently checked-out branch)
- [ ] Confirm which branch/tag the final docx/PDF should be generated from — README.md explicitly says other branches (including `test-js-09`, `feature/reproducible-platform`) were "not used to produce the experimental results reported in the thesis"; verify the current branch matches `pipeline-v2-phase1` / `thesis-submission-v1.0` in substance, or reconcile the discrepancy before generating the final output file
- [ ] No separate top-level formatting-requirements document (page limits, font, margins, spacing) was found anywhere in this repository — README.md and CLAUDE.md (repo root) do not specify these. Confirm formatting requirements directly against the SRH program handbook (external to this repo) before final layout.

## 7. Final proofreading / formatting pass

- [ ] Full read-through of THESIS_DRAFT_V3.md for typos, grammar, and consistent terminology (independent of the audit passes already logged in `docs/audit/`)
- [ ] Confirm all internal cross-references (§ numbers, table numbers, figure numbers) still resolve correctly after any length-expansion edits (item 2) or figure insertion (item 4)
- [ ] Confirm the "Items That Still Require Manual Completion By The Author" section (THESIS_DRAFT_V3.md lines 637–644) is fully resolved and removed (or updated to reflect only genuinely remaining items) before the docx conversion is finalized — do not submit a thesis whose own body still contains an open TODO list to the author
- [ ] Final PDF generated and visually verified (see `SUBMISSION_QA_REPORT.md` once produced by the parallel work in this session)
- [ ] Final docx visually proofed (headers/footers, page numbers, table of contents, table/figure rendering) — tracked separately in this session
