# Pre-Registration Amendment — v2.0
## Master's Thesis: Context-Aware Dependency Remediation in SBOM-Driven CI Pipelines Using Large Language Model

**Author:** Santosh Nagaraj  
**University:** SRH University Berlin  
**Original pre-registration date:** 2026-06-28  
**Amendment date:** 2026-07-08  
**Amendment status:** Approved prior to LLM experiment execution

---

## What This Document Is

This amendment formally records the changes made to the experimental design between the original pre-registration (2026-06-28) and the start of the LLM experiment phase. It exists to maintain academic transparency — the scenarios changed, and this document explains exactly why, what changed, and what was done before proceeding.

The baseline experiment has been run against the amended scenario set. The LLM experiment has not run yet at the time of this amendment.

---

## Change 1 — Ghost CMS Disqualified and Removed

### What the original design said

The original pre-registration described 18 scenarios across three applications: OWASP Juice Shop (6), Ghost CMS (6), and Apache Airflow (6).

### What was discovered

During CI/CD pipeline construction, Ghost CMS v5.76.0 was found to use `yarn` as its package manager and ships a `yarn.lock` file rather than `package-lock.json`. The CI environment was built around `npm` for Node.js applications. Running `npm install` on a Ghost repository managed by yarn produces unreliable results — the two package managers maintain separate lockfile formats and resolution algorithms, and mixing them corrupts the dependency tree.

The correct fix would be to use `yarn` in the Ghost CI workflow. However, this would introduce a third package manager into the experiment (npm for Juice Shop, yarn for Ghost, pip for Airflow), creating an uncontrolled variable — differences in Ghost results could be attributable to the package manager behaviour rather than the LLM's remediation reasoning.

### Decision

Ghost CMS was formally disqualified and removed from the experiment. This decision was formally documented before the experiment proceeded.

### What replaced Ghost

The experiment was restructured to a 50/50 ecosystem split: 9 scenarios for OWASP Juice Shop (npm) and 9 scenarios for Apache Airflow (PyPI), totalling 18 scenarios.

This preserves the two-ecosystem design (npm and PyPI) and increases statistical power within each ecosystem from 6 to 9 scenarios.

---

## Change 2 — Refinement of Validation Gate 1 (Topological Integrity)

What the original design stated: Validation Gate 1 (Dependency Resolution) and Gate 2 (Build Success) evaluated whether the package manager exited with code 0 and the application compiled.

What was empirically discovered during baseline calibration: Originally, it was hypothesized that modern package managers might silently bypass transitive conflicts by elevating them to direct dependencies (Graph Pollution), which would yield an Exit Code 0. However, upon enforcing strict CI environmental controls (executing with the frozen root `package-lock.json`), npm (v8+) correctly enforced strict peer dependency checks. This caused a 100% fatal crash rate (`ERESOLVE unable to resolve dependency tree`), exiting with code 1.

The Methodological Amendment: To accurately measure automated remediation and prevent potential false positives during the LLM phase, Gate 1 is formally amended from 'Dependency Resolution' to 'Safe Dependency Resolution (Topological Integrity)'. A remediation is now explicitly defined as a FAILURE if it successfully builds only by forcing a transitive dependency into the direct dependency graph (Graph Pollution) OR if it fatally crashes the resolver (ERESOLVE). Consequently, any LLM recommendation that resorts to topological vandalization or crashes the build is correctly classified as an architectural failure.

---

## Change 3 — Scenario Count Per Application Increased From 6 to 9

### What changed

With Ghost removed, each remaining application was allocated 9 scenarios instead of 6 to maintain the total of 18.

### Selection methodology

The same algorithmic selection process was used, with the following rules applied consistently:

- Artifact type must be `npm` (Juice Shop) or `python` (Airflow) — OS packages, go-modules, and UnknownPackage types excluded
- Fix state must be `fixed` in Grype output with at least one valid fix version
- CVSS score must be ≥ 7.0
- Fix version must be strictly greater than the current version (no downgrades, no pre-releases)
- One scenario per package — no package concentration
- For Airflow: `apache-airflow-providers-*` packages excluded (first-party framework plugins, not third-party dependencies); self-referential packages excluded; packages requiring framework-level architectural changes excluded

Candidates were ranked by CVSS score descending. The top 9 per application were selected.

The full selection audit log is preserved at `preregistration/scenario_selection_log.md`.

---

## Change 4 — Specific Scenarios That Changed

### Original Juice Shop scenarios (pre-registration v1, 2026-06-28)

