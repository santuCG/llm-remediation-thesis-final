# `metrics.json` Field Ownership Audit

**Purpose.** Completeness check requested as part of Pipeline v2.0 Phase 4: for every field in
a scenario's `metrics.json`, identify (1) every code location that writes it, (2) whether those
writers are mutually exclusive (safe) or can race/overwrite unintentionally (a defect), and (3)
every downstream reader that treats the field as ground truth. This is an audit, not a new fix —
its job is to confirm the Phase 1 defect-register work (Fixes #1–#10) actually closed every
field, not just the ones already suspected, and to surface anything it missed.

Traced directly against `scripts/remediation/generic_remediation.py`,
`scripts/remediation/retry_remediation.py`, `scripts/remediation/validator.py`,
`.github/workflows/generic-remediation.yml`, and `scripts/validate_consistency.py` — not
inferred from field names.

## Writer/reader table

| Field | Writer(s) | Sites | Reader(s) | Notes |
|---|---|---|---|---|
| `application`, `ecosystem` | `generic_remediation.py` skeleton write | 1 | `generate_manifest.py`, thesis docs | Written once, never mutated. Single owner. |
| `candidate_count` | `generic_remediation.py` (`len(all_candidates)`, sourced from `prioritize.py`'s return) | 1 | Thesis docs (Fix #10 regression check used this field directly) | Single write site; semantic source is `prioritize.py`'s candidate pool. |
| `selected_package`, `selected_cve`, `api_cve_id`, `severity`, `cvss`, `epss`, `epss_timestamp`, `kev_status` | `generic_remediation.py` skeleton write, from `prioritize.py`'s `candidate` dict | 1 | `validate_consistency.py`, thesis docs | Single owner. |
| `dependency_type` | `generic_remediation.py`, via `_get_dependency_type()` | 1 | Thesis docs, case studies | Single owner code-wise, but see **Related Finding** below — the *computation* this owner performs disagrees with the preregistration's `is_direct_dependency` field for 6/9 JS scenarios. Single-writer does not imply single-source-of-truth across the whole project. |
| `strategy`, `remediation_type`, `llm_response_valid` | `generic_remediation.py` (attempt 1) **and** `retry_remediation.py` (retry) | 2, mutually exclusive by attempt | `validate_consistency.py`, thesis docs | By design: retry overwrites with "latest attempt" semantics; attempt-1 values are separately preserved as `*-attempt1.json` (Fix #9), so no information is lost despite the overwrite. |
| `build_success` | `.github/workflows/generic-remediation.yml`, inline `jq`, at the build-check step for: attempt 1 success, attempt 1 failure, apply-fix failure, retry success, retry failure | 5, mutually exclusive by branch | `retry_remediation.py` (decides retry context wording), `validate_consistency.py` | Traced all 5 call sites — confirmed mutually exclusive (each guarded by a distinct `if`/`else` branch, never two in the same run). This is the field Fix #1 and Fix #6 both touched; both fixes verified live. No new defect found. |
| `test_success` | Same workflow file, `jq`, at: attempt 1 pass, attempt 1 fail, retry (always `null` — tests never run on retry, by design, confirmed in a prior session) | 3, mutually exclusive | `validate_consistency.py` | Same pattern as `build_success`. No new defect found. |
| `dependency_verified` | `validator.py`, `verify_dependency_installed()` | 1 (called once per attempt — attempt 1 and retry both invoke the same function) | Thesis docs | Single logical owner (Fix #2's independent check). No new defect found. |
| `rescan_success` | `validator.py`, `if`/`else` on rescan result | 1 function, 2 mutually exclusive branches | `validate_consistency.py`, thesis docs (primary success signal per `THESIS_DRAFT_V3.md` §3.5) | Single owner. No new defect found. |
| `runtime_success` | `generic_remediation.py` skeleton write only | 1 (always `None`) | None found | **Flag, not a defect**: no runtime-check stage exists anywhere in the pipeline, so this field is permanently `null` across all 18 scenarios. The code comment at the write site is explicit about this being intentional ("null … rather than False, which would misleadingly imply a check ran and failed"). Documented here so it isn't later mistaken for missing data — it is a genuinely unimplemented, disclosed pipeline stage, not a bug. |
| `lockfile_regenerated` | `generic_remediation.py` (init `false`) + workflow `sed`, only inside the "Fallback Lockfile Regeneration" step | 2, conditional | Thesis docs | Single conditional owner. No new defect found. |
| `execution_time_seconds` | `generic_remediation.py` skeleton write, `int(time.time() - start_time)` | 1, computed once | Thesis docs (implicitly, if execution time is ever reported) | **New finding, see below.** |
| `retry_count`, `llm_iteration` | `generic_remediation.py` (init `0`/`1`) + `retry_remediation.py` (set `1`/`2` on retry) | 2, by design (monotonic 0→1 / 1→2 transition) | `validate_consistency.py`, thesis docs | Same pattern as `strategy`/`remediation_type`. No new defect found. |
| `validation_stage_reached`, `failure_stage` | `generic_remediation.py` (init) + workflow `jq` (build/apply_fix failure) + `retry_remediation.py` (llm parsing) + `validator.py` (validator failure) | 4 files, each writing its own stage name | Thesis docs, `REGENERATION_LOG.md` throughout this session | By design — a state-machine field where each pipeline stage records its own name on the way through or on failure. Multiple writers is the correct pattern here, not a defect; confirmed no two stages write conflicting values for the same run (each is reached only if the prior stage succeeded). |

## New finding: `execution_time_seconds` does not measure what its name implies

`execution_time_seconds` is computed exactly once, in `generic_remediation.py`, at the moment the
initial `metrics.json` skeleton is written — which is **before** the build step, the test step,
`validator.py`'s rescan, and any retry ever run. It is never updated afterward, including through
a retry that adds a second full LLM call, a second `npm install`/`pip install`, and a second
build+validate cycle.

**Concretely**: for a scenario that retries (9 of 9 npm scenarios, historically), the recorded
`execution_time_seconds` reflects only the time from pipeline start through the LLM's first
response and `apply_remediation()` — a small fraction of the scenario's true end-to-end wall-clock
time. For a first-attempt success (typical of the pip scenarios), the field is closer to accurate
but still excludes the build/test/rescan time that follows it.

**Not fixed, only documented**, consistent with this audit's scope (completeness check, not a new
fix) and the project's established disclose-rather-than-silently-patch pattern. If per-scenario
wall-clock time is ever reported in the thesis, it should either be sourced from the GitHub Actions
run's own duration (`gh run view --json ... .createdAt/.updatedAt`, or per-job timestamps) rather
than this field, or this field's name/meaning should be corrected and clearly scoped ("orchestration
setup time," not "execution time") before being cited as a metric.

## Scope correction: this audit did not cover the deterministic baseline workflow

**Found during final thesis review, not during the original Phase 4 pass.** The file list above
(`generic_remediation.py`, `retry_remediation.py`, `validator.py`, `generic-remediation.yml`,
`validate_consistency.py`) is the LLM-pipeline arm only. `.github/workflows/grype-baseline.yml` —
the deterministic-baseline arm, whose evidence populates `results/reproducibility_verification/`
and Table 5/6 of `THESIS_DRAFT_V3.md` — was never examined by this audit, despite writing a
`metrics.json` with several identically-named fields. The "24 have a single, unambiguous owner"
conclusion below describes only the LLM-pipeline arm; it does not extend to the baseline.

Traced directly against `grype-baseline.yml` (all versions from `30843e65`, the commit that
produced the currently-archived baseline evidence, through the current `HEAD`) and
`scripts/remediation/validator.py`'s 3-argument invocation path:

| Field | Writer | Behavior |
|---|---|---|
| `build_success`, `test_success`, `validation_success` | `grype-baseline.yml` "Initialize Metrics" step | Set to `true` in the workflow's metrics-initialisation step; set to `false` only by the "Update Metrics on Build/Apply-Fix Failure" handlers. In the LLM-pipeline arm, `build_success` is initialised `false` in `generic_remediation.py` and set `true` only on an affirmative success step. Same field name, different initial value and different update condition in each workflow. |
| `dependency_verified` (baseline, pip records only) | 3-argument `validator.py` invocation (`grype-baseline.yml:145` at commit `30843e65`) | Set in the same code branch as `rescan_success`. In the LLM-pipeline arm, `dependency_verified` is set by a separate function, `verify_dependency_installed()` (added in Fix #2), called with additional arguments not passed in the baseline arm's invocation. |
| `vulnerability_removed` | `grype-baseline.yml` "Initialize Metrics" step | Set to `false` in the workflow's metrics-initialisation step. No subsequent assignment to this field occurs within the baseline workflow, at the commit that produced the archived baseline evidence (`30843e65`) or at the current commit (`grep -c vulnerability_removed scripts/remediation/validator.py` returns 0 at both). Every baseline record therefore has this field set to `false`. For the 9 pip records, `rescan_success` in the same file is `true`; target-CVE presence in `baseline-grype.json` vs. `rescan.json` was checked directly for these 9 records (`THESIS_DRAFT_V3.md` §3.5, §4.2). |

**No code has been changed as a result of this section**, consistent with the repository being
treated as frozen pending Round-2 review. This section documents the baseline workflow's existing
field behaviour; it does not report a code change.

## Summary

Of 26 tracked fields in the **LLM-pipeline arm**, 24 have a single, unambiguous owner (or a small
number of writers that are provably mutually exclusive by branch or represent an intentional,
monotonic state transition). No race conditions, silent overwrites, or dual-ownership conflicts
were found in that arm beyond what Fixes #1–#10 already closed. One field (`runtime_success`) is a
disclosed no-op by design. One field (`execution_time_seconds`) has a real semantic gap — it
measures a smaller window than its name implies — newly surfaced by this audit and documented
above rather than silently corrected. **The deterministic-baseline arm was out of this audit's
original scope and is covered separately above; `vulnerability_removed` in that arm is initialised
but not subsequently updated, and two other fields have different initial values or update
conditions than their same-named counterparts
in the LLM-pipeline arm.**
