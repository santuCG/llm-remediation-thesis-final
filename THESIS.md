# [University name — to be provided]
## [Faculty / Department — to be provided]

<br>

# Empirical Evaluation of LLM-Assisted Dependency Remediation in SBOM-Driven CI/CD Pipelines

<br>

A thesis submitted in partial fulfilment of the requirements for the degree of
**Master of Science in Computer Science (Cybersecurity)**

by

**Santosh Nagaraj**
Matriculation Number: **[to be provided]**

First Supervisor: **[Primary Supervisor — to be provided]**
Second Supervisor: **[Associate Supervisor — to be provided]**

Submission Date: **[to be provided]**

---

> **Author's note on evidence and citations (please read).** This thesis was written against a frozen research repository (tag `thesis-freeze-2026-08-02`, commit `5a227c8f`). Every quantitative statement is drawn from files in that repository and is cited by path. The thesis uses five evidence labels to keep claims traceable: **FACT** (direct repository evidence), **OBSERVATION** (a measured experimental result), **INTERPRETATION** (the author's explanation), **LIMITATION** (a known weakness), and **FUTURE WORK** (not implemented). External citations use IEEE format and refer only to real, verifiable sources (standards, tools, vulnerability records, and organisations). No citation has been fabricated. Where a claim would need a specific peer-reviewed source that could not be verified from the repository, this is marked **[ACADEMIC CITATION TO BE ADDED BY AUTHOR]** rather than invented.

---

## Abstract

Modern software depends heavily on third-party open-source packages. A single vulnerable package can affect many applications at once, often through transitive dependencies that a project does not declare directly. Automated tools now detect these vulnerabilities well. Fixing them is harder. A direct version upgrade frequently fails when the vulnerable package is nested beneath other packages, because package managers enforce version constraints across the whole dependency graph.

This thesis evaluates whether a Large Language Model (LLM) can generate context-aware remediation strategies for known dependency vulnerabilities, and whether those strategies pass deterministic validation. The work does not propose replacing vulnerability scanners. It treats each LLM recommendation as an engineering hypothesis that must be verified by a package manager, a dependency-graph check, a regenerated Software Bill of Materials (SBOM), and a repeat vulnerability scan.

The study uses a controlled pipeline built on GitHub Actions, Syft for SBOM generation, and Grype for vulnerability scanning. It evaluates eighteen pre-registered scenarios across two applications: OWASP Juice Shop (npm) and Apache Airflow (pip). For each scenario the LLM receives structured vulnerability intelligence and the dependency subgraph, and returns a structured remediation strategy. A separate deterministic baseline applies the scanner's recommended version bump without any LLM involvement.

The results show a clear split between the two ecosystems. **OBSERVATION:** For all nine pip scenarios the deterministic baseline already succeeded — it built and removed the target vulnerability — so the LLM offered no advantage there. For all nine npm scenarios the deterministic baseline did not complete, while the LLM pipeline reached a validated state in which the target vulnerability was absent from the regenerated scan. **INTERPRETATION:** The LLM's contribution is specific to transitive npm cases, where dependency shadowing defeats naive upgrades. **LIMITATION:** The npm applications did not fully compile under their pinned legacy toolchain in either approach; this failure is pre-existing and unrelated to the remediation, and it means "vulnerability removed" is not the same as "application builds." The thesis reports these findings with their limitations and does not generalise beyond the evaluated scenarios.

*Keywords: software supply chain security, dependency remediation, SBOM, vulnerability scanning, large language models, CI/CD.*

---

## Acknowledgements

*[To be completed by the author.]*

---

## Table of Contents

1. Introduction
   1.1 Background
   1.2 Problem Statement
   1.3 Research Question
   1.4 Hypothesis
   1.5 Objectives
   1.6 Scope
   1.7 Limitations
   1.8 Significance
   1.9 Structure of the Thesis
2. Literature Review
   2.1 Theoretical Framework
   2.2 Literature Gap
3. Methodology
   3.1 Research Design
   3.2 Scenario Selection
   3.3 Pipeline Design
   3.4 Data Collection
   3.5 Data Analysis
   3.6 Reliability
   3.7 Validity
   3.8 Ethics
   3.9 Methodology Limitations
4. Findings and Discussion
   4.1 Experimental Results
   4.2 Scenario Analysis
   4.3 Research Question Analysis
   4.4 Discussion
   4.5 Comparison
   4.6 Chapter Summary
5. Conclusion
   5.1 Overall Conclusion
   5.2 Research Contributions
   5.3 Limitations
   5.4 Recommendations
   5.5 Future Work
References
Appendices

---

## List of Figures

- **Figure 1.** The LLM-assisted remediation pipeline (twelve stages). *Source: `.github/workflows/generic-remediation.yml`, `docs/04-experimental-methodology.md`.*
- **Figure 2.** The deterministic baseline pipeline. *Source: `.github/workflows/grype-baseline.yml`.*
- **Figure 3.** Transitive dependency shadowing in scenario JS-01 (`juice-shop → juicy-chat-bot → vm2`). *Source: `results/execution_evidence/JS-01/llm-request.json`.*
- **Figure 4.** Deterministic baseline versus LLM pipeline outcomes by ecosystem. *Source: `results/reproducibility_verification/`, `results/execution_evidence/`.*

*(Figures are described textually in this draft; the author will render them.)*

---

## List of Tables

