# Juice Shop Vulnerability Pre-Registration
## SBOM-Driven LLM-Assisted Dependency Remediation — Master's Thesis

**Application:** OWASP Juice Shop v15.3.0  
**Thesis:** Context-Aware Dependency Remediation in SBOM-Driven CI Pipelines Using Large Language Model  
**Author:** Santosh Nagaraj — SRH University Berlin  
**Date of scan and data snapshot:** 2026-06-28  
**Tools:** Syft v1.44.0 · Grype v0.112.0 · Python 3.x

---

## What This Document Is

This README records every step taken to arrive at the 9 pre-registered vulnerability scenarios for Juice Shop. It exists so that:

1. Reviewers can verify the selection was not arbitrary
2. The process can be reproduced exactly for  and Apache Airflow
3. The scripts used are preserved alongside the rationale

---

## Prerequisites

Before starting, the following must be installed on the target environment or machine:

```bash
# Verify versions match exactly — these are locked for the thesis
syft version       # must show v1.44.0
grype version      # must show v0.112.0
python3 --version  # any 3.x is fine
```

Juice Shop must be cloned at exactly v15.3.0:

```bash
git clone https://github.com/juice-shop/juice-shop.git
cd juice-shop
git checkout v15.3.0
cat package.json | grep '"version"'
# Must print: "version": "15.3.0"
```

---

## Step 1 — Generate the SBOM via Lockfile Freeze

An SBOM (Software Bill of Materials) is a machine-readable list of every package the application depends on, with version numbers. Initially, the methodology attempted to generate this from the official Docker image to ensure parity with the CI validation environment.

However, scanning the Docker image introduced massive OS-level package pollution. To ensure experimental rigor and isolate the exact Node.js dependency graph, the methodology was frozen to use explicit package lockfiles as the definitive source of truth. Syft generates the SBOM directly from the lockfile.

**The correct command:**

```bash
syft file:package-lock.json -o spdx-json=juice-shop_sbom.json
```

This produces `juice-shop_sbom.json` — a SPDX-JSON format SBOM. The format is locked to SPDX-JSON throughout the thesis (not CycloneDX, despite the original proposal).

**Verify the SBOM captured npm packages:**

```bash
python3 -c "
import json
with open('juice-shop_sbom.json', encoding='utf-8') as f:
    data = json.load(f)
pkgs = data.get('packages', data.get('artifacts', []))
print(f'Total packages: {len(pkgs)}')
for p in pkgs[:5]:
    print(p.get('name'), p.get('version', p.get('versionInfo')))
"
```

Expected output: ~2041 packages, starting with npm package names like `1to2`, `@babel/...` etc.  
If only 26 packages or packages named `libc6`, `openssl` — the wrong directory or wrong cataloger was used.

---

## Step 2 — Run Grype Vulnerability Scan

Grype takes the SBOM and checks every package against vulnerability databases (NVD, GitHub Advisory, OSV, etc.).

```bash
grype sbom:juice-shop_sbom.json -o json=juice-shop_grype.json
```

**Verify the scan captured npm-level vulnerabilities:**

```bash
python3 -c "
import json
with open('juice-shop_grype.json', encoding='utf-8') as f:
    data = json.load(f)
matches = data.get('matches', [])
print(f'Total matches: {len(matches)}')
npm_matches = [m for m in matches if m['artifact']['type'] in ['npm', 'node-module', 'javascript']]
print(f'npm matches: {len(npm_matches)}')
for m in npm_matches[:10]:
    vuln = m['vulnerability']
    fix = vuln.get('fix', {}).get('versions', [])
    print(f\"{vuln['id']} | {m['artifact']['name']} {m['artifact']['version']} | fix: {fix} | {vuln.get('severity','?')}\")
"
```

Expected: 320 total matches, 231 npm matches.

---

## Step 3 — Filter to Usable Candidates

Not all 231 npm matches are usable for the thesis. The filter rules are:

