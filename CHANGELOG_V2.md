# Pipeline v2.0 Engineering Changelog

Running record of every engineering change made while moving this pipeline out of
frozen-evidence mode and into active development, per the Phase 1–6 plan. Each row
is one isolated commit. Documentation is explicitly out of scope until Phase 1 is
complete and approved.

## Phase 1 — Correctness fixes

| Change | Why | Affected scenarios | Requires rerun? | Methodology change? |
|---|---|---|---|---|
| `build_success` reflects actual compile result, not just install | `npm run build:server` ran in a step with no `set -o pipefail`, so a real `tsc` failure could never flip `build_success` back to false; the retry path never ran a compile step at all | All 9 npm scenarios (JS-01–09). Python unaffected — no separate compile phase exists there | Yes, for all 9 npm scenarios | No — bug fix, not a design change |
| Fix #1a: unify `grype-baseline.yml` onto `check_npm_build.sh` | Code review found `grype-baseline.yml` had its own separate, duplicated npm build-check implementation that bypassed the shared script entirely — same semantic-drift risk Fix #1 was meant to close. Added a `--fatal` mode to the shared script so both workflows' genuinely different designs (baseline aborts immediately on build failure and never runs tests; LLM-remediation continues to gather evidence) share one implementation instead of two | All npm scenarios in both workflows (18 remediation scenarios + `results/reproducibility_verification/` baseline runs) | No — `grype-baseline.yml`'s behavior was already correct (it already had `set -o pipefail`); this is a pure refactor. Verified via fresh dispatch: JS-01 baseline output is byte-for-byte identical to the historical evidence, AF-01 baseline unaffected | No — pure refactor, verified behavior-preserving |
| Fix #2: `dependency_verified` is an independent check | `validator.py` set `dependency_verified = true` in the exact same branch as `rescan_success`, purely because the target CVE was absent from the rescan — not an independent verification of the dependency graph despite the field name. Added `verify_dependency_installed()`: an actual `npm ls`/`pip show` check of the installed graph against the LLM's (or Grype's, for the baseline) recommended version, completely decoupled from the rescan result. Required updating all three call sites that invoke `validator.py` — `generic-remediation.yml`'s first attempt and retry, and `grype-baseline.yml` — found via the same completeness check that found Fix #1a | All 18 scenarios (both workflows use the shared `validator.py`) | Yes, for any scenario where a genuinely independent check would produce a different value than the old rescan-coupled one — not yet determined without a full rerun | No — bug fix, not a design change. `rescan_success` logic untouched |
| Fix #3: install `ng`, `sentry-sdk`, `datadog` for the test stage | Test-stage failures were CI-environment gaps, not remediation defects. Confirmed directly in a Fix #2 verification run: `sentry-sdk` actually installs fine and its own tests pass, but the suite still fails on `ModuleNotFoundError: No module named 'datadog'` (never installed anywhere); `ng` was never installed at all (globally or otherwise), so `npm test` always failed with `ng: not found` even though `npm run build:*` resolves it fine via the local `node_modules` path. Added `npm install -g @angular/cli@15.0.4` (version-matched to `applications/juice-shop/frontend/package.json`'s own `^15.0.4` pin) and added `datadog` to the pip install line in both workflows (also added `sentry-sdk` to `grype-baseline.yml`, which never had it) | All 18 scenarios | Yes, for any scenario where `test_success` was previously false purely due to a missing module | No — infrastructure fix, not a design change |
| Fix #4: restore missing upstream `karma.conf.js` | Fixing Fix #3's `ng: not found` uncovered a second, previously-masked npm-test blocker: `Error: Cannot find module '.../frontend/src/karma.conf.js'`. Traced to source and ruled out workflow, environment, Node version, Angular CLI, path resolution, and ESM/CommonJS as causes (each checked with direct evidence — see investigation notes). Root cause: `karma.conf.js` is a genuine upstream Juice Shop v15.3.0 source file (confirmed tracked in `juice-shop/juice-shop` at tag `v15.3.0` via the GitHub API), but was never committed to *this* repo because `applications/juice-shop/.gitignore:32` (`frontend/src/**/*.js`, intended to exclude compiled TS output) incidentally also matched this hand-written config, so `actions/checkout` in CI never had it. Added a targeted `!frontend/src/karma.conf.js` exception and force-added the file. **Verified**: fresh JS-01 dispatch (run `30850432630`) shows Karma launching and executing all 686 frontend tests, vs. previously failing before a single test ran | JS scenarios only (npm ecosystem, Karma test stage). AF scenarios unaffected — Python has no Karma stage | Yes, for any npm scenario whose `test_success` was previously false or unreached purely due to this blocker | No — bug fix (missing tracked file), not a design change |
| Fix #5: upstream compatibility fix for `jws.decode()` null-safety in `lib/insecurity.ts` | With Fix #4 letting `npm test` reach `test:server` for the first time, a new blocker appeared: `TSError: lib/insecurity.ts(58,51): error TS2531: Object is possibly 'null'.` **Root cause, fully traced**: `package-lock.json` pins `@types/jws@3.2.7` (non-nullable `decode()` return type), but `generic-remediation.yml`'s Apply Fix / retry steps run `npm install` (not `npm ci`, which only the initial baseline-install step uses) after patching `package.json` — this re-resolves the `^3.2.5`-ranged `@types/jws` to whatever the registry currently has, which is `3.2.11` (nullable `decode()` return type, confirmed by diffing both versions' actual `.d.ts` files from npm). `tsconfig.json`'s `strict: true` is byte-identical to upstream v15.3.0 (diffed directly) — not a changed setting. Node and TypeScript versions confirmed unchanged (`4.6.4` in both the lockfile and the run's own `dependency-graph.log`). This is a **pre-existing, latent upstream Juice Shop defect**, not something introduced by this pipeline or by the vm2 remediation: upstream hit the identical issue and fixed it in commit `992780c17c45aac1922b9d9fbf2ea61d66df8e05` ("Make property access null-safe", 2024-04-22) — five and a half months after the vendored `v15.3.0` tag (2023-11-02). Applied that exact upstream diff, verbatim (`.payload` → `?.payload`), as the reference implementation — one line changed, formatting and all surrounding code untouched. **Verified**: fresh JS-01 dispatch (run `30856810471`) shows `test:server` compiling and running to completion (`193 passing, 2 pending`), zero TypeScript errors, where it previously failed to compile at all | JS scenarios only (npm ecosystem, `test:server`/backend TypeScript compilation). AF scenarios unaffected — Python has no `tsc`/`ts-node` stage | Yes, for any npm scenario whose `test_success` was previously false or unreached purely due to this blocker | **No** — an upstream compatibility fix, not an LLM-methodology change, not a remediation-logic change. Fixes latent dependency drift caused by fresh `npm install` resolution outrunning a point-in-time vendored lockfile; does not touch `vm2`, the LLM's recommendation, or any pipeline decision logic |
| Fix #6: preserve `build.log` across retry (append, not overwrite) | Full pipeline readiness review (pre-regeneration) found `build.log` was opened via `tee` **without** `-a` at three call sites — `Apply Fix & Verify`, `Fallback Lockfile Regeneration`, and `Retry Remediation Strategy` — while `check_npm_build.sh`'s own writes correctly appended. For any scenario that retries, attempt 1's install + build-check output (including the failure that triggered the retry) was silently destroyed and replaced by only the retry's content. Fixed all three call sites (both npm and pip branches) with `tee -a`. The third call site (`Fallback Lockfile Regeneration`) was missed in the original review and caught live during verification, when a real Gemini JSON-parse failure (see Fix #8) actually exercised that step | Any of the 18 that trigger a retry (historically common for JS scenarios) | Yes, for any retrying scenario | **No** — pure evidence-completeness fix. Verified via live retry run (`30859856985`→`30861449583` series): `build_success`/`test_success` computation, LLM behavior, and remediation decisions are unaffected — confirmed identical outcomes with and without the fix, only the log's completeness changed |
| Fix #7: refresh `dependency-graph.log` on retry | Same readiness review: `dependency-graph.log` was captured once during attempt 1 and never regenerated on retry, even though the retry reinstalls a completely different dependency graph. For any retrying scenario this evidence file showed a stale, superseded graph that no longer matched what `dependency_verified`'s live `npm ls`/`pip show` check actually validated. Added the same capture call to the retry step (both ecosystems) | Any of the 18 that trigger a retry | Yes, for any retrying scenario | **No** — `dependency_verified` is computed live and independently of this file; purely restores evidence accuracy. Verified: post-fix `dependency-graph.log` correctly reflects the retry's fresh graph, cross-checked consistent with `dependency_verified`, `package-after.json`, and `experiment_manifest.json`'s artifact hashes |
| Fix #8: raise instead of `sys.exit` on LLM response failures | `llm_reasoner.py` called `sys.exit(1)` when all fallback models failed to respond, and when the response failed to parse as JSON. `SystemExit` is not an `Exception` subclass, so both calls bypassed the `except Exception` handlers in `generic_remediation.py`/`retry_remediation.py` whose purpose is to catch exactly these failures and record `llm_response_valid=False` gracefully — instead the process would die immediately, on attempt 1 specifically before `metrics.json` is ever written, turning a recoverable failure into total silent evidence loss for that scenario. Changed both call sites to `raise` (`RuntimeError`/`ValueError`) instead. Left the `GEMINI_API_KEY`-missing check as `sys.exit` — a genuine unrecoverable configuration failure, not a per-attempt condition | None historically (zero occurrences across the 18 scenarios or ~20+ runs this session) — a safety net for the regeneration's 18 fresh API calls | No rerun required for existing evidence | **No** — zero behavior change for the valid-JSON case (100% of runs to date). **Verified twice**: a controlled local simulation (mocked malformed Gemini JSON through the real code path — `metrics.json` written, `llm_response_valid: false`, `failure_stage: "llm_parsing"`, clean exit, all evidence artifacts present, simulation fully reverted) and, unexpectedly, **live** — run `30859088661`'s `Determine Remediation Strategy` step hit a real Gemini JSON-parse failure and the fix handled it exactly as designed |
| Fix #9: preserve attempt 1's LLM I/O, applied patch, and metrics before retry | Discovered while exhaustively re-checking every evidence writer for the same class of bug as Fix #6: `llm_reasoner.py`'s `get_llm_recommendation()` (writes `llm-request.json`/`llm-response.json`/`llm-response-full.json`) and `manifest_editor.py`'s `apply_remediation()` (writes `package-after.json`) are called identically on attempt 1 and retry, both in truncate mode. Confirmed on **two independent live retry runs** that attempt 1's actual LLM request/response/reasoning and applied patch are permanently unrecoverable from the archived evidence for any retrying scenario — the same defect class as Fix #6, but on the pipeline's primary research artifact. `metrics.json`'s `strategy`/`remediation_type` fields are similarly overwritten. Added a preservation step at the top of `Retry Remediation Strategy`, before `retry_remediation.py` runs: copies `llm-request.json`, `llm-response.json`, `llm-response-full.json`, `package-after.json`, and `metrics.json` to `*-attempt1.json`. Canonical (unprefixed) names keep reflecting the latest/final attempt, unchanged | Any of the 18 that trigger a retry | Yes, for any retrying scenario (to obtain the attempt-1 evidence retroactively) | **No** — pure evidence preservation via copy, no control-flow change. **Verified**: fresh JS-01 dispatch (run `30861449583`) confirms `llm-request-attempt1.json` lacks the retry marker (`llm-request.json` correctly has it), `llm-response-attempt1.json` differs in content from `llm-response.json`, and `metrics-attempt1.json` correctly shows `retry_count: 0, llm_iteration: 1` vs. the final `metrics.json`'s `retry_count: 1, llm_iteration: 2` |

