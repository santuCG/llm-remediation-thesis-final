# Thesis Insights: Legacy Runs & Iterative Development

*Note: This document extracts all positive findings, critical errors, and required outputs from the initial prototype runs (JS-01 / JS-08) prior to the rigorous methodology overhaul.*

## 1. Prototype Successes (Positives)

- **LLM Determinism Achieved:** Across multiple prototype executions with `temperature: 0.0` and `seed: 42`, the LLM produced syntactically valid JSON on the first attempt 100% of the time. The prompt architecture proved highly resilient to hallucinations regarding JSON structure.
- **Pipeline Fail-Safe Validation:** The framework successfully proved its core DevSecOps value. When the LLM confidently supplied a `transitive_override` for `vm2` (CVE-2023-32314), the pipeline updated the manifest. However, the subsequent `npm install` pulled in newer transitive types (`@types/lodash`) that were incompatible with Juice Shop's legacy TypeScript compiler (`tsc ~4.6.0`). The pipeline caught the `TS1005: '?' expected` error and correctly halted the run, proving that **vulnerability removal alone does not equal a functional application.**

## 2. Methodology Discoveries (Why We Overhauled)

- **The Problem with Raw String Manifest Patching:** The original pipeline expected the LLM to output a raw string for `"manifest_patch"`. This worked for `npm` (e.g., `{"overrides": {"vm2": "3.9.18"}}`), but proved entirely incompatible with PyPI constraints where simple overrides don't exist. This necessitated the methodology shift to a **structured intermediate representation** (`operation`, `package`, `constraint`).
- **Manual Baseline Contamination Risk:** Our initial exploratory case study compared the pipeline to a theoretical manual approach where the "human" iterated on the pipeline's failures. We realized this invalidates the human control group. The new methodology mandates a pure, unassisted human baseline starting from the identical commit SHA.
- **Data Governance & Auditability:** We discovered that GitHub Actions artifacts expire and can be lost. To ensure thesis defense capability, we instituted the `gh run download` flat-directory structure, pulling down the `llm-request`, `llm-response`, `metrics`, and newly added `candidate-ranking` JSON files immediately after every run.

## 3. Extracted Logs & Telemetry

### JS-01 `vm2` Failed Build Log
```bash
> juice-shop@15.3.0 build:server
> tsc

node_modules/@types/babel__traverse/index.d.ts(1467,40): error TS1005: '?' expected.
node_modules/@types/babel__traverse/index.d.ts(1475,42): error TS1005: '?' expected.
node_modules/@types/lodash/common/common.d.ts(266,65): error TS1005: '?' expected.
```

### JS-01 `vm2` Legacy Metrics Snapshot
```json
{
  "application": "applications/juice-shop",
  "ecosystem": "npm",
  "selected_package": "vm2",
  "api_cve_id": "CVE-2023-32314",
  "strategy": "transitive_override",
  "llm_response_valid": true,
  "build_success": false,
  "failure_stage": "build"
}
```

*All legacy scripts, logs, and artifacts have been moved to the `archive/` directory to preserve historical record without contaminating the final 18 scenarios.*