- **Exclude OS packages** (`deb` type): `libc6`, `libssl1.1`, `openssl` — not application dependencies
- **Exclude runtime packages** (`UnknownPackage` type): `node` — not remediable via npm
- **Exclude vm2**: Over 20 CVEs were detected against vm2 3.9.17. Fix versions exist on npm (3.9.18, 3.10.0, 3.11.x confirmed). vm2 was excluded due to package concentration — having 20+ scenarios from one package would skew the results toward that single package's behaviour. However, this exclusion was an experimental oversight for one specific reason: vm2 suffered a sandbox escape severe enough that its maintainers formally declared it unmaintained and recommended migrating away from it entirely (see https://github.com/patriksimek/vm2/issues/533). A single vm2 scenario would have tested whether the LLM can identify an unpatchable package and produce a migration advisory instead of a version recommendation — an output type not represented by any of the 18 selected scenarios. moment (JS-06) partially covers the deprecated-library edge case but still has a real fix version. This gap is acknowledged in the limitations section of the master pre-registration document.
- **Require a fix version**: scenarios with no fix version cannot be used for remediation testing
- **Require High or Critical severity**: Medium and below excluded to keep scenarios experimentally meaningful

**Filter script (`trim.py` — extended version):**

```python
# save as trim_npm.py
import json

EXCLUDE_TYPES = {'deb', 'UnknownPackage'}
EXCLUDE_PKGS = {
    'vm2', 'node', 'libc6', 'libssl1.1', 'openssl',
    'libgcc-s1', 'libgomp1', 'libstdc++6'
}

with open('juice-shop_grype.json', encoding='utf-8') as f:
    data = json.load(f)

seen = {}
for m in data['matches']:
    art = m['artifact']
    vuln = m['vulnerability']

    if art['type'] in EXCLUDE_TYPES:
        continue
    if art['name'] in EXCLUDE_PKGS:
        continue

    fix_versions = vuln.get('fix', {}).get('versions', [])
    if not fix_versions:
        continue

    severity = vuln.get('severity', '')
    if severity not in ['High', 'Critical']:
        continue

    pkg = art['name']
    vid = vuln['id']
    key = f'{pkg}:{vid}'

    if key not in seen:
        seen[key] = {
            'id': vid,
            'package': pkg,
            'current_version': art['version'],
            'fix_version': fix_versions[0],
            'severity': severity,
            'type': art['type']
        }

for k, v in seen.items():
    print(f"{v['severity']:8} | {v['package']:30} {v['current_version']:15} -> {v['fix_version']:15} | {v['id']}")
```

```bash
python3 trim_npm.py
```

This produces ~60 unique candidates across different packages.

---

## Step 4 — Map GHSA IDs to CVE IDs

Grype reports many vulnerabilities using GitHub Security Advisory IDs (GHSA-xxxx-xxxx-xxxx). The thesis requires CVE IDs for NVD verification. The OSV API provides the mapping.

**Why this matters:** NVD verification is the pre-registration proof. GHSA IDs alone are not sufficient.

**Script to get CVE mappings:**

```python
# save as get_cve_mappings.py
import urllib.request, json, time

candidates = [
    ('jsonwebtoken', '0.1.0', 'GHSA-c7hr-j4mj-j2w6'),
    ('crypto-js', '3.3.0', 'GHSA-xwcq-pm8m-c4vf'),
    ('handlebars', '4.7.7', 'GHSA-2w6w-674q-4c4q'),
    ('lodash', '2.4.2', 'GHSA-jf85-cpcp-j695'),
    ('sanitize-html', '1.4.2', 'GHSA-cgfm-xwp7-2cvr'),
    ('sequelize', '6.34.0', 'GHSA-6457-6jrx-69cr'),
    ('body-parser', '1.20.1', 'GHSA-qwcr-r2fm-qrc7'),
    ('socket.io-parser', '4.0.5', 'GHSA-677m-j7p3-52f9'),
    ('tough-cookie', '2.5.0', 'GHSA-72xf-g2v4-qvf3'),
    ('moment', '2.0.0', 'GHSA-8hfj-j24r-96c4'),
    ('path-to-regexp', '0.1.7', 'GHSA-9wv6-86v2-598j'),
    ('ws', '7.4.6', 'GHSA-3h5v-q93c-6h6q'),
]

for pkg, ver, ghsa in candidates:
    time.sleep(1)
    try:
        url = f'https://api.osv.dev/v1/vulns/{ghsa}'
        req = urllib.request.urlopen(url, timeout=5)
        data = json.loads(req.read())
        aliases = data.get('aliases', [])
        cves = [a for a in aliases if a.startswith('CVE')]
        print(f'{ghsa} | {pkg:20} | CVE: {cves}')
    except Exception as e:
        print(f'{ghsa} | {pkg:20} | ERROR: {e}')
```