| ID | CVE | Package | CVSS |
|----|-----|---------|------|
| JS-01 | CVE-2015-9235 | jsonwebtoken | 9.8 |
| JS-02 | CVE-2023-46233 | crypto-js | 9.1 |
| JS-03 | CVE-2019-10744 | lodash | 9.1 |
| JS-04 | CVE-2024-45590 | body-parser | 7.5 |
| JS-05 | CVE-2026-30951 | sequelize | 7.5 |
| JS-06 | CVE-2022-24785 | moment | 7.5 |

### Amended Juice Shop scenarios (v2, 2026-07-08)

| ID | CVE | Package | CVSS | Upgrade Type |
|----|-----|---------|------|--------------|
| JS-01 | CVE-2023-32314 | vm2 | 9.8 | Patch |
| JS-02 | CVE-2026-33937 | handlebars | 9.8 | Patch |
| JS-03 | CVE-2025-7783 | form-data | 9.4 | Minor |
| JS-04 | CVE-2023-46233 | crypto-js | 9.1 | Major |
| JS-05 | CVE-2015-9235 | jsonwebtoken | 9.0 | Major |
| JS-06 | CVE-2026-33228 | flatted | 8.9 | Minor |
| JS-07 | CVE-2024-37890 | ws | 8.7 | Minor |
| JS-08 | CVE-2024-45590 | body-parser | 8.7 | Patch |
| JS-09 | CVE-2026-3520 | multer | 8.7 | Major |

### Original Ghost scenarios — removed entirely

GH-01 through GH-06 (growl, mysql2, protobufjs, sha.js, knex, nth-check) are no longer part of the experiment. Ghost CMS is disqualified.

### Original Airflow scenarios (pre-registration v1, 2026-06-28)

| ID | CVE | Package | CVSS |
|----|-----|---------|------|
| AF-01 | CVE-2026-8838 | redshift-connector | 9.8 |
| AF-02 | CVE-2025-43859 | h11 | 9.1 |
| AF-03 | CVE-2024-6345 | setuptools | 8.8 |
| AF-04 | CVE-2024-34069 | werkzeug | 7.5 |
| AF-05 | CVE-2024-52804 | tornado | 7.5 |
| AF-06 | CVE-2023-50782 | cryptography | 7.5 |

### Amended Airflow scenarios (v2, 2026-07-08)

| ID | CVE | Package | CVSS | Upgrade Type |
|----|-----|---------|------|--------------|
| AF-01 | CVE-2026-8838 | redshift-connector | 9.8 | Patch |
| AF-02 | CVE-2025-43859 | h11 | 9.1 | Minor |
| AF-03 | CVE-2023-50782 | cryptography | 8.7 | Major |
| AF-04 | CVE-2026-44307 | mako | 8.7 | Patch |
| AF-05 | CVE-2026-0994 | protobuf | 8.2 | Major |
| AF-06 | CVE-2024-56326 | jinja2 | 7.8 | Patch |
| AF-07 | CVE-2024-21272 | mysql-connector-python | 7.7 | Major |
| AF-08 | CVE-2026-2473 | google-cloud-aiplatform | 7.7 | Minor |
| AF-09 | CVE-2024-34069 | werkzeug | 7.5 | Major |

Note: AF-01 (redshift-connector) and AF-02 (h11) are carried over from the original pre-registration unchanged.

---

## Change 5 — vm2 Is Now Included

The original pre-registration excluded vm2 due to package concentration concerns. The automated selection script included it as the highest-CVSS candidate in Juice Shop (CVE-2023-32314, CVSS 9.8, sandbox escape vulnerability).