**Regeneration Gate Review — CERTIFIED.** Full pipeline re-read against the categories that would compromise scientific correctness of regenerated evidence (evidence loss, incorrect metrics, incorrect provenance, corrupted LLM inputs/outputs, invalidated evidence): no remaining defects in these categories. Fixes #6–#9 above were found and closed during this review, each verified via live CI runs (and one local simulation for Fix #8) rather than by reasoning alone. Cleared to proceed with regeneration.

## Fix #5 candidate — resolved (see Fix #5 above)

**Originally observed in JS-01 verification run `30850432630` (Fix #4 verification).**
With `karma.conf.js` restored, `npm test` progressed past Karma — all 686
frontend tests executed — and then failed in `test:server` with
`TS2531: Object is possibly 'null'` in `lib/insecurity.ts`. Root-caused and
fixed; see the Fix #5 row above for the full investigation and resolution.

**Resolved sub-finding: `test_success: null` on the retry path is by design,
not a bug.** `generic-remediation.yml`'s "Retry Remediation Strategy" step has
an explicit comment: *"Tests are never executed on the retry path, so
`test_success` is recorded as null (not executed) rather than a misleading
stale false."* Confirmed by reading the step's own logic — it never invokes
`npm test`/`pytest` at all, only install + build-check + rescan. This closes
what was flagged as an open question for the metric-ownership audit; no code
change needed, it was already correct.

## New finding — Chrome Headless disconnect during Fix #5 verification, classified as non-reproducible CI flakiness

**Observed in the first Fix #5 verification run (`30853719226`).** Karma
disconnected mid-suite: `Disconnected, because no message in 30000 ms` at test
207/686, before `test:server` was ever reached — so that run could not confirm
the TS2531 fix directly. Per instruction, stopped before making any further
change and reasoned about likely cause rather than guessing: `lib/insecurity.ts`
is backend-only and compiled by `test:server`, which runs *after* Karma —
a one-line backend change cannot plausibly cause a frontend browser-process
disconnect. The immediately preceding run (`30850432630`, Fix #4 verification)
completed all 686 Karma tests with zero disconnects under otherwise-identical
conditions.

**Re-ran JS-01 once more, no code changes, purely to test reproducibility**
(run `30856810471`). Karma completed all 686 tests with no disconnect, and
`test:server` ran to completion (`193 passing, 2 pending`, zero TypeScript
errors) — confirming the Fix #5 fix. The disconnect did not recur under the
same conditions. **Classified as non-reproducible CI runner flakiness**
(headless Chrome timing out on a GitHub-hosted runner), not a deterministic
infrastructure defect. No further action taken; not treated as a root cause
requiring investigation, per the explicit reproduce-or-clear test applied.

## Audit — `npm install` vs `npm ci` across the npm pipeline, recorded, not yet actioned

Prompted by Fix #5's discovery that `npm install` (used after any manifest
patch) silently drifts every loosely-pinned dependency, not just the one being
deliberately changed. Audited all 7 occurrences across both workflows; no code
changed as a result of this audit.

| Occurrence | Why `npm install` not `ci` | Drift intended? | Reproducibility lost? | Recommendation |
|---|---|---|---|---|
| `generic-remediation.yml`/`grype-baseline.yml` frontend + root baseline install (`npm ci`, both files) | N/A — already `npm ci` | No | No | Keep as-is |
| `generic-remediation.yml:101` "Apply Fix & Verify" (after `generic_remediation.py` patches `package.json`) | Required — `npm ci` hard-fails once `package.json` no longer matches the lockfile | No — only the LLM's chosen override was meant to change | **Yes, silently** — this is the exact mechanism that produced the Fix #5 `@types/jws` drift | Keep `npm install` (no alternative both applies the patch and populates `node_modules` for the next step); disclose as a known methodology limitation rather than changing the command |
| `grype-baseline.yml:120` "Apply Grype Recommendation" (after `update_manifest.py`) | Same as above | Same — unintended side effect | Same | Same |
| `generic-remediation.yml:128` "Fallback Lockfile Regeneration" (`if: failure()`, explicit `rm -f package-lock.json && rm -rf node_modules` first) | Required — no lockfile survives the `rm` | **Yes — fully intentional**, step's own name/log message says so | Yes, by design | Keep `npm install` — working as intended |
| `generic-remediation.yml:219` Retry path (same explicit `rm` pattern) | Required, same reason | Yes — intentional, same clean-slate rationale | Yes, by design | Keep `npm install` — working as intended |
| `npm install -g @angular/cli@15.0.4` (both workflows) | Global CLI tool install, outside the project's dependency tree entirely | N/A | No — different category | Keep as-is, not a lockfile concern |

**Bottom line:** every `npm install` here is either impossible to replace with
`npm ci` (package.json just changed, or the lockfile was deliberately deleted)
or isn't a project-dependency command at all. Exactly one real, unintended
reproducibility gap exists — the manifest-patch-then-install pattern (rows 2–3)
— and no install-command change fixes it without a logic redesign (e.g. a
targeted `npm install <pkg>@<version>` instead of a blanket install), which is
out of scope here. Recorded as a disclosure item for the methodology docs.

## Planned — after Phase 1 is complete (not yet actioned)

**Single-owner-per-metric-field audit.** Once all Phase 1 fixes land, verify every
`metrics.json` field has exactly one clear owner in the code, e.g.:

| Metric | Source |
|---|---|
| `build_success` | build validation (`check_npm_build.sh` / install step) |
| `dependency_verified` | independent dependency graph check (`validator.py`) |
| `rescan_success` | validator/rescan (`validator.py`) |
| `test_success` | test runner (workflow `TEST_EXIT` check) |
| `failure_stage` | workflow control logic |

This is a completeness check, not a new fix — its purpose is to confirm the Phase 1
defect register work actually closed every field, not just the ones that were
already suspected.

**Phase 5 regeneration sequencing.** Do not regenerate all 18 scenarios in one
batch. First regenerate AF-01 and JS-01 only as smoke tests (one npm, one Python)
and confirm they behave correctly end-to-end. Only after that passes, regenerate
the remaining scenarios one at a time (not in parallel), given each is a real
Gemini API call — this minimizes the chance of discovering a pipeline regression
after already spending hours rerunning every scenario.

## Fix #11: `verify_dependency_installed()` used exact version equality, producing false-negative `dependency_verified`

**Discovered during JS-08 regeneration** (`body-parser`/`CVE-2024-45590`, run `30945593368`).
`rescan_success: true` (Grype independently confirms the vulnerability is gone) but
`dependency_verified: false` — an unusual combination, since these two fields are supposed to be
independent signals that normally agree.

**Root cause.** `validator.py`'s `verify_dependency_installed()` (`_npm_tree_contains_version`
for npm, the `pip show` branch for Python) compared the installed version to the LLM's
`recommended_package_version` using exact string equality. The LLM recommended `1.20.3`;
`manifest_editor.py` wrote a caret-range constraint (`^1.20.3`), correctly reflecting the LLM's
own `manifest_patch.constraint`; `npm install` then legitimately resolved that range to the
newest compatible release, `1.20.6` (confirmed in `dependency-graph.log`) — safe, and newer than
the fix version, but not string-identical to `"1.20.3"`, so the exact-match check reported
"unverified" despite the dependency graph being correct.