```bash
python3 get_cve_mappings.py
```

**Results obtained (2026-06-28):**

| GHSA | Package | Mapped CVE |
|------|---------|------------|
| GHSA-c7hr-j4mj-j2w6 | jsonwebtoken | CVE-2015-9235 |
| GHSA-xwcq-pm8m-c4vf | crypto-js | CVE-2023-46233 |
| GHSA-2w6w-674q-4c4q | handlebars | CVE-2026-33937 |
| GHSA-jf85-cpcp-j695 | lodash | CVE-2019-10744 |
| GHSA-cgfm-xwp7-2cvr | sanitize-html | CVE-2022-25887 |
| GHSA-6457-6jrx-69cr | sequelize | CVE-2026-30951 |
| GHSA-qwcr-r2fm-qrc7 | body-parser | CVE-2024-45590 |
| GHSA-677m-j7p3-52f9 | socket.io-parser | CVE-2026-33151 |
| GHSA-72xf-g2v4-qvf3 | tough-cookie | CVE-2023-26136 |
| GHSA-8hfj-j24r-96c4 | moment | CVE-2022-24785 |
| GHSA-9wv6-86v2-598j | path-to-regexp | CVE-2024-45296 |
| GHSA-3h5v-q93c-6h6q | ws | CVE-2024-37890 |

---

## Step 5 — Verify Fix Versions Exist on npm

A scenario is only valid if the fix version Grype recommends actually exists on the npm registry. If it does not, the remediation test cannot run.

The fix versions extracted from Grype's JSON output (`fix.versions[0]`) are exact semantic version strings — for example `4.17.12`, not a constraint like `>=4.17.12`. Grype resolves constraints internally before writing the output field. Each extracted string was verified as a published tag in the npm registry via `https://registry.npmjs.org/{package}/{version}`. HTTP 404 = disqualified immediately.

```python
# save as verify_npm_versions.py
import urllib.request, json

checks = [
    ('jsonwebtoken', '4.2.2'),
    ('crypto-js', '4.2.0'),
    ('handlebars', '4.7.9'),
    ('lodash', '4.17.12'),
    ('sanitize-html', '2.7.1'),
    ('sequelize', '6.37.8'),
    ('body-parser', '1.20.3'),
    ('socket.io-parser', '4.2.6'),
    ('moment', '2.29.2'),
    ('path-to-regexp', '0.1.10'),
    ('ws', '7.5.10'),
    ('tough-cookie', '4.1.3'),
]

for pkg, fix_ver in checks:
    try:
        url = f'https://registry.npmjs.org/{pkg}/{fix_ver}'
        req = urllib.request.urlopen(url, timeout=5)
        data = json.loads(req.read())
        actual = data.get('version', 'NOT FOUND')
        print(f'OK  | {pkg:25} {fix_ver} -> confirmed: {actual}')
    except urllib.error.HTTPError as e:
        print(f'FAIL| {pkg:25} {fix_ver} -> HTTP {e.code}')
    except Exception as e:
        print(f'ERR | {pkg:25} {fix_ver} -> {e}')
```

```bash
python3 verify_npm_versions.py
```

