# Apache Airflow Vulnerability Pre-Registration
## SBOM-Driven LLM-Assisted Dependency Remediation — Master's Thesis

**Application:** Apache Airflow v2.9.2  
**Thesis:** Context-Aware Dependency Remediation in SBOM-Driven CI/CD Pipelines Using Large Language Models  
**Author:** Santosh Nagaraj — SRH University Berlin  
**Date of scan and data snapshot:** 2026-06-28  
**Tools:** Syft v1.44.0 · Grype v0.112.0 · Python 3.x  
**Image used:** `apache/airflow:2.9.2` (Docker Hub official image)

---

## What This Document Is

This README records every step taken to arrive at the 9 pre-registered vulnerability scenarios for Apache Airflow v2.9.2. The same manual process used for Juice Shop was followed here. The key difference is that Airflow is a Python application — the ecosystem is PyPI instead of npm, fix version verification uses the PyPI JSON API, and the Grype artifact type is `python` instead of `npm`.

---

## Prerequisites

```bash
syft version       # must show v1.44.0
grype version      # must show v0.112.0
python3 --version  # any 3.x is fine
docker --version   # required for Airflow — see Step 1
```

---

## Step 1 — Why Docker Was Required for Airflow

For Juice Shop, Syft scanned the cloned source directory directly and found npm packages from the lockfile. Airflow is different.

When the Airflow repository was cloned at tag 2.9.2 and ran Syft on the directory, the scan returned 144 matches — all npm packages from Airflow's bundled React frontend UI. Zero Python packages were found. This is because Syft's Python catalogers (`python-installed-package-cataloger`, `python-package-cataloger`) only find packages that are actually installed in a Python environment. A source checkout does not have installed packages — only `pyproject.toml` declaring what should be installed.

Since no Python environment with Airflow's dependencies was set up on the VM, the official Docker image was used instead. The Docker image has all Python dependencies pre-installed, so Syft can catalogue them correctly.

```bash
# Scan with Syft directly against the image registry
syft scan registry:apache/airflow:2.9.2 -o spdx-json=airflow_sbom.json

# Run Grype against the SBOM
grype sbom:airflow_sbom.json -o json=airflow_grype.json
```

**Why this is valid for the thesis:** The Docker image `apache/airflow:2.9.2` is the official published release artifact from the Apache Airflow project. It reflects the actual deployed state of Airflow 2.9.2 with all runtime dependencies pinned. Scanning the image is more representative of a real CI/CD environment than scanning a source checkout.

Reference: https://hub.docker.com/r/apache/airflow/tags

---

## Step 2 — Verify the Scan Captured Python Packages

After running Syft on the Docker image:

- Total Grype matches: 1379
- Artifact types found: `deb` (1054), `python` (167), `UnknownPackage` (51), `go-module` (107)
- Python matches: 167

The 167 Python matches are the usable pool. The deb, go-module, and UnknownPackage entries are OS-level or runtime packages — out of scope for this thesis.

---

## Step 3 — Filter to Usable Candidates

Filter rules applied:

- Exclude `deb`, `UnknownPackage`, `go-module` artifact types
- Exclude `apache-airflow` itself — upgrading the framework version is not a dependency remediation scenario
- Exclude `apache-airflow-providers-*` packages — these are first-party Airflow plugin packages, not third-party dependencies
- Require a fix version to exist in the Grype output
- Require High or Critical severity only
- Deduplicate by package+CVE (same package appearing multiple times with different GHSA IDs for the same CVE counted once)

This produced a shortlist of 15 unique candidates across different packages.

---

## Step 4 — Map GHSA IDs to CVE IDs

Same process as Juice Shop. OSV API used to map GHSA identifiers to CVE IDs.

Reference: https://osv.dev/

**Results (2026-06-28):**

| GHSA | Package | Mapped CVE |
|------|---------|------------|
| GHSA-2g68-c3qc-8985 | werkzeug | CVE-2024-34069 |
| GHSA-cx63-2mw6-8hw5 | setuptools | CVE-2024-6345 |
| GHSA-3ww4-gg4f-jr7f | cryptography | CVE-2023-50782 |
| GHSA-8w49-h785-mj3c | tornado | CVE-2024-52804 |
| GHSA-29h4-r29x-hchv | redshift-connector | CVE-2026-8838 |
| GHSA-rgxp-2hwp-jwgg | pyarrow | CVE-2026-25087 |
| GHSA-vqfr-h8mv-ghfj | h11 | CVE-2025-43859 |
| GHSA-wvwj-cvrp-7pv5 | authlib | CVE-2026-27962 |
| GHSA-38jv-5279-wg99 | urllib3 | CVE-2026-21441 |
| GHSA-2h4p-vjrc-8xpq | mako | CVE-2026-44307 |
| GHSA-xgmm-8j9v-c9wx | pyjwt | CVE-2026-48526 |
| GHSA-vfmq-68hx-4jfw | lxml | CVE-2026-41066 |
| GHSA-6mq8-rvhq-8wgg | aiohttp | CVE-2025-69223 |
| GHSA-hgjp-83m4-h4fj | mysql-connector-python | CVE-2024-21272 |
| GHSA-jr27-m4p2-rc6r | pyasn1 | CVE-2026-30922 |