- **Table 1.** The eighteen pre-registered scenarios.
- **Table 2.** Pipeline stages and their purpose.
- **Table 3.** Recorded LLM-pipeline metrics for all eighteen scenarios.
- **Table 4.** Deterministic baseline outcomes by ecosystem.
- **Table 5.** Deterministic baseline versus LLM pipeline — summary comparison.
- **Table 6.** Threats to validity.
- **Table 7.** Limitations.

---

## List of Abbreviations

| Abbreviation | Meaning |
|---|---|
| CI/CD | Continuous Integration / Continuous Delivery |
| CVE | Common Vulnerabilities and Exposures |
| CVSS | Common Vulnerability Scoring System |
| EPSS | Exploit Prediction Scoring System |
| GHSA | GitHub Security Advisory |
| KEV | Known Exploited Vulnerabilities (CISA catalog) |
| LLM | Large Language Model |
| NVD | National Vulnerability Database |
| RCE | Remote Code Execution |
| SBOM | Software Bill of Materials |
| SCA | Software Composition Analysis |
| SPDX | Software Package Data Exchange |

---

# Chapter 1 — Introduction

## 1.1 Background

Modern applications are assembled, not only written. A typical project declares a small number of direct dependencies, and each of those pulls in further packages. The result is a large dependency graph in which most packages are *transitive* — present because another package requires them, not because the developer chose them directly.

This model speeds up development. It also concentrates risk. A flaw in one widely used package can affect many applications at the same time. Two well-documented incidents illustrate the scale. The Log4Shell vulnerability in the Apache Log4j library (CVE-2021-44228) exposed a very large number of Java applications through a single logging component [1]. The XZ Utils backdoor (CVE-2024-3094) introduced malicious code into a core Linux compression library and threatened widely deployed infrastructure [2]. **FACT:** Both incidents are recorded in the National Vulnerability Database and are referenced in the project's own background material (`docs/01-overview.md`).

To manage this risk, the industry has adopted the Software Bill of Materials (SBOM). An SBOM is a machine-readable inventory of every package in an application. Two open standards describe SBOM formats: SPDX, maintained by the Linux Foundation [3], and CycloneDX, maintained by OWASP [4]. Tools such as Syft generate SBOMs [5], and scanners such as Grype cross-reference an SBOM against vulnerability databases including the NVD [6] and the CISA Known Exploited Vulnerabilities catalog [7].

Detection has therefore improved. Remediation has not kept pace. Knowing that a package is vulnerable does not tell a developer how to fix it safely. For transitive packages this is genuinely difficult, because the fix must satisfy the constraints of the whole dependency graph, not just a single line in a manifest file.

## 1.2 Problem Statement

The core problem this thesis addresses is the gap between vulnerability *detection* and vulnerability *remediation*.

A naive fix is to upgrade the vulnerable package to a patched version. For a direct dependency in a flat-resolution ecosystem, such as Python's pip, this often works. For a transitive dependency in a nested-resolution ecosystem, such as Node.js npm, it often does not. The vulnerable version can remain nested beneath an intermediate parent that pins it, a situation known as dependency shadowing. Forcing the update can also trigger package-manager resolution errors (for example npm `ERESOLVE` or `EOVERRIDE`).

**INTERPRETATION:** Traditional Software Composition Analysis (SCA) tools recommend version bumps but do not reason about these graph-level constraints. This leaves a decision-support gap: given a detected vulnerability and its dependency context, what is a remediation strategy that both removes the vulnerability and respects the constraints of the dependency graph?

This thesis investigates whether an LLM can help fill that gap, and whether its recommendations survive deterministic verification.

## 1.3 Research Question

The primary research question is stated in the project's own overview and is reproduced here without change.

> **RQ (primary):** Can an LLM generate context-aware dependency remediation strategies that successfully resolve selected transitive dependency vulnerabilities under controlled SBOM-driven workflows, where basic deterministic package upgrade strategies do not achieve the intended remediation objective? *(Source: `docs/01-overview.md`.)*

To analyse this question against the evidence, the thesis examines three aspects of it, without introducing any new research question:

- **A. Generation.** Does the LLM produce structurally valid, non-hallucinated remediation strategies for the selected vulnerabilities?
- **B. Validation.** Do those strategies pass deterministic validation (installation, dependency-graph verification, SBOM regeneration, and repeat scanning)?
- **C. Comparison.** How do the LLM outcomes compare with a deterministic scanner-recommended baseline, especially for transitive cases?

## 1.4 Hypothesis

The study's documentation frames every LLM recommendation as an *engineering hypothesis* rather than an accepted result (`docs/03-llm-configuration.md`, `docs/04-experimental-methodology.md`). The research hypothesis follows from this framing:

> **H:** For transitive dependency vulnerabilities where a deterministic direct upgrade does not achieve the remediation objective, an LLM supplied with structured vulnerability intelligence and dependency-graph context can generate remediation strategies that, after deterministic validation, remove the target vulnerability.

The design is deliberately conservative. A recommendation is counted only if it passes deterministic gates, not because the LLM asserts it is correct.

## 1.5 Objectives

**General objective.** To evaluate, under controlled and reproducible conditions, whether LLM-generated remediation strategies can resolve selected dependency vulnerabilities that deterministic upgrades do not.