**Fix.** Added `_version_at_least(installed, expected)`: parses both strings into comparable
tuples (splitting on `.`/`-`/`+`) and accepts the installed version if it is equal to or newer
than the recommended fix version, falling back to exact-match behavior only when a component
can't be meaningfully ordered (e.g. comparing an int position to a non-numeric one). Applied to
both the npm (`_npm_tree_contains_version`) and Python (`pip show`) branches — the Python branch
had the identical exact-match bug, though pip's typical `==`-pinned installs make it less likely
to have been triggered in practice. Verified with a 9-case local test (exact match, newer patch,
older/genuinely-unverified, newer major, older minor, and a `lts`-suffixed version string) — all
pass, including the exact `1.20.6`-installed-vs-`1.20.3`-recommended case from JS-08's real run.

| Change | Why | Affected scenarios | Requires rerun? | Methodology change? |
|---|---|---|---|---|
| `validator.py`: version-aware (not exact-string) comparison in `verify_dependency_installed()` | Exact-match comparison produced a false-negative `dependency_verified` whenever the package manager legitimately resolved a range to a newer, still-safe version than the LLM's specific recommendation | JS-08 confirmed affected; any already-completed scenario using a range-based strategy (`direct_upgrade`/`transitive_override` with a caret/tilde constraint) could theoretically be affected if the resolved version happened to differ from the recommendation | Yes, for JS-08 (re-dispatched under the fix). Other already-completed scenarios were spot-checked (see `docs/METRIC_FIELD_OWNERSHIP.md`/`REGENERATION_LOG.md`) rather than blanket-rerun, since this is a strictly-more-permissive check — nothing that previously verified `true` can flip to `false` | **No** — makes an already-independent check (Fix #2) correctly permissive for legitimately-newer resolutions; does not touch `rescan_success`, which was already correct and unaffected by this bug |
| `validator.py`: strip leading range-operator prefix (`^`, `~`, `>=`, etc.) before comparing versions | **Self-caught follow-up bug in Fix #11 itself**, found immediately when re-verifying JS-08 and JS-09 under the fix: `recommended_package_version` is sometimes a bare version (`"1.20.3"`) and sometimes carries a range prefix (`"^1.20.3"`, observed on retry attempts) from the same LLM. The first `_version_tuple()` implementation split on `.`/`-`/`+` only, so `"^1.20.3"`'s first component parsed as the string `'^1'` instead of the int `1`, tripping the type-mismatch fallback and returning `False` even for a correctly-newer installed version | Would have affected JS-08's second attempt and JS-09 (both hit the prefixed form on retry) had it shipped unfixed | Yes, for JS-08 (third dispatch) and JS-09 | **No** — same permissive-only direction as the parent fix; verified with 5 additional cases covering `^`, `>=`, `~` prefixes on top of the original 9 |