This is actually a more defensible decision than the original exclusion. vm2 3.9.18 is a real, published fix version. Including it tests whether the LLM correctly identifies that while 3.9.18 technically addresses this specific CVE, the vm2 package has subsequently been declared abandoned by its maintainers (https://github.com/patriksimek/vm2/issues/533) and recommends migration away from the package entirely. The deterministic baseline simply applies 3.9.18 and moves on. Whether the LLM goes further is one of the data points.

---

## Change 6 — mako Is Now Included

The original pre-registration incorrectly excluded mako (CVE-2026-44307) based on the assumption that NVD had no CVSS score for it. Re-verification showed NVD does report a CVSS v4.0 score of 8.7. The automated script correctly identified and included it. This corrects the earlier error.

---

## Baseline Experiment Results (Deterministic Control Group)

The baseline experiment was run against all 18 amended scenarios via GitHub Actions before the LLM phase began. Results are publicly verifiable at the CI log URLs below.

### Methodological Note on Pipeline Execution

The baseline CI execution evaluated Gate 1 (Dependency Resolution). For the PyPI scenarios, a methodology of 'inject-alongside' was utilized (pip install pkg==ver -r req.txt) rather than 'edit-then-install' to force the in-memory resolver to calculate the constraint collapse. Consequently, the PyPI scenarios fatally failed at Gate 1, and Gates 2, 3, and 4 were never reached. Both pipelines were subsequently hardened by explicitly pinning tool versions (pip==24.0 and npm==10.8.1) to ensure absolute historical reproducibility of these resolver mechanics.

### Results Summary

| Scenario | Package | Ecosystem | Result | CI Log |
|----------|---------|-----------|--------|--------|
| JS-01 | vm2 | npm | FAIL (ERESOLVE Conflict) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974209645 |
| JS-02 | handlebars | npm | FAIL (ERESOLVE Conflict) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974217042 |
| JS-03 | form-data | npm | FAIL (ERESOLVE Conflict) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974224878 |
| JS-04 | crypto-js | npm | FAIL (ERESOLVE Conflict) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974231824 |
| JS-05 | jsonwebtoken | npm | FAIL (ERESOLVE Conflict) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974239083 |
| JS-06 | flatted | npm | FAIL (ERESOLVE Conflict) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974246389 |
| JS-07 | ws | npm | FAIL (ERESOLVE Conflict) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974253894 |
| JS-08 | body-parser | npm | FAIL (ERESOLVE Conflict) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974261283 |
| JS-09 | multer | npm | FAIL (ERESOLVE Conflict) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974268830 |
| AF-01 | redshift-connector | PyPI | FAIL (Constraint Collapse) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974276127 |
| AF-02 | h11 | PyPI | FAIL (Constraint Collapse) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974283989 |
| AF-03 | cryptography | PyPI | FAIL (Constraint Collapse) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974291869 |
| AF-04 | mako | PyPI | FAIL (Constraint Collapse) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974299744 |
| AF-05 | protobuf | PyPI | FAIL (Constraint Collapse) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974307197 |
| AF-06 | jinja2 | PyPI | FAIL (Constraint Collapse) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974314895 |
| AF-07 | mysql-connector-python | PyPI | FAIL (Constraint Collapse) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974322051 |
| AF-08 | google-cloud-aiplatform | PyPI | FAIL (Constraint Collapse) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974329695 |
| AF-09 | werkzeug | PyPI | FAIL (Constraint Collapse) | https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28974336701 |

### Interpretation of Results

**npm — ERESOLVE Constraint Violation (9/9 baseline_success: false)**

All nine npm scenarios exited with code 1. Modern npm (v8+) enforces strict peer dependency checks. When `npm install <package>@<version>` is run for a nested package, the package manager detects a conflict between the requested version and the constraints defined by the parent package in the root `package-lock.json`. This triggers a fatal `ERESOLVE unable to resolve dependency tree` error, immediately crashing the build.

This is a true failure — the basic version bump from a static scanner is fundamentally rejected by the package manager's strict topological integrity checks. The previously reported "Graph Pollution" narrative was an artifact of a CI misconfiguration (executing in an empty directory) and has been corrected.

**PyPI — Constraint Collapse (9/9 baseline_success: false)**

All nine PyPI scenarios exited with code 1. Apache Airflow enforces strict version constraints across its dependency tree. When pip attempts to install a newer version of a package than the constraints allow, the resolver raises `ResolutionImpossible` and fails immediately. The build never starts.

This is a true failure — the basic version bump from a static scanner is not applicable in a tightly constrained environment without understanding and modifying the constraint graph.

**What this establishes**

The baseline result of 0% safe remediation (0 out of 18 scenarios produced a safe, architecturally sound fix) establishes the control group measurement. The LLM phase will be evaluated against this baseline — can contextual reasoning produce better outcomes than basic version application?

**Correction note (added during repository remediation, 2026-08-01):** The specific failure descriptions above ("immediately crashing the build," "the build never starts") describe results captured in an external, separate repository (`santuCG/llm-sbom-remediation-experiment`, per the run URLs in the table above); that repository's raw run data is not present in this repository and was not independently re-verified during this remediation pass. Separately, this repository's own currently-implemented baseline mechanism — the `grype-baseline.yml` workflow — was sampled directly via GitHub's public Actions API during the accompanying audit (11 of 36 completed runs checked). In every sampled run, the step that installs the scanner's recommended version succeeded; the run's eventual failure occurred at a later build/test/rescan step instead, not at package-manager resolution. This does not disprove the mechanism described above for the separate, external experiment — that experiment was not independently checked here — but it does mean the two should not be assumed to describe the same failure mechanism without further verification, and any future re-confirmation of the "0% baseline" claim should be checked against `grype-baseline.yml`'s actual run history rather than assumed from this section alone.

**Disclosure note — AF-06 / JS-06 execution mismatch (added during repository remediation, 2026-08-01):** the scenario identities locked in this document (AF-06 = `jinja2`/CVE-2024-56326; JS-06 = `flatted`/CVE-2026-33228) do not match the package/CVE recorded in `results/execution_evidence/AF-06/metrics.json` and `results/execution_evidence/JS-06/metrics.json` respectively. `AF-06`'s executed evidence shows `werkzeug`/CVE-2024-34069 — identical to AF-09's target. `JS-06`'s executed evidence shows `lodash`/CVE-2021-23337, which does not correspond to any of the 18 locked scenarios. Both scenario folders were added to the repository for the first time in a single commit, with no earlier, differently-identified version in the repository's history to compare against, so the origin of the mismatch could not be determined with certainty from committed history alone. This note records the discrepancy as found; it does not resolve it. Whether the correct remedy is to re-execute AF-06 and JS-06 against their locked targets above, or to formally amend this pre-registration to accept the substituted targets, is a decision for the repository owner and has not been made as part of this note.

**Update (added during documentation synchronisation, 2026-08-02): root cause confirmed; rerun attempted and found currently infeasible.** Full detail in `docs/audit/af06_js06_rerun_attempt_2026-08-02.md`. Summary:
- **Root cause, now confirmed:** `profiles/AF-06.yaml` and `profiles/JS-06.yaml`, from an earlier per-scenario-workflow architecture (since replaced by the current generic pipeline), were seeded with the wrong `target_package`/`target_cve` at creation time — `profiles/AF-06.yaml` was byte-identical to `profiles/AF-09.yaml`. This was a profile copy-paste/templating error, not a later pipeline defect.
- **Rerun attempted:** both scenarios were re-dispatched against their correct, locked pre-registered targets (jinja2/CVE-2024-56326 for AF-06; flatted/CVE-2026-33228 for JS-06) via CI runs [30756155220](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30756155220) and [30756158221](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30756158221).
- **Result: not currently reproducible.** Both reruns again selected the same off-target package/CVE as the original mismatched evidence. Grype's live, unpinned vulnerability database has changed since the 2026-07-08 pre-registration snapshot: jinja2's advisory is now classified "Medium" severity (below the pipeline's "High" candidate filter), and flatted's advisory is no longer detected at all. This is the same disclosed live-database limitation (`THESIS_LIMITATIONS.md` item 4) independently observed here as a scenario-selection failure, not merely a scanner-finding-count drift.
- **No historical evidence was modified.** `results/execution_evidence/AF-06` and `results/execution_evidence/JS-06` remain exactly as they were; the rerun CI runs' output was not merged in, since it reproduced the same mismatch rather than correcting it. A precautionary archive made before the attempt was removed afterward, since it never became part of the evidence chain.
**The investigation is complete.** The pre-registration is correct, the scenario definitions in `results/scenarios/final_18_scenarios.json` are correct, and the package/version targets are correct and remain technically installable today. The reruns were attempted against these correct, locked targets and failed to reproduce them — not because of any error in the experimental design, but because Grype's live vulnerability database evolved after the original experiments were run (§ above). The remaining issue is a **documented external reproducibility limitation**, not an unresolved design question. The pre-registered scenarios above are **not** amended and **not** replaced with the executed `werkzeug`/`lodash` identities: they remain unchanged because they accurately represent the original experimental design and intent. This amendment records why those exact scenarios cannot currently be regenerated under a live, unpinned vulnerability database — it does not, and should not, retroactively redefine what AF-06 and JS-06 were pre-registered to test.

**Update (added during Pipeline v2.0 regeneration, 2026-08-04): the 2026-08-02 conclusion above was incorrect — root cause found, fixed, and both scenarios successfully regenerated against their correct preregistered targets.** Full detail in `docs/FINDING_CVE_DETECTION_GAPS.md`, `CHANGELOG_V2.md` (Fix #10), and `docs/CVE_MATCH_VERIFICATION.md`. Summary:

- **The actual root cause was not "Grype's live database evolved" as an unfixable external limitation — it was a fixable pipeline design defect.** `prioritize.py`'s severity filter (`severity in ["high","critical"]`), intended only to guide *automatic* candidate discovery when no target is specified, was also being applied when an explicit `TARGET_CVE` was set. When a preregistered target's Grype-reported severity fell below that threshold — AF-06's advisory carries two different CVSS scores under two different scoring standards for the same vulnerability (v3.1 = 7.8/"High", v4.0 = 5.4/"Medium"; Grype's severity label derives from the v4.0 score) — the explicit `TARGET_CVE` match never ran against it, and the code silently fell back to a different, unrelated candidate. This is a real, general, and correctable pipeline behavior, not an artifact of the live vulnerability database changing over time.
- **Fix implemented and verified.** `prioritize.py` was restructured so an explicit `TARGET_CVE` is matched against the full structurally-valid candidate pool regardless of severity (bypassing the automatic-discovery filter, which continues to apply unchanged when no target is specified), and a target that still cannot be found now fails the run loudly instead of silently substituting.
- **AF-06 result: successfully regenerated against its correct preregistered target.** Run [30942956346](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30942956346): `jinja2` upgraded `3.1.4` → `3.1.5`, `CVE-2024-56326` confirmed absent from the rescan, `build_success`/`test_success`/`dependency_verified`/`rescan_success` all `true`. This directly supersedes both the original mismatched evidence and the 2026-08-02 conclusion that this scenario "cannot currently be regenerated."
- **JS-06 result: still does not produce remediation evidence, but now for an independently confirmed, different, and more specific reason than "no longer detected."** `flatted` is absent from the SBOM Syft generates for this project — confirmed via the actual CI run, an independent local reproduction with identical Syft/Grype binary versions, and a hand-constructed SBOM containing only `flatted` (which Grype matched correctly when given the chance). This is a package-cataloging gap in the SBOM-generation stage, not a matching or database-currency issue, and not something `prioritize.py`'s fix could resolve on its own, since the vulnerability never reaches Grype or the pipeline's candidate pool. Under the corrected pipeline, the run for JS-06 now fails loudly with an explicit "not found among any structurally-valid candidate" message and produces no substitute evidence, rather than silently substituting a different CVE as the original run did.
- **Correction to this document's prior conclusion.** The 2026-08-02 update above states "the investigation is complete" and "not because of any error in the experimental design." Both are superseded: the investigation was not complete (the fixable pipeline defect had not yet been isolated from the genuine, separate CVSS/SBOM findings), and AF-06's failure to reproduce specifically *was* a pipeline design defect (severity filter overriding an explicit target), now fixed. JS-06 remains a genuine, disclosed detection gap unrelated to `prioritize.py`, consistent with the earlier note's observation that `flatted` was "no longer detected," but now root-caused to SBOM cataloging specifically rather than left as an unexplained database-drift symptom.
- **The pre-registered scenarios remain unchanged and unamended** — this update does not redefine what AF-06 or JS-06 were preregistered to test; it corrects the pipeline so AF-06 could finally be executed against that original definition, and documents precisely why JS-06 still cannot be.

**Disclosure note — Grype "Cold Start" database clause was never implemented (added during documentation synchronisation, 2026-08-02):** `preregistration/MASTER_METHODOLOGY_RECORD.md` (and, until this pass, `docs/06-reproducibility.md`) instructed that exact reproducibility of scanner findings requires manually importing a specific Grype vulnerability database snapshot (dated 2026-07-08) via `grype db import`, with auto-updates disabled, before scanning. Checked directly against both CI workflows (`.github/workflows/generic-remediation.yml` and `grype-baseline.yml`): neither contains a `grype db import` step, or any step that pins or restores a specific database snapshot. Every scan in the frozen dataset ran against whichever Grype vulnerability database was live at the time of that CI run; `GRYPE_DB_VALIDATE_AGE=false` only suppresses Grype's staleness check and does not pin a snapshot. This means the pre-registered reproducibility procedure for the vulnerability database was not followed for any of the 18 scenarios. This is a known, disclosed limitation of the study (absolute scanner-finding counts are not expected to reproduce exactly on a later re-run; target-CVE eradication is the reproducible signal — see `docs/05-results-and-discussion.md`), and `docs/06-reproducibility.md` has been corrected accordingly as part of this pass. This note records the deviation for the pre-registration record; it does not change any experimental evidence or result.

---

## KEV Status — Amendment Note

As noted in the original pre-registration, all 18 scenarios across both applications return KEV=FALSE. This is unchanged in the amended set. The KEV sub-question from the thesis proposal cannot be evaluated empirically. The research question remains scoped to CVSS versus EPSS signal contrast only.

---

## Data Snapshot

All enrichment data (EPSS probabilities, KEV status, MITRE CVE descriptions, CVSS vectors) was fetched and frozen at the time of scenario generation: **2026-07-08T18:28:12Z**. Raw API responses are saved to `applications/evidence/` in the repository. This prevents data drift between the scenario selection and the LLM execution phases.

**Clarification (added during documentation synchronisation, Run B remediation, 2026-08-02):** the KEV component of this enrichment data specifically involves two distinct files, not one single snapshot. Scenario generation (`scripts/generate_final_cves.py`) reads `preregistration/kev_snapshot.json` (`catalogVersion 2026.06.18`). The live pipeline's runtime KEV enrichment (`scripts/remediation/prioritize.py`) reads a separate, later file, `scripts/remediation/snapshots/kev_snapshot.json` (`catalogVersion 2026.07.24`), which was introduced in a subsequent commit and was never backported to the file above. This means the single "2026-07-08" date above does not describe the KEV data precisely — the file used for scenario selection and the file used at execution time are genuinely different snapshots, not just differently worded references to the same one.

**This does not affect any reported result.** None of the 18 pre-registered target CVEs appear in either KEV snapshot file's `vulnerabilities` list, confirmed by direct inspection of both files. The recorded `kev_status: false` for all 18 scenarios (`results/execution_evidence/*/metrics.json`) is identical under either file. This clarification is a documentation-accuracy correction only; it changes no experimental evidence, no metric, and no conclusion.

---

## Files Updated By This Amendment

| File | Status |
|------|--------|
| `results/scenarios/pre_registered/scenarios.json` | Replaced with amended 18 scenarios |
| `results/execution_evidence/` | New - execution logs and baseline CI results for all 18 scenarios |
| `preregistration/scenario_selection_log.md` | New — automated selection audit log |
| `preregistration/PRE_REGISTRATION_AMENDMENT.md` | This document |
| `preregistration/MASTER_METHODOLOGY_RECORD.md` | Original — preserved for record, superseded by this amendment |
| `preregistration/GHOST_PREREGISTRATION.md` | Archived — Ghost CMS disqualified |

---

## Change 7 – Pipeline Methodology Overhaul

Mid-experiment, a critical protocol update was instituted to shift from a raw string manifest patch to a structured intermediate representation. This ensures ecosystem-agnostic execution across npm and PyPI.

Specifically, this amendment formally documents:
1. The transition from a raw string `manifest_patch` to a structured intermediate representation (`{"operation", "package", "constraint"}`).
2. The introduction of the `validation_stage_reached` metric alongside `failure_stage`.
3. The explicit export of `candidate-ranking.json`, `llm-request.json`, and `llm-response.json` as permanent artifacts to ensure auditability.

**Legacy Scenario Nullification:**
0 of 18 scenarios have final validated data under the old schema being kept; all 18 run fresh under the new pipeline. The final dataset will use the new-pipeline output for JS-01 and JS-08 regardless of whether it matches their legacy results.

---

## What Has Not Changed

- The primary research question is unchanged
- The two-condition design (deterministic baseline vs LLM-assisted) is unchanged
- The LLM model family (Gemini, temperature 0, JSON schema enforcement) is unchanged
- The hallucination detection method (registry API validation) is unchanged
- The KEV limitation is unchanged
- The data snapshot date and methodology for EPSS/KEV/CVSS enrichment is unchanged

**Correction note (added during documentation synchronisation, 2026-08-02):** the line above originally read "The LLM model (Gemini 2.5 Flash...) is unchanged." The specific model identifier is not, in fact, fixed: the pipeline (`scripts/remediation/llm_reasoner.py`) submits requests to a fallback list (`gemini-3.6-flash → gemini-2.5-flash → gemini-2.0-flash → gemini-1.5-flash`), and the model that actually responds is recorded per scenario. Across the 18 frozen scenarios, 17 recorded `gemini-2.5-flash` and one (JS-09, regenerated after the fallback list was updated) recorded `gemini-3.6-flash`. See `docs/03-llm-configuration.md` for the full, evidence-verified configuration.
