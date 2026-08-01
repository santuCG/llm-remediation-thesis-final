# PHASE 7 — FULL PIPELINE SMOKE TEST

## Scope decision

Phase 4 already exhaustively audited all 18 scenarios' recorded evidence. Re-running the full `generic-remediation.yml` (real Gemini API calls, builds, retries) for all 18 scenarios today would mean re-executing the actual experiment, not validating it — and would consume real LLM API quota for no incremental audit value beyond what Phase 4 + Phase 5 already established. Instead: **one smoke test** (JS-01, the most already-scrutinized scenario) was dispatched to confirm the full pipeline still runs correctly end-to-end with today's two Phase 5 fixes (frontend lockfile pin, `**/bin` exclusion) in place.

## Result: pipeline infrastructure ran correctly

Run `30719624009` completed its full lifecycle without any infrastructure-level crash: checkout → environment setup → baseline install → SBOM/Grype scan → LLM candidate selection → apply fix → validate/rescan (failed, expected) → **retry triggered correctly** → LLM iteration 2 → rebuild → rescan → validator → evidence gathered → artifact uploaded. All 13 expected evidence files were produced. Today's fixes did not break anything.

## New finding, surfaced by this live run (not present in any prior static evidence read)

**The retry path's build validation is structurally weaker than the first attempt's, and this was previously invisible because it only manifests when a retry's own build has a genuine failure.**

- The **first attempt** ("Validate Remediation & Rescan" step) explicitly runs `npm run build:frontend` and `npm run build:server`, each with `|| (echo "...Failed" && exit 1)` — a real build failure here is fatal and correctly propagates to `build_success: false`.
- The **retry step** ("Retry Remediation Strategy") does not call `build:frontend`/`build:server` directly at all — it runs a plain `npm install`, which triggers Juice Shop's own `postinstall` script: `cd frontend && npm install --legacy-peer-deps && cd .. && npm run build:frontend && (npm run --silent build:server || cd .)`. Note the **`|| cd .`** — Juice Shop's own postinstall deliberately swallows a `build:server` failure. So when the same pre-existing `tsc`/`@types` incompatibility (documented in Phase 4, unrelated to today's fixes) occurs during the retry, it produces the identical `error TS1005` output in the log, but does **not** fail the step — the retry step reports `success`, and the pipeline proceeds straight to rescan/validator as if the build had been checked and passed.
- Consequence: `metrics.json`'s `build_success: false` after a retry is a **stale carry-over from the first attempt's explicit failure**, not a genuine re-check of the retry's own build. `failure_stage: "none"` (set by `retry_remediation.py` whenever `llm_response_valid` is true, regardless of what happens afterward) compounds this — neither field reflects the retry attempt's real build outcome.
- `dependency_verified: true` / `rescan_success: true` are legitimate and independent of this gap: the SBOM/Grype rescan only checks whether `vm2` is at the patched version, which it genuinely is regardless of whether the unrelated TypeScript server compiles.

This is a **methodology gap in the pipeline itself**, not a data-integrity problem in existing evidence — it means any scenario that goes through a retry has no reliable signal of whether *that specific retry's* application actually builds cleanly, only whether the dependency fix was applied and the vulnerability is gone. Given this changes what "success" means for retried scenarios, I have not modified the retry step's build-validation logic — that's a real behavior change to the experiment's success criteria, not a metrics-consistency nit, and warrants your decision rather than a unilateral fix mid-audit.

## Verdict

Pipeline infrastructure: **validated, working correctly** post-fix. One structural gap in retry-path build validation: **newly discovered, documented, not modified** — flagged for your review.
