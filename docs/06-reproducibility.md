# Reproducing the Experimental Workflow

This repository accompanies the Master's thesis as a **reproducible research artifact**.

Its primary objective is to document the experimental methodology used to evaluate LLM-assisted dependency remediation rather than to reproduce a single numerical result.

A researcher following the documented workflow should be able to reproduce the complete experimental process, generate comparable remediation decisions, and validate those decisions using deterministic software supply chain tooling.

Because vulnerability databases evolve over time (for example, Grype's vulnerability database), the absolute number of scanner findings may differ when the experiments are repeated at a later date.

For this reason, archived SBOMs, vulnerability reports, prompts, generated JSON recommendations, and validation artifacts should be preserved whenever possible.

---

# Experimental Execution Sequence

Each experimental scenario follows the identical sequence of operations.

## Step 1 — Restore the Experimental Baseline

Restore the repository to a deterministic baseline.

```bash
git checkout package.json package-lock.json
npm ci --ignore-scripts
```

---

## Step 2 — Generate the Baseline SBOM

```bash
syft file:package-lock.json \
  -o spdx-json=baseline-lockfile-sbom.json
```

---

## Step 3 — Generate the Baseline Vulnerability Report

```bash
grype sbom:baseline-lockfile-sbom.json \
  -o json \
  --file baseline-lockfile-grype.json
```

> **Grype database was not pinned for the frozen dataset.** The pre-registration (`preregistration/MASTER_METHODOLOGY_RECORD.md`) originally specified that researchers should import a specific Grype database snapshot via `grype db import` before scanning, to maximise reproducibility of exact scanner-finding counts. This was not implemented: neither CI workflow (`generic-remediation.yml` nor `grype-baseline.yml`) contains a database-import step; every scan ran against whichever Grype vulnerability database was live at CI-run time (`GRYPE_DB_VALIDATE_AGE=false` only suppresses the staleness check — it does not pin a snapshot). This deviation is recorded in `preregistration/PRE_REGISTRATION_AMENDMENT.md`. Consequently, a later re-run of this workflow should not be expected to reproduce the exact same absolute scanner-finding counts (see the note above this clause); the reproducible signal is target-CVE eradication, not the aggregate count.

---

## Step 4 — Extract the Experimental Scenario

Collect the scenario-specific information required for prompt construction.

This typically includes:

- CVE identifier
- affected package
- installed package version
- recommended patched version
- CVSS score
- MITRE / NVD vulnerability description
- dependency graph observations

---

## Step 5 — Construct the LLM Prompt

Construct the user prompt using the standard prompt template.

Populate the template with:

- vulnerability metadata
- threat intelligence
- EPSS score
- EPSS percentile
- CISA KEV status
- dependency graph observations
- package manager behaviour
- required JSON schema

The system prompt remains identical across every experimental scenario.

---

## Step 6 — Generate the Remediation Recommendation

Submit the completed prompt to the Google Generative Language API using the documented model fallback list and generation configuration (see `docs/03-llm-configuration.md`).

The generated recommendation is treated as a **hypothesis** rather than experimental evidence.

---

## Step 7 — Apply the Recommendation

Apply the generated remediation strategy.

If package manager constraints prevent successful execution (for example `npm ERR! EOVERRIDE`), record the observed behaviour as part of the experiment.

Do **not** silently modify the recommendation.

If a revised constraint-aware workflow is introduced, document the change before repeating the experiment.

---

## Step 8 — Verify the Dependency Graph

Representative verification commands include:

```bash
npm ls <package>
```

Dependency graph verification provides independent evidence that the intended package versions have been resolved successfully.

---

## Step 9 — Generate the Remediated SBOM

Generate a new SBOM using the updated dependency graph.

Use the same Syft version employed during baseline generation.

---

## Step 10 — Generate the Remediated Vulnerability Report

Generate the post-remediation Grype report using the identical scanner configuration employed during baseline analysis.

---

## Step 11 — Compare Baseline and Remediated Results

Perform a programmatic comparison between the baseline and remediated reports.

The comparison should evaluate:

- total scanner findings
- ecosystem-specific findings
- removed findings
- remaining findings
- target CVE verification
- percentage change

---

## Step 12 — Produce the Experimental Summary

Separate the final report into:

- observations
- measured values
- interpretations
- conclusions

Only conclusions directly supported by deterministic experimental evidence should be reported.

---

# Research Artifact Organisation

The repository layout is shown below.

```text
.
├── applications/                    # Target applications (juice-shop, airflow) + pinned evidence lockfiles
│
├── results/
│   ├── scenarios/                   # The 18 pre-registered scenario definitions
│   ├── execution_evidence/          # Per-scenario raw evidence (SBOMs, Grype scans, LLM I/O, metrics, manifests)
│   └── reproducibility_verification/# Post-fix deterministic-baseline re-run evidence (Phase 5 audit)
│
├── preregistration/                 # Locked scenario/methodology pre-registration + amendments
│
├── scripts/                         # remediation/ (CI-invoked pipeline) + baseline/ + orchestration tooling
│
├── .github/workflows/               # generic-remediation.yml (LLM pipeline) + grype-baseline.yml (deterministic)
│
├── docs/                            # Canonical methodology, results, reproducibility, and audit/ trail
│
├── archive/                         # Superseded drafts and legacy artifacts (not part of the active dataset)
│
└── README.md                        # Navigation hub
```

Each experimental scenario should preserve:

- baseline SBOM
- remediated SBOM
- baseline Grype report
- remediated Grype report
- prompt
- generated JSON recommendation
- dependency graph verification
- comparison report
- experimental summary

Maintaining these artifacts enables independent verification of every evaluated scenario.

---

# Artifact Verification Checklist

Before considering an experiment complete, verify that all of the following conditions have been satisfied.

| Verification Item | Status |
| :--- | :---: |
| Clean baseline restored | ☐ |
| Baseline SBOM generated | ☐ |
| Baseline Grype report generated | ☐ |
| Threat intelligence collected | ☐ |
| Prompt generated | ☐ |
| Structured JSON recommendation generated | ☐ |
| Package manager accepted remediation | ☐ |
| Dependency graph verified | ☐ |
| Remediated SBOM generated | ☐ |
| Remediated Grype report generated | ☐ |
| Programmatic comparison completed | ☐ |
| Experimental summary documented | ☐ |

---

# Experimental Integrity

Researchers extending this repository are encouraged to preserve the following principles.

- Use version-pinned tooling.
- Preserve identical prompt structure across scenarios.
- Archive generated artifacts.
- Record package manager constraints rather than bypassing them.
- Clearly distinguish observations from interpretations.
- Validate every remediation using deterministic tooling.
- Preserve baseline and remediated artifacts for independent verification.

Most importantly:

> **The recommendation generated by the LLM is not considered experimental evidence. Experimental evidence is obtained only after successful deterministic validation through package manager execution, dependency graph verification, SBOM regeneration, and post-remediation vulnerability analysis.**

This principle underpins the entire experimental methodology documented within this repository.

---

# Extending the Methodology

The methodology documented in this repository is intentionally independent of any specific vulnerability.

To evaluate additional scenarios, only the following inputs should change:

- CVE identifier
- affected package
- installed version
- patched version
- CVSS score
- EPSS score
- KEV status
- dependency graph observations

The remaining workflow should remain unchanged.

Maintaining an identical methodology across scenarios improves experimental comparability and reproducibility.

---

# Citation

If this repository contributes to academic research, please cite the accompanying Master's thesis.

```text
Santosh Nagaraj.

An Exploratory Evaluation of LLM-Assisted Dependency Remediation in SBOM-Driven CI/CD Pipelines.

Master of Science (M.Sc.) Thesis.

SRH University of Applied Sciences, Berlin.

2026.
```

BibTeX:

```bibtex
@mastersthesis{nagaraj2026,
  author = {Santosh Nagaraj},
  title = {An Exploratory Evaluation of LLM-Assisted Dependency Remediation in SBOM-Driven CI/CD Pipelines},
  school = {SRH University of Applied Sciences},
  year = {2026}
}
```

---

# Acknowledgements

This work builds upon established software supply chain security tooling, including:

- Syft for Software Bill of Materials (SBOM) generation.
- Grype for deterministic vulnerability analysis.
- npm for dependency resolution.
- OWASP Juice Shop and Apache Airflow as representative application ecosystems.
- Google Gemini (via the Generative Language API, with a documented model fallback list — see `docs/03-llm-configuration.md`) for structured remediation recommendation generation.

The contribution of this repository is not the development of these individual tools, but the reproducible integration of deterministic software supply chain analysis with structured LLM-assisted remediation and deterministic validation.

---

# Final Remarks

This repository does **not** propose replacing deterministic Software Composition Analysis (SCA) tools with Large Language Models (LLMs).

Instead, it documents a reproducible methodology for evaluating whether contextual reasoning can assist dependency remediation after vulnerabilities have already been identified by deterministic tooling.

Accordingly, every LLM-generated recommendation is treated as an engineering hypothesis that must undergo deterministic validation through:

1. package manager execution,
2. dependency graph verification,
3. SBOM regeneration,
4. post-remediation vulnerability analysis.

Only recommendations that successfully satisfy all validation stages are considered experimentally successful.

This separation between recommendation generation and deterministic validation represents the central methodological principle of the accompanying Master's thesis and forms the basis for evaluating all eighteen experimental scenarios documented throughout the research.