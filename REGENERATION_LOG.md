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

## Batch 5 (interrupted): AF-06, JS-06 — silent CVE substitution discovered

Before this batch was dispatched, the user cross-checked the *preregistered* AF-06/JS-06 CVEs
(CVE-2024-56326/jinja2, CVE-2026-33228/flatted) directly against NVD/GitHub and noticed both still
carry high CVSS scores there — inconsistent with what the pipeline had been about to produce. This
triggered investigation rather than a normal regeneration; see `docs/FINDING_CVE_DETECTION_GAPS.md`
and `CHANGELOG_V2.md`'s Fix #10 entry for the full root-cause writeup. Summary: `prioritize.py`'s
severity filter ran before `TARGET_CVE` matching, so a preregistered target with the "wrong" reported
severity (AF-06) or absent from the SBOM entirely (JS-06) was invisible to the matching loop, and the
code silently substituted `candidates[0]` — a different CVE — with no warning. Confirmed via historical
`execution_evidence` that this substitution predates this session (present in the *original* dataset).

Fixed in `prioritize.py` (commit `a7606850`, regression-fixed in `36cc51fd`): `TARGET_CVE` is now
authoritative — matched against the full structurally-valid pool (severity filter bypassed for this
lookup only), and a not-found target fails the run loudly instead of substituting silently. Both
scenarios re-dispatched under the fix:

### AF-06 — CVE-2024-56326 (jinja2)
First re-run (commit `a7606850`, pre-regression-fix): succeeded — `selected_package: jinja2,
api_cve_id: CVE-2024-56326, severity: medium` (correctly bypassing the severity filter), full clean
result (`build_success`/`test_success`/`dependency_verified`/`rescan_success` all `true`) — but
`candidate_count: 1`, the regression described in Fix #10. **Superseded** by a second re-run under
`36cc51fd`: run [30942956346](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30942956346)
— success, first attempt, no retry:

```json
{
  "selected_package": "jinja2", "selected_cve": "GHSA-q2x7-8rv6-6q7h", "api_cve_id": "CVE-2024-56326",
  "severity": "medium", "cvss": 7.8, "candidate_count": 66, "dependency_type": "direct",
  "strategy": "direct_upgrade", "remediation_type": "Direct Upgrade",
  "llm_response_valid": true, "build_success": true, "test_success": true,
  "dependency_verified": true, "rescan_success": true, "retry_count": 0, "failure_stage": "none"
}
```

`candidate_count: 66` confirms the regression fix works in real evidence (in line with other
AF scenarios' ~60-130 range, not collapsed to 1). `severity: medium` with the target still
correctly selected confirms the severity-bypass path works end-to-end, not just in the local
test harness. This is the evidence of record for AF-06 going forward; the first (pre-regression-fix)
re-run is superseded and not used.

### JS-06 — CVE-2026-33228 (flatted)
Re-run under `a7606850`: **failed as designed**, confirmed for precisely the intended reason (log
excerpt, not paraphrased):

```
[PRIORITIZE] TARGET_CVE=CVE-2026-33228 is set: performing an authoritative lookup against all 245
structurally-valid candidates (severity filter not applied to this lookup).
[ERROR] TARGET_CVE=CVE-2026-33228 was not found among any structurally-valid candidate (fix exists,
ecosystem=npm) in this scan.
[ERROR] Structurally-valid CVE/GHSA IDs that WERE available: [140+ CVE/GHSA IDs listed, confirmed
NOT including CVE-2026-33228, but including CVE-2021-23337 — lodash's previously wrongly-substituted
CVE, confirming lodash remains a valid candidate but is no longer silently chosen]
[ERROR] Refusing to silently substitute a different vulnerability. Failing.
##[error]Process completed with exit code 1.
```

This is the correct, expected outcome: `flatted` is genuinely absent from Syft's generated SBOM (root
cause under separate investigation, `docs/FINDING_CVE_DETECTION_GAPS.md`), so no structurally-valid
candidate can ever match `CVE-2026-33228` until that SBOM-cataloging gap is independently resolved.
The fix's job — refusing to substitute a different CVE in its place — worked exactly as intended.
**Decision (approved): JS-06 is documented as a confirmed, investigated detection gap** — no valid
remediation evidence exists for this scenario and none will be forced; see `docs/FINDING_CVE_DETECTION_GAPS.md`
and Phase 2 completion below.

