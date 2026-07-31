# Experimental Results and Discussion

This section presents the observed results obtained from the documented experimental workflow.

Only measurements directly supported by the experimental evidence are reported.

Interpretations are explicitly separated from observations wherever possible.

The methodology documented in this repository is demonstrated using **two representative scenarios** from the complete experimental dataset. The identical workflow is subsequently applied to the remaining scenarios described in the accompanying thesis.

---

## Representative Experimental Scenarios

The methodology documented in this repository is demonstrated using two representative remediation scenarios from **OWASP Juice Shop v15.3.0**.

| Scenario | CVE | Package | Remediation Strategy |
| :--- | :--- | :--- | :--- |
| **JS-01** | CVE-2023-32314 | `vm2` | Dependency Override |
| **JS-08** | CVE-2024-45590 | `body-parser` | Direct Dependency Alignment + Dependency Override |

These representative scenarios were selected because they expose different dependency graph behaviours while exercising the same validation methodology.

---

## Experimental Observations

### Observation 1 — Baseline Vulnerability Identification

Baseline SBOM generation and Grype analysis successfully identified the selected target vulnerabilities.

The baseline vulnerability report served as the experimental control for all subsequent comparisons.

---

### Observation 2 — Deterministic Package Upgrade Behaviour

Initial deterministic package installation completed successfully.

However, dependency graph inspection demonstrated that vulnerable package instances remained within transitive portions of the dependency graph for the evaluated scenarios.

This observation motivated the evaluation of an alternative remediation strategy.

---

### Observation 3 — Package Manager Constraint

The initial implementation of the LLM-generated recommendation resulted in an npm `EOVERRIDE` constraint because the recommended override conflicted with an existing direct dependency declaration.

Rather than bypassing this behaviour, the constraint was documented as an observed experimental result and incorporated into the methodology.

A constraint-aware remediation workflow was subsequently introduced that aligned direct dependencies while preserving the intended transitive remediation strategy.

---

### Observation 4 — Dependency Graph Resolution

Following the revised remediation workflow:

- Package manager execution completed successfully.
- Dependency graph verification confirmed the expected package versions.
- Updated lockfiles were generated.
- Regenerated SBOMs were successfully produced.

These observations established that the recommended remediation strategy had been successfully applied.

---

### Observation 5 — Vulnerability Verification

Post-remediation vulnerability analysis confirmed that:

- `CVE-2023-32314` was no longer detected.
- `CVE-2024-45590` was no longer detected.

These observations were verified through comparison of the regenerated Grype reports.

---

### Observation 6 — Objective Validation and LLM-Generated Metadata

An important observation during manual inspection of the execution artifacts was that successful vulnerability remediation and semantically consistent descriptive metadata are distinct properties. In a small number of scenarios, auxiliary metadata fields associated with the generated remediation exhibited internal inconsistencies, despite the resulting dependency modifications successfully satisfying all deterministic validation gates. Since experimental success was defined by objective verification (dependency installation, build validation, vulnerability rescanning, and pipeline validation) rather than the semantic correctness of descriptive metadata, these inconsistencies did not affect the experimental outcomes. This distinction illustrates why the experimental methodology evaluated remediation success using deterministic pipeline outcomes rather than relying on the semantic correctness of explanatory metadata. Accordingly, LLM-generated outputs should be treated as candidate engineering solutions that require deterministic verification rather than authoritative results accepted without validation.

---

## Quantitative Results

The controlled comparison between the baseline and remediated SBOMs produced the following measurements.

| Metric | Baseline | Remediated |
| :--- | :---: | :---: |
| **Total detected scanner findings** | 182 | 181 |
| **npm ecosystem scanner findings** | 182 | 181 |
| **Net reduction** | — | 1 |
| **Percentage reduction** | — | 0.55% |

In addition to the aggregate scanner findings shown above:

- `CVE-2023-32314` was absent from the remediated Grype report.
- `CVE-2024-45590` was absent from the remediated Grype report.

---

## Interpretation of the Quantitative Results

The experimental results demonstrate that successful remediation of individual vulnerabilities does not necessarily produce a proportional reduction in aggregate scanner findings.

Within the evaluated representative scenarios:

- Two targeted vulnerabilities were no longer detected.
- Aggregate scanner findings decreased by one.

This observation demonstrates that aggregate scanner findings should not be interpreted as a direct measure of remediation quality.

Instead, aggregate scanner findings represent the overall state of the dependency graph reported by the vulnerability scanner at a particular point in time.

Consequently, successful remediation of individual vulnerabilities does not necessarily correspond to an equivalent numerical reduction in aggregate scanner findings.

Determining the precise cause of the remaining aggregate finding would require a detailed comparison of every baseline and remediated scanner finding. A supplementary diff analysis of the Grype JSON files confirms that the successful removal of the two target CVEs coincided with the introduction of a new parallel finding due to the upgraded sub-dependency tree, resulting in the net reduction of exactly one finding.

