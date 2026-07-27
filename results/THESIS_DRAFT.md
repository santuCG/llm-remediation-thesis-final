# Abstract
[This section is pending completion pending final quantitative results.]

# Chapter 1: Introduction
Modern software supply chains rely heavily on open-source dependencies. When a vulnerability (CVE) is discovered deep within a dependency tree, traditional deterministic tools (like `npm audit`) often fail to resolve it, leading to "update fatigue." This thesis explores whether Large Language Models (LLMs) can safely and accurately navigate complex dependency graphs and remediate vulnerabilities without breaking the application build.

# Chapter 2: Methodology
To evaluate the efficacy of LLMs in DevSecOps, a rigorous, double-blind execution pipeline was constructed. 

## 2.1 The Automated LLM Pipeline
The automated pipeline relies on Gemini 2.5 Flash as the reasoning engine. 
- **SBOM Generation:** `syft` and `grype` generate a precise snapshot of the vulnerable state.
- **Context Windowing:** Irrelevant metadata is stripped from `package.json` to prevent prompt poisoning.
- **Structured Output:** The LLM is strictly constrained to output a JSON schema (`{"operation", "package", "constraint"}`), ensuring agnostic application across npm and PyPI.
- **Build Validation:** The objective of the experiment is to evaluate whether the LLM-selected remediation itself is compatible with the application, independent of unrelated dependency graph updates. Using `pip install --no-deps` isolates the proposed intervention while preserving the frozen dependency baseline used throughout the experiment. Integration tests and post-remediation vulnerability rescanning then determine whether the isolated intervention succeeds.
- **Dual-Metric Validation:** To prove viability, two metrics are logged: `failure_stage` (where the pipeline broke) and `validation_stage_reached` (the highest CI/CD gate successfully passed, e.g., build vs test).

## 2.2 The Human Control Group (Baseline)
To establish a verifiable baseline, 18 real-world CVE scenarios were executed manually by a human engineer without any AI assistance, starting from the exact same vulnerable commit SHA.

# Chapter 3: Results
[This section is pending completion pending final quantitative results.]

[This section will provide an in-depth analysis of specific failure stages based on the finalized dataset.]
