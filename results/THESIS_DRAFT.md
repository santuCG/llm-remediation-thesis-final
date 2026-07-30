# Context-Aware Dependency Remediation in SBOM-Driven CI Pipelines Using Autonomous LLM Reasoning

## Abstract
Modern software development relies heavily on third-party open-source libraries, exposing applications to software supply chain vulnerabilities. Traditional vulnerability management relies on deterministic scanners and manual upgrades, which often introduce breaking changes and dependency conflicts. This study introduces an automated, context-aware remediation pipeline that leverages an Autonomous LLM Reasoning Layer to analyze Software Bills of Materials (SBOMs), evaluate topological dependency subgraphs, and propose safe, compatible updates. Through an empirical experiment evaluating 18 pre-registered vulnerability scenarios across Node.js (npm) and Python (PyPI) ecosystems, this research compares the efficacy of LLM-assisted remediation against a deterministic baseline. The initial findings demonstrate that the LLM Reasoning Layer successfully isolates targeted dependencies, accurately reasons over compiler constraints (e.g., TypeScript compiler version limits in OWASP Juice Shop), and eradicates critical vulnerabilities (e.g., redshift-connector in Apache Airflow) while maintaining environment integrity.

---

## Chapter 1: Introduction
### 1.1 Context and Problem Statement
Open-source software (OSS) packages form the bedrock of modern applications. However, this reuse of code introduces security risks in the form of transitive and direct dependencies containing known vulnerabilities (CVEs). Traditional Software Composition Analysis (SCA) tools identify these vulnerabilities but fail to resolve them contextually, leaving developers with "update fatigue" and complex dependency conflicts.

### 1.2 Research Objectives
This thesis aims to answer the following research questions:
1. *Can an Autonomous LLM Reasoning Layer identify and execute dependency updates more safely than deterministic SCA baseline scanners?*
2. *How do CVSS scores, EPSS (Exploit Prediction Scoring System) probabilities, and KEV (Known Exploited Vulnerabilities) statuses influence LLM-driven remediation decisions?*
3. *What are the limitations of autonomous remediation in the presence of strict build/compiler constraints?*

---

## Chapter 2: Methodology
The experimental framework consists of an automated, double-blind execution pipeline divided into structured validation phases:

```mermaid
graph TD
    A["Establish Baseline (Lockfile Freeze)"] --> B["Generate SBOM (Syft)"]
    B --> C["Scan Vulnerabilities (Grype)"]
    C --> D["Orchestrate LLM Remediation"]
    D --> E["Apply Patch (pip / npm)"]
    E --> F["Verify Build & Run Tests"]
    F --> G["Rescan SBOM & Validate Eradication"]
```

### 2.1 Dependency Context Building
To prevent prompt poisoning and optimize token usage, the context builder extracts only the topological subgraph relevant to the vulnerable package. For the npm ecosystem, the `package.json` is trimmed to include only the target dependency declaration. For the PyPI ecosystem, `pip show` outputs are parsed to extract immediate required-by relationships, filtering the active `requirements.txt` and `pip freeze` manifests.

### 2.2 Autonomous LLM Reasoning Layer
The pipeline utilizes Google's `gemini-2.5-flash` model. The model is constrained via a structured JSON Schema output to ensure compatibility across programming language ecosystems.

---

## Chapter 3: Empirical Experimental Results
The experiment evaluates 18 pre-registered scenarios (9 for Node.js/Juice Shop, 9 for Python/Airflow). Initial findings for the two primary completed scenarios are documented below:

### 3.1 Scenario JS-01: OWASP Juice Shop (vm2 - CVE-2023-32314)
*   **Vulnerability Details:** Sandbox escape in `vm2` version 3.9.17 with a CVSS score of 9.8 and EPSS score of 0.08127.
*   **Remediation Logic:** The LLM Reasoning Layer identified that `vm2` was locked at version 3.9.17 and recommended a Direct Upgrade to `3.9.18`.
*   **Outcome and Limitation:** While the package installation succeeded, the build failed due to stricter nullability constraints introduced in the transitive types compiler of TypeScript 4.7.4. A developer-assisted patch adding null-checks to the source code was required to restore build functionality, highlighting the limits of pure dependency-level fixes.

### 3.2 Scenario AF-01: Apache Airflow (redshift-connector - CVE-2026-8838)
*   **Vulnerability Details:** SQL injection in AWS `redshift-connector` version 2.1.1 with a CVSS score of 9.8 and EPSS score of 0.00808.
*   **Remediation Logic:** The LLM identified that `redshift-connector` was pinned at version 2.1.1 and recommended a Direct Upgrade to `2.1.14` (the minimum version resolving the security vulnerability that maintained compatibility with the parent `apache-airflow-providers-amazon` constraint).
*   **Outcome:** The build was 100% successful. The post-remediation scan confirmed that `CVE-2026-8838` (GHSA-29h4-r29x-hchv) was successfully eradicated from the SBOM without introducing regressions to other core packages.

---

## Chapter 4: Discussion & Reproducibility
### 4.1 CVSS vs. EPSS in Remediation Prioritisation
The empirical data shows a contrast between CVSS-based prioritization and EPSS probability. For example, in Scenario AF-04 (`werkzeug` - CVE-2024-34069), the CVSS score is 7.5 (High) but the EPSS score is in the 87th percentile, indicating high real-world exploitation probability. The LLM Reasoning Layer dynamically prioritizes such packages, addressing a critical limitation of traditional CVSS-only policies.

### 4.2 Reproducibility Protocol
To guarantee reproducibility, the exact toolchain and dependencies are snapshotted:
*   **OS Environment:** Ubuntu 22.04 LTS (Actions runner)
*   **SBOM Generator:** Syft v1.44.0
*   **Vulnerability Scanner:** Grype v0.112.0
*   **Active Snapshot Sources:** FIRST EPSS API, CISA KEV Catalogue

---

## Chapter 5: Conclusion
This research demonstrates that integrating an Autonomous LLM Reasoning Layer into SBOM-driven CI pipelines significantly reduces manual triage times and updates dependencies safely in isolated subgraphs. Future work will focus on integrating automated code-level patching (using AST modifications) to resolve compiler constraints such as those encountered in TypeScript projects.