**Results (2026-06-28):** All 12 fix versions confirmed on npm registry.

---

## Step 6 — NVD Verification

Every CVE must exist in the National Vulnerability Database. NOT FOUND = disqualified. No exceptions.

**Note on NVD rate limiting:** The NVD REST API applies strict rate limits. Add a 6-second sleep between requests. If an HTTP 429 error occurs, a 60-second wait should be initiated. 60 seconds and retry.

```python
# save as nvd_verify.py
import urllib.request, json, time

cves = [
    ('jsonwebtoken', 'CVE-2015-9235'),
    ('crypto-js', 'CVE-2023-46233'),
    ('handlebars', 'CVE-2026-33937'),
    ('lodash', 'CVE-2019-10744'),
    ('sanitize-html', 'CVE-2022-25887'),
    ('sequelize', 'CVE-2026-30951'),
    ('body-parser', 'CVE-2024-45590'),
    ('socket.io-parser', 'CVE-2026-33151'),
    ('tough-cookie', 'CVE-2023-26136'),
    ('moment', 'CVE-2022-24785'),
    ('path-to-regexp', 'CVE-2024-45296'),
    ('ws', 'CVE-2024-37890'),
]

for pkg, cve in cves:
    time.sleep(6)
    try:
        url = f'https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve}'
        req = urllib.request.Request(url, headers={'User-Agent': 'thesis-research/1.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        total = data.get('totalResults', 0)
        if total > 0:
            vuln = data['vulnerabilities'][0]['cve']
            cvss = 'N/A'
            metrics = vuln.get('metrics', {})
            for key in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
                if key in metrics:
                    cvss = metrics[key][0]['cvssData']['baseScore']
                    break
            status = vuln.get('vulnStatus', '?')
            print(f'FOUND | {cve:20} | {pkg:20} | CVSS: {cvss} | Status: {status}')
        else:
            print(f'NOT FOUND | {cve:20} | {pkg:20} | DISQUALIFIED')
    except Exception as e:
        print(f'ERROR | {cve:20} | {pkg:20} | {e}')
```

```bash
python3 nvd_verify.py
```

**Results (2026-06-28):**

| CVE | Package | CVSS | NVD Status | Decision |
|-----|---------|------|------------|----------|
| CVE-2015-9235 | jsonwebtoken | 9.8 | Modified | PASS |
| CVE-2023-46233 | crypto-js | 9.1 | Modified | PASS |
| CVE-2026-33937 | handlebars | 9.8 | Analyzed | PASS |
| CVE-2019-10744 | lodash | 9.1 | Modified | PASS |
| CVE-2022-25887 | sanitize-html | 5.3 | Modified | PASS (not selected — CVSS too low) |
| CVE-2026-30951 | sequelize | 7.5 | Analyzed | PASS |
| CVE-2024-45590 | body-parser | 7.5 | Analyzed | PASS |
| CVE-2026-33151 | socket.io-parser | 7.5 | Analyzed | PASS (not selected) |
| CVE-2023-26136 | tough-cookie | 6.5 | Modified | PASS (not selected) |
| CVE-2022-24785 | moment | 7.5 | Modified | PASS |
| CVE-2024-45296 | path-to-regexp | N/A (Not Scheduled) | High via GHSA | PASS — CVSS sourced from GHSA |
| CVE-2024-37890 | ws | N/A (Not Scheduled) | High via GHSA | PASS — CVSS sourced from GHSA |

**Note on CVE-2024-45296 and CVE-2024-37890:** NVD has marked these "Not Scheduled for enrichment." CVSS scores were obtained from GitHub Security Advisory database (GHSA), which is a primary source. Both confirmed as High severity via CVSS v4. This is documented as a protocol decision.

---

## Step 7 — Collect EPSS Scores

EPSS (Exploit Prediction Scoring System) estimates the probability a vulnerability will be exploited in the next 30 days. This is one of the three enrichment signals in the thesis.