**Specific objectives.**
1. To design an SBOM-driven CI/CD pipeline that generates an SBOM, detects vulnerabilities, requests an LLM remediation strategy, applies it, and validates the result deterministically.
2. To define a deterministic baseline pipeline that applies the scanner-recommended version without LLM involvement.
3. To evaluate both pipelines on eighteen pre-registered scenarios across two applications and two package ecosystems.
4. To record complete, verifiable execution evidence for every scenario.
5. To compare the LLM pipeline against the deterministic baseline and report the findings with their limitations.

## 1.6 Scope

The study evaluates dependency remediation *after* a vulnerability has already been detected. Following the project's stated scope (`docs/01-overview.md`), it does **not** evaluate vulnerability detection accuracy, CVSS prediction, exploit prediction, SCA performance, or the replacement of scanners. It treats the LLM as a decision-support component that operates after deterministic detection, not as a discovery tool.

## 1.7 Limitations

The main limitations are summarised here and stated in full in Chapter 5 and in the repository file `THESIS_LIMITATIONS.md`.

- The npm target application does not fully compile under its pinned legacy TypeScript toolchain, in either the baseline or the LLM pipeline. This failure is pre-existing and unrelated to remediation.
- Exact scanner counts are not bit-for-bit reproducible because the scanner uses a live vulnerability database; the target-vulnerability detection signal, however, did reproduce.
- The study uses one LLM configuration, two applications, and a strict one-retry policy.

## 1.8 Significance

**INTERPRETATION:** The study contributes an honest, evidence-based evaluation of a specific and practical question: can an LLM act as a graph-aware decision-support layer for dependency remediation, verified by deterministic gates rather than trusted on assertion? Its value lies less in a headline success rate and more in the careful separation of what was measured (vulnerability removal, dependency-graph verification) from what was not achieved (full application compilation), and in identifying exactly where an LLM adds value (transitive npm cases) and where it does not (flat pip cases).

## 1.9 Structure of the Thesis

Chapter 2 reviews the relevant tools, standards, and concepts, and identifies the literature gap. Chapter 3 describes the research design, the eighteen scenarios, the pipeline, and the analysis method. Chapter 4 presents the findings, analyses them against the research question, and discusses them. Chapter 5 concludes, states contributions and limitations, and lists future work.

---

# Chapter 2 — Literature Review

*This chapter synthesises the tools, standards, and concepts on which the study depends, and then states the gap the study addresses. External references are limited to verifiable standards, tools, and vulnerability records. Specific peer-reviewed sources that the author intends to add are marked accordingly.*

## 2.1 Theoretical Framework

**Software supply chain risk.** An application inherits the security posture of every package it includes, directly or transitively. Real incidents such as Log4Shell (CVE-2021-44228) [1] and the XZ Utils backdoor (CVE-2024-3094) [2] show how one package can create widespread exposure. This motivates tooling that inventories and checks dependencies automatically.

**Software Bill of Materials (SBOM).** An SBOM lists every component in a build in a machine-readable form. The two common standards are SPDX [3] and CycloneDX [4]. This study generates SBOMs in SPDX-JSON format using Syft [5]. **FACT:** The pipeline invokes Syft with SPDX-JSON output (`.github/workflows/generic-remediation.yml`).

**Vulnerability scanning and databases.** A scanner matches SBOM components against known-vulnerability data. This study uses Grype [8], which draws on data such as the NVD [6] and GitHub Security Advisories. The CISA KEV catalog [7] records vulnerabilities known to be exploited in the wild.

**Vulnerability prioritisation.** Not all vulnerabilities are equally urgent. Three signals are widely used: CVSS, a severity score [9]; EPSS, an estimated probability of exploitation in the near term [10]; and KEV membership, which marks confirmed active exploitation [7]. **FACT:** The pipeline ranks candidates by KEV, then EPSS, then CVSS in descending order (`scripts/remediation/prioritize.py`).

**Dependency resolution models.** Package ecosystems resolve versions differently. Python's pip uses a mostly flat model with a single installed version per package, so a direct upgrade usually propagates cleanly. Node.js npm uses a nested model that can hold multiple versions and can pin a transitive version beneath a parent; npm provides an `overrides` mechanism to force a transitive version [11]. This structural difference is central to the study's findings.

**LLMs for security and code tasks.** LLMs have been applied to code generation, code review, and security analysis. Their known weakness is confident but incorrect output, including invented package versions. **INTERPRETATION:** This is exactly why the present study does not trust LLM output directly; it validates every recommendation with deterministic tools. [ACADEMIC CITATION TO BE ADDED BY AUTHOR: recent peer-reviewed work on LLMs for vulnerability repair / dependency management.]

## 2.2 Literature Gap

The tools above solve detection and prioritisation well. **INTERPRETATION:** They are weaker at *remediation*, and weakest at remediation of transitive vulnerabilities that cannot be fixed by a simple direct upgrade. Scanners typically recommend a fixed version but do not reason about whether that version can be installed given the constraints of the whole dependency graph.

LLMs have been studied for detection and for general code generation, but their use as a *constraint-aware remediation* layer — one that reads the dependency subgraph, proposes a strategy such as a transitive override, and is then held to deterministic verification — is not well established. [ACADEMIC CITATION TO BE ADDED BY AUTHOR.]

**The gap this study addresses:** an empirical, reproducible evaluation of LLM-generated dependency remediation strategies, verified by deterministic gates, on transitive vulnerabilities where deterministic upgrades do not succeed.

---

# Chapter 3 — Methodology

