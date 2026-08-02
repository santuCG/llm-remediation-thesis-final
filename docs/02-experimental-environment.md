# Experimental Environment

All experiments were performed within a controlled and reproducible software environment using version-pinned tooling. The objective was to minimise environmental variation between baseline and remediated executions so that any observed differences could be attributed solely to the applied remediation strategy.

Unlike container image scanning workflows, the definitive experimental evaluation documented in this repository was performed directly against the application's dependency lockfile. This design excludes operating system packages, container runtime libraries, and other infrastructure components that are unrelated to the application dependency graph under investigation.

---

## Experimental Platform

| Component | Version |
| :--- | :--- |
| **Host Operating System** | Ubuntu 24.04 (GitHub Actions Runner) |
| **Node.js** | 18.x |
| **npm** | 9.x |
| **Git** | 2.47.1 |
| **Python** | 3.12.x |
| **Syft** | 1.44.0 |
| **Grype** | 0.112.0 |
| **Target Application** | OWASP Juice Shop 15.3.0 & Apache Airflow 2.9.2 |

The software versions above were recorded immediately before the experiments commenced and remained unchanged throughout all validation stages.

> **Note on environments and Node.js engine strictness.** The frozen eighteen-scenario dataset was generated in the CI environment (GitHub Actions, Node.js 18.x, as pinned in `.github/workflows/`), which is the environment recorded in the table above and confirmed by the CI run identifiers in each `experiment_manifest.json`. Separate local exploratory runs used Node.js v24.18.0, which is newer than Juice Shop's declared engine range (`16 - 20`) and produces `EBADENGINE` warnings during `npm` execution. In both environments `npm` successfully resolves and generates the dependency graph despite such warnings, so they do not invalidate the experiment; the specific Node/npm version is not treated as a variable of the study.

---

# Software Components

## OWASP Juice Shop

OWASP Juice Shop was selected because it represents a modern JavaScript application with a large dependency graph containing both direct and transitive package relationships.

The application provides a realistic dependency ecosystem suitable for evaluating remediation strategies involving nested dependencies.

The representative scenarios documented within this repository focus exclusively on dependency management behaviour and **do not** evaluate the overall security posture of OWASP Juice Shop itself.

---

## Anchore Syft

Syft was used to generate **Software Bills of Materials (SBOMs)** from the application dependency lockfile.

SPDX JSON was selected as the interchange format because it:

- Is machine-readable.
- Is fully supported by Grype.
- Preserves package metadata.
- Provides a standardised representation of application dependencies.

Throughout the experiments, Syft was executed as a native Windows binary rather than through a containerised wrapper.

Native execution reduced environmental complexity while ensuring that the generated SBOMs originated directly from the application's dependency lockfile.

---

## Anchore Grype

Grype was used as the deterministic **Software Composition Analysis (SCA)** engine.

Within this research, Grype performs two functions:

1. Identifying vulnerable packages within the generated SBOM.
2. Verifying the post-remediation dependency state.

Grype itself is **not** evaluated as part of this research.

Instead, its output serves as the deterministic baseline against which remediation strategies are assessed.

---

## Google Gemini 2.5 Flash

Google Gemini 2.5 Flash (Google AI Studio) was selected as the experimental reasoning engine responsible for generating remediation recommendations.

The model does **not** perform vulnerability discovery.

Instead, it receives structured information extracted during previous experimental stages, including:

- Vulnerability metadata.
- Package versions.
- Dependency graph observations.
- Threat intelligence.
- Package manager behaviour.
- Remediation constraints.

The generated recommendation is **not considered experimental evidence**.

Instead, it is treated as an engineering hypothesis that is subsequently evaluated through deterministic package manager validation, dependency graph verification, SBOM regeneration, and post-remediation vulnerability analysis.

---

# Why Lockfile-Based SBOM Generation?

Early exploratory experiments compared:

- SBOMs generated from the complete Docker image.

against

- SBOMs generated directly from the application lockfile.

This approach was rejected because the resulting datasets represented different experimental populations.

Container image SBOMs include:

- Operating system packages.
- System libraries.
- Container runtime components.
- Package manager metadata, **and**
- Application dependencies.

Lockfile SBOMs include only the application's dependency graph.

Comparing these two populations would invalidate quantitative before-and-after measurements because observed scanner findings would originate from fundamentally different software populations.

Consequently, all definitive experiments documented within this repository generate both baseline and remediated SBOMs exclusively from:

```text
package-lock.json
```

This ensures that both datasets represent identical application populations.

Only the dependency graph changes between experimental conditions.

---

# Experimental Variables

To preserve internal validity, only one independent variable changes during each experiment.