## Fix #10: `TARGET_CVE` is authoritative in `prioritize.py` — no silent substitution

**Discovered during regeneration, not the pre-regeneration gate review.** User
noticed AF-06 (jinja2, CVE-2024-56326) and JS-06 (flatted, CVE-2026-33228) —
both freshly regenerated with `candidate_count`/`selected_package` values that
didn't match the pre-registered scenario — while cross-checking NVD/GitHub
directly against the regenerated evidence.

**Root cause.** `prioritize_vulnerabilities()` built its candidate list by
applying the `severity in ['high','critical']` filter *before* `TARGET_CVE`
matching ran, and `TARGET_CVE` was only ever searched against that
already-filtered list. If the preregistered target's Grype-reported severity
fell below `high` for any reason, it was invisible to the matching loop, and
the code silently fell back to `candidates[0]` — a *different* CVE — with no
warning, log line, or failure of any kind.

- **AF-06**: `CVE-2024-56326`/jinja2 genuinely present in a fresh Grype scan,
  but Grype reports `severity: "Medium"`. GitHub's own advisory record
  (`GHSA-q2x7-8rv6-6q7h`) carries two different CVSS scores for the same
  advisory — v3.1 = 7.8 ("High"), v4.0 = 5.4 ("Medium") — and Grype's
  `severity` field derives from the v4.0 number. The preregistration itself
  recorded the v3.1 score (7.8) paired with a v4.0 vector string, an internal
  inconsistency predating this session.
