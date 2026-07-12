# Pre-Registration Data

This directory contains all artifacts generated **before** running the LLM remediation experiment. Pre-registration locks the 18 vulnerability scenarios in advance, preventing post-hoc cherry-picking of results.

**Date of pre-registration:** 2026-06-28

---

## Directory Contents

### Core Pre-Registration Documents

| File | Description |
|------|-------------|
| `MASTER_METHODOLOGY_RECORD.md` | **The primary document.** Records all 18 scenarios, the full 8-step selection pipeline, every dropped candidate and its reason, limitations, and what happens next in the experiment. |
| `JUICESHOP_PREREGISTRATION.md` | Step-by-step walkthrough for Juice Shop v15.3.0 — all 8 pipeline steps with inline Python scripts and the 6 registered scenarios. |
| `AIRFLOW_PREREGISTRATION.md` | Step-by-step walkthrough for Apache Airflow v2.9.2 — all 8 pipeline steps with inline Python scripts and the 6 registered scenarios. |

### Supporting Files

| File | Description |
|------|-------------|
| `protocol.md` | Full experimental protocol for all 6 phases (acquisition → SBOM → scan → selection → LLM experiment → evaluation). |
| `tool_versions.md` | Exact tool versions used during scanning. |
| `kev_snapshot.json` | Static snapshot of the CISA KEV catalog downloaded on 2026-06-28. Proves what the KEV catalog contained at the time of selection. All 18 scenarios returned KEV=FALSE against this snapshot. |

---

## Raw Evidence

The raw SBOM and Grype scan outputs are stored in `../applications/evidence/`:

| File | Application | Scan Method |
|------|-------------|-------------|
| `juiceshop-sbom.spdx.json` | Juice Shop v15.3.0 | Source directory |
| `juiceshop-grype.json` | Juice Shop v15.3.0 | Source directory |
| `airflow-sbom.spdx.json` | Apache Airflow v2.9.2 | Docker image `apache/airflow:2.9.2` |
| `airflow-grype.json` | Apache Airflow v2.9.2 | Docker image `apache/airflow:2.9.2` |

---

## Machine-Readable Scenarios

The final 18 scenarios are also available as a structured JSON file for use by the experiment pipeline:

`../experiment/final_18_scenarios.json`

This file has been cross-verified field-by-field against all four pre-registration Markdown tables. No discrepancies.