## Independent Variable

The remediation strategy applied to the dependency graph.

Representative strategies include:

- Direct package installation.
- Dependency overrides.
- No-action recommendation.

---

## Controlled Variables

The following remained constant across every experiment.

| Variable | Controlled |
| :--- | :---: |
| Application version | ✓ |
| `package-lock.json` baseline | ✓ |
| Node.js version | ✓ |
| npm version | ✓ |
| Syft version | ✓ |
| Grype version | ✓ |
| Operating system | ✓ |
| SBOM format | ✓ |
| Vulnerability scanner | ✓ |
| Validation workflow | ✓ |
| Prompt structure | ✓ |

This experimental design allows any observed differences to be attributed to the applied remediation strategy rather than environmental variation.

---

# Threat Model

This research evaluates software supply chain vulnerabilities introduced through third-party dependencies.

The documented workflow assumes:

1. A deterministic vulnerability scanner has already identified vulnerable packages.
2. Package metadata is available.
3. A remediation recommendation must be generated.
4. The package manager determines whether that recommendation can be successfully applied.

The repository does **not** evaluate:

- Malware detection.
- Runtime exploitation.
- Endpoint security.
- Intrusion detection.
- Exploit development.
- Binary analysis.
- Operating system vulnerabilities.

The scope is intentionally restricted to dependency remediation within application software supply chains.

---

# Experimental Workflow

Every experimental scenario follows the identical processing pipeline.

```text
Application Source
        │
        ▼
package-lock.json
        │
        ▼
Syft
        │
        ▼
SPDX SBOM
        │
        ▼
Grype
        │
        ▼
Target Vulnerability Selection
        │
        ▼
Threat Intelligence Collection
        │
        ▼
Prompt Construction
        │
        ▼
Google Gemini 2.5 Flash
        │
        ▼
Structured JSON Recommendation
        │
        ▼
Constraint-Aware Injection
        │
        ▼
npm Dependency Resolution
        │
        ▼
Dependency Graph Verification
        │
        ▼
Updated package-lock.json
        │
        ▼
Syft
        │
        ▼
Grype
        │
        ▼
Experimental Comparison
```

Every representative scenario documented throughout this repository follows this sequence.

No stages are skipped.

---

# Reproducibility Controls

The experiments were designed to minimise procedural variation.

The following controls were applied before every experimental execution:

- Clean dependency restoration using Git.
- Deterministic dependency installation.
- Regeneration of the baseline SBOM.
- Regeneration of the baseline vulnerability report.
- Identical prompt structure.
- Identical model configuration.
- Identical validation methodology.

When package-manager constraints prevented successful remediation during the initial local experiments (for example, npm `EOVERRIDE`), that initial attempt was stopped before validation.

The observed package-manager behaviour was recorded as experimental evidence rather than bypassed.

A documented constraint-aware remediation workflow and a single-retry mechanism were then introduced, and the final CI-executed scenarios ran under these controlled conditions; where the constraint recurred (JS-05, JS-08) it was resolved automatically on retry and the scenario reached a validated remediation.

---

# Internal Validity

Several design decisions were introduced to strengthen internal validity.

## Controlled Baseline

Each experiment begins from an identical application state.

This prevents contamination between experimental scenarios.

---

## Identical Scanner Configuration

Baseline and remediated SBOMs are generated using the identical Syft version and analysed using the identical Grype version.

---

## Identical Prompt Structure

Every experimental scenario uses the same prompt architecture.

Only scenario-specific values change.

Representative inputs include:

- CVE identifier.
- Package name.
- Package version.
- CVSS score.
- EPSS metrics.
- CISA KEV status.
- Dependency graph observations.

The prompt structure itself remains unchanged throughout the research.

---

## Constraint-Aware Validation

Recommendations generated by the **Large Language Model (LLM)** are **not** accepted as successful solely because they appear reasonable.

Every recommendation must successfully satisfy all deterministic validation stages:

1. Package manager execution.
2. Dependency graph verification.
3. SBOM regeneration.
4. Post-remediation vulnerability analysis.

Only recommendations that successfully complete the entire validation workflow are considered experimentally successful.

---

# Scope and Limitations

The experimental environment documented within this repository was intentionally designed to evaluate dependency remediation methodology rather than general software security.

Consequently:

- Results should not be interpreted as evaluating all JavaScript or Python applications.
- Conclusions should not be generalised to all package managers.
- The representative scenarios evaluate selected dependency remediation workflows.
- Additional validation across larger datasets, package ecosystems, and application domains is required before broader conclusions can be drawn.

These limitations do not diminish the reproducibility of the documented methodology but define the scope within which the reported conclusions should be interpreted.