## Batch 5: AF-07, JS-07

### AF-07 — CVE-2024-21272 (mysql-connector-python)
Run: [30943518765](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30943518765) — success, first attempt, no retry.

```json
{
  "selected_package": "mysql-connector-python", "api_cve_id": "CVE-2024-21272", "candidate_count": 65,
  "strategy": "direct_upgrade", "remediation_type": "Direct Upgrade",
  "llm_response_valid": true, "build_success": true, "test_success": true,
  "dependency_verified": true, "rescan_success": true, "retry_count": 0, "failure_stage": "none"
}
```
Clean. Correct CVE selected (matches preregistration), `candidate_count: 65` consistent with other AF
scenarios' historical range — further confirms Fix #10's regression fix generalizes beyond AF-06.

### JS-07 — CVE-2024-37890 (ws) — genuine, structurally-explained remediation failure
Run: [30943524500](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30943524500) — job `failure`, and unlike JS-03/04/05, **remediation genuinely did not succeed** (not just the usual masked build quirk).

```json
{
  "selected_package": "ws", "api_cve_id": "CVE-2024-37890", "candidate_count": 139, "severity": "high",
  "dependency_type": "transitive", "strategy": "transitive_override", "remediation_type": "Transitive Override",
  "llm_response_valid": true, "build_success": false, "test_success": null,
  "dependency_verified": false, "rescan_success": false, "retry_count": 1, "failure_stage": "validator"
}
```

