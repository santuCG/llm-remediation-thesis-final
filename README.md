# Empirical Evaluation of LLM-Assisted Dependency Remediation in SBOM-Driven CI/CD Pipelines

**Master's Thesis — Santosh Nagaraj**  
**SRH University Berlin — MSc Computer Science (Cybersecurity)**  

This repository serves as the empirical evidence archive and experimental framework for the Master's thesis investigating context-aware dependency remediation.

> **Navigation Hub:** To prevent synchronisation drift, this README does not duplicate methodology, results, or scientific discussion. It serves strictly as a directory to the canonical, mathematically verified documentation and raw execution evidence contained within the repository.

---

## 1. What is this repository?
This repository contains the complete, reproducible experimental pipeline and the recorded execution artifacts used to evaluate Large Language Model (LLM) reasoning within Software Bill of Materials (SBOM) driven CI/CD workflows. It includes the automation scripts, the vulnerability intelligence pipelines, and the empirical evidence proving execution integrity.

## 2. What was researched?
This research evaluated whether an LLM—supplied with structured vulnerability intelligence, threat signals (CVSS, EPSS, KEV), and dependency graph constraints—can generate dependency remediation strategies that resolve software supply chain vulnerabilities where applying a deterministic vulnerability scanner's direct upgrade recommendation fails.

## 3. Where is the final methodology?
The canonical methodology, describing the strict 12-stage experimental pipeline and constraint-aware remediation workflow, is located in:
*   [docs/04-experimental-methodology.md](docs/04-experimental-methodology.md)

*(For an overview of the platform and toolchains, see [docs/02-experimental-environment.md](docs/02-experimental-environment.md).)*

## 4. Where are the results?
The aggregated results, statistical findings, and scientific discussion are located in:
*   [docs/05-results-and-discussion.md](docs/05-results-and-discussion.md)

## 5. Where is the execution evidence?
The raw, tier-1 empirical evidence—including `build.log`, `test.log`, generated SBOMs, and the exact input/output of the LLM for every scenario—is located in:
*   [results/execution_evidence/](results/execution_evidence/)

This directory is the ultimate source of truth for the repository.

## 6. Where is the pre-registration?
The pre-registration documents locking the 18 specific vulnerability scenarios before the experiments commenced are located in:
*   [preregistration/MASTER_METHODOLOGY_RECORD.md](preregistration/MASTER_METHODOLOGY_RECORD.md)
*   [preregistration/PRE_REGISTRATION_AMENDMENT.md](preregistration/PRE_REGISTRATION_AMENDMENT.md)

## 7. Where are the historical/evolution docs?
Early-stage methodologies, proof-of-concept workflows, and manual testing protocols are preserved for historical completeness in:
*   [docs/07-manual-validation-protocol.md](docs/07-manual-validation-protocol.md)
*   [docs/08-cicd-pipeline-poc.md](docs/08-cicd-pipeline-poc.md)
*   [docs/methodology_evolution_record.md](docs/methodology_evolution_record.md)

## 8. Where are the zero-trust audit reports?
The final, independent, zero-trust cryptographic and methodological verification reports conducted prior to academic submission are located in:
*   [audit_reports/](audit_reports/)
