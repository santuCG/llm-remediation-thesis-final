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
