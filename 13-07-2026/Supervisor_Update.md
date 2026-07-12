# Research Update: Context-Aware Dependency Remediation in SBOM-Driven CI Pipelines Using Large Language Model

**Author:** Santosh Nagaraj, SRH University Berlin
**Date:** 13 July 2026
**Repository:** https://github.com/santuCG/llm-remediation-thesis-final

Dear Professor,

This document summarises the current state of the thesis experiment, explains the methodological decisions we have made so far, presents the key findings from our completed experiments, and outlines the exact plan for the remaining work. Every claim made here is backed by a file path or URL so you can verify it directly.

## 1. What We Set Out To Do

The core research question asks whether an LLM can generate context-aware dependency remediation strategies that succeed where naive deterministic scanner recommendations fail. We designed 18 pre-registered scenarios, 9 from the OWASP Juice Shop application using the npm ecosystem and 9 from Apache Airflow using the PyPI ecosystem. Each scenario targets a specific known CVE in a transitive or direct dependency.

The full list of all 18 scenarios, including CVE identifiers, package names, severity scores, and fix versions, is recorded in:
- `experiment/final_18_scenarios.json`

The pre-registration documents that lock down our methodology before execution are stored in:
- `preregistration/protocol.md`
- `preregistration/JUICESHOP_PREREGISTRATION.md`
- `preregistration/AIRFLOW_PREREGISTRATION.md`
- `preregistration/PRE_REGISTRATION_AMENDMENT.md`
- `preregistration/MASTER_METHODOLOGY_RECORD.md`

## 2. What Major Changes We Made and Why

### 2a. From Fully Automated CI to Manual Validation for the Core 18 Scenarios

