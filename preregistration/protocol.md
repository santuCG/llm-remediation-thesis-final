# Experimental Protocol

**Thesis:** Context-Aware Dependency Remediation in SBOM-Driven CI/CD Pipelines Using Large Language Models  
**Author:** Santosh Nagaraj — SRH University Berlin  
**Date:** 2026-06-28

---

## Phase 1: Setup — Application Acquisition

Two open-source applications were selected at pinned versions:

| Application | Version | Acquisition Method |
|-------------|---------|-------------------|
| OWASP Juice Shop | v15.3.0 | `git clone https://github.com/juice-shop/juice-shop.git && git checkout v15.3.0` |
| Apache Airflow | v2.9.2 | `docker pull apache/airflow:2.9.2` |

---

## Phase 1: Setup — SBOM Generation

**Tool:** Syft (see `tool_versions.md` for exact versions)  
**Output format:** SPDX-JSON

**Methodology split (dictated by language ecosystem):**

**Methodology Divergence and Boundary Scoping:** Syft was run against the source code repositories for Juice Shop and , whereas it was run against the official compiled Docker image for Apache Airflow. This variance was dictated by language ecosystem behaviors.

Python applications utilizing standard `pyproject.toml` files do not lock transitive runtime dependencies in source control; therefore, scanning the compiled Airflow Docker image's `site-packages` was required to generate an accurate runtime SBOM. Conversely, Node.js applications include a deterministic `package-lock.json`, allowing Syft to capture the entire dependency tree directly from source.

Utilizing the Node.js source repositories explicitly expands the security boundary to include development-time vulnerabilities (`devDependencies`). Scanning the corresponding Node.js production Docker images would strip these out via `npm ci --production`. While excluding `devDependencies` reflects the true runtime attack surface, the source-code repository scan was selected for Node.js to capture a broader, lifecycle-wide view of engineering dependencies, marking a documented variance in the experimental setup.

Reference: https://spdx.dev/

---

## Phase 3 — Vulnerability Detection

**Tool:** Grype v0.112.0  
**Input:** SPDX-JSON SBOM from Phase 2  
**Output format:** JSON  
**Inclusion threshold for further consideration:** CVSS ≥ 7.0 (High or Critical only)

Grype checks every package against multiple vulnerability databases: NVD, GitHub Security Advisories (GHSA), and OSV.

Reference: https://github.com/anchore/grype

---

## Phase 2: Deterministic Baseline — Scenario Selection (Pre-Registration)

A vulnerability scenario is eligible only when **all** of the following are satisfied:

1. **Ecosystem scope:** npm (for Juice Shop) or python (for Airflow). OS-level (`deb`) and runtime (`UnknownPackage`) packages are excluded.
2. **Fix version exists:** Grype must report a `fix.state = "fixed"` and at least one fix version. Scenarios with no available fix cannot be tested.
3. **Fix version registry-verified:** The fix version must exist on the official package registry (npm or PyPI). Verified via direct HTTP lookup — HTTP 404 = disqualified.
4. **CVE ID confirmed:** To validate vulnerabilities against the National Vulnerability Database (NVD) (which relies on Common Vulnerabilities and Exposures (CVE) IDs), GHSA IDs were mapped GitHub Security Advisory (GHSA) IDs reported by Grype to their corresponding CVE IDs using the Open Source Vulnerability (OSV) API (https://osv.dev/). No CVE ID = cannot verify in NVD = disqualified.
5. **NVD-verified:** The CVE must appear in the NVD REST API with a CVSS score. NOT FOUND = disqualified. Reference: https://nvd.nist.gov/developers/vulnerabilities
6. **CVSS ≥ 7.0:** Sourced from NVD where available. Where NVD enrichment is unavailable ("Not Scheduled"), CVSS sourced from GitHub Security Advisory as authoritative fallback.
7. **Package diversity:** No two scenarios within the same application use the same package.

Enrichment signals collected for each selected scenario:
- **CVSS** — severity/impact score from NVD or GHSA
- **EPSS** (Exploit Prediction Scoring System) — exploit prediction probability from FIRST API (https://api.first.org/data/v1/epss)
- **KEV** — CISA Known Exploited Vulnerabilities status (https://www.cisa.gov/known-exploited-vulnerabilities-catalog)

**Target:** 9 scenarios per application, 18 total. Full selection rationale in `PRE_REGISTRATION_MASTER.md`.

---

## Phase 3: LLM Execution

Two conditions are applied to each of the 18 scenarios:

**Baseline (Deterministic):** The fix version recommended by Grype is applied directly to the dependency file. No LLM involved.

**Experimental (Gemini 2.5 Flash):** The LLM receives a structured input payload containing: package name, vulnerable version, CVE ID, CVSS score, EPSS score, KEV status, and Grype-recommended fix version. It returns a JSON response with its recommended action and version.

**LLM configuration:**
- Model: Gemini 2.5 Flash
- Temperature: 0
- JSON schema enforcement: enabled
- Web grounding / Google Search tool: NOT enabled

---

## Phase 6 — Evaluation

Each remediation attempt passes through four validation gates in sequence:

| Gate | Check | Tool |
|------|-------|------|
| 1 | Safe Dependency Resolution (Topological Integrity) — package manager accepts the new version without conflicts and WITHOUT graph pollution/transitive elevation | npm / pip |
| 2 | Build success — application builds with the updated dependency | npm build / pip install |
| 3 | Test pass — existing automated tests still pass | npm test / pytest |
| 4 | Vulnerability rescan — Grype confirms CVE is no longer present | Grype |

A remediation attempt is counted as **successful** only if it passes all four gates.

**Metrics collected:**
- Remediation success rate (all 4 gates passed)
- Gate failure distribution (which gate failed, if any)
- LLM-recommended version correctness (matches a valid registry version)
- LLM major-version-jump risk flagging (did the LLM warn about breaking changes?)
- Special case: did the LLM recommend migration for JS-06 (moment, deprecated package)?

---

## Environment Reset

Each scenario runs in a clean, isolated environment. The application is restored to its original pinned version before each test run. For Airflow, each run uses a fresh Docker container.