## 3.1 Research Design

The study uses a controlled, reproducible experiment. It compares two pipelines on the same eighteen scenarios:

1. A **deterministic baseline** pipeline that applies the scanner-recommended version bump without any LLM (`.github/workflows/grype-baseline.yml`).
2. An **LLM-assisted** pipeline that asks an LLM for a remediation strategy and then validates it deterministically (`.github/workflows/generic-remediation.yml`).

Both pipelines run in GitHub Actions on isolated runners. Each scenario is pre-registered, meaning its target vulnerability is fixed in advance so that results do not depend on scanner ordering. **FACT:** The eighteen scenario definitions are stored in `results/scenarios/`, and the pre-registration material is in `preregistration/`.

The design is conservative by intention. Success is defined by deterministic gates, not by the LLM's own claim (`docs/04-experimental-methodology.md`).

## 3.2 Scenario Selection

The study evaluates eighteen scenarios across two open-source applications and two ecosystems: OWASP Juice Shop (npm) [12] and Apache Airflow (pip) [13]. Nine scenarios (JS-01 to JS-09) target npm packages; nine (AF-01 to AF-09) target pip packages. Each scenario targets one known vulnerability with a published fixed version.

Table 1 lists all eighteen scenarios. **FACT:** Every value is taken from the per-scenario file `results/execution_evidence/<ID>/selected-candidate.json`.

**Table 1. The eighteen pre-registered scenarios.**

| ID | Application | Ecosystem | Package | CVE | Severity | CVSS | Vulnerable → Fixed |
|---|---|---|---|---|---|---|---|
| JS-01 | Juice Shop | npm | vm2 | CVE-2023-32314 | critical | 9.8 | 3.9.17 → 3.9.18 |
| JS-02 | Juice Shop | npm | handlebars | CVE-2026-33937 | critical | 9.8 | 4.7.7 → 4.7.9 |
| JS-03 | Juice Shop | npm | form-data | CVE-2025-7783 | critical | 9.4 | 2.3.3 → 2.5.4 |
| JS-04 | Juice Shop | npm | crypto-js | CVE-2023-46233 | critical | 9.1 | 3.3.0 → 4.2.0 |
| JS-05 | Juice Shop | npm | jsonwebtoken | CVE-2015-9235 | critical | 0.0* | 0.1.0 → 4.2.2 |
| JS-06 | Juice Shop | npm | lodash | CVE-2021-23337 | high | 7.2 | 2.4.2 → 4.17.21 |
| JS-07 | Juice Shop | npm | ws | CVE-2024-37890 | high | 7.5 | 7.4.6 → 7.5.10 |
| JS-08 | Juice Shop | npm | body-parser | CVE-2024-45590 | high | 7.5 | 1.20.1 → 1.20.3 |
| JS-09 | Juice Shop | npm | multer | CVE-2026-3520 | high | 8.7 | 1.4.5-lts.1 → 2.1.1 |
| AF-01 | Airflow | pip | redshift-connector | CVE-2026-8838 | critical | 9.8 | 2.1.1 → 2.1.14 |
| AF-02 | Airflow | pip | h11 | CVE-2025-43859 | critical | 9.1 | 0.14.0 → 0.16.0 |
| AF-03 | Airflow | pip | cryptography | CVE-2023-50782 | high | 7.5 | 41.0.7 → 42.0.0 |
| AF-04 | Airflow | pip | mako | CVE-2026-44307 | high | 8.7 | 1.3.5 → 1.3.12 |
| AF-05 | Airflow | pip | protobuf | CVE-2026-0994 | high | 8.2 | 4.25.3 → 5.29.6 |
| AF-06 | Airflow | pip | werkzeug | CVE-2024-34069 | high | 7.5 | 2.2.3 → 3.0.3 |
| AF-07 | Airflow | pip | mysql-connector-python | CVE-2024-21272 | high | 7.5 | 8.4.0 → 9.1.0 |
| AF-08 | Airflow | pip | google-cloud-aiplatform | CVE-2026-2473 | high | 7.7 | 1.53.0 → 1.133.0 |
| AF-09 | Airflow | pip | werkzeug | CVE-2024-34069 | high | 7.5 | 2.2.3 → 3.0.3 |

*\*JS-05 records a CVSS of 0.0 in `selected-candidate.json`; this is a recorded data value and is discussed as a data-quality note in Chapter 4.*

**LIMITATION:** Scenarios AF-06 and AF-09 both resolve to the same package and CVE (`werkzeug` / CVE-2024-34069). The project discloses that the executed target for one scenario differs from its original pre-registered identity; this is recorded in `preregistration/PRE_REGISTRATION_AMENDMENT.md` and is treated transparently rather than hidden.

## 3.3 Pipeline Design

The LLM pipeline follows a fixed sequence of stages, documented as a twelve-stage workflow (`docs/04-experimental-methodology.md`) and implemented in `.github/workflows/generic-remediation.yml`. Table 2 summarises the stages.

**Table 2. Pipeline stages and their purpose.**

