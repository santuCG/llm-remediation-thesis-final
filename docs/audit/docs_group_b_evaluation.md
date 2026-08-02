# GROUP B — EVALUATION FRAMEWORK RESULTS

Every item below was investigated directly (API calls, code reads, log inspection) — no answer here is a guess.

> **PARTIALLY SUPERSEDED (2026-08-03).** Item 1's fix correctly replaced fabricated `repository_commit` hashes with real ones, but for 8 of the 9 affected scenarios (AF-05/06/07/08, JS-05/06/07/08) the "real" hash was queried from the `workflow_url` recorded at the time — which was itself wrong (see `docs/audit/workflow_url_provenance_correction_2026-08-03.md`), shared across those scenarios rather than each one's own genuine run. Once each scenario's true run was recovered, each one's true `head_sha` was re-queried directly and found to differ from what this fix had assigned for those 8 (AF-09 and the fifth of the original nine were already correctly attributed and remain so). This section is not rewritten, per this repository's practice — the analysis below reflects what was known and correctly reasoned at the time, given the information available. Full detail: `docs/audit/workflow_url_provenance_correction_2026-08-03.md` and `docs/audit/repository_commit_correction_2026-08-03.md`.

---

## 1. Repository provenance fix (9 fabricated `repository_commit` hashes)

- **Can it be implemented?** Partially, and with an important caveat discovered during this evaluation. The 9 affected manifests (AF-05/06/07/08/09, JS-05/06/07/08) all carry a valid `workflow_url` pointing to a real GitHub Actions run. Querying the GitHub API for those runs returns an authoritative `head_sha` in every case — so the *fabrication* (a real-looking hash padded with non-corresponding hex characters) is directly correctable with a real value, not a guess.
  - **New finding this evaluation surfaced:** 8 of the 9 scenarios (all except AF-09) cite the exact same `workflow_url` (run `30592634834`) — one CI run producing 8 scenarios' worth of distinct evidence is architecturally implausible for this pipeline (each scenario is a separate `workflow_dispatch`). This means: I can replace the fabricated hash with a *real* commit hash for that URL, but I cannot fully verify that commit is the one whose code specifically produced each of those 8 scenarios' evidence content — only that it's a genuine commit that existed. AF-09's URL is unique to it and its recovered hash is more trustworthy for that reason.
- **Scientific impact:** None on the reported CVE/remediation results — this field is metadata about *how* the evidence was produced, not the evidence itself.
- **Methodology impact:** None — doesn't touch prompts, LLM behavior, or scan logic.
- **Evidence impact:** Modifies 9 existing `experiment_manifest.json` files (a metadata field only, not `metrics.json`/`llm-response.json`/scan results).
- **Estimated effort:** Small (script to query 2 run IDs via API, replace 9 fields).
- **Validation approach:** Re-verify each replaced hash resolves via `git cat-file -e` and matches the API's `head_sha` exactly (not just prefix-matches).
- **Rerun all scenarios required?** No.
- **Classification:** Engineering Enhancement (provenance correction, not methodology change).
- **Recommendation:** **Implement before freeze**, with disclosure of the shared-URL caveat for the 8 affected scenarios (i.e., the corrected hash is "a verified real commit associated with this evidence's origin," not "cryptographically proven to be the exact commit that generated this specific file").

### RESOLVED

Implemented and pushed. `AF-05`, `AF-06`, `AF-07`, `AF-08`, `JS-05`, `JS-06`, `JS-07`, `JS-08` → `241b549e07430f9520d1a116360ae194d1ba84f6` (real `head_sha` of run `30592634834`, shared across these 8 — see the caveat above, still applicable). `AF-09` → `16a551ed6c7569848711da6f431cae58d4d008fe` (real `head_sha` of its own uniquely-referenced run `30585687941`). Both values re-verified via `git cat-file -e` immediately before writing.

Each of the 9 `experiment_manifest.json` files had exactly 2 occurrences of its fabricated hash (the primary JSON body and the human-readable `EMPIRICAL EVIDENCE` trailer copy) — both replaced identically. Diff confirmed scoped to exactly those 2 lines per file, 18 lines total across 9 files; no other field, no `metrics.json`, no scan result touched.

---

## 2. Retry build validation fix

- **Can it be implemented?** Yes. Root cause (Phase 7): the retry step runs a plain `npm install`, which triggers Juice Shop's own `postinstall` hook — and that hook's `(npm run --silent build:server || cd .)` silently swallows build failures. The first attempt, by contrast, calls `build:frontend`/`build:server` explicitly with `|| (echo "...Failed" && exit 1)`. The fix is to add the same explicit, fatal-on-failure calls to the retry step, matching the first attempt's rigor.
- **Scientific impact:** Improves the *fidelity of measurement* of retry outcomes going forward — doesn't change what the LLM is asked to do or how it reasons, only whether we correctly detect when its retry's build genuinely fails.
- **Methodology impact:** None on the experiment's independent variable (LLM prompt/behavior). This is a measurement-instrument correctness fix, not a methodology change — classified Engineering on that basis.
- **Evidence impact:** None on existing historical evidence (no rerun forced). Only affects future runs' metrics accuracy.
- **Estimated effort:** Small — mirror ~3 lines from the "Validate Remediation & Rescan" step into "Retry Remediation Strategy."
- **Validation approach:** Dispatch JS-01 again (guaranteed retry path, known build failure) and confirm `build_success`/`failure_stage` now correctly reflect the retry's real build outcome instead of a stale/lenient value.
- **Rerun all scenarios required?** No.
- **Classification:** Engineering Enhancement.
- **Recommendation:** **Implement before freeze.**