**Note on API versioning:** The correct endpoint is `/data/v1/epss` not `/data/1.0/epss`. The older path returns 404.

```python
# save as get_epss.py
import urllib.request, json, time

cves = [
    'CVE-2015-9235',
    'CVE-2023-46233',
    'CVE-2019-10744',
    'CVE-2024-45590',
    'CVE-2026-30951',
    'CVE-2022-24785',
]

for cve in cves:
    time.sleep(2)
    try:
        url = f'https://api.first.org/data/v1/epss?cve={cve}'
        resp = urllib.request.urlopen(url, timeout=10)
        data = json.loads(resp.read())
        if data['data']:
            d = data['data'][0]
            print(f"{d['cve']:20} | EPSS: {float(d['epss']):.4f} | Percentile: {float(d['percentile']):.2f}")
        else:
            print(f'{cve:20} | NOT FOUND in EPSS')
    except Exception as e:
        print(f'{cve:20} | ERROR: {e}')
```

```bash
python3 get_epss.py
```

**Results (2026-06-28):**

| CVE | EPSS Score | Percentile |
|-----|------------|------------|
| CVE-2015-9235 | 0.0866 | 94th |
| CVE-2023-46233 | 0.0063 | 46th |
| CVE-2019-10744 | 0.0501 | 91st |
| CVE-2024-45590 | 0.0082 | 53rd |
| CVE-2026-30951 | 0.0038 | 30th |
| CVE-2022-24785 | 0.0566 | 92nd |

---

## Step 8 — Check CISA KEV Status

The CISA Known Exploited Vulnerabilities catalogue lists CVEs confirmed to be actively exploited in the wild.

```python
# save as check_kev.py
import urllib.request, json

url = 'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'
resp = urllib.request.urlopen(url, timeout=15)
data = json.loads(resp.read())

targets = {
    'CVE-2015-9235', 'CVE-2023-46233', 'CVE-2019-10744',
    'CVE-2024-45590', 'CVE-2026-30951', 'CVE-2022-24785'
}

found = set()
for v in data['vulnerabilities']:
    if v['cveID'] in targets:
        found.add(v['cveID'])
        print(f"KEV=TRUE  | {v['cveID']} | {v['vendorProject']} | {v['vulnerabilityName']}")

for cve in targets - found:
    print(f'KEV=FALSE | {cve}')
```

```bash
python3 check_kev.py
```

**Results (2026-06-28):** All 6 selected CVEs returned KEV=FALSE.

**Limitation:** The thesis proposal lists KEV as one of the three enrichment signals and asks whether combining CVSS, EPSS, and KEV changes prioritisation. With all 6 Juice Shop scenarios returning KEV=FALSE, KEV is a constant in this application's data, not a variable. No empirical claim about KEV's influence on LLM output can be made from Juice Shop data alone. This is consistent across all two applications — see the master pre-registration document for the full limitation statement.

---

## Final Pre-Registered Scenarios — Juice Shop v15.3.0

All data snapshotted on 2026-06-28.

| ID | CVE | Package | Vuln Ver | Fix Ver | CVSS | EPSS | Percentile | KEV | Severity | Jump Type |
|----|-----|---------|----------|---------|------|------|------------|-----|----------|-----------|
| JS-01 | CVE-2015-9235 | jsonwebtoken | 0.1.0 | 4.2.2 | 9.8 | 0.0866 | 94th | No | Critical | Major (0→4) |
| JS-02 | CVE-2023-46233 | crypto-js | 3.3.0 | 4.2.0 | 9.1 | 0.0063 | 46th | No | Critical | Major (3→4) |
| JS-03 | CVE-2019-10744 | lodash | 2.4.2 | 4.17.12 | 9.1 | 0.0501 | 91st | No | Critical | Major (2→4) |
| JS-04 | CVE-2024-45590 | body-parser | 1.20.1 | 1.20.3 | 7.5 | 0.0082 | 53rd | No | High | Patch |
| JS-05 | CVE-2026-30951 | sequelize | 6.34.0 | 6.37.8 | 7.5 | 0.0038 | 30th | No | High | Minor |
| JS-06 | CVE-2022-24785 | moment | 2.0.0 | 2.29.2 | 7.5 | 0.0566 | 92nd | No | High | Minor (deprecated lib) |