---

## Primary Research Outcome

The principal outcome of this research is **not** the reduction in aggregate scanner findings.

Instead, the experiments demonstrate a reproducible workflow consisting of:

1. Deterministic vulnerability identification.
2. Threat intelligence enrichment.
3. Context-aware recommendation generation.
4. Constraint-aware package manager execution.
5. Dependency graph verification.
6. SBOM regeneration.
7. Post-remediation vulnerability analysis.

The documented workflow demonstrates that LLM-generated remediation recommendations can be evaluated objectively using deterministic validation rather than subjective assessment.

---

## Contribution of the Experimental Workflow

This repository does **not** propose replacing deterministic Software Composition Analysis (SCA) tools.

Instead, it positions the **Large Language Model (LLM)** as a decision-support component operating after deterministic vulnerability identification.

Within the representative scenarios documented in this repository, the generated remediation recommendations subsequently satisfied deterministic validation through:

- Successful package manager execution.
- Dependency graph verification.
- Regenerated SBOM generation.
- Post-remediation vulnerability analysis.

The contribution of this work is therefore the integration of contextual reasoning into an SBOM-driven remediation workflow while preserving deterministic verification throughout the experimental pipeline.

---

## Threats to Validity

The following considerations should be taken into account when interpreting the reported results.

### Internal Validity

The experiments were designed to minimise environmental variation through:

- Version-pinned tooling.
- Identical application versions.
- Identical prompt structure.
- Identical model configuration.
- Identical validation methodology.
- Repeated restoration of the experimental baseline.

Consequently, observed differences are attributed to the applied remediation strategy rather than environmental variation.

---

### Construct Validity

The evaluation focuses specifically on dependency remediation.

The experiments do **not** evaluate:

- Vulnerability discovery.
- Software Composition Analysis (SCA) accuracy.
- Vulnerability scanner performance.
- Exploit prediction.
- Runtime exploit mitigation.
- Application functionality beyond basic module loading.
- Overall software quality.

Accordingly, conclusions should be interpreted solely within the context of dependency remediation workflows.

---

### External Validity

The representative scenarios documented within this repository originate from **OWASP Juice Shop**.

The complete thesis additionally evaluates **Apache Airflow** using the identical experimental methodology.

Although the methodology is intentionally application-independent, the reported results should not be generalised to all software ecosystems without additional empirical evaluation.

Future work involving additional package ecosystems and application domains would strengthen external validity.

---

### Reproducibility

The experimental workflow has been designed to maximise reproducibility through:

- Version-pinned tooling.
- Standardised prompt templates.
- Documented model configuration.
- Structured JSON outputs.
- Deterministic validation stages.
- Archived experimental artifacts.

Minor lexical variation may occur within the LLM-generated rationale despite using a temperature of `0.0`.

However, during the documented experiments, no variation affecting the evaluated decision variables (`action_type`, `package_name`, or `target_version`) was observed.

---

## Limitations

Several limitations should be acknowledged.

The representative scenarios documented within this repository evaluate only a subset of the complete experimental dataset.

The repository intentionally focuses on demonstrating the reproducible methodology rather than presenting all eighteen experimental scenarios.

Furthermore:

- Only representative dependency remediation scenarios are documented in this repository.
- The repository examples focus on the npm ecosystem.
- Runtime verification is limited to representative module loading rather than comprehensive application testing.
- Aggregate scanner findings alone are insufficient to characterise remediation quality.
- The repository documents the methodology rather than the complete empirical dataset presented in the accompanying thesis.

These limitations define the scope within which the reported conclusions should be interpreted.

---

## Lessons Learned

Several practical observations emerged during the development of the experimental workflow.

- **Installation vs. Remediation:** Successful package installation should not be interpreted as successful dependency remediation.

- **Dependency Graph Verification:** Inspecting the dependency graph provides complementary evidence beyond package manager exit codes and is therefore an essential validation step.

- **Package Manager Constraints:** Package manager constraints (for example, npm `EOVERRIDE`) constitute measurable experimental observations and should be incorporated into remediation workflows rather than bypassed.

- **Deterministic Validation:** LLM-generated recommendations should always undergo deterministic validation through package manager execution, dependency graph verification, SBOM regeneration, and vulnerability rescanning.

---

## Summary

The representative experiments demonstrate a reproducible methodology for evaluating LLM-assisted dependency remediation under controlled conditions.

Rather than relying solely on the remediation recommendation generated by the LLM, every recommendation is subjected to deterministic validation through package manager execution, dependency graph verification, SBOM regeneration, and post-remediation vulnerability analysis.

The recommendation generated by the LLM is therefore treated as an engineering hypothesis rather than experimental evidence.

Only recommendations that successfully satisfy every validation stage are considered experimentally successful.

This separation between recommendation generation and deterministic validation represents the principal methodological contribution documented within this repository and forms the foundation for evaluating all eighteen experimental scenarios presented in the accompanying Master's thesis.