---

## Step 5 — Verify Fix Versions Exist on PyPI

Unlike Juice Shop which used the npm registry, Airflow fix versions are verified against the PyPI JSON API.

Reference: https://pypi.org/pypi/{package}/{version}/json

**Results (2026-06-28):** All 15 fix versions confirmed on PyPI.

---

## Step 6 — NVD Verification

All 15 CVEs checked against the NVD REST API with 6-second sleep between requests to avoid rate limiting.

Reference: https://services.nvd.nist.gov/rest/json/cves/2.0

**Results (2026-06-28):**

| CVE | Package | CVSS | NVD Status | Decision |
|-----|---------|------|------------|----------|
| CVE-2026-8838 | redshift-connector | 9.8 | Awaiting Analysis | PASS |
| CVE-2025-43859 | h11 | 9.1 | Deferred | PASS |
| CVE-2026-27962 | authlib | 9.1 | Analyzed | PASS |
| CVE-2024-6345 | setuptools | 8.8 | Deferred | PASS |
| CVE-2024-34069 | werkzeug | 7.5 | Analyzed | PASS |
| CVE-2023-50782 | cryptography | 7.5 | Modified | PASS |
| CVE-2024-52804 | tornado | 7.5 | Modified | PASS |
| CVE-2026-25087 | pyarrow | 7.0 | Analyzed | PASS (not selected — see rationale) |
| CVE-2026-21441 | urllib3 | 7.5 | Modified | PASS (not selected) |
| CVE-2026-44307 | mako | 8.7 (CVSS v4.0) | Deferred | PASS (not selected — see note below) |
| CVE-2026-48526 | pyjwt | 7.4 | Analyzed | PASS (not selected) |
| CVE-2026-41066 | lxml | 7.5 | Analyzed | PASS (not selected) |
| CVE-2025-69223 | aiohttp | 7.5 | Analyzed | PASS (not selected) |
| CVE-2024-21272 | mysql-connector-python | 7.5 | Analyzed | PASS (not selected) |
| CVE-2026-30922 | pyasn1 | 7.5 | Modified | PASS (not selected) |

**mako — correction note:** This package was initially excluded from the candidate pool on the assumption that NVD had no CVSS score for CVE-2026-44307. That was wrong. NVD does report a CVSS v4.0 base score of 8.7 (High), sourced from GitHub Security Advisories. EPSS for this CVE is 0.0061 (45th percentile), KEV=FALSE. CVSS 8.7 is actually higher than AF-06 cryptography (7.5), the lowest-CVSS scenario in the final 6.

This was caught after the final 6 Airflow scenarios were already selected and documented. The decision was made to keep the original 6 as pre-registered rather than swap mako in after seeing the full comparison, since revising scenario selection after the fact — even to fix an error — risks introducing selection bias. mako is documented here as a known limitation: a valid, arguably stronger candidate that was wrongly excluded from consideration during the original selection pass.

---

## Step 7 — Collect EPSS Scores

EPSS API endpoint used: `https://api.first.org/data/v1/epss`

Note: The older endpoint `/data/1.0/epss` returns 404 — the correct path is `/data/v1/epss`.

**Results (2026-06-28):**

| CVE | EPSS Score | Percentile |
|-----|------------|------------|
| CVE-2026-8838 | 0.0081 | 52nd |
| CVE-2025-43859 | 0.0052 | 40th |
| CVE-2026-27962 | 0.0041 | 33rd |
| CVE-2024-6345 | 0.0194 | 78th |
| CVE-2024-34069 | 0.0340 | 87th |
| CVE-2023-50782 | 0.0112 | 62nd |
| CVE-2024-52804 | 0.0105 | 60th |
| CVE-2026-25087 | 0.0081 | 52nd |
| CVE-2026-21441 | 0.0068 | 48th |
| CVE-2026-48526 | 0.0023 | 14th |
| CVE-2026-41066 | 0.0032 | 24th |
| CVE-2025-69223 | 0.0030 | 22nd |
| CVE-2024-21272 | 0.0052 | 40th |
| CVE-2026-30922 | 0.0058 | 43rd |

---

## Step 8 — Check CISA KEV Status

Reference: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json

**Results (2026-06-28):** All 14 candidates returned KEV=FALSE.

**Limitation:** KEV is a constant (always FALSE) across all Airflow scenarios. The KEV enrichment signal cannot produce differential data for this application. See master pre-registration document for the full limitation statement.

---

## Final Pre-Registered Scenarios — Apache Airflow v2.9.2

