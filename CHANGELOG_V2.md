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

## New Fix #5 candidate — observed during Fix #4 verification, not yet investigated

**Observed in the same JS-01 verification run (30850432630) that confirmed Fix #4.**
With `karma.conf.js` restored, `npm test` (which runs both `test:client` (Karma)
and `test:server` (mocha/ts-node) sequentially) progressed past Karma — all 686
frontend tests executed — and then failed in `test:server`:

```
TSError: Unable to compile TypeScript:
lib/insecurity.ts(58,51): error TS2531: Object is possibly 'null'.
```

This surfaced compiling `routes/b2bOrder.ts`. Not yet root-caused against the
same taxonomy used for Fix #4 (workflow / environment / Juice Shop / Node
version / ts-node config / strict-null-checks setting). Matches the
already-named "Fix 5: Remaining npm test infrastructure" step in the roadmap.
**Status: recorded only, not investigated, not fixed.**

Also observed: in this same run, `metrics.json` shows `build_success: false`
(correctly — the retry's `npm run build:server` hit the already-documented
`TS1005 '?' expected` `@types/babel__traverse`/`@types/lodash` errors recorded
under the Phase 2 finding above, a known pre-existing JS-01 condition, not a
regression) alongside `rescan_success: true` and `dependency_verified: true`,
but `test_success: null` rather than `true`/`false` even though `npm test`
demonstrably ran. Whether `test_success` should have been set here is a
single-owner-per-metric-field question — recorded for that already-planned
audit below, not investigated now.

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