- **JS-06**: `CVE-2026-33228`/flatted never reached the candidate list at all
  — confirmed absent from Syft's generated SBOM in both the live CI run and
  an independent local reproduction (same Syft/Grype versions, full scan of
  the real `node_modules`), while a hand-built SBOM containing only `flatted`
  was correctly matched by Grype. Fault isolated to Syft's cataloging stage,
  not severity filtering, matching, or a stale DB — see
  `docs/FINDING_CVE_DETECTION_GAPS.md` for the full investigation. This
  fix does not resolve JS-06's underlying detection gap; it only stops the
  pipeline from silently substituting a different CVE when the intended one
  can't be found.
- **Historical scope**: cross-checked all 18 scenarios' preregistered CVE
  against the *original* (pre-this-session) `results/execution_evidence/*/metrics.json`.
  16 of 18 match exactly; AF-06 and JS-06 do not — the original historical
  evidence already shows werkzeug/CVE-2024-34069 and lodash/CVE-2021-23337
  respectively. This confirms the substitution bug has been present since the
  original dataset generation, not introduced this session.

**Fix.** Restructured `prioritize_vulnerabilities()`: build the full
structurally-valid candidate pool once (fix exists, ecosystem matches — no
severity filter). If `TARGET_CVE` is set, search that full pool; found → use
it (bypassing severity), not found → print every structurally-valid CVE/GHSA
ID that *was* available and `sys.exit(1)` — no fallback. If `TARGET_CVE` is
not set, apply the severity filter exactly as before (unchanged automatic-
discovery behavior). Commit `a7606850`.

