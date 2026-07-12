# Research Update: Context-Aware Dependency Remediation in SBOM-Driven CI Pipelines Using Large Language Model

**Author:** Santosh Nagaraj, SRH University Berlin
**Date:** 13 July 2026
**Repository:** https://github.com/santuCG/llm-remediation-thesis-final

Dear Professor,

This document summarises the current state of my thesis experiment, explains the methodological decisions I have made so far, presents the key findings from my completed experiments on two core scenarios, and outlines the exact plan for the remaining work. Every claim made here is backed by a file path or URL so you can verify it directly.

## 1. What I Set Out To Do

The core research question asks whether an LLM can generate context-aware dependency remediation strategies that succeed where naive deterministic scanner recommendations fail. I designed 18 pre-registered scenarios, 9 from the OWASP Juice Shop application using the npm ecosystem and 9 from Apache Airflow using the PyPI ecosystem. Each scenario targets a specific known CVE in a transitive or direct dependency.

The full list of all 18 scenarios, including CVE identifiers, package names, severity scores, and fix versions, is recorded in:
- `experiment/final_18_scenarios.json`

The pre-registration documents that lock down my methodology before execution are stored in:
- `preregistration/protocol.md`
- `preregistration/JUICESHOP_PREREGISTRATION.md`
- `preregistration/AIRFLOW_PREREGISTRATION.md`
- `preregistration/PRE_REGISTRATION_AMENDMENT.md`
- `preregistration/MASTER_METHODOLOGY_RECORD.md`

## 2. What Major Changes I Made and Why

### 2a. From Fully Automated CI to Manual Validation for the Core 18 Scenarios

Originally, I planned to validate all 18 scenarios through fully automated GitHub Actions CI pipelines. During early testing in my previous repository, I discovered that automating LLM execution across 18 complex dependency graphs introduced serious reliability risks. These included API rate-limiting from the LLM provider, arbitrary CI runner timeouts on GitHub Actions, and hidden npm or PyPI registry network failures that had nothing to do with my experiment but would corrupt the results.

I therefore made the decision to validate all 18 core scenarios using a strict, manual, step-by-step protocol on my local execution environment. This means I execute each command myself, pipe every output to a permanent log file, and commit the evidence directly to the repository. This gives me full control over every variable and guarantees that a failure in my results is genuinely caused by a dependency conflict, not by a transient CI infrastructure problem.

### 2b. CI Automation Will Still Be Demonstrated for Two Proof-of-Concept Scenarios

Because the thesis title explicitly references SBOM-Driven CI Pipelines, I cannot drop CI automation entirely. To satisfy this architectural requirement, I will build a fully automated end-to-end GitHub Actions workflow for exactly two representative scenarios: one from the npm ecosystem (Juice Shop) and one from the PyPI ecosystem (Airflow). The specific CVEs for these two scenarios will be chosen from my 18 pre-registered scenarios once manual validation is complete. This proves that the approach works in a real CI environment while keeping the core evaluation focused on the LLM reasoning quality.

### 2c. Repository Migration

