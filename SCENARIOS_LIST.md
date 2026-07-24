# Pre-Registered Scenarios List

This file contains the 18 pre-registered vulnerability scenarios used for testing the LLM-Assisted Dependency Remediation Pipeline in this thesis. These scenarios are documented extensively in `preregistration/PRE_REGISTRATION_AMENDMENT.md`.

## Node.js / NPM (OWASP Juice Shop)

| ID | CVE | Package | CVSS | Upgrade Type |
|---|---|---|---|---|
| JS-01 | CVE-2023-32314 | vm2 | 9.8 | Patch |
| JS-02 | CVE-2026-33937 | handlebars | 9.8 | Patch |
| JS-03 | CVE-2025-7783 | form-data | 9.4 | Minor |
| JS-04 | CVE-2023-46233 | crypto-js | 9.1 | Major |
| JS-05 | CVE-2015-9235 | jsonwebtoken | 9.0 | Major |
| JS-06 | CVE-2026-33228 | flatted | 8.9 | Minor |
| JS-07 | CVE-2024-37890 | ws | 8.7 | Minor |
| JS-08 | CVE-2024-45590 | body-parser | 8.7 | Patch |
| JS-09 | CVE-2026-3520 | multer | 8.7 | Major |

## Python / PyPI (Apache Airflow)

| ID | CVE | Package | CVSS | Upgrade Type |
|---|---|---|---|---|
| AF-01 | CVE-2026-8838 | redshift-connector | 9.8 | Patch |
| AF-02 | CVE-2025-43859 | h11 | 9.1 | Minor |
| AF-03 | CVE-2023-50782 | cryptography | 8.7 | Major |
| AF-04 | CVE-2026-44307 | mako | 8.7 | Patch |
| AF-05 | CVE-2026-0994 | protobuf | 8.2 | Major |
| AF-06 | CVE-2024-56326 | jinja2 | 7.8 | Patch |
| AF-07 | CVE-2024-21272 | mysql-connector-python | 7.7 | Major |
| AF-08 | CVE-2026-2473 | google-cloud-aiplatform | 7.7 | Minor |
| AF-09 | CVE-2024-34069 | werkzeug | 7.5 | Major |
