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