Originally, we planned to validate all 18 scenarios through fully automated GitHub Actions CI pipelines. During early testing in our previous repository (https://github.com/santuCG/llm-sbom-remediation-experiment), we discovered that automating LLM execution across 18 complex dependency graphs introduced serious reliability risks. These included API rate-limiting from the LLM provider, arbitrary CI runner timeouts on GitHub Actions, and hidden npm or PyPI registry network failures that had nothing to do with our experiment but would corrupt our results.

We therefore made the decision to validate all 18 core scenarios using a strict, manual, step-by-step protocol. This means we execute each command ourselves, pipe every output to a permanent log file, and commit the evidence directly to the repository. This gives us full control over every variable and guarantees that a failure in our results is genuinely caused by a dependency conflict, not by a transient CI infrastructure problem.

### 2b. CI Automation Will Still Be Demonstrated for Two Proof-of-Concept Scenarios

Because the thesis title explicitly references SBOM-Driven CI Pipelines, we cannot drop CI automation entirely. To satisfy this architectural requirement, we will build a fully automated end-to-end GitHub Actions workflow for exactly two representative scenarios: one from the npm ecosystem (Juice Shop) and one from the PyPI ecosystem (Airflow). The specific CVEs for these two scenarios have not yet been selected but will be chosen from our 18 pre-registered scenarios once manual validation is complete. This proves that the approach works in a real CI environment while keeping the core evaluation focused on the LLM reasoning quality.

### 2c. Repository Migration

All previous exploratory CI scripts, draft workflows, and intermediate outputs from the old repository have been archived. We created a clean, new repository (https://github.com/santuCG/llm-remediation-thesis-final) that contains only the finalised methodology documentation, the pre-registered datasets, the validated experiment outputs, and the strict logging artifacts. This ensures the repository is defence-ready for thesis submission.

## 3. What We Found in Our Experiments

### 3a. The Deterministic Baseline: 100 Percent Failure Rate

We ran the deterministic baseline for all 18 scenarios. In every single case, blindly applying the vulnerability scanner's recommended fix version failed. The package manager rejected the update.

For the 9 npm scenarios (Juice Shop), the failure was always an ERESOLVE conflict. This means npm detected that the fix version conflicted with strict peer dependency constraints defined by other packages in the dependency tree and refused to install it.

For the 9 PyPI scenarios (Airflow), the failure was always a ResolutionImpossible error. This means pip detected that the fix version violated strict version bounds declared in the requirements.txt constraint file and refused to resolve the dependency graph.

Every single baseline failure, including the exact error trace and the CI log URL from the original automated run, is permanently recorded in:
- `experiment/deterministic_baseline_results.json`

Here are two concrete examples:

**JS-01 (vm2, CVE-2023-32314):** The scanner recommended upgrading vm2 from 3.9.17 to 3.9.18. Running npm install with this version produced a fatal ERESOLVE conflict. The CI log is at https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28975890716.

**AF-01 (redshift-connector, CVE-2026-8838):** The scanner recommended upgrading redshift-connector to 2.1.14. Running pip install with this version produced a ResolutionImpossible error. The CI log is at https://github.com/santuCG/llm-sbom-remediation-experiment/actions/runs/28975952833.

### 3b. The LLM Remediation: Reasoning About Dependency Constraints

After recording the baseline failures, we fed the LLM (Gemini) the dependency graph context along with the baseline error trace for each scenario. The LLM was asked to propose a remediation strategy.

The complete set of LLM proposals, including the full rationale text, the recommended action type, the confidence score, and the gate pass/fail results, is recorded in:
- `experiment/llm_remediation_results.json`

Here is a summary of the LLM's outcomes across all 18 scenarios:

For npm (Juice Shop), the LLM proposed the OVERRIDE action type for 8 out of 9 scenarios, correctly identifying that npm's overrides mechanism can force a specific version past peer dependency conflicts. One scenario (JS-09, multer) received a CONSTRAINT_RELAXATION recommendation instead. Out of the 9 npm scenarios, 6 passed Gate 1 (dependency resolution succeeded), and 3 failed Gate 1 (resolution still failed even with the LLM strategy).

For PyPI (Airflow), the LLM proposed CONSTRAINT_RELAXATION for all 9 scenarios. However, 6 out of 9 PyPI scenarios were flagged as HALLUCINATED_VERSION, meaning the LLM recommended a fix version that does not actually exist on the PyPI registry. Only 3 PyPI scenarios had valid versions, and none of those passed Gate 1.

### 3c. What We Have Manually Validated So Far

We have completed full manual validation for two npm scenarios:

**JS-01 (vm2, CVE-2023-32314):** We applied the LLM's recommended npm override to force vm2 from 3.9.17 to 3.9.18. The override resolved successfully, npm install completed without errors, and Grype confirmed the target vulnerability (GHSA-whpj-8f3w-67p5) was no longer present in the remediated scan. The evidence files are:
- `experiment/raw_outputs/JS-01-baseline-sbom.json`
- `experiment/raw_outputs/JS-01-baseline-grype.json`
- `experiment/raw_outputs/JS-01-remediated-sbom.json`
- `experiment/raw_outputs/JS-01-remediated-grype.json`

**JS-08 (body-parser, CVE-2024-45590):** We applied the LLM's recommended npm override to force body-parser from 1.20.1 to 1.20.3. The override resolved successfully. Grype confirmed the target vulnerability (GHSA-qwcr-r2fm-qrc7) was eliminated. The evidence files are:
- `experiment/raw_outputs/JS-08-baseline-sbom.json`
- `experiment/raw_outputs/JS-08-baseline-grype.json`
- `experiment/raw_outputs/JS-08-remediated-sbom.json`
- `experiment/raw_outputs/JS-08-remediated-grype.json`

## 4. Key Technical Learnings

### 4a. Grype Uses GHSA Identifiers, Not CVE Identifiers

This was a significant practical discovery. When we examined the Grype vulnerability scan output, we found that 100 percent of the 182 vulnerability matches in our baseline scan used GitHub Security Advisory (GHSA) identifiers rather than CVE identifiers. For example, the vm2 sandbox escape vulnerability that we know as CVE-2023-32314 appears in Grype's output as GHSA-whpj-8f3w-67p5. Similarly, the body-parser denial of service vulnerability known as CVE-2024-45590 appears as GHSA-qwcr-r2fm-qrc7.

This matters for the thesis because our pre-registration documents and the NVD data all reference CVE identifiers, but the actual scanning tool we use for verification reports GHSA identifiers. We need to map between the two when confirming whether a specific vulnerability has been remediated. The GHSA to CVE mapping can be verified at:
- https://github.com/advisories/GHSA-whpj-8f3w-67p5 (maps to CVE-2023-32314)
- https://github.com/advisories/GHSA-qwcr-r2fm-qrc7 (maps to CVE-2024-45590)

You can verify this yourself by examining the raw Grype output. Open `experiment/raw_outputs/JS-01-baseline-grype.json` and search for the vulnerability id field. Every single entry starts with GHSA, not CVE.

### 4b. The LLM Hallucinated Fix Versions for 6 out of 9 PyPI Scenarios

One of the most striking findings is that the LLM hallucinated non-existent package versions for 6 out of 9 Airflow (PyPI) scenarios. These are flagged as HALLUCINATED_VERSION in the outcome field of `experiment/llm_remediation_results.json`. The affected scenarios are AF-02 (h11), AF-04 (mako), AF-05 (protobuf), AF-06 (jinja2), AF-07 (mysql-connector-python), and AF-09 (werkzeug). This is a meaningful negative result that directly addresses the reliability question in our research.

### 4c. The LLM Correctly Distinguishes Between npm and PyPI Remediation Strategies

For npm scenarios, the LLM consistently recommended using the overrides mechanism in package.json, which is the correct technical approach for bypassing ERESOLVE peer dependency conflicts. For PyPI scenarios, the LLM correctly identified that the problem lies in the requirements.txt constraint file and recommended CONSTRAINT_RELAXATION, which is the appropriate strategy for pip's ResolutionImpossible errors. This shows the LLM understands the fundamental architectural difference between the two ecosystems.

## 5. What We Will Do Next

The remaining work follows a clear sequence:

**Step 1:** Complete manual validation for the remaining 7 npm scenarios (JS-02 through JS-07 and JS-09) using the exact same protocol we used for JS-01 and JS-08. For each scenario, we will restore the environment to the clean baseline, inject the LLM recommended strategy, run the package manager resolution with output piped to a log file, verify the dependency tree, regenerate the SBOM using Syft, and rescan using Grype. All output files will be saved to the repository using the naming convention we have established (for example, JS-02-baseline-sbom.json, JS-02-remediated-grype.json).

**Step 2:** Complete manual validation for the 9 Airflow (PyPI) scenarios (AF-01 through AF-09) using the equivalent protocol adapted for pip and requirements.txt.

**Step 3:** Once all 18 scenarios are validated, select two representative CVEs (one npm, one PyPI) and build a fully automated GitHub Actions CI workflow that demonstrates end-to-end SBOM generation, vulnerability scanning, LLM remediation, and verification. This will satisfy the CI pipeline requirement of the thesis.

**Step 4:** Compile the final results across all 18 scenarios into the thesis results chapter, including pass/fail rates, hallucination rates, confidence score analysis, and the GHSA-to-CVE mapping methodology.

All validation logs and evidence files will continue to be committed directly to this repository as they are produced.
