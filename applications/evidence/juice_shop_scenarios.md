# Juice Shop Scenarios (Docker-Based Methodology)

## Strict Reproducibility Baseline

- **Target Docker Image Version:** bkimminich/juice-shop:v15.3.0
- **Grype Version & DB Build Date:** v0.112.0 (DB Built: 2026-07-08T07:03:51Z)
- **SBOM Tool:** syft-1.44.0
- **Total Packages Scanned:** 2042
- **Total Raw Vulns Detected:** 378

**State-Freeze Rationale:**
To reproduce the raw baseline (e.g., 378 vulnerabilities), the exact Docker Image tag must be scanned. However, to guarantee the LLM's remediation targets do not drift over time, the exact transitive dependency graph was extracted via package-lock.json and stored in this evidence folder. This ensures the LLM acts upon a cryptographically frozen snapshot of the application's dependencies.

## Steps for Exact Reproducibility

To guarantee that any researcher can reproduce these exact Grype findings and LLM responses, a strict Docker-based snapshot approach is followed.

**Generating the SBOM:**
```bash
syft scan registry:bkimminich/juice-shop:v15.3.0 -o spdx-json=juice_shop_sbom.json
```

**Scanning the SBOM:**
```bash
GRYPE_DB_AUTO_UPDATE=false grype sbom:juice_shop_sbom.json -o json=juice_shop_grype.json
```


> **Phase 2 Context:** The deterministic baseline was executed on remote GitHub Actions CI. The outcome for npm was a silent success that caused 'Graph Pollution' (elevating transitive packages to direct dependencies). The methodology is now transitioning into Phase 3 (LLM Execution).
