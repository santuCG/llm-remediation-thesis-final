# Empirical Evaluation of LLM-Assisted Dependency Remediation in SBOM-Driven CI/CD Pipelines

> **Master's Thesis Research Artifact**

---

# Abstract

This repository accompanies the Master's thesis:

> **"An Exploratory Evaluation of LLM-Assisted Dependency Remediation in SBOM-Driven CI/CD Pipelines."**

The repository provides a reproducible experimental framework for evaluating whether a **Large Language Model (LLM)**, when supplied with structured vulnerability intelligence and dependency graph context, can recommend remediation strategies for software supply chain vulnerabilities that are not resolved through conventional deterministic package upgrade workflows.

Unlike traditional vulnerability management studies that evaluate scanner detection accuracy, this work focuses on **dependency remediation strategy generation**. The experiments compare deterministic remediation recommendations with context-aware LLM-generated recommendations using identical Software Bills of Materials (SBOMs), vulnerability scanner outputs, and package management workflows.

The experimental methodology is designed to be reproducible and is executed using version-pinned tooling, controlled dependency graphs, and standardised validation procedures. The repository documents the complete workflow used throughout the thesis, including:

- SBOM generation
- Vulnerability identification
- Threat intelligence enrichment
- Prompt construction
- LLM recommendation generation
- Package manager validation
- Dependency graph verification
- Post-remediation vulnerability comparison

Two representative experimental scenarios from **OWASP Juice Shop** are included within this repository as reference implementations:

- **JS-01** – `CVE-2023-32314` (`vm2`)
- **JS-08** – `CVE-2024-45590` (`body-parser`)

These scenarios demonstrate the complete methodology applied throughout the research.

The identical workflow is subsequently applied to the remaining experimental scenarios (18 total representative scenarios spanning **OWASP Juice Shop** and **Apache Airflow**) described in the accompanying Master's thesis.

---

# Research Motivation

Modern software applications routinely depend on thousands of third-party software components.

While Software Bills of Materials (SBOMs) and automated vulnerability scanners have significantly improved visibility into software supply chain risk, remediation frequently remains a manual engineering task requiring developers to understand:

- Dependency graph topology
- Package manager behaviour
- Transitive dependency relationships
- Semantic version compatibility
- Operational risk

Existing vulnerability scanners typically recommend upgrading the directly affected package to the nearest patched version whenever a known vulnerability is detected.

Although this recommendation is often technically correct at the package level, it does not necessarily result in remediation across the complete dependency graph.

For applications containing deeply nested transitive dependencies, vulnerable package versions may continue to exist beneath intermediate parent packages despite successful execution of a direct package installation.

This repository investigates whether structured contextual information—including dependency graph observations, vulnerability metadata, and external threat intelligence—can assist an LLM in generating remediation strategies that address these graph-level constraints.

---

# Research Question

The primary research question addressed by this work is:

> **Can an LLM generate context-aware dependency remediation strategies that successfully resolve selected transitive dependency vulnerabilities under controlled SBOM-driven workflows where basic deterministic package upgrade strategies do not achieve the intended remediation objective?**

This repository does **not** evaluate:

- Vulnerability detection accuracy.
- CVSS prediction.
- Exploit prediction.
- Software Composition Analysis (SCA) performance.
- Replacement of vulnerability scanners.

Instead, the focus is restricted to evaluating remediation recommendations generated **after** deterministic vulnerability identification has already occurred.

---

# Scope of the Repository

This repository documents the **experimental framework** used throughout the thesis rather than presenting every individual experimental result.

The repository includes:

- Reproducible SBOM generation workflows.
- Vulnerability identification using Grype.
- Structured threat intelligence enrichment.
- Prompt engineering methodology.
- LLM configuration.
- Package manager validation.
- Dependency graph verification.
- Post-remediation SBOM comparison.
- Quantitative evaluation procedures.

The repository intentionally demonstrates the methodology using two representative scenarios.

The identical workflow is subsequently applied to all remaining scenarios evaluated within the accompanying thesis.

---

# Research Contribution