**Self-caught regression, same investigation.** The first version of this fix
returned `(candidate, [candidate])` on a direct `TARGET_CVE` match, collapsing
`candidate_count` to `1` for every one of the 18 scenarios (all pass
`TARGET_CVE`) — a metric that previously reported the size of the
severity-filtered pool (~60–130 depending on scenario). Caught by comparing
AF-06's freshly-regenerated `metrics.json` (`candidate_count: 1`) against
already-regenerated AF-02–JS-05 (`63`/`134`). Fixed by always computing the
severity-filtered pool regardless of which branch selects the final
candidate, and returning that pool (plus the matched candidate appended only
if it fell outside it) — preserving `candidate_count`'s established meaning
across all 18 scenarios. Verified with a 4-case local test harness, including
a dedicated regression check for the common case (target already inside the
severity-filtered pool — 16 of 18 real scenarios). Commit `36cc51fd`.

| Change | Why | Affected scenarios | Requires rerun? | Methodology change? |
|---|---|---|---|---|
| `prioritize.py`: `TARGET_CVE` authoritative, fail loudly if not found | Silent fallback let AF-06/JS-06 drift to a different, unregistered CVE with zero signal | AF-06, JS-06 confirmed drifted; all 18 pass through the changed code path | Yes — AF-06, JS-06 (both re-dispatched under the fix: AF-06 succeeded against the correct target; JS-06 correctly failed loudly, confirming the Syft gap is untouched by this fix) | **No** — restores the preregistration's own authority over target selection; automatic-discovery behavior (no `TARGET_CVE`) is byte-for-byte unchanged |
| `prioritize.py`: preserve `candidate_count` across the `TARGET_CVE` path | Self-caught regression in the fix above — direct-match branch was returning a 1-element list, corrupting the metric for all future scenarios | Would have affected AF-06 through JS-09 (12 scenarios not yet regenerated at time of discovery) had it shipped unfixed; already-completed AF-02–JS-05 evidence used the pre-Fix-#10 code and is unaffected | No — caught before any of AF-07–JS-09 were dispatched. AF-06's first re-run (pre-regression-fix) was superseded by a second re-run under the corrected code | **No** — pure evidence-fidelity fix, no change to which candidate is selected |