| Stage | Action | Purpose |
|---|---|---|
| Baseline install | Install pinned dependencies | Establish the vulnerable baseline |
| SBOM generation | Run Syft (SPDX-JSON) | Inventory all components |
| Vulnerability scan | Run Grype | Detect vulnerabilities |
| Prioritisation | Rank by KEV → EPSS → CVSS | Select the pre-registered target |
| Context building | Collect dependency subgraph | Give the LLM graph context |
| LLM reasoning | Request a strategy | Generate the remediation hypothesis |
| Apply fix | Edit the manifest | Enact the recommendation |
| Fallback / retry | One retry on failure | Allow a single refined attempt |
| Rebuild | Reinstall dependencies | Realise the change |
| SBOM regeneration | Run Syft again | Inventory the remediated state |
| Repeat scan | Run Grype again | Check the target vulnerability |
| Validation | Run `validator.py` | Confirm the target is absent |

**Tools and versions. FACT:** The pipeline pins Syft 1.44.0 and Grype 0.112.0 (`.github/workflows/generic-remediation.yml`). The scanner uses a live vulnerability database; this is discussed under reliability.

**LLM configuration. FACT:** The LLM is Google Gemini (primary model `gemini-3.6-flash`, with a documented fallback list), configured with `temperature 0.0, topP 1.0, topK 1, seed 42`, and a strict JSON response schema (`results/execution_evidence/AF-01/llm-request.json`, `scripts/remediation/llm_reasoner.py`). The response schema requires the fields `reasoning`, `strategy`, `remediation_type`, `recommended_package_version`, and `manifest_patch`.

**Prompt. FACT:** The system instruction directs the model to evaluate the topological subgraph, consider all feasible strategies (direct upgrade, transitive override, resolution, replacement, or manual review), and not to invent package versions (`results/execution_evidence/AF-01/llm-request.json`). On a retry, the prompt also includes the previous build failure so the model can refine its recommendation.

**Retry policy. FACT:** The pipeline permits at most one retry (`.agents/AGENTS.md`, rule 5; `scripts/remediation/retry_remediation.py`).

**Validation gates. FACT:** The validator confirms whether the target vulnerability is present in the regenerated scan and records the result in `metrics.json` (`scripts/remediation/validator.py`). The validator is responsible only for vulnerability verification; build status is recorded separately by the workflow.

**Figure 1** should show this twelve-stage flow. **Figure 2** should show the shorter deterministic baseline, which applies the scanner-recommended version and then scans, without any LLM stage.

## 3.4 Data Collection

Each scenario produces a complete evidence folder at `results/execution_evidence/<ID>/`. **FACT:** A folder contains, among other files, the baseline SBOM and scan, the candidate ranking, the LLM request and response, the before/after manifests, the rebuild and test logs, the regenerated scan, the metrics, and an experiment manifest with artifact hashes.

Provenance is recorded in `experiment_manifest.json`, including the repository commit and the GitHub Actions run identifier. **LIMITATION:** During the project's audit, nine manifests were found to contain non-authentic commit hashes; these were corrected against the real run history and the correction is documented (`docs/audit/`).

## 3.5 Data Analysis

The analysis uses the deterministic gate outcomes recorded in each `metrics.json`. The key recorded fields are `build_success` (installation completed), `dependency_verified` (the intended version resolved in the graph), and `rescan_success` (the target vulnerability was absent after remediation). The comparison against the deterministic baseline uses the same fields from `results/reproducibility_verification/`, which stores fresh baseline runs produced during the project's reproducibility audit.

**INTERPRETATION:** The primary analytical signal is `rescan_success` (was the target vulnerability removed), read together with `build_success` and the build logs, so that "vulnerability removed" is never confused with "application compiles."

## 3.6 Reliability

The study improves reliability through version-pinned tools, a fixed model configuration (`temperature 0.0`, fixed seed), pinned vulnerability-intelligence snapshots, and repeated restoration of the baseline (`docs/05-results-and-discussion.md`).

**OBSERVATION:** During the reproducibility audit, the target-vulnerability detection signal reproduced for all eighteen scenarios. **LIMITATION:** Exact scanner counts did not reproduce bit-for-bit, because Grype downloads a live vulnerability database on each run; the project documents this and the fact that a database-pinning clause was specified but not implemented (`docs/06-reproducibility.md`, `THESIS_LIMITATIONS.md`).

## 3.7 Validity

The study's threats to validity are recorded in `docs/05-results-and-discussion.md` and summarised in Table 6.

**Table 6. Threats to validity.**

| Type | Threat | Mitigation / disclosure |
|---|---|---|
| Internal | Environmental variation could explain differences | Version pinning, fixed configuration, baseline restoration |
| Construct | "Success" could be misread as full functionality | Success defined as vulnerability removal + install + graph verification, not full compilation |
| External | Two applications, two ecosystems | Findings not generalised beyond the evaluated scenarios |
| Reliability | Live scanner database | Target-detection reproduced; exact counts disclosed as non-reproducible |

## 3.8 Ethics

The study uses two open-source applications. OWASP Juice Shop is a deliberately vulnerable training application; Apache Airflow is a widely used open-source platform used here in a controlled test setting. The work involves no human participants and no personal data. It targets already-public, already-fixed vulnerabilities, and its purpose is defensive: to evaluate a remediation aid. Secrets used during execution (for example an LLM API key) are handled through repository secrets and are not part of the published evidence; the project's audit checked for leaked credentials (`docs/audit/`).

## 3.9 Methodology Limitations

**LIMITATION.** The main methodological limitations are: a single LLM configuration; two applications and two ecosystems; a strict one-retry policy; a live scanner database that prevents exact count reproduction; and the pre-existing npm compilation failure that limits what "success" can mean for the npm scenarios. These are carried into Chapter 4 and Chapter 5 rather than set aside.

