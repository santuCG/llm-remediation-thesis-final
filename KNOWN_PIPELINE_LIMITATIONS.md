# Known Pipeline Limitations

Findings about the remediation pipeline's own mechanics, distinct from findings about LLM
reasoning quality. Recorded here so they survive independently of any one experiment.

## Lockfile-regeneration trigger does not cover stale-resolution-after-successful-install

**Current behaviour.** Lockfile regeneration is triggered only after installation failures
(`Fallback Lockfile Regeneration`, gated on the preceding install step's exit code), although
stale dependency resolution can also occur after a successful installation.

**Evidence.** JS-01 (`vm2`, CVE-2023-32314), reproduced in both the original hinted pipeline run
(`30948623108`, 2026-08-04) and the hint-removal ablation (`31224096838`, 2026-08-07). Same
override, same version, same package, in both:

- Attempt 1: `transitive_override` to `vm2@3.9.18` — installs without error — validator still
  detects the target CVE (466/464 remaining matches respectively).
- Attempt 2: identical version (`3.9.18`), no change to the recommendation — the retry path's
  own lockfile wipe runs as a side effect of dispatching a new LLM call — validator passes.

**Interpretation.** The recovery trigger fires too late to catch this failure mode, and the
mechanism that does catch it is coupled to a full new LLM reasoning cycle it doesn't need.
Phrased to the level this evidence actually supports: the current trigger condition (install
exit code) is sufficient for installation failures but not for stale dependency-resolution
failures that only become visible during validation. Whether the original design intentionally
traded this off against fewer clean reinstalls, faster CI, or other considerations is not
evaluated here.

**Open question, not investigated further here.** Investigate whether a clean dependency
re-resolution should be performed after applying npm overrides but before invoking a second
LLM reasoning cycle. Deliberately not investigated or implemented on any branch that reports
experimental results, to avoid introducing an uncontrolled pipeline-mechanics variable into
results already in progress. A reasonable target for a future "Pipeline v2.1" pass.

**Full evidence trail:** `results/execution_evidence_no_hint/EXPERIMENT_MANIFEST.yaml`
(Hint Removal Ablation experiment), sections on JS-01.

## `is_direct_dependency` in preregistration metadata disagrees with the live dependency tree for 6 of 9 Juice Shop scenarios

**Current state.** `preregistration/final_18_scenarios.json` records `is_direct_dependency: true`
for all 18 scenarios, both ecosystems, uniformly. For 6 of the 9 Juice Shop scenarios
(JS-01, JS-02, JS-03, JS-04, JS-06, JS-07), the package the scenario targets is, in the
current `applications/juice-shop/package.json`, absent from both `dependencies` and
`devDependencies` — i.e. transitive, not direct. The live pipeline's own
`_get_dependency_type()` (`scripts/remediation/generic_remediation.py`) computes this
correctly at execution time and writes the live-computed value into each scenario's
`metrics.json`; only the preregistration field is affected.

**Root cause.** A spot-check against the *original*, pre-Pipeline-v2.0 historical evidence
for JS-02/`handlebars` shows the same "direct" claim already present before any engineering
work this project — i.e. this looks like a value that was never individually verified
against the manifest at registration time, not a value that was once correct and drifted.
See `docs/FINDING_CVE_DETECTION_GAPS.md`'s "Related finding" section for the full
per-scenario comparison.

**What was not done, and why.** `preregistration/final_18_scenarios.json`'s
`is_direct_dependency` field has not been retroactively edited. It is a preregistered
scenario-metadata field; correcting it after the fact would be indistinguishable from
amending the preregistration to fit later findings. It is documented here, and in
`docs/FINDING_CVE_DETECTION_GAPS.md`, instead.

## The LLM arm and the deterministic-baseline arm are not symmetric in recovery mechanics

**Current state.** `.github/workflows/generic-remediation.yml` (LLM arm) has a one-retry
step and a "Fallback Lockfile Regeneration" step; `.github/workflows/grype-baseline.yml`
(deterministic-baseline arm) has neither. Separately, the baseline arm's build-verification
step runs with an immediately-fatal flag (`--fatal`, `scripts/ci/check_npm_build.sh`) that
the LLM arm's equivalent step does not use.

**Interpretation.** These are deliberate properties of evaluating the LLM pipeline as a
complete, self-recovering remediation workflow rather than a single-shot model query — not
an oversight — but they mean a like-for-like reading of "the LLM arm succeeded more often"
should account for the fact that the LLM arm has recovery mechanisms available to it that
the baseline arm does not. Not itemized as a caveat until this entry.

**What was not done, and why.** No code change. This is a disclosure of an existing,
deliberate design asymmetry, not a defect to fix — changing it would alter the treatment
being evaluated for a dataset that has already been generated under the current design.
