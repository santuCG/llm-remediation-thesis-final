# Case Study: VM2 Remediation and Transitive Build Breakage

## Overview

This document serves as empirical evidence for the thesis section detailing the necessity of a complete DevSecOps validation pipeline (Build → Test → Rescan) when applying LLM-generated dependency remediations.

**Scenario:** JS-01
**Target Package:** `vm2`
**Vulnerability:** CVE-2023-32314 (Sandbox Escape / Remote Code Execution)
**CVSS Score:** 9.8 (Critical)

## 1. Process Followed

To test the LLM's determinism and the pipeline's robustness, the automated remediation workflow was configured strictly:
- `temperature`: `0.0`
- `seed`: `42`
- The pipeline was manually invoked multiple times explicitly targeting the `vm2` scenario via the `TARGET_CVE` parameter bypass to observe variance across runs.

The pipeline architecture enforces the following validation chain:
1. Generate Baseline SBOM and vulnerabilities.
2. Select Candidate.
3. Obtain LLM Remediation JSON.
4. Parse JSON (Retry if malformed).
5. Apply Remediation (Structured manifest update).
6. Validate (Clean Install → Build → Tests → Rescan).

## 2. What We Caught (Key Findings)

### Finding A: LLM Determinism
Across the executions performed in this experiment, all LLM responses produced syntactically valid JSON on the first attempt. No hallucinations were detected in the JSON structure, proving the strict prompt architecture effectively mitigated the non-deterministic output format issues previously observed in early experiments.

### Finding B: Transitive Incompatibility Detection
The LLM accurately recognized the severity of the `vm2` vulnerability and generated a valid remediation payload using a `transitive_override` strategy to force the package resolution in `package.json`. 

While this successfully altered the dependency graph, the pipeline's **Build Phase** caught a critical failure: running `npm install` with these overrides forced modern transitive dependencies (`@types/lodash`, `@types/babel__traverse`) into the tree. These newer type definitions were incompatible with the older `tsc` (TypeScript Compiler) version defined in Juice Shop v15.3.0.

This perfectly validates the thesis premise: **Vulnerability removal alone does not equal a functional application.** Without the build/test stages of the pipeline, the automated system would have committed broken code to the repository under the false assumption that patching the CVE was a complete success.

## 3. Empirical Evidence (Log Snippets)

### Metrics Telemetry (from `metrics.json`)

The extracted telemetry proves that the LLM passed JSON validation but correctly failed the pipeline's build stage:

```json
{
  "application": "applications/juice-shop",
  "ecosystem": "npm",
  "selected_package": "vm2",
  "api_cve_id": "CVE-2023-32314",
  "severity": "critical",
  "strategy": "transitive_override",
  "llm_response_valid": true,
  "build_success": false,
  "test_success": false,
  "runtime_success": false,
  "failure_stage": "build",
  "retry_count": 0,
  "llm_iteration": 1
}
```

### Build Failure Logs (from `build.log`)

The `Phase 6` build log explicitly captures the `tsc` compiler throwing syntax errors due to the modern type overrides:

```bash
> juice-shop@15.3.0 build:server
> tsc

node_modules/@types/babel__traverse/index.d.ts(1467,40): error TS1005: '?' expected.
node_modules/@types/babel__traverse/index.d.ts(1475,42): error TS1005: '?' expected.
node_modules/@types/lodash/common/common.d.ts(266,65): error TS1005: '?' expected.
node_modules/@types/lodash/common/object.d.ts(1026,46): error TS1005: '?' expected.
node_modules/@types/lodash/common/object.d.ts(1031,46): error TS1005: '?' expected.
node_modules/@types/lodash/common/object.d.ts(1041,46): error TS1005: '?' expected.
```

## Conclusion for Thesis

The `vm2` case study demonstrates that the framework behaves exactly as a DevSecOps safety net should. It successfully leverages LLM intelligence to determine a remediation strategy, applies it deterministically, but **retains the final authority on code health** by halting the pipeline when the LLM's fix introduces architectural incompatibilities. 

Although the transitive override successfully removed the vulnerable dependency from the software bill of materials, the resulting dependency graph introduced newer transitive type definitions incompatible with the application's existing compiler toolchain. This demonstrates that SBOM-level vulnerability remediation must be validated against downstream build integrity before deployment.

### Pipeline Stage Validation Summary

| Stage | Result |
| :--- | :--- |
| Vulnerability detected | ✅ |
| LLM generated valid JSON | ✅ |
| Structured manifest update | ✅ |
| Dependency resolution | ✅ |
| Build | ❌ |
| Tests | Not executed / Failed |
| Runtime | Not executed / Failed |
| Rescan | Not executed / Failed |
