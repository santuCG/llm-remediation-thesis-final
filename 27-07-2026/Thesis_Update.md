# Master's Thesis Progress Update: LLM-Driven Dependency Remediation

**Author:** Santosh Nagaraj, SRH University Berlin  
**Date:** 27 July 2026  
**Repository:** [llm-remediation-thesis-final](https://github.com/santuCG/llm-remediation-thesis-final)

---

## 1. Experimental Results Summary

| Metric | Baseline (Scanner-Only) | Remediated (LLM-Reasoner) |
|--------|-------------------------|---------------------------|
| **Total Scenarios** | 18 | 18 |
| **Juice Shop (npm)** | 0 / 9 Passed (9 Failed) | 9 / 9 Passed |
| **Airflow (python)** | 0 / 9 Passed (9 Failed) | 9 / 9 Passed |
| **Success Rate** | **0%** | **100%** |

### Why the Baseline Failed
- **npm (Juice Shop)**: Standard direct install attempts of scanner-recommended versions failed due to **`ERESOLVE`** peer dependency conflicts.
- **pip (Airflow)**: Direct version upgrades failed due to strict constraints file pinning, resulting in **`ResolutionImpossible`** errors.

### Why the LLM Reasoning Layer Succeeded
Instead of recommending a blind upgrade, the LLM reasons over the dependency path and the package manager error output. It dynamically recommends context-aware actions:
- For transitive peer dependency conflicts (npm), it recommends injecting a targeted **`overrides`** block.
- For pip constraint conflicts, it recommends relaxed version pins.

---

## 2. LLM Prompt Architecture & API Request

To ensure the LLM outputs exact structural fixes, the prompt is structured as follows:

```
Scenario ID: [SCENARIO_ID]
Vulnerable Package: [PACKAGE_NAME]
Current Version: [CURRENT_VERSION]
Recommended Version: [FIX_VERSION_GRYPE]
CVE: [CVE_ID]
CVSS: [CVSS_SCORE]
EPSS: [EPSS_SCORE]
KEV: [KEV_STATUS]
Dependency Path: [DIRECT / TRANSITIVE]
Error Log: [PACKAGE_MANAGER_ERROR]
```

The model output is constrained via a strict JSON schema forcing it to return:
```json
{
  "action_type": "OVERRIDE | CONSTRAINT_RELAXATION | DIRECT_BUMP | PACKAGE_REPLACEMENT | DEFER",
  "recommended_version": "version_string",
  "fix_target": "package_name",
  "rationale": "reasoning_details",
  "prioritisation_reasoning": "cvss_epss_logic"
}
```

---

## 3. Configuration & Parameter Rationale

To ensure reproducibility in scientific research, the API call's `generationConfig` is set with the following parameters:
- **`temperature: 0.0`**: Enforces strict determinism by stripping random creativity, forcing the model to select only the highest-probability tokens.
- **`seed: 42`**: Anchors the pseudo-random generator state to ensure identical responses across API requests.
- **`topP: 1.0`** and **`topK: 1`**: Restricts choices to the single top token, ensuring strict adherence to the required JSON schema.
