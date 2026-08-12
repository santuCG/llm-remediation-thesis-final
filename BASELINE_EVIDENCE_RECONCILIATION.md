# Baseline Evidence Reconciliation

This document exists because two records in this repository describe the deterministic
(Grype-recommended-version) baseline's outcome differently. It does not amend either
record; it states both precisely, side by side, and says which is authoritative for which
purpose.

## The historical claim

`preregistration/MASTER_METHODOLOGY_RECORD.md`, "The 0% Safe Remediation Rate":

> Empirical execution on the remote GitHub Actions CI established a **0% Safe Remediation
> Rate**. Static scanners failed to safely and correctly remediate a single scenario out of
> the 18 targeted vulnerabilities... PyPI/Airflow: the constraint solver was fatally crashed
> (`ResolutionImpossible`)... NPM/Juice Shop: the constraint solver fatally crashed
> (`ERESOLVE unable to resolve dependency tree`).

This claim's own execution evidence is not present in this repository. It is not
independently re-verifiable from anything archived here.

## The current evidence

`results/reproducibility_verification/` — described in `README.md` as "the deterministic
baseline's own evidence" — contains a fresh run of all 18 scenarios through this
repository's own `grype-baseline.yml` workflow. Read directly from each scenario's
`metrics.json`:

| Ecosystem | `build_success` | `test_success` | `dependency_verified` | `rescan_success` | `failure_stage` |
|---|---|---|---|---|---|
| All 9 Airflow/pip (AF-01–09) | `true` | `true` | `true` | `true` | `none` |
| All 9 Juice Shop/npm (JS-01–09) | `false` | `false` | *(not reached)* | *(not reached)* | `build` |

None of the 9 pip scenarios show a crashed resolver — dependency resolution, build, test,
and rescan all succeed, and the rescan confirms the target CVE is gone. The 9 npm scenarios
do fail, but at the **build** stage, not at dependency resolution — no `ERESOLVE` appears in
this evidence.

## What this does and does not establish

- The historical claim's specific mechanism (`ResolutionImpossible` for pip, `ERESOLVE` for
  npm, both at Gate 1) is not reproduced by the current evidence.
- **The cause of the difference cannot be determined from archived evidence.** The current
  evidence has no `grype-db-metadata.json` to compare against a database snapshot from the
  historical run, and the historical run's own raw execution data is not archived anywhere
  in this repository (per the correction note in `preregistration/PRE_REGISTRATION_AMENDMENT.md`
  dated 2026-08-01). Plausible explanations include a live, unpinned Grype database and
  package-registry state differing between the two points in time (both scanners' database
  and the target applications' upstream packages are explicitly disclosed elsewhere as
  unpinned — `docs/06-reproducibility.md`, `preregistration/PRE_REGISTRATION_AMENDMENT.md`'s
  "Cold Start" note) — but this is not confirmed, only plausible. No other candidate cause
  (environment drift, pipeline defect) has supporting evidence either.
- This does not affect the thesis's own conclusions: the thesis does not use the "0%"
  figure or the `ERESOLVE`/`ResolutionImpossible` mechanism anywhere. Its own baseline
  comparison already reports the npm result as "build did not complete" and explicitly
  scopes the comparison as being between two end-to-end workflows, not raw scanner output
  (see the thesis, §3.8).

## Which record is authoritative for which purpose

- For the **original, locked pre-registration record** of what was planned and initially
  observed: `preregistration/MASTER_METHODOLOGY_RECORD.md`, unaltered, as historical record.
- For the **current, in-repository, independently verifiable baseline-arm evidence**:
  `results/reproducibility_verification/`.
- Neither is silently preferred over the other; both are preserved, and this document is
  the pointer between them.

## Rerun assessment

No rerun of the 18-scenario experiment is required. This is a reconciliation-of-record
question, not a defect in the frozen LLM-arm evidence, and the thesis's own conclusions do
not depend on the historical claim's specific figure or mechanism.
