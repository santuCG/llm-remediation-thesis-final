# Master Methodology Record

## 1. The Core Philosophy
**Objective:** Context-Aware Dependency Remediation in CI Pipelines.
**Strict Constraint:** The LLM must orchestrate remediations by modifying manifest files ONLY (e.g., `package.json`, `requirements.txt`). No system-level changes, root commands, or bypasses are permitted.

## 2. The Exclusion Ledger & Ghost Archival
To maintain a pristine experimental environment, rigorous filtering was applied during scenario selection. Candidates were excluded based on the following rules:

- **OS Packages (~1400+ dropped):** LLMs restricted to modifying `package.json` or `requirements.txt` cannot patch Alpine, Debian, or Ubuntu binaries (e.g., `libssl`, `curl`). Only `npm` and `python` ecosystems are permitted.
- **Airflow Providers (`apache-airflow-providers-*`):** These were excluded because they are core framework plugins, not standard third-party dependencies, and updating them requires complex internal framework migrations.
- **Self-Referential Packages:** Packages matching the application name (e.g., `ghost` inside Ghost) were dropped. Updating an application from within itself breaks the definition of third-party dependency remediation.
- **Blacklisted Packages (`authlib`, `urllib3`):** Dropped during composition review to prevent framework-level architectural migrations that distract from standard dependency updates.
- **Yarn Ban & Ghost Archival:** Strict `npm`/`PyPI` isolation was enforced to prevent package manager collisions in the CI runner. During the methodology audit, it was discovered that Ghost CMS relies on `yarn` and builds using a `yarn.lock` file. To preserve absolute environment fidelity and avoid `npm`/`yarn` collisions, **Ghost CMS was formally disqualified and archived**. 

## 3. The 9/9 Selection Ledger
Following Ghost's disqualification, the experimental baseline pivoted to a strict 50/50 ecosystem split: **9 scenarios for Juice Shop (npm) and 9 scenarios for Airflow (PyPI), totaling 18 scenarios.**

These 18 scenarios were selected using strict mathematical boundaries:
- **Severity:** Strictly CVSS >= 7.0 with a verified upstream fix (`fix.state == 'fixed'`).
- **Standard CVEs:** Vulnerability IDs starting with `GHSA-` were parsed and mapped to their standard CVE formats to guarantee compatibility with external lookup APIs (CISA KEV, FIRST EPSS).
- **Version Math:** No downgrades or pre-releases (alpha/beta/rc) were permitted. The target version must be logically strictly greater than the currently installed version.

## 4. The Reproducibility Engine
To guarantee academic reproducibility and prevent data drift, the experimental state was frozen:

- **Dependency Tree Fidelity:** The exact dependency trees at the time of SBOM generation are frozen via `package-lock.json` (for Node) and `pip freeze` / `pipdeptree` (for Python).
- **Targeted Data Freezing:** CISA KEV, FIRST EPSS, and MITRE API responses were fetched and saved locally to `applications/evidence/` for the final 18 scenarios. This prevents API rate-limiting or data drift during the offline experiment.
- **Airflow Constraint Rule:** Airflow requires strict Apache constraint URLs during pip installation/validation. This rule was injected into the documentation to ensure the LLM knows how to resolve dependencies without cyclic conflicts.

## 5. Reproducibility Guarantee
The exact tool configurations, DB snapshots, and lockfile justifications have been programmatically recorded in the app-specific markdown files in the `applications/evidence/` folder. This documentation ensures cryptographic-level reproducibility across time, verifying the exact number of raw vulnerabilities detected and the transitive topological graph that the automated LLM agent will evaluate.

**The "Cold Start" Database Clause:** Future researchers must manually download and import the Grype vulnerability database snapshot from 2026-07-08 using the `grype db import` command before running the scan with auto-updates disabled.

## 6. The Remediation Success Metric (The Denominator Fix)
Remediation success is measured as a binary (1/0) outcome based on a Four-Gate Validation Pipeline:
1. **Gate 1: Safe Dependency Resolution (Topological Integrity)** — The package manager must accept the new version without conflicts AND without graph pollution/transitive elevation. Elevating a transitive dependency to a direct dependency constitutes an automatic failure.
2. **Gate 2: Build success** — The application must compile/build successfully.
3. **Gate 3: Test pass** — Existing automated tests must still pass.
4. **Gate 4: Vulnerability rescan** — Grype must confirm the target CVE-ID is no longer present.

Total vulnerability counts were used to establish the baseline severity, but are excluded from the individual remediation success metric to prevent OS-level background noise from skewing the data.

**Scope Defense regarding Optional Providers (e.g., Airflow):** Packages locked within the `pip freeze` or `package-lock.json` are considered part of the CI-build attack surface and are valid remediation targets, regardless of runtime execution paths. The goal is manifest remediation, not runtime analysis.

## 7. Data Science Standards for Baseline Evaluation
To ensure absolute statistical integrity for the final evaluation phase, strict data science standards were enforced on the extracted JSON payload:
- **Strict Null Enforcement:** Vulnerability parameters (e.g., CVSS vectors, CWE IDs, and descriptions) were sanitized during extraction. Empty strings and pure whitespace were programmatically converted to true JSON `null` values to guarantee accurate statistical modeling.
- **Semantic Versioning (SemVer) Classification:** A programmatic version parser compares the current package version to the Grype-recommended target version, automatically classifying the required fix as a `major`, `minor`, or `patch` upgrade. This stratification is critical for analyzing the LLM's success rate against upgrade complexity.
- **Metadata Timestamp Injection:** A globally synchronized UTC timestamp (`metadata_snapshot_date`) is injected into the root of every baseline scenario object. This acts as a cryptographic timestamp, proving the exact moment the API data (EPSS, KEV, MITRE) was snapshotted and frozen.

### The 0% Safe Remediation Rate
Empirical execution on the remote GitHub Actions CI established a **0% Safe Remediation Rate**. Static scanners failed to safely and correctly remediate a single scenario out of the 18 targeted vulnerabilities. When applying the naive recommended version bump:
1. **PyPI/Airflow (Constraint Collapse):** The constraint solver was fatally crashed (`ResolutionImpossible`) due to strict version boundaries.
2. **NPM/Juice Shop (ERESOLVE Conflict):** The constraint solver fatally crashed (`ERESOLVE unable to resolve dependency tree`) due to strict peer dependencies.

## Phase 3 LLM Success Criteria (The 4 Gates)

Define the precise success criteria the LLM must meet to prove its superiority over the baseline:

**Gate 1 (Dependency Resolution):** The package manager successfully resolves the new dependency graph without ERESOLVE or ResolutionImpossible errors.

**Gate 2 (Topological Integrity):** 
* For NPM: The LLM must NOT pull transitive dependencies into the root dependencies block. It must utilize "overrides" in package.json to surgically patch the nested package.
* For PyPI: The LLM must gracefully adjust strictly pinned parent bounds in the constraints file to accommodate the new sub-dependency, rather than forcing a conflict.

**Gate 3 (Build/Test):** The application's native test suites exit with code 0, proving the remediation did not break runtime application logic.

**Gate 4 (Vulnerability Rescan):** A subsequent vulnerability scan confirms the target CVE is completely eliminated from the dependency tree.