All data snapshotted on 2026-06-28.

| ID | CVE | Package | Vuln Ver | Fix Ver | CVSS | EPSS | Percentile | KEV | Severity | Jump Type |
|----|-----|---------|----------|---------|------|------|------------|-----|----------|-----------|
| AF-01 | CVE-2026-8838 | redshift-connector | 2.1.1 | 2.1.14 | 9.8 | 0.0081 | 52nd | No | Critical | Minor |
| AF-02 | CVE-2025-43859 | h11 | 0.14.0 | 0.16.0 | 9.1 | 0.0052 | 40th | No | Critical | Minor |
| AF-03 | CVE-2024-6345 | setuptools | 66.1.1 | 70.0.0 | 8.8 | 0.0194 | 78th | No | High | Minor |
| AF-04 | CVE-2024-34069 | werkzeug | 2.2.3 | 3.0.3 | 7.5 | 0.0340 | 87th | No | High | Major (2→3) |
| AF-05 | CVE-2024-52804 | tornado | 6.4 | 6.4.2 | 7.5 | 0.0105 | 60th | No | High | Patch |
| AF-06 | CVE-2023-50782 | cryptography | 41.0.7 | 42.0.0 | 7.5 | 0.0112 | 62nd | No | High | Minor |

### Selection Rationale

**AF-01 redshift-connector** — Highest CVSS (9.8) in the Airflow candidate pool. SQL injection vulnerability in an AWS Redshift database connector. Minor version jump but spans 13 patch releases (2.1.1→2.1.14), which is an unusual gap worth noting in the experiment. Adds cloud data warehouse ecosystem coverage that does not appear in the Juice Shop scenarios.

**AF-02 h11** — CVSS 9.1, HTTP/1.1 protocol library used internally by httpcore and httpx. Minor version jump (0.14→0.16). h11 is a transitive dependency — it is unlikely to appear in Airflow's direct dependency declarations. This tests whether the pipeline correctly identifies and remediates transitive Python dependencies, which is a known practical challenge in dependency management.

**AF-03 setuptools** — CVSS 8.8, remote code execution via a malicious wheel file during package installation. Minor version jump (66.1→70.0). setuptools is a build tool present in virtually every Python environment. High practical relevance. EPSS at 78th percentile is the second highest in the Airflow pool.

**AF-04 werkzeug** — CVSS 7.5 but EPSS at 87th percentile — the highest exploitation probability score in the entire Airflow candidate pool, despite not having the highest CVSS. This is directly relevant to the research sub-question about whether CVSS-only prioritisation is sufficient. werkzeug is a direct Airflow dependency via Flask. Major version jump (2→3) introduces breaking change risk, making this the most complex remediation scenario in the Airflow set.

**AF-05 tornado** — CVSS 7.5, HTTP header parsing vulnerability (DoS). Patch-level fix (6.4→6.4.2), lowest remediation risk in the set. Serves as the Airflow control scenario — expected to succeed under both baseline and LLM conditions. Equivalent function to body-parser (Juice Shop) in the overall design.

**AF-06 cryptography** — CVSS 7.5, Bleichenbacher timing attack via RSA PKCS#1 v1.5 decryption. Minor version jump (41.0.7→42.0.0). The cryptography package is one of the most mature and widely used Python security libraries. Its fix is well-documented and the upgrade path is stable — useful contrast against redshift-connector and h11 in terms of package maturity and expected LLM confidence.

### Composition of the 9 Scenarios

- CVSS range: 9.8, 9.1, 8.8, 7.5, 7.5, 7.5
- Severity: 2 Critical, 4 High
- Jump type: 1 patch, 4 minor, 1 major
- Package categories: database connector, HTTP protocol library, build tooling, web framework middleware, async web server, cryptographic library
- No package overlap within Airflow scenarios
- No CVE repeated from the Juice Shop scenarios
- Ecosystem: PyPI only
- KEV: 0/6, all KEV=FALSE
- All fix versions confirmed on PyPI 2026-06-28
- All CVEs confirmed in NVD 2026-06-28

---

## Files Produced

| File | Description |
|------|-------------|
| `airflow_sbom.json` | Syft SPDX-JSON SBOM from Docker image apache/airflow:2.9.2 — **to be attached as evidence** |
| `airflow_grype.json` | Grype scan output — **to be attached as evidence** |
| `trim_npm.py` | Filter script adapted for Python artifact type |
| `get_cve_mappings_airflow.py` | Maps GHSA IDs to CVE IDs via OSV API |
| `verify_pypi_versions_airflow.py` | Confirms fix versions exist on PyPI JSON API |
| `nvd_verify_airflow.py` | Verifies each CVE exists in NVD with CVSS score |
| `get_epss_airflow.py` | Retrieves EPSS scores from FIRST API |
| `check_kev_airflow.py` | Checks CVEs against CISA KEV catalogue |