The contribution of this work is **not** the development of a new vulnerability scanner, nor does it claim that LLMs should replace deterministic Software Composition Analysis (SCA) tools.

Instead, the core **scientific contribution** of this Master's thesis is the isolation and evaluation of Large Language Model reasoning as a decision-support layer to solve deterministic topological constraint failures. 

Traditional SCA tools treat dependencies as isolated entities. They recommend basic version bumps that frequently fail (resulting in the 0% deterministic success rate observed in the baseline of this research) because they ignore the strict constraints of the holistic dependency graph. 

This research demonstrates how to transform vulnerability management from a basic suggestion engine into a graph-aware remediation protocol. By synthesising multiple sources of structured intelligence—including dependency graph observations, package manager error behaviors, and external threat signals (CVSS, EPSS)—this work evaluates the efficacy of LLM-generated strategies in bridging the gap between static vulnerability detection and deterministic constraint satisfaction.

Accordingly, the scientific novelty is centred entirely on **context-aware remediation strategy generation**, effectively treating the LLM as a topological reasoning engine rather than a discovery tool.

---

# Experimental Design

Each experimental scenario follows an identical controlled workflow.

```text
Target Application
        │
        ▼
Software Bill of Materials (SBOM)
        │
        ▼
Grype Vulnerability Scan
        │
        ▼
Target Vulnerability Selection
        │
        ▼
Threat Intelligence Enrichment
        │
        ▼
Structured Prompt Construction
        │
        ▼
Google Gemini 2.5 Flash
        │
        ▼
Structured JSON Recommendation
        │
        ▼
Constraint-Aware Package Injection
        │
        ▼
Dependency Resolution
        │
        ▼
Dependency Graph Verification
        │
        ▼
Regenerated SBOM
        │
        ▼
Post-remediation Grype Scan
        │
        ▼
Quantitative Comparison
```

Only one independent variable changes during each experiment:

> **The remediation strategy applied to the dependency graph.**

All remaining variables—including application version, scanner versions, SBOM generation methodology, operating environment, prompt structure, and validation workflow—remain constant.

---

## Experimental Scenarios Included

The methodology is demonstrated using two representative scenarios from **OWASP Juice Shop v15.3.0**.

| Scenario | CVE | Package | Initial Version | Patched Version |
| :--- | :--- | :--- | :---: | :---: |
| **JS-01** | CVE-2023-32314 | `vm2` | 3.9.17 | 3.9.18 |
| **JS-08** | CVE-2024-45590 | `body-parser` | 1.20.1 | 1.20.3 |

These scenarios were selected because they expose graph-level remediation behaviour involving transitive dependencies and therefore provide suitable case studies for evaluating dependency remediation strategies.

The repository intentionally documents these representative scenarios in detail to enable independent reproduction of the complete methodology before it is applied to the remaining experimental scenarios described in the accompanying thesis.

---

# Repository Structure

The repository is organised to separate experimental inputs, automation scripts, generated artifacts, and experimental outputs.

```text
.
├── applications/
│   ├── juice-shop/
│   └── airflow/
│
├── experiment/
│   ├── raw_outputs/
│   ├── remediation_reports/
│   └── results/
│
├── preregistration/
│
├── scripts/
│
├── analysis/
│
├── manual-validation-docs/
│
└── README.md
```

Directory names may differ slightly from the final repository layout; however, the logical separation between prompts, automation, experimental artifacts, and results is preserved throughout the project.

---

# Reproducibility Statement

Every experiment documented within this repository follows the same methodology.

To maximise reproducibility:

- Software versions are explicitly pinned.
- Identical vulnerability scanners are used throughout.
- SBOM generation methodology remains unchanged.
- Prompt templates are reused across every scenario.
- Experimental validation follows the same verification gates.
- Quantitative comparison is performed using identical analysis scripts.

Where experimental limitations were observed (for example, package manager constraints), these are documented as part of the methodology rather than hidden or bypassed.

The objective is to enable independent researchers to reproduce the documented workflow using the same inputs, generate comparable remediation recommendations, and validate those recommendations using deterministic software supply chain tooling.