### Selection Rationale

**JS-01 jsonwebtoken** — Highest CVSS (9.8) and highest EPSS (94th percentile) in the candidate pool. Authentication bypass via weak algorithm acceptance. The jump from 0.x to 4.2.2 is a major version change — the correct LLM output should flag API breaking changes in an auth library, not just recommend the version bump blindly.

**JS-02 crypto-js** — CVSS 9.1, broken PRNG vulnerability. Major version jump (3→4). Security-critical cryptography library. EPSS at 46th percentile despite Critical CVSS — interesting signal contrast for the CVSS vs EPSS sub-question.

**JS-03 lodash** — CVSS 9.1, prototype pollution (CVE-2019-10744). Well-cited in the academic literature. Jump across two major versions (2→4) is the most aggressive upgrade in the set — high likelihood of dependency conflicts, which is exactly what the thesis is testing.

**JS-04 body-parser** — CVSS 7.5, ReDoS. Patch-level fix (1.20.1→1.20.3). Lowest remediation risk scenario. Expected to succeed under both baseline and LLM conditions — serves as a control scenario to confirm the pipeline works before harder cases.

**JS-05 sequelize** — CVSS 7.5, SQL injection in ORM layer. Minor version bump (6.34→6.37). Database middleware dependency adds functional diversity to the scenario set. Low EPSS (30th percentile) despite meaningful CVSS — another good signal contrast case.

**JS-06 moment** — CVSS 7.5, path traversal. moment.js is officially deprecated by its maintainers as of 2020. The correct LLM output is not just "upgrade to 2.29.2" but a recommendation to migrate to an actively maintained alternative (date-fns or dayjs). Unlike vm2 which was excluded due to package concentration, moment was selected precisely because it has a real upgrade path while still presenting the deprecated library edge case.

### Composition of the 6 Scenarios

- CVSS range: 9.8, 9.1, 9.1, 7.5, 7.5, 7.5 — Critical and High, no Medium
- Severity: 3 Critical, 3 High
- Jump type: 3 major (JS-01, JS-02, JS-03), 1 patch (JS-04), 2 minor (JS-05, JS-06 — moment is also deprecated)
- Package categories: authentication, cryptography, utility, HTTP middleware, ORM, date handling
- KEV: 0/6 — all KEV=FALSE; KEV sub-question scoped to EPSS only per protocol.md
- All fix versions confirmed on npm registry as of 2026-06-28
- All CVEs confirmed in NVD as of 2026-06-28

---

## Files Produced

| File | Description |
|------|-------------|
| `juice-shop_sbom.json` | Syft SPDX-JSON SBOM — **to be attached as evidence** |
| `juice-shop_grype.json` | Grype scan output — **to be attached as evidence** |
| `trim.py` | Original filter script (High/Critical with fix versions) |
| `trim_npm.py` | Extended filter — excludes OS packages, vm2, deduplicates |
| `get_cve_mappings.py` | Maps GHSA IDs to CVE IDs via OSV API |
| `verify_npm_versions.py` | Confirms fix versions exist on npm registry |
| `nvd_verify.py` | Verifies each CVE exists in NVD with CVSS score |
| `get_epss.py` | Retrieves EPSS scores from FIRST API |
| `check_kev.py` | Checks CVEs against CISA KEV catalogue |

---

## Next Steps

Repeat this entire process for:

1. ** v5.76.0** — target 6 scenarios (npm ecosystem)
2. **Apache Airflow v2.9.2** — target 6 scenarios (PyPI ecosystem)

The same selection criteria apply: High/Critical only, fix version confirmed in registry, CVE confirmed in NVD, no abandoned packages without explicit protocol handling, no duplicate packages within the same application's scenario set.
