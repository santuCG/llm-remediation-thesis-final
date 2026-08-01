# 07 — Manual Validation Protocol & Methodological Evolution

> **Historical Note:** This document describes an earlier methodology and is preserved for historical completeness. The final methodology is described in [docs/04-experimental-methodology.md](04-experimental-methodology.md).

This document formalizes the rigorous manual validation procedures employed during the thesis experiment, ensuring reproducible and mathematically airtight results. Furthermore, it explicitly documents the methodological evolution of Software Bill of Materials (SBOM) generation, culminating in the lockfile-freeze strategy.

## 1. The Three-Stage SBOM Generation Evolution

A critical factor in evaluating LLM-driven dependency remediation is defining the precise dependency graph upon which the model will reason. Throughout the design of this experiment, the methodology for generating the topological source of truth (the SBOM) evolved through three distinct stages to eliminate noise and ensure experimental validity.

### Stage 1: The Source Code Strategy (Discarded)
Initially, the `syft dir:.` command was used to scan the raw source directory of the applications.
- **The Failure:** This approach failed specifically for Python applications (Apache Airflow). Static source directories lack the installed dependency tree unless the environment is fully built. Consequently, Syft missed critical transitive dependencies and failed to accurately map the runtime graph.

### Stage 2: The Docker Image Strategy (Discarded)
To capture a built environment, the methodology pivoted to scanning the official production Docker images (e.g., `apache/airflow:2.9.2`).
- **The Failure:** While this captured the application dependencies, it introduced massive OS-level package pollution (`deb`, `apk`, `libc`, `apt`). This polluted the experimental population, mixing the application's native dependency graph with the container's infrastructure graph, making it exceptionally difficult to isolate language-specific remediation capabilities.

### Stage 3: The Lockfile Freeze Strategy (Finalised)
The final, mathematically rigorous methodology abandons directory and image scanning in favour of exact dependency lockfiles.
- **The Solution:** For Node.js (OWASP Juice Shop), the SBOM is generated exclusively using `syft file:package-lock.json`. For Python (Apache Airflow), the equivalent frozen state (`requirements.txt` or `pip freeze` output) is used.
- **The Scientific Benefit:** This method isolated the exact application dependency tree, effectively removing OS noise. It establishes a 1-to-1 match between the experimental population (the vulnerabilities in the lockfile) and the remediation target. The lockfile is the definitive source of truth.

## 2. Manual Validation Procedure

To eliminate any potential errors introduced by automated orchestration scripts, the final evaluation of the LLM's remediation hypotheses is conducted entirely manually under strict procedural rules.

### The Four-Gate Manual Pipeline

For each scenario, the LLM produces a remediation hypothesis (e.g., an `npm install <package>@<version> --save-exact` command with or without overrides). The manual validator must execute the following gates in a sterile environment:

#### Gate 0: Registry Verification
- **Action:** The validator manually checks the public registry (npm or PyPI) to ensure the version string recommended by the LLM actually exists.
- **Pass Condition:** The version is published and available.
- **Fail Condition:** The LLM hallucinated a non-existent version.

#### Gate 1: Topological Integrity (Safe Resolution)
- **Action:** The validator manually applies the recommended fix exactly as output by the LLM. For npm, this involves editing `package.json` to include the `overrides` or running the `npm install` command.
- **Pass Condition:** The package manager (`npm` or `pip`) successfully resolves the entire dependency tree and exits with code 0.
- **Fail Condition:** The package manager throws an `ERESOLVE` or `ResolutionImpossible` error due to conflicting bounds.

#### Gate 2: Build Integrity
- **Action:** The validator manually executes the application build sequence (e.g., `npm run build` or the Python equivalent).
- **Pass Condition:** The application compiles without syntax or type errors introduced by breaking API changes in the upgraded package.
- **Fail Condition:** The build fails.

#### Gate 3: Graph Confirmation
- **Action:** The validator runs `npm ls <package>` or `pip show <package>` to confirm the requested version is physically present in the `node_modules` or site-packages.
- **Pass Condition:** The specific version is installed.

#### Gate 4: Vulnerability Eradication
- **Action:** The validator generates a new SBOM from the modified lockfile (`syft file:package-lock.json`) and manually rescans it (`grype sbom:new-sbom.json`).
- **Pass Condition:** The target CVE is no longer present in the Grype output.
- **Fail Condition:** The vulnerability remains.

### Evidence Persistence Rule
Every command executed during the manual validation phase must have its output explicitly piped or saved to the `experiment/results/` directory. Terminal buffers are insufficient. The exact `package-lock.json` lockfiles (baseline and remediated) are preserved in `experiment/raw_outputs/` as immutable evidence.