Correct CVE selected (no drift — `CVE-2024-37890` matches preregistration exactly), so this is not an
AF-06/JS-06-class substitution issue. The `build_success: false` **is** the known pre-existing `TS1005`
issue (confirmed identical error lines in `build.log`; `test.log` shows the full `193 passing, 2
pending` suite ran regardless, matching JS-03/04/05's pattern) — but `dependency_verified: false` and
`rescan_success: false` are new and real: `rescan.json` shows `ws@7.4.6` still present with
`GHSA-3h5v-q93c-6h6q` unfixed after **both** the first attempt (override to `^7.5.10`) and the retry
(override to `7.5.13`).

**Root-caused, not just observed** (full writeup: `CHANGELOG_V2.md`, "Finding: `manifest_editor.py`
only patches the root `package.json`"): Juice Shop is a two-tree monorepo — root `npm install` and a
`postinstall`-triggered, fully independent `cd frontend && npm install --legacy-peer-deps`.
`manifest_editor.py` only ever writes the root `package.json`. Confirmed `frontend/package-lock.json`
carries its own independent `ws@7.4.6` (via `engine.io-client`) with no `overrides` mechanism reaching
it from the root manifest — so neither attempt's override could ever have cleaned the frontend copy,
and the retry was mechanically guaranteed to fail the same way attempt 1 did. Confirmed this is not a
universal problem: JS-03/04/05's target packages (`form-data`, `crypto-js`, `jsonwebtoken`) are absent
from `frontend/package-lock.json` entirely, which is exactly why those root-only overrides worked
cleanly. JS-07 is simply the first regenerated scenario whose vulnerable package also happens to be
frontend-reachable.

**Decision: documented as a confirmed remediation-completeness gap, not fixed or re-attempted.**
Retrying further would not help — the failure is deterministic given the current root-only
`manifest_editor.py`, not transient. Matches the same disclose-rather-than-silently-patch approach
applied to JS-06. No pipeline code changed as a result of this finding.

## Batch 6: AF-08, JS-08

### AF-08 — CVE-2026-2473 (google-cloud-aiplatform)
Run: [30945587353](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30945587353) — success, first attempt, no retry.

```json
{
  "selected_package": "google-cloud-aiplatform", "api_cve_id": "CVE-2026-2473", "candidate_count": 65,
  "strategy": "direct_upgrade", "remediation_type": "Direct Upgrade",
  "llm_response_valid": true, "build_success": true, "test_success": true,
  "dependency_verified": true, "rescan_success": true, "retry_count": 0, "failure_stage": "none"
}
```
Clean. Correct CVE selected, `candidate_count` consistent with other AF scenarios' range.

### JS-08 — CVE-2024-45590 (body-parser) — discovered Fix #11
Run: [30945593368](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30945593368) — job `failure`.

```json
{
  "selected_package": "body-parser", "api_cve_id": "CVE-2024-45590", "candidate_count": 139,
  "strategy": "direct_upgrade", "remediation_type": "Direct Upgrade",
  "llm_response_valid": true, "build_success": false, "test_success": null,
  "dependency_verified": false, "rescan_success": true, "retry_count": 1, "failure_stage": "none"
}
```

Correct CVE selected — not an AF-06/JS-06/JS-07-class problem. `build_success: false` is the same
known, unrelated, pre-existing `TS1005` build issue as JS-02–05/07 (confirmed via `build.log`).
`rescan_success: true` confirms the vulnerability is genuinely gone. But `dependency_verified:
false` alongside `rescan_success: true` is a new, previously-unseen combination — these two
signals are supposed to be independent but normally agree. **Root-caused, not just observed** (see
`CHANGELOG_V2.md` Fix #11): `manifest_editor.py` wrote the LLM's own recommended constraint
(`^1.20.3`) correctly, `npm install` legitimately resolved it to `1.20.6` (confirmed in
`dependency-graph.log`) — safe, newer than the fix, but not string-identical to the LLM's specific
`recommended_package_version` of `1.20.3`, which `validator.py`'s exact-equality check flagged as
"unverified" despite being correct. Fixed `verify_dependency_installed()` to accept installed ≥
recommended (proper version comparison, not string equality), applied to both npm and Python
branches, verified with a 9-case local test (commit `3ec871f9`). **Superseded** by a second
re-run under the fix — see below.

### JS-08 (re-run under Fix #11) — second attempt also revealed a Fix #11 follow-up bug
Run: [30946746060](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30946746060) —
still `dependency_verified: false`. Root-caused immediately (not left unresolved): the retry's
`recommended_package_version` was `"^1.20.3"` (range-prefixed), not the bare `"1.20.3"` attempt 1
used — `_version_tuple()`'s naive `.`/`-`/`+` split parsed `^1` as a string, not the int `1`,
tripping the type-mismatch guard. Fixed (`CHANGELOG_V2.md` Fix #11 follow-up, commit `febf62e0`):
strip a leading `^`/`~`/`>=`/`<=`/`>`/`<`/`=`/`v` before parsing. Verified with 5 additional cases
covering exactly this shape. **Third dispatch, under the fully-fixed validator:**

Run: [30948318473](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30948318473) — job `failure` (same known, unrelated `TS1005` build issue as JS-01/03/04/05/07/09), but the actual signals are clean:

```json
{
  "selected_package": "body-parser", "api_cve_id": "CVE-2024-45590", "candidate_count": 139,
  "dependency_verified": true, "rescan_success": true, "retry_count": 1, "failure_stage": "none"
}
```
`dependency_verified: true` this time — confirms the Fix #11 follow-up actually resolved it, not
just in the local test harness. This is the evidence of record for JS-08.

## Batch 7: AF-09, JS-09

### AF-09 — CVE-2024-34069 (werkzeug)
First dispatch, run [30946772227](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30946772227) — failed with `llm_response_valid: false`, `failure_stage: "llm_parsing"`. A genuine Gemini API-layer failure (same class as JS-02 batch 1's mixed 429/503/404 pattern), not a pipeline logic bug; handled gracefully by Fix #8 (metrics.json written correctly, no evidence lost). Re-dispatched.

Run: [30948331316](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30948331316) — success, first attempt, no retry:
```json
{
  "selected_package": "werkzeug", "api_cve_id": "CVE-2024-34069", "candidate_count": 65,
  "strategy": "direct_upgrade", "llm_response_valid": true, "build_success": true,
  "test_success": true, "dependency_verified": true, "rescan_success": true, "retry_count": 0
}
```
Genuinely preregistered as `werkzeug`/`CVE-2024-34069` — not a substitution artifact; this is
AF-09's real, original target, which happens to share the same CVE that AF-06 was wrongly
executing before Fix #10 (already disclosed pre-session in `preregistration/PRE_REGISTRATION_AMENDMENT.md`
and `THESIS_DRAFT_V3.md` Table 1's footnote).

### JS-09 — CVE-2026-3520 (multer)
Run: [30948325107](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30948325107) — job `failure` (known unrelated `TS1005` issue), signals clean:
```json
{
  "selected_package": "multer", "api_cve_id": "CVE-2026-3520", "candidate_count": 139,
  "dependency_verified": true, "rescan_success": true, "retry_count": 1, "failure_stage": "none"
}
```

## Batch 8: AF-01, JS-01 refresh — bringing the smoke-test scenarios to the same final pipeline state

AF-01/JS-01's committed evidence predated Fix #4 (`karma.conf.js`) and Fix #5 (`jws` null-safety),
i.e. it was from before this engagement's npm-test-blocking issues were fixed — inconsistent with
the other 16 scenarios' final, fully-fixed state. Re-dispatched both under current `HEAD` so all 18
scenarios reflect identical pipeline code.

### AF-01 — CVE-2026-8838 (redshift-connector)
Run: [30948616416](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30948616416) — success, first attempt, no retry. Clean, matches historical outcome.

### JS-01 — CVE-2023-32314 (vm2)
Run: [30948623108](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30948623108) — job `failure` (known unrelated `TS1005` issue), signals clean (`dependency_verified`/`rescan_success` both `true`). **Notable difference from the historical run**: `strategy` is now `transitive_override`, not the original `manual_review` — a real behavioral difference between prompt v1.2 and the original prompt, not a data error. `dependency_type` is now correctly `transitive` (the historical evidence's `dependency_type: "direct"` was already flagged as a defect in `docs/case_studies/JS-01_vm2_case_study.md` before this session).

## All 18 scenarios: final regeneration status

Every scenario now has evidence committed under the fully-fixed Pipeline v2.0 (`prioritize.py`
Fix #10, `validator.py` Fix #11 + follow-up, prompt v1.2). 16 of 18 produced valid remediation
evidence (clean pass, `dependency_verified`/`rescan_success` both `true`). Two did not, both for
root-caused, documented reasons rather than pipeline defects:
- **JS-06**: no remediation evidence exists — `flatted` is absent from Syft's generated SBOM
  (confirmed detection gap, `docs/FINDING_CVE_DETECTION_GAPS.md`); the pipeline correctly refused
  to substitute a different CVE.
- **JS-07**: remediation was attempted and failed — `ws`'s vulnerable copy lives in Juice Shop's
  independently-installed `frontend/` tree, which `manifest_editor.py` cannot reach (confirmed
  remediation-completeness gap, `CHANGELOG_V2.md`).

See `docs/CVE_MATCH_VERIFICATION.md` for the full 18-scenario preregistered-vs-executed CVE table.

## Reproducibility Verification

Coverage-based reproducibility check: one independent re-dispatch per distinct execution path
present in the final dataset (AF clean/first-attempt, AF severity-bypass, JS clean-with-retry,
JS negative/no-candidate, JS negative/genuine-failure), each re-run under the identical, unchanged
pipeline code and compared field-by-field against the corresponding committed evidence in
`results/execution_evidence/<ID>/metrics.json`. No workflow, prompt, or evidence-generation code
was modified for this check.

**Fields compared:** `api_cve_id`, `selected_package`, `strategy`, `remediation_type`,
`build_success`, `test_success`, `dependency_verified`, `rescan_success`, `retry_count`,
`failure_stage`.

| Scenario | Path | Repro run | Result |
|---|---|---|---|
| AF-02 | AF clean/first-attempt | [30951503294](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30951503294) | **Match** — all 10 fields identical |
| JS-03 | JS clean-with-retry | [30951515254](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30951515254) | **Match** — all 10 fields identical |
| JS-06 | JS negative/no-candidate | [30951521049](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30951521049) | **Match** — no `metrics.json` produced in either the original or the repro run (Failure Category A, by design); `candidate-ranking.json` in the repro run independently confirms 245 structurally-valid candidates with `CVE-2026-33228` absent, matching the original |
| JS-07 | JS negative/genuine-failure | [30951527616](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30951527616) | **Match** — all 10 fields identical |
| AF-06 | AF severity-bypass | *(pending — see below)* | — |

**AF-06's first dispatch attempt** (run [30951509577](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30951509577)) did not complete: `gemini-2.0-flash` returned `RESOURCE_EXHAUSTED` (free-tier per-minute input-token quota) and the fallback `gemini-1.5-flash` returned `404 Not Found` (model not available on this API version) — the same known fallback-list gap documented in Batch 1. This is a quota/availability outcome, not a reproducibility mismatch; AF-06's coverage path remains unverified pending a clean re-dispatch.