---

## 3. JS-09 rerun

- **Can it be implemented?** Yes — dispatch `generic-remediation.yml` for JS-09 (`multer`, `CVE-2026-3520`), already pre-approved by you in an earlier session turn.
- **Scientific impact:** Fills a genuinely incomplete data point (missing `EMPIRICAL EVIDENCE` block); doesn't touch the other 17 scenarios.
- **Methodology impact:** One real nuance: JS-09 would be regenerated using *today's* pipeline (frontend lockfile pin + bin exclusion +, if approved, the retry-validation fix), which is methodologically *better* than what generated the original 17 — but that means JS-09 would not be generated under bit-for-bit identical pipeline conditions as the other 17 were. This should be disclosed as a footnote, not hidden.
- **Evidence impact:** Replaces JS-09's evidence directory only (already your stated intent).
- **Estimated effort:** Small (one CI dispatch + download).
- **Validation approach:** Confirm all 13(+3 new) files present, `EMPIRICAL EVIDENCE` block present, target CVE detected.
- **Rerun all scenarios required?** No, JS-09 only.
- **Classification:** Engineering/evidence-completion (doesn't change what's being evaluated).
- **Recommendation:** **Implement before freeze**, with the pipeline-version footnote disclosed.

---

## 4. LLM confidence score

- **Can it be implemented?** Yes, technically — ask Gemini to emit a confidence value alongside its fix.
- **Scientific impact:** Would enable a genuinely new analysis (confidence vs. success correlation) — but that analysis doesn't exist in the current 18-scenario dataset.
- **Methodology impact:** **High.** Changes the prompt template and expected response schema — directly alters what the LLM is asked to produce (AGENTS.md rule 4's "unbiased reasoning" contract). Any rerun under this change would not be comparable to the original 18.
- **Evidence impact:** To apply to the actual evaluated data would require a full 18-scenario rerun; without a rerun, it's a capability that was never exercised.
- **Estimated effort:** Medium (prompt change + response parsing + metrics field).
- **Validation approach:** N/A until a decision is made to rerun.
- **Rerun all scenarios required?** Yes, if it's to apply to the actual results.
- **Classification:** **Research Enhancement** (changes what the LLM produces).
- **Recommendation:** **Future Work.**

---

## 5. Improved prompt engineering

- **Can it be implemented?** Yes, trivially in terms of code (edit `context_builder.py`).
- **Scientific impact:** Could plausibly improve remediation quality — but that's exactly why it's off-limits pre-freeze: it's a hypothesis about improving the independent variable, not a bug fix.
- **Methodology impact:** **High** — this *is* the methodology (what information/instructions the LLM receives).
- **Evidence impact:** Full rerun required to apply to evaluated results.
- **Estimated effort:** Medium-high (prompt redesign + re-validation of all 18 scenarios' outputs against a new baseline).
- **Rerun all scenarios required?** Yes.
- **Classification:** **Research Enhancement.**
- **Recommendation:** **Future Work.**

---

## 6. Improved retry prompt using failure logs

- **Can it be implemented?** Yes — extend the retry prompt to include the actual build/test failure output.
- **Scientific impact:** Changes what information the LLM has access to on its second attempt — directly relevant to AGENTS.md rule 5 (strict one-retry policy) and rule 4 (unbiased reasoning); giving the LLM diagnostic feedback it didn't have in the original 18 scenarios changes the retry mechanism's design, not just its instrumentation.
- **Methodology impact:** **High.**
- **Evidence impact:** Full rerun required for any scenario that used a retry to be comparable.
- **Estimated effort:** Medium.
- **Rerun all scenarios required?** Yes (at minimum, all scenarios that underwent a retry).
- **Classification:** **Research Enhancement** — confirmed, matches your own conclusion.
- **Recommendation:** **Future Work.**

---

## 7. Raw LLM response preservation (cross-check against Group A)

- **Confirmed correctly placed in Group A.** `llm-response-full.json` was already being written by `llm_reasoner.py` (unused/discarded, never gathered into the evidence artifact) — capturing it doesn't change what the LLM is asked, what it returns, or how its response is parsed for the experiment. Purely an audit-trail capture of data that already existed. **Engineering Enhancement, no rerun required, correctly implemented pre-freeze.**

---

## 8. Dependency graph / provenance enhancements (cross-check against Group A)

- **Confirmed correctly placed in Group A.** `npm list --depth=0` was already being run (output discarded); `pip list --format=freeze` and Grype DB metadata (`grype version -o json`, `grype db status -o json`) are informational captures that don't alter scan behavior, package resolution, or LLM interaction. **Engineering Enhancement, no rerun required, correctly implemented pre-freeze.**

---

## Summary table

| # | Item | Classification | Recommendation |
|---|---|---|---|
| 1 | Provenance fix (9 hashes) | Engineering | Implement before freeze (with caveat disclosed) |
| 2 | Retry build validation | Engineering | Implement before freeze |
| 3 | JS-09 rerun | Engineering/completion | Implement before freeze (with footnote) |
| 4 | Confidence score | **Research** | Future Work |
| 5 | Improved prompt engineering | **Research** | Future Work |
| 6 | Improved retry prompt (failure logs) | **Research** | Future Work |
| 7 | Raw LLM response preservation | Engineering | Already implemented (Group A) |
| 8 | Dependency graph / DB metadata | Engineering | Already implemented (Group A) |
