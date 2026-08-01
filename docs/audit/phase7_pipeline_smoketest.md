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

## Verdict (superseded by the update below — kept for the audit trail)

Pipeline infrastructure: **validated, working correctly** post-fix. One structural gap in retry-path build validation: **newly discovered, documented, not modified** — flagged for your review.

---

## UPDATE: root cause corrected, and a much larger regression found — both now RESOLVED before freeze

The diagnosis above (build validation "structurally weaker" on retry, attributed to `tsc`/`postinstall` swallowing) was **partially wrong**. A full line-by-line reconstruction of the JS-01 run's actual log output — not just step conclusions — showed the real trigger for Attempt 1's failure was `validator.py` correctly detecting `GHSA-whpj-8f3w-67p5 is still present` (the override was applied but a stale vulnerable copy survived an incremental `npm install`). The `tsc` error is real but never gates success in either attempt.

### The actual, much larger root cause

Tracing every write to `build_success` across the whole codebase (not just the retry path) found: commit `0cb56095` ("fix: resolve all academic review critical and major issues") removed an implicit `metrics["build_success"] = True # Build implicitly succeeded if we reached here` from `validator.py` — correctly, since it was masking genuine build failures (e.g. JS-03's fatal `npm error EINVALIDTAGNAME` historically recorded as `build_success: true`). **But no replacement was ever added anywhere in the workflow.** This left `build_success` permanently stuck at its initial `false` default for *every* scenario from that commit forward, confirmed directly: a fresh `AF-01` run with `retry_count: 0` (no retry at all) still showed `build_success: false`.

This is not retry-specific — it affects every future run of `generic-remediation.yml`, first-attempt or retried.

### Full metrics.json field audit (every field, not just build_success/test_success)

| Field | Disposition |
|---|---|
| `application`, `ecosystem`, `candidate_count`, `selected_package`, `selected_cve`, `api_cve_id`, `severity`, `cvss`, `epss`, `epss_timestamp`, `kev_status`, `dependency_type` | Correctly static/invariant across attempts |
| `strategy`, `remediation_type`, `llm_response_valid`, `retry_count`, `llm_iteration` | Correctly recomputed by `retry_remediation.py` each attempt |
| `dependency_verified`, `rescan_success` | Correctly written by `validator.py` on both branches |
| `failure_stage` | Correctly recomputed across the full lifecycle (fixed in an earlier pass) |
| `build_success` | **Fixed — see below** |
| `test_success` | **Fixed — see below** |
| `validation_stage_reached` | Minor related gap: `validator.py`'s failure branch never set this (only success did) — fixed with a symmetric write |
| `lockfile_regenerated` | Correctly conditional — gated on a *different* recovery path ("Apply Fix & Verify" failing) than the LLM retry path. Not stale, just path-dependent; documented, not changed |
| `runtime_success` | Never set anywhere — no runtime-check stage exists in this pipeline at all. Changed from misleading `false` to `null` (not applicable) |
| `execution_time_seconds` | Measures only Attempt 1's orchestration phase, never extended across a retry — understates total duration when a retry occurs. Not cited anywhere in thesis statistics (checked via `grep`). Documented as a known limitation; left unchanged (doesn't claim pass/fail, and changing its meaning is a larger change than this fix's scope) |

### The fix (commit `f856b891`)

Constraints followed: `validator.py` remains responsible only for vulnerability verification, not build status (no implicit restoration); build success is now set explicitly by the workflow at the point the build genuinely succeeded; no Option-B-style build-failure policy change (existing pass/fail semantics for the retry's install untouched — it still isn't fatal, exactly as before).

- **`generic-remediation.yml` "Apply Fix & Verify"**: writes `build_success = true` immediately after the install completes. Safe because `set -o pipefail` (added in an earlier pass) means a genuine install failure already halts this step via `|| exit 1` before this line is reached.
- **`generic-remediation.yml` "Retry Remediation Strategy"**: this step's own install has no such pipefail gating (unchanged — install failures here are intentionally not fatal). Captured the install's real exit code via `${PIPESTATUS[0]}` instead, so `build_success` reflects the retry's actual outcome without changing whether the step continues afterward. Also records `test_success = null` (not executed) instead of a misleading stale `false`, since no test suite ever runs on the retry path.
- **`validator.py`**: added the same `validation_stage_reached = "validator"` write to the failure branch, symmetric with the existing success-branch write.
- **`generic_remediation.py`**: `runtime_success` now initializes to `null` instead of `False`.
- **`rebuild_manifests.py`**: `v()` helper now serializes `None` as JSON `null` (previously would have emitted the invalid literal `None` if ever run against new-format metrics).

### New metric state: `null` = "not applicable / not executed"

Two fields can now be JSON `null` rather than only `true`/`false`:
- **`test_success: null`** — the retry path never executes a test suite; `null` means "not executed," distinct from `false` ("executed and failed"). Only ever `null` for a scenario's retry attempt; a first attempt still reports a real boolean.
- **`runtime_success: null`** — always `null` for every scenario, since no runtime-check stage exists anywhere in this pipeline yet. Not scenario-dependent.

Any downstream analysis of these two fields (e.g. an aggregate "N% of builds pass" statistic) must treat `null` as its own category, not silently coerce it to `false`.

### Validation evidence (three fresh CI runs + one isolated logic test)

| Scenario | Path | `build_success` (post-fix) | `test_success` (post-fix) |
|---|---|---|---|
| AF-01 (run `30722390034`) | First attempt, clean success, `retry_count: 0` | `true` | `false` (tests genuinely ran, real boolean) |
| JS-01 (run `30722392269`) | Retry succeeded, `retry_count: 1` | `true` | `null` |
| JS-03 (run `30722394340`) | Retry succeeded, `retry_count: 1` | `true` | `null` |
| Isolated bash logic test | Simulated failing install (`PIPESTATUS` = 1) | `false` (verified directly, since none of the 3 live dispatches happened to hit a genuine install failure) | `null` |

**Remediation/validator behavior confirmed unchanged**: comparing JS-01 pre-fix (original smoke test, run `30719624009`) against post-fix (run `30722392269`) — identical `strategy` (`transitive_override`), identical `dependency_verified`/`rescan_success` (both `true`), identical `validation_stage_reached` (`"validator"`). Only `build_success` (`false` → `true`) and `test_success` (`false` → `null`) changed, exactly as intended.

**Historical evidence confirmed untouched**: `git status --short results/execution_evidence/` is empty; the last commit touching that directory predates this entire audit.

## Final verdict

Both the originally-suspected retry-path gap and the much larger universal `build_success` regression it led to are **resolved before freeze**, verified with real CI runs plus a targeted local logic test for the one branch (genuine failure) that didn't occur naturally across the three dispatches. Classification: **Engineering Enhancement** — methodology unchanged, no historical evidence invalidated, no thesis statistic affected (checked directly, not assumed).