---

# Chapter 4 — Findings and Discussion

*This chapter reports only measured results. Each result is drawn from repository files and labelled. Limitations are discussed alongside positive findings, as required.*

## 4.1 Experimental Results

### 4.1.1 Recorded LLM-pipeline outcomes

Table 3 shows the recorded deterministic-gate outcomes for the LLM pipeline across all eighteen scenarios. **FACT:** Every value is taken from `results/execution_evidence/<ID>/metrics.json`.

**Table 3. Recorded LLM-pipeline metrics (all eighteen scenarios).**

| ID | Strategy | Retry | build_success | dependency_verified | rescan_success | failure_stage |
|---|---|---|---|---|---|---|
| JS-01 | manual_review | 1 | true | true | true | build |
| JS-02 | transitive_override | 1 | true | true | true | build |
| JS-03 | transitive_override | 1 | true | true | true | build |
| JS-04 | direct_upgrade | 1 | true | true | true | build |
| JS-05 | direct_upgrade | 1 | true | true | true | build |
| JS-06 | direct_upgrade | 1 | true | true | true | build |
| JS-07 | transitive_override | 1 | true | true | true | build |
| JS-08 | transitive_override | 1 | true | true | true | build |
| JS-09 | direct_upgrade | 1 | true | true | true | none |
| AF-01 | direct_upgrade | 0 | true | true | true | none |
| AF-02 | direct_upgrade | 0 | true | true | true | none |
| AF-03 | direct_upgrade | 0 | true | true | true | none |
| AF-04 | direct_upgrade | 0 | true | true | true | none |
| AF-05 | direct_upgrade | 0 | true | true | true | none |
| AF-06 | direct_upgrade | 0 | true | true | true | none |
| AF-07 | direct_upgrade | 0 | true | true | true | none |
| AF-08 | direct_upgrade | 0 | true | true | true | none |
| AF-09 | direct_upgrade | 0 | true | true | true | none |

**OBSERVATION:** In the recorded metrics, all eighteen scenarios show `dependency_verified = true` and `rescan_success = true`. The nine npm scenarios each used one retry; the nine pip scenarios succeeded on the first attempt.

**LIMITATION (important):** Two facts must be read together with Table 3. First, `build_success = true` records that dependency *installation* completed; it does not assert that the application *compiled*. Second, the nine npm scenarios also record `failure_stage = "build"`, which co-occurs with `build_success = true`. This co-occurrence is a known inconsistency in the historical npm metrics; the project's audit root-caused it, corrected the pipeline code, and disclosed that the historical records were not retrospectively rewritten (`docs/audit/phase7_pipeline_smoketest.md`, `docs/audit/phase4_scenario_audit.md`). The metric values in Table 3 are therefore reported as recorded, with this inconsistency stated openly.

### 4.1.2 Deterministic baseline outcomes

Table 4 shows the deterministic baseline results, taken from the fresh baseline runs in `results/reproducibility_verification/`.

**Table 4. Deterministic baseline outcomes by ecosystem.**

| Ecosystem | Scenarios | Baseline build | Target vulnerability |
|---|---|---|---|
| pip (AF-01…AF-09) | 9 | built successfully (all 9) | removed (all 9) |
| npm (JS-01…JS-09) | 9 | did not complete build (all 9) | not validated (build halted before rescan) |

**OBSERVATION:** For all nine pip scenarios the deterministic baseline both built and removed the target vulnerability. For all nine npm scenarios the deterministic baseline recorded `build_success = false` and did not reach the rescan stage (`results/reproducibility_verification/<ID>/metrics.json`).

### 4.1.3 Two detailed cases

Two scenarios are documented in full as case studies in the repository.

**AF-01 (`redshift-connector`, CVE-2026-8838).** A direct pip dependency upgraded from `2.1.1` to `2.1.14`. **FACT:** The baseline scan reported the target advisory against `2.1.1`; the regenerated scan no longer reported it; total scanner matches moved from 583 to 581 (`results/execution_evidence/AF-01/`). The metrics record is internally consistent and the scenario succeeded on the first attempt. **INTERPRETATION:** This is the clean reference case — but for this pip scenario the deterministic baseline also succeeded, so AF-01 demonstrates correct pipeline operation, not an LLM advantage.

**JS-01 (`vm2`, CVE-2023-32314).** A transitive npm dependency (`juice-shop → juicy-chat-bot → vm2`). **FACT:** The baseline scan reported `vm2 3.9.17` with the target advisory; after applying an override to `3.9.18`, the regenerated scan no longer reported the target advisory; total scanner matches moved from 383 to 187 (`results/execution_evidence/JS-01/`). **OBSERVATION:** On its retry, the LLM's recorded reasoning identified that forcing the update pulls in modern type-definition packages incompatible with the project's legacy TypeScript compiler, and it recommended manual review while still supplying the override patch (`results/execution_evidence/JS-01/llm-response.json`). **LIMITATION:** The application's server did not compile (a `tsc` failure), and this failure is pre-existing and unrelated to the remediation; the JS-01 metrics also carry the documented inconsistencies noted in 4.1.1.

## 4.2 Scenario Analysis

**OBSERVATION:** The strategy the LLM used depended on the ecosystem and the dependency type. For the pip scenarios and for several npm scenarios the strategy was a direct upgrade. For transitive npm cases the strategy was a transitive override. For JS-01 the final strategy was manual review.

