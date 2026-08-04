# Regeneration Log — Pipeline v2.0 / Prompt v1.2

Unattended regeneration run of AF-02–AF-09 and JS-02–JS-09 (16 scenarios),
dispatched 2 at a time (one AF + one JS per batch), on branch
`pipeline-v2-phase1` under prompt v1.2. AF-01 and JS-01 were already
smoke-tested clean in the prior engineering phase and are not repeated here.

Each row is one scenario. `metrics` is the exact final `metrics.json`
summary (not paraphrased). Stops for quota exhaustion or any undocumented
failure pattern are called out explicitly, not silently absorbed.

## Batch 1: AF-02, JS-02

### AF-02 — CVE-2025-43859 (h11)
Run: [30865157364](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30865157364) — success, first attempt, no retry.

```json
{
  "selected_package": "h11", "strategy": "direct_upgrade", "remediation_type": "Direct Upgrade",
  "llm_response_valid": true, "build_success": true, "test_success": true,
  "dependency_verified": true, "rescan_success": true, "retry_count": 0, "failure_stage": "none"
}
```
Clean. No anomalies.

### JS-02 — CVE-2026-33937 (handlebars)
Run: [30865161354](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30865161354) — job failure (retry's LLM call failed).

```json
{
  "selected_package": "handlebars", "strategy": "", "remediation_type": "Transitive Override",
  "llm_response_valid": false, "build_success": false, "test_success": false,
  "dependency_verified": false, "rescan_success": false, "retry_count": 1,
  "llm_iteration": 2, "failure_stage": "build"
}
```

Attempt 1 hit the known pre-existing `TS1005` build failure (`@types/babel__traverse`/`@types/lodash`,
documented in `CHANGELOG_V2.md`'s Phase 2 finding — unrelated to this scenario's remediation choice)
and triggered a retry. **The retry's own LLM call then failed on all 4 fallback models**, each for a
different reason (confirmed from raw log text, not inferred):

| Model | Error |
|---|---|
| gemini-3.6-flash | `503 Service Unavailable` |
| gemini-2.5-flash | `404 Not Found` |
| gemini-2.0-flash | `429 Too Many Requests` |
| gemini-1.5-flash | `404 Not Found` |

**Not treated as a quota-exhaustion stop signal**: only 1 of 4 failures is an actual `429`; the two
`404`s indicate those model IDs are not available to this API key at all (a pre-existing fallback-list
configuration gap, out of scope to fix mid-run per the plan), and the `503` is a transient server-side
issue. AF-02 — dispatched moments earlier in the same batch — succeeded cleanly on the *same* primary
model (gemini-3.6-flash), which argues against sustained exhaustion. Handled gracefully by Fix #8
(`raise` instead of `sys.exit`): `metrics.json` was written correctly with `llm_response_valid: false`,
no evidence lost. Continuing to batch 2, watching for a *repeated* 429 pattern as the real stop signal.

## Batch 2: AF-03, JS-03

### AF-03 — CVE-2023-50782 (cryptography)
Run: [30866015290](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30866015290) — success, first attempt, no retry.

```json
{
  "selected_package": "cryptography", "strategy": "direct_upgrade", "remediation_type": "Direct Upgrade",
  "llm_response_valid": true, "build_success": true, "test_success": true,
  "dependency_verified": true, "rescan_success": true, "retry_count": 0, "failure_stage": "none"
}
```
Clean. No anomalies.

### JS-03 — CVE-2025-7783 (form-data)
Run: [30866019450](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30866019450) — job conclusion `failure`, but **remediation actually succeeded**.

```json
{
  "selected_package": "form-data", "strategy": "transitive_override", "remediation_type": "Transitive Override",
  "llm_response_valid": true, "build_success": false, "test_success": null,
  "dependency_verified": true, "rescan_success": true, "retry_count": 1, "failure_stage": "none"
}
```

`rescan_success: true` and `dependency_verified: true` confirm the CVE was eradicated. Attempt 1 hit
the known pre-existing `TS1005` build failure (same class as JS-02, unrelated to `form-data` or this
scenario's remediation choice) and triggered a retry; the retry's LLM call succeeded this time and the
override worked. `build_success: false` correctly reflects that the pre-existing TS1005 issue persists
regardless of remediation (it's a frontend `@types/babel__traverse`/`@types/lodash` incompatibility, not
caused by this or any other scenario's package choice). The job-level `failure` conclusion is the
already-documented, pre-existing quirk where a successful retry still reports job failure (tracked as
GitHub issue #1, not investigated further per that earlier decision). No new anomaly. Continuing to
batch 3.

## Batch 3: AF-04, JS-04

### AF-04 — CVE-2026-44307 (mako)
Run: [30866826162](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30866826162) — success, first attempt, no retry.

```json
{
  "selected_package": "mako", "strategy": "direct_upgrade", "remediation_type": "Direct Upgrade",
  "llm_response_valid": true, "build_success": true, "test_success": true,
  "dependency_verified": true, "rescan_success": true, "retry_count": 0, "failure_stage": "none"
}
```
Clean. No anomalies.

### JS-04 — CVE-2023-46233 (crypto-js)
Run: [30866830764](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30866830764) — job conclusion `failure`, remediation actually succeeded.

```json
{
  "selected_package": "crypto-js", "strategy": "transitive_override", "remediation_type": "Transitive Override",
  "llm_response_valid": true, "build_success": false, "test_success": null,
  "dependency_verified": true, "rescan_success": true, "retry_count": 1, "failure_stage": "none"
}
```
Same pattern as JS-03: `rescan_success`/`dependency_verified` both true confirm the CVE was eradicated;
retry triggered by the known pre-existing TS1005 build issue; job-level `failure` is the same
pre-existing quirk. No new anomaly. Continuing to batch 4.

## Batch 4: AF-05, JS-05

### AF-05 — CVE-2026-0994 (protobuf)
Run: [30875173695](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30875173695) — success, first attempt, no retry.

```json
{
  "selected_package": "protobuf", "strategy": "direct_upgrade", "remediation_type": "Direct Upgrade",
  "llm_response_valid": true, "build_success": true, "test_success": true,
  "dependency_verified": true, "rescan_success": true, "retry_count": 0, "failure_stage": "none"
}
```
Clean. No anomalies.

### JS-05 — CVE-2015-9235 (jsonwebtoken)
Run: [30875177735](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30875177735) — job conclusion `failure`, remediation actually succeeded.

```json
{
  "selected_package": "jsonwebtoken", "strategy": "direct_upgrade", "remediation_type": "Direct Upgrade",
  "llm_response_valid": true, "build_success": false, "test_success": null,
  "dependency_verified": true, "rescan_success": true, "retry_count": 1,
  "lockfile_regenerated": true, "failure_stage": "none"
}
```
Slightly different path than JS-03/04: `lockfile_regenerated: true` indicates the "Fallback Lockfile
Regeneration" step fired (i.e., `Apply Fix & Verify` itself failed on attempt 1, not just the later
build-check), before the retry ran and succeeded — `rescan_success`/`dependency_verified` both true
confirm the CVE was eradicated. Job-level `failure` conclusion is the same pre-existing quirk. No
undocumented anomaly. Continuing to batch 5.
