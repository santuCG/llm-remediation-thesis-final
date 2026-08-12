# Airflow Scenarios (Docker-Based Methodology)

## Strict Reproducibility Baseline

- **Target Docker Image Version:** apache/airflow:2.9.2
- **Grype Version & DB Build Date:** v0.112.0 (DB Built: 2026-07-08T07:03:51Z)
- **SBOM Tool:** syft-1.44.0
- **Total Packages Scanned:** 622
- **Total Raw Vulns Detected:** 1659

**State-Freeze Rationale:**
To reproduce the raw baseline (e.g., 1659 vulnerabilities), the exact Docker Image tag must be scanned. However, to guarantee the LLM's remediation targets do not drift over time, the exact transitive dependency graph was extracted via pip freeze and stored in this evidence folder. This ensures the LLM acts upon a cryptographically frozen snapshot of the application's dependencies.\n\n**Airflow Constraints Warning:** Airflow packages strictly require Apache constraint files during pip install to resolve dependencies without conflicts.

## Steps for Exact Reproducibility

To guarantee that any researcher can reproduce these exact Grype findings and LLM responses, a strict Docker-based snapshot approach is followed.

**Generating the SBOM:**
```bash
syft scan registry:apache/airflow:2.9.2 -o spdx-json=airflow_sbom.json
```

**Scanning the SBOM:**
```bash
GRYPE_DB_AUTO_UPDATE=false grype sbom:airflow_sbom.json -o json=airflow_grype.json
```


> **Phase 2 Context:** The deterministic baseline was executed on remote GitHub Actions CI. The outcome for PyPI was a failure via 'Constraint Collapse' (ResolutionImpossible). The methodology is now transitioning into Phase 3 (LLM Execution).