All previous exploratory CI scripts, draft workflows, and intermediate outputs from the old repository have been archived. I created a clean, new repository (https://github.com/santuCG/llm-remediation-thesis-final) that contains only the finalised methodology documentation, the pre-registered datasets, the validated experiment outputs, and the strict logging artifacts. This ensures the repository is defence-ready for thesis submission.

### 2d. Scenario Reallocation and Ghost CMS Disqualification

I permanently removed Ghost CMS from the study because it relies on `yarn` (`yarn.lock`). Including it would have introduced a third package manager, creating an uncontrolled variable. To maintain the 18 scenarios, I restructured the experiment into a strict 50/50 ecosystem split: 9 scenarios for OWASP Juice Shop (npm) and 9 for Apache Airflow (PyPI).

### 2e. Data Snapshotting to Prevent Drift

To prevent data drift during the manual validation phase, all enrichment data from external APIs (EPSS probabilities, KEV status, MITRE descriptions) was locally snapshotted. This ensures the LLM is evaluated on frozen intelligence data. Additionally, all 18 scenarios returned `KEV=FALSE`, meaning the KEV impact sub-question from the original proposal cannot be empirically evaluated.

## 3. What I Found in My Experiments (Current Progress: 2 Scenarios)

I am currently in the process of manually executing the validation protocol. So far, I have fully completed local execution and validation for 2 out of the 18 scenarios (both from the Juice Shop npm ecosystem). The remaining scenarios will be updated in the future following the exact same protocol.

### 3a. The Deterministic Baseline: Local Failure Evidence

For the two scenarios I have executed (JS-01 and JS-08), blindly applying the vulnerability scanner's recommended fix version failed. The package manager rejected the update due to an `ERESOLVE` conflict, meaning npm detected that the fix version conflicted with strict peer dependency constraints defined by other packages in the dependency tree.

The evidence for the existence of these vulnerabilities in the baseline state can be found in my local execution outputs:
- `experiment/raw_outputs/JS-01-baseline-grype.json` (Proves GHSA-whpj-8f3w-67p5 exists in vm2)
- `experiment/raw_outputs/JS-08-baseline-grype.json` (Proves GHSA-qwcr-r2fm-qrc7 exists in body-parser)

A consolidated historical record of the baseline error traces for all scenarios can also be found in:
- `experiment/deterministic_baseline_results.json`

### 3b. The LLM Remediation: Reasoning About Dependency Constraints

After recording the baseline failures, I fed the LLM the dependency graph context along with the baseline error trace. The LLM was asked to propose a remediation strategy.

The complete set of LLM proposals is recorded in:
- `experiment/llm_remediation_results.json`

For the two scenarios I have validated so far, the LLM correctly identified that npm's `overrides` mechanism can force a specific version past peer dependency conflicts. 

**JS-01 (vm2, CVE-2023-32314):** I applied the LLM's recommended npm override to force vm2 from 3.9.17 to 3.9.18. The override resolved successfully, npm install completed without errors, and Grype confirmed the target vulnerability was no longer present in the remediated scan. The local evidence files are:
- `experiment/raw_outputs/JS-01-remediated-sbom.json`
- `experiment/raw_outputs/JS-01-remediated-grype.json`

**JS-08 (body-parser, CVE-2024-45590):** I applied the LLM's recommended npm override to force body-parser from 1.20.1 to 1.20.3. The override resolved successfully, and Grype confirmed the target vulnerability was eliminated. The local evidence files are:
- `experiment/raw_outputs/JS-08-remediated-sbom.json`
- `experiment/raw_outputs/JS-08-remediated-grype.json`

## 4. Key Technical Learnings

### 4a. Grype Uses GHSA Identifiers, Not CVE Identifiers

This was a significant practical discovery during my local execution. When I examined the Grype vulnerability scan output, I found that 100 percent of the vulnerability matches in my baseline scans used GitHub Security Advisory (GHSA) identifiers rather than CVE identifiers. 

For example, the vm2 sandbox escape vulnerability that I track as CVE-2023-32314 appears in Grype's output as GHSA-whpj-8f3w-67p5. Similarly, the body-parser denial of service vulnerability known as CVE-2024-45590 appears as GHSA-qwcr-r2fm-qrc7.

This matters for the thesis because my pre-registration documents and the NVD data all reference CVE identifiers, but the actual scanning tool I use for verification reports GHSA identifiers. I need to map between the two when confirming whether a specific vulnerability has been remediated. The GHSA to CVE mapping can be verified at:
- https://github.com/advisories/GHSA-whpj-8f3w-67p5 (maps to CVE-2023-32314)
- https://github.com/advisories/GHSA-qwcr-r2fm-qrc7 (maps to CVE-2024-45590)

You can verify this by examining the raw Grype output (e.g., `experiment/raw_outputs/JS-01-baseline-grype.json`), where every vulnerability ID field starts with GHSA.

### 4b. LLM Wording Variability Despite Zero Temperature

My pre-registration protocol (`preregistration/protocol.md`) strictly dictates using a temperature of 0 to ensure deterministic, reproducible outputs from the LLM. However, I have learned that even with a temperature of 0 and strict JSON schema enforcement, the exact wording of the rationale text generated by the LLM can occasionally vary across different runs. While the final logic and the suggested commands remain consistent, the linguistic phrasing is not perfectly rigid, which is a valuable insight into the behavior of the model during these automated tasks.

### 4c. LLM Configuration and Limitations

The LLM (Google Gemini 2.5 Flash via Google AI Studio) is strictly configured with a temperature of 0.0 and "Thinking Mode" set to High. Its capabilities are heavily restricted (no internet access, no tool use), and it is forced to return a raw JSON object. The LLM's recommendation is treated purely as an engineering hypothesis, not experimental evidence. Evidence is only obtained after deterministic downstream validation.

### 4d. Runtime Verification and Dependency Shadowing

I observed that scanner counts do not strictly equal remediation quality. Fixing a specific CVE can sometimes introduce a new, parallel vulnerability via an upgraded sub-dependency. Furthermore, the runtime validation in this experiment only checks basic module loading, not comprehensive functional application testing. I also introduced the concept of "Dependency Shadowing," where upgrading a root dependency leaves vulnerable versions lingering beneath transitive parent packages.

## 5. What I Will Do Next

The remaining work follows a clear sequence:

**Step 1:** Complete manual validation for the remaining 7 npm scenarios (JS-02 through JS-07 and JS-09) using the exact same local execution protocol I used for JS-01 and JS-08. For each scenario, I will restore the environment to the clean baseline, inject the LLM recommended strategy, run the package manager resolution, verify the dependency tree, regenerate the SBOM using Syft, and rescan using Grype. All output files will be saved to `experiment/raw_outputs/`. I will update this document once this phase is complete.

**Step 2:** Complete manual validation for the 9 Airflow (PyPI) scenarios (AF-01 through AF-09) using the equivalent protocol adapted for pip and `requirements.txt`.

**Step 3:** Once all 18 scenarios are validated, select two representative CVEs (one npm, one PyPI) and build a fully automated GitHub Actions CI workflow that demonstrates end-to-end SBOM generation, vulnerability scanning, LLM remediation, and verification. This will satisfy the CI pipeline requirement of the thesis.

**Step 4:** Compile the final results across all 18 scenarios into the thesis results chapter, including pass/fail rates, confidence score analysis, and the GHSA-to-CVE mapping methodology.

All validation logs and evidence files will continue to be committed directly to this repository as they are produced.