**INTERPRETATION:** This pattern is consistent with the structural difference between the ecosystems. Flat pip resolution allows a direct upgrade to succeed. Nested npm resolution sometimes requires an override to reach the fixed version, and in at least one case (JS-01) the model judged that no override could make the application safe to build without a deeper toolchain change.

## 4.3 Research Question Analysis

The research question asks whether an LLM can resolve transitive vulnerabilities where deterministic upgrades do not.

**A. Generation.** **OBSERVATION:** For all eighteen scenarios the LLM returned a structurally valid response (`llm_response_valid = true`), and in the two audited case studies it recommended the correct fixed version without inventing a version. This supports aspect A.

**B. Validation.** **OBSERVATION:** In the recorded metrics, all eighteen LLM-pipeline runs reached `dependency_verified = true` and `rescan_success = true`. **LIMITATION:** For the npm scenarios this validated state co-exists with a non-compiling application and with the metric inconsistency in 4.1.1, so aspect B is supported for *vulnerability removal and dependency-graph verification*, but not for full application compilation.

**C. Comparison.** **OBSERVATION:** The deterministic baseline completed and removed the target vulnerability for all nine pip scenarios, but did not complete for any of the nine npm scenarios. The LLM pipeline reached a validated vulnerability-removed state for the npm scenarios where the deterministic baseline did not complete.

**INTERPRETATION (answer to the RQ):** The evidence supports an affirmative but bounded answer. For the transitive npm class, the LLM pipeline reached a validated dependency-level remediation that the deterministic baseline did not reach. For the flat pip class, the deterministic baseline already succeeded, so the LLM added no advantage. The LLM's contribution is therefore specific to the transitive-dependency case, and it is a contribution at the level of *dependency remediation and graph verification*, not at the level of full application build success.

## 4.4 Discussion

**Installation is not remediation, and remediation is not compilation.** The study repeatedly separates three ideas: that a package installs, that a target vulnerability is removed, and that the application compiles. **INTERPRETATION:** The npm scenarios show why this separation matters. The target vulnerability was removed at the scanner level, but the application did not compile, because of a pre-existing toolchain incompatibility unrelated to the fix. A single success or failure flag would misrepresent this; the pipeline records the properties separately.

**The value of an LLM here is constraint reasoning, not version lookup.** **INTERPRETATION:** For a direct pip dependency, a scanner's version bump is enough, and the LLM adds nothing. The LLM becomes useful only when the fix must respect graph constraints, as in the npm override cases. JS-01 is the clearest example: the model reasoned about a downstream compiler consequence and declined to claim a safe automated fix. For a decision-support tool, correctly recommending human review is a reasonable outcome, not a failure.

**Honest treatment of imperfect evidence.** **LIMITATION:** Some historical npm metrics are internally inconsistent, and one scenario's evidence (JS-09) was regenerated during the audit under a corrected pipeline. These facts are disclosed rather than hidden, and they are the reason the analysis relies on the vulnerability-removal signal and the build logs together, not on a single composite flag.

## 4.5 Comparison

Table 5 summarises the comparison between the two pipelines.

**Table 5. Deterministic baseline versus LLM pipeline — summary.**

| Aspect | Deterministic baseline | LLM pipeline |
|---|---|---|
| pip scenarios (9) | Built and removed target (9/9) | Removed target (9/9); no added advantage |
| npm scenarios (9) | Build did not complete (0/9) | Reached validated vulnerability-removed state (recorded) |
| Strategy variety | Fixed (version bump) | Direct upgrade, transitive override, or manual review |
| Application compiles (npm) | No | No (pre-existing toolchain failure) |

**INTERPRETATION:** The comparison shows an ecosystem-dependent result. The LLM pipeline matches the baseline on pip and goes further than the (non-completing) baseline on npm, at the level of vulnerability removal and graph verification, while neither approach produces a compiling npm application.

## 4.6 Chapter Summary

**OBSERVATION:** The deterministic baseline succeeds on flat pip dependencies and does not complete on transitive npm dependencies. The LLM pipeline reaches a validated vulnerability-removed state on the npm scenarios, using strategies such as transitive overrides. **LIMITATION:** For npm, "vulnerability removed" is not "application compiles," and some historical metrics are internally inconsistent. **INTERPRETATION:** The LLM's contribution is real but specific: it helps where deterministic upgrades cannot satisfy dependency-graph constraints.

---

# Chapter 5 — Conclusion

## 5.1 Overall Conclusion

This thesis evaluated whether an LLM can generate context-aware dependency remediation strategies that pass deterministic validation, on eighteen pre-registered scenarios across npm and pip.

**INTERPRETATION:** The answer is a bounded yes. The deterministic scanner-recommended baseline is sufficient for flat pip dependencies, where a direct upgrade works. For transitive npm dependencies, the deterministic baseline did not complete, while the LLM pipeline reached a validated state in which the target vulnerability was removed, using graph-aware strategies such as transitive overrides. The LLM's value is therefore specific to the transitive case. The study also shows, honestly, that removing a vulnerability at the scanner level is not the same as producing a compiling application, and it keeps these properties separate throughout.

## 5.2 Research Contributions

