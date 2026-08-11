# Empirical Evaluation of LLM-Assisted Dependency Remediation in SBOM-Driven CI/CD Pipelines

**Master's Thesis — Santosh Nagaraj**  
**SRH University Berlin — MSc Computer Science (Cybersecurity)**  

This repository serves as the empirical evidence archive and experimental framework for the Master's thesis investigating context-aware dependency remediation.

> **Navigation Hub:** To prevent synchronisation drift, this README does not duplicate methodology, results, or scientific discussion. It serves strictly as a directory to the canonical, mathematically verified documentation and raw execution evidence contained within the repository.

> **Repository status:** The thesis results, evidence, and analysis correspond to the `pipeline-v2-phase1` branch. Two supplementary research branches were used to produce evidence now also copied into this branch for self-containment (§3.9a/§4.9/§4.11/§4.12 of the thesis, Section 5 below): `research/pipeline-v2-lockfile-controlled` (controlled lockfile-preservation validation) and `research/hint-removal-ablation` (no-hint ablation study, including its JS-08 extension); both remain on the remote for full CI-run-level provenance. All other branches (`research/js01-graph-reasoning`, `research/no-hint-search-grounding`, `test-js-09`, `feature/reproducible-platform`, and this fork's own `main`) are historical or exploratory development work, not part of the evaluated pipeline, and were not used to produce any result reported in the thesis; `research/js01-graph-reasoning` specifically is discussed in §5.9 of the thesis precisely because its results are excluded.

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

This directory is the ultimate source of truth for the repository, and is the sole basis for the thesis's primary eighteen-scenario dataset and research-question conclusion.

Supplementary evidence, explaining rather than replacing the primary dataset (see the thesis's §3.9a and §5.9a for what is, and is not, claimed from it):
*   [results/execution_evidence_lockfile_preserved/](results/execution_evidence_lockfile_preserved/) — controlled lockfile-preservation validation
*   [results/execution_evidence_no_hint/](results/execution_evidence_no_hint/) and [results/execution_evidence_no_hint_lockfile_preserved/](results/execution_evidence_no_hint_lockfile_preserved/) — no-hint ablation study and its JS-08 extension

## 6. Where is the pre-registration?
The pre-registration documents locking the 18 specific vulnerability scenarios before the experiments commenced are located in:
*   [preregistration/MASTER_METHODOLOGY_RECORD.md](preregistration/MASTER_METHODOLOGY_RECORD.md)
*   [preregistration/PRE_REGISTRATION_AMENDMENT.md](preregistration/PRE_REGISTRATION_AMENDMENT.md)

## 7. Where are the historical/evolution docs?
Early-stage methodologies, proof-of-concept workflows, and manual testing protocols are preserved for historical completeness in:
*   [docs/07-manual-validation-protocol.md](docs/07-manual-validation-protocol.md)
*   [docs/08-cicd-pipeline-poc.md](docs/08-cicd-pipeline-poc.md)
*   [docs/methodology_evolution_record.md](docs/methodology_evolution_record.md)

## 8. Where are the independent audit reports?
The independent reproducibility and methodological verification reports conducted prior to academic submission are located in:
*   [docs/audit/](docs/audit/)

These reports document the audit process itself and should be treated as a historical record of findings, not as evidence — the underlying claims are verified against the primary sources listed above.

## 9. Local tool requirements
This repository does not commit tool binaries (`tools/**/bin/`, `tools/**/*.exe` are gitignored). Both CI workflows (`.github/workflows/generic-remediation.yml`, `.github/workflows/grype-baseline.yml`) download these exact pinned versions at run time, and any local reproduction should use the same versions:
*   **Syft v1.44.0** — [anchore/syft releases](https://github.com/anchore/syft/releases/tag/v1.44.0)
*   **Grype v0.112.0** — [anchore/grype releases](https://github.com/anchore/grype/releases/tag/v0.112.0)
*   **GitHub CLI (`gh`)** — used locally for workflow dispatch and log retrieval; any current release is compatible, no version pinning required for this role.