## Finding: `manifest_editor.py` only patches the root `package.json` — invisible to Juice Shop's independently-installed `frontend/` tree

**Discovered during JS-07 regeneration** (`ws`/`CVE-2024-37890`, run `30943524500`). Job
completed with `build_success: false` (the known, pre-existing, unrelated `TS1005`
`@types/babel__traverse`/`@types/lodash` issue — same as JS-03/04/05) but, unlike those three,
also `dependency_verified: false` and `rescan_success: false` on **both** attempt 1 and the
retry — i.e., the vulnerability was never actually eradicated, not just masked by the known
build quirk.

**Root cause, evidence-traced.** `applications/juice-shop` is a two-tree monorepo: the root
`npm install` resolves root `package.json`/`package-lock.json`, and a `postinstall` script
separately runs `cd frontend && npm install --legacy-peer-deps`, resolving `frontend/package.json`/
`frontend/package-lock.json` completely independently. `manifest_editor.py:21-64`
(`apply_remediation`) only ever reads/writes `package.json` in the scenario's `app_dir` — it has
no code path that touches `frontend/package.json`. An `"overrides"` entry added to the root
manifest is therefore invisible to whatever `npm install` resolves inside `frontend/`.

Confirmed directly: `frontend/package-lock.json` contains its own independent copy of the
vulnerable package (`node_modules/engine.io-client/node_modules/ws@7.4.6`, alongside
`node_modules/ws@8.18.0`), with no `overrides` key of its own. Both attempts' LLM-recommended
override (`ws@^7.5.10`, then `ws@7.5.13` on retry) was correctly written to the root
`package.json` (confirmed in `package-after.json`) and did take effect in the root tree — but
`frontend/`'s independently-resolved `ws@7.4.6` was structurally unreachable by either patch, so
Grype's rescan (which scans the whole repository, both trees) continued to report
`GHSA-3h5v-q93c-6h6q` unfixed. This is why the **retry produced a different version string but
an identical outcome**: no override targeting only the root manifest can fix this class of
vulnerability, so retrying was never going to help.