1. A reproducible SBOM-driven pipeline that treats each LLM remediation as a hypothesis and verifies it with deterministic gates.
2. A controlled comparison, across two ecosystems, showing exactly where an LLM adds value (transitive npm) and where it does not (flat pip).
3. A careful separation of measurable properties — installation, vulnerability removal, and compilation — that prevents over-claiming.
4. A complete, audited evidence archive for all eighteen scenarios, including honest disclosure of the evidence's imperfections.

## 5.3 Limitations

The full limitation list is in `THESIS_LIMITATIONS.md`. The most important are: the npm application does not compile under its pinned toolchain (pre-existing, unrelated to remediation); exact scanner counts are not bit-for-bit reproducible because of the live database; some historical npm metrics are internally inconsistent; the study uses one LLM configuration, two applications, and a one-retry policy; and for eight scenarios the corrected provenance hash is a verified real commit associated with the evidence's origin rather than a per-file cryptographic proof.

## 5.4 Recommendations

**INTERPRETATION:** For practitioners, the study suggests using deterministic upgrades first, and reserving LLM assistance for transitive or constrained cases where a direct upgrade cannot satisfy the dependency graph. It also suggests treating any LLM remediation as a hypothesis to be verified, and recording installation, vulnerability removal, and compilation as separate signals.

## 5.5 Future Work

The following directions are recorded in `THESIS_FUTURE_WORK.md`. **FUTURE WORK:** adding an LLM confidence score; prompt-engineering ablation; removing the fixed-version hint to test unaided reasoning; allowing multiple retries; adding semantic or functional compatibility checks beyond compilation; pinning the scanner database for exact reproducibility; internet-enabled or tool-using reasoning; multi-agent proposer–critic designs; retrieval-augmented generation; model comparison; and additional ecosystems. Each would change the experiment and would require re-running scenarios, so each is left for future study to preserve the comparability of the present dataset. **CORRECTION:** an earlier draft of this list also included "feeding build/test failure logs into the retry prompt"; that mechanism is not future work — it is already implemented (`scripts/remediation/retry_remediation.py`, `scripts/remediation/llm_reasoner.py`) and evidenced in the frozen dataset.

---

# References

*Note: The following are real, verifiable sources (standards, tools, organisations, and vulnerability records). Full IEEE bibliographic details (versions, access dates, URLs) are to be finalised by the author, and additional peer-reviewed academic sources marked in Chapter 2 are to be added. No reference has been fabricated.*

[1] National Vulnerability Database, "CVE-2021-44228 (Apache Log4j)," NIST. [Full citation to be finalised by author.]
[2] National Vulnerability Database, "CVE-2024-3094 (XZ Utils)," NIST. [Full citation to be finalised by author.]
[3] The Linux Foundation, "SPDX (Software Package Data Exchange) Specification." [Full citation to be finalised by author.]
[4] OWASP Foundation, "CycloneDX SBOM Standard." [Full citation to be finalised by author.]
[5] Anchore, "Syft: SBOM generator." [Full citation to be finalised by author.]
[6] National Institute of Standards and Technology, "National Vulnerability Database (NVD)." [Full citation to be finalised by author.]
[7] Cybersecurity and Infrastructure Security Agency, "Known Exploited Vulnerabilities (KEV) Catalog." [Full citation to be finalised by author.]
[8] Anchore, "Grype: vulnerability scanner." [Full citation to be finalised by author.]
[9] FIRST, "Common Vulnerability Scoring System (CVSS)." [Full citation to be finalised by author.]
[10] FIRST, "Exploit Prediction Scoring System (EPSS)." [Full citation to be finalised by author.]
[11] npm, Inc., "npm dependency resolution and `overrides` documentation." [Full citation to be finalised by author.]
[12] OWASP Foundation, "OWASP Juice Shop." [Full citation to be finalised by author.]
[13] The Apache Software Foundation, "Apache Airflow." [Full citation to be finalised by author.]
[14] Google, "Gemini API documentation." [Full citation to be finalised by author.]

*[ACADEMIC CITATIONS TO BE ADDED BY AUTHOR: peer-reviewed sources on (a) LLMs for vulnerability repair and code generation, (b) software supply-chain security, and (c) dependency-management studies, to support the scholarly claims marked in Chapter 2.]*

---

# Appendices

## Appendix A — Repository provenance
- Frozen tag: `thesis-freeze-2026-08-02`; commit `5a227c8f`.
- Verdict of the pre-freeze examiner review: Accept with minor revisions (revisions applied). *Source: `FINAL_VERDICT.md`, `FREEZE_REPORT.md`.*

## Appendix B — Evidence map
- Per-scenario evidence: `results/execution_evidence/<ID>/`.
- Deterministic baseline verification: `results/reproducibility_verification/<ID>/`.
- Case studies: `docs/case_studies/JS-01_vm2_case_study.md`, `docs/case_studies/AF-01_redshift-connector_case_study.md`.
- Methodology: `docs/04-experimental-methodology.md`. Reproducibility: `docs/06-reproducibility.md`.
- Audit trail: `docs/audit/`. Limitations: `THESIS_LIMITATIONS.md`. Future work: `THESIS_FUTURE_WORK.md`.

## Appendix C — Workflows
- LLM pipeline: `.github/workflows/generic-remediation.yml`.
- Deterministic baseline: `.github/workflows/grype-baseline.yml`.

---

*End of draft. This document is a complete first draft written against the frozen repository. Placeholders (university, supervisors, matriculation number, submission date), the final title decision, figure rendering, and the finalisation of external citations remain for the author.*
