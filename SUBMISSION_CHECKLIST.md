# Submission Checklist

Practical, checkable list of what must be true before this thesis (`THESIS_DRAFT_V3.md`, "Empirical Evaluation of LLM-Assisted Dependency Remediation in SBOM-Driven CI/CD Pipelines", Santosh Nagaraj) can actually be submitted.

Originally built from the thesis's own self-reported gaps; **revised 2026-08-09** after a thesis-wide quality and compliance pass. The "Quality Report" and "Items That Still Require Manual Completion By The Author" sections that this checklist was first derived from have since been removed from the thesis, because a submitted thesis must not carry its own internal TODO list. The authoritative requirements are now `Masters_Thesis/Thesis Template MSc New.docx` and `Masters_Thesis/BST_FAQ_Master Thesis_Computer Science.pdf`. This file does not modify any evidence, the thesis file, or any docx/pdf — checklist only.

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

## 2. Length (RESOLVED — verify at submission time)

The 32,000–36,000-word figure previously recorded here had no source outside the thesis file itself. The **authoritative requirement**, from `Masters_Thesis/BST_FAQ_Master Thesis_Computer Science.pdf`, is:

> "The recommended length of the document is 30,000 words with Times New Roman font size 12 with 1,5 spacing. This does not include table of contents, graphs, annexures etc. The length of the document can be discussed and agreed with the primary supervisor as this is subject to topic, methodology and other attributes."

- [x] Chapter 2 deepened (§2.0 review method, §2.13 theoretical framework); Chapter 3 expanded with reproducibility detail; the eleven scenarios without individual case studies now covered in §4.6a; Chapter 5 expanded with threats to validity, literature comparison, and implications; Chapter 6 expanded with SQ answers, methodological reflection, and take-home messages.
- **Current measured count:** ~24,800 words core (Chapters 1–6) raw, ~22,400 excluding tables and code blocks; ~28,500 whole-document raw. Re-measure before submission — the counting script is described in the QA report.
- [ ] **Author decision required:** the count sits below the 30,000 recommendation. The FAQ explicitly permits the length to be "discussed and agreed with the primary supervisor." Either agree the current length with the primary supervisor, or extend further — but only with evidence-bearing material, not padding.

## 3. References (49 numbered entries + 18 scenario CVE records; ~67 sources; item 3)

- [ ] Verify remaining author lists for the ~8 academic entries not yet fully confirmed (Quality Report: "~26 of 34 academic entries have fully verified author lists; the remainder are verified by title/venue/year/DOI with author lists to confirm")
- [ ] Decide whether to expand references toward 80–90 (author's proposed route: add ~15–25 further verified sources on reachability analysis, SSVC in practice, npm production-dependency studies, additional LLM-repair evaluations) or submit with the current ~67 — no fabricated references either way
- [ ] Fill in "Access dates to be finalised by the author" (References section header note, THESIS_DRAFT_V3.md line 477)
- [ ] Confirm final IEEE citation formatting (the repo does not contain a separate style-guide document — IEEE format is asserted only within THESIS_DRAFT_V3.md itself; confirm this is the program's actual required citation style)

## 4. Figures (RESOLVED)

Five figures are now rendered and integrated, replacing the earlier list of sixteen *suggested* figures. All are generated programmatically from the frozen evidence archive by `scripts/figures/make_figures.py`; no value in any figure is hand-entered, and re-running that script from the repository root regenerates all five.

- [x] Figure 1 — two-arm experimental design (§3.1)
- [x] Figure 2 — recorded deterministic-gate outcomes, all eighteen scenarios (§4.1)
- [x] Figure 3 — scanner match counts before and after remediation (§4.1)
- [x] Figure 4 — JS-01 transitive shadowing and the override path (§4.4)
- [x] Figure 5 — JS-07 two-tree resolution and manifest-editing scope (§4.3c)
- [x] Each figure has a number, a caption, a source line, and an in-text reference; verified programmatically that no figure is defined-but-unreferenced or referenced-but-undefined.
- [x] The earlier F1–F16 vs "15 figures" count mismatch is void — that list and the Quality Report that contradicted it have both been removed.
- [ ] Confirm the figures render correctly in the generated docx/PDF at 300 dpi.

## 5. Evidence archive integrity (existence/count check only — not modified)

- [ ] `results/execution_evidence/` — confirmed present: 19 entries (AF-01–AF-09, JS-01–JS-09, `manual_baselines/`), 318 files total. Spot-check this count is unchanged at final submission time.
- [ ] `results/reproducibility_verification/` — confirmed present: 18 scenario dirs + `README.md`, 109 files total.
- [ ] `results/scenarios/` — confirmed present: 18 per-scenario `.json` files + `final_18_scenarios.json` + `README.md` + `pre_registered/`.
- [ ] `results/execution_evidence_no_hint/` exists (100 files: AF-01, JS-01, JS-05, JS-09, plus a `JS-09-CONTAMINATED` directory, and `EXPERIMENT_MANIFEST.yaml`). This is a separate no-hint experiment tree, not part of the 18 preregistered scenarios reported in THESIS_DRAFT_V3.md — confirm it is intentionally excluded from the submitted thesis body and does not need reconciling with Chapter 4's scenario count. The `-CONTAMINATED` naming in particular should be understood before submission (confirm it is inert/excluded, not an unresolved data-quality issue).
- [ ] Confirm no evidence files were altered by this checklist-writing pass (none were — read-only checks only were performed)

## 6. Repository-state consistency

- [x] **Branch confirmed.** The submission branch is `pipeline-v2-phase1` — the branch README.md identifies as having produced the reported experimental results. (An earlier revision of this checklist was written while `research/no-hint-search-grounding` was checked out and flagged a mismatch; that flag is resolved and no longer applies.) Confirm `git status` is clean on `pipeline-v2-phase1` immediately before generating the final output file.
- [ ] Confirm which branch/tag the final docx/PDF should be generated from — README.md explicitly says other branches (including `test-js-09`, `feature/reproducible-platform`) were "not used to produce the experimental results reported in the thesis"; verify the current branch matches `pipeline-v2-phase1` / `thesis-submission-v1.0` in substance, or reconcile the discrepancy before generating the final output file
- [ ] No separate top-level formatting-requirements document (page limits, font, margins, spacing) was found anywhere in this repository — README.md and CLAUDE.md (repo root) do not specify these. Confirm formatting requirements directly against the SRH program handbook (external to this repo) before final layout.

## 7. Final proofreading / formatting pass

- [ ] Full read-through of THESIS_DRAFT_V3.md for typos, grammar, and consistent terminology (independent of the audit passes already logged in `docs/audit/`)
- [ ] Confirm all internal cross-references (§ numbers, table numbers, figure numbers) still resolve correctly after any length-expansion edits (item 2) or figure insertion (item 4)
- [ ] Confirm the "Items That Still Require Manual Completion By The Author" section (THESIS_DRAFT_V3.md lines 637–644) is fully resolved and removed (or updated to reflect only genuinely remaining items) before the docx conversion is finalized — do not submit a thesis whose own body still contains an open TODO list to the author
- [ ] Final PDF generated and visually verified (see `SUBMISSION_QA_REPORT.md` once produced by the parallel work in this session)
- [ ] Final docx visually proofed (headers/footers, page numbers, table of contents, table/figure rendering) — tracked separately in this session