**Scope check.** Confirmed this is not a universal problem: `form-data` (JS-03), `crypto-js`
(JS-04), and `jsonwebtoken` (JS-05) — the three prior scenarios whose root-only override
succeeded cleanly — are **absent** from `frontend/package-lock.json` entirely, which is exactly
why those overrides worked. JS-07 is the first regenerated scenario whose vulnerable package
happens to also be resolved independently inside `frontend/`.

**Status: documented, not fixed.** Per the same disclose-rather-than-silently-patch approach
applied to JS-06, no change has been made to `manifest_editor.py`. A fix (patching both
manifests, or detecting and warning when a package is frontend-reachable) is a real design
change with unclear blast radius across already-accepted evidence (JS-02–JS-05 were never
checked against this specific failure mode because their target packages happened not to
trigger it) and is out of scope for a same-session code change. JS-07 is being treated the same
way as JS-06: a confirmed, evidence-backed remediation-completeness gap, not silently
re-attempted or forced to a different outcome. See `REGENERATION_LOG.md`'s JS-07 entry for the
full evidence trail.

## Phase 2 — Findings recorded, not yet actioned

These are observations surfaced while verifying Phase 1 fixes. Per the approved
plan, retry reasoning and prompt quality are explicitly out of scope until Phase 1
is complete and approved. Recorded here so they aren't lost before Phase 2 starts.

### Finding: retry produced an identical remediation despite receiving the real failure log

**Observed during Fix #1 verification** (JS-01-v2test run, `workflow_run_id` visible in that run's own evidence).

- Both attempt 1 and the retry recommended the exact same `manifest_patch`
  (`add_override`, `vm2`, `3.9.18`) — same strategy, same version, same operation.
- Confirmed this is **not** a caching artifact: `llm_reasoner.py` makes a fresh API
  call each time, and the two attempts' `reasoning` text is genuinely different
  prose (quoted below), proving the model re-processed the input rather than
  replaying a cached response.
- Confirmed the retry prompt **did** contain the real failure signal — the exact
  `TS1005` compiler errors from the first attempt's `tsc` run were present in full
  in the "Previous Attempt Failure Logs" section fed to the retry. This was
  checked directly against the CI log, not assumed.
- Despite having that error text available, neither attempt's reasoning ever
  mentions TypeScript, `tsc`, or `@types` — both reasoned instead about an
  unrelated `ELSPROBLEMS` npm-resolution message that appeared in the *separate*
  `npm_ls` dependency-context block, and converged on the same override via that
  different reasoning path.
- Contrast: JS-01's original historical run (predating all v2.0 work) **did**
  reason about this exact `@types/babel__traverse`/`@types/lodash` incompatibility
  from the same class of failure log, and concluded `manual_review` instead of
  repeating the broken override. Same failure class, different outcome — so this
  is not a deterministic guarantee of "the model always ignores the compile
  error," but the model's attention to the failure log is not reliable
  run-to-run.

**Attempt 1 reasoning:** *"Defining an override in package.json to force vm2 to
version 3.9.18 cleanly remediates the flaw across the dependency tree without
breaking compatibility."*

**Attempt 2 (retry) reasoning:** *"To ensure npm cleanly resolves vm2 to 3.9.18
without ELSPROBLEMS invalid node_modules errors, an npm dependency override must
be explicitly configured in package.json targeting vm2."*

**Likely contributing factor (not yet verified as root cause):** `temperature: 0.0`,
`topK: 1`, `seed: 42` in `llm_reasoner.py`'s `generationConfig` are deliberate,
documented settings for reproducibility. They make the model pick its single
highest-probability completion rather than explore alternatives. Combined with
`selected-candidate.json.fixed_versions` containing exactly one known fix version
and the system prompt's explicit "do not hallucinate versions" instruction, the
model may have very little room to land anywhere but the same version regardless
of which failure signal it actually attends to.

**Practical cost:** in this run, the retry added a second Gemini call and roughly
doubled pipeline wall-clock time for zero behavioral change. Whether this is
representative of the other 7 npm scenarios that historically retried, or specific
to this one, is unverified — no conclusion should be drawn about the other
scenarios from this single observation alone.

**Status:** Recorded only. No prompt, retry-reasoning, or methodology change has
been made or proposed. To be addressed in Phase 2, if at all, as a deliberate,
disclosed methodology decision — not folded into Phase 1's bug fixes.
