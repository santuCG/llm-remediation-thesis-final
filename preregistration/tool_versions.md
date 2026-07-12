# Tool Versions
**Date of environment snapshot:** 2026-06-28

| Tool | Version | Notes |
|------|---------|-------|
| Syft | v1.44.0 | SBOM generation. Same version across all three applications. |
| Grype | v0.112.0 | Vulnerability scanning. Same version across all three applications. |
| Python | 3.x | Filtering and API verification scripts. |
| Docker | 29.5.3 | Required for Airflow Docker image scan only. |
| Git | 2.x | Version control. |

## Grype Vulnerability Database

Grype downloads and uses its own vulnerability database at scan time. The database version is embedded in the Grype scan output JSON under the `descriptor.db` field. The scan outputs are preserved in `applications/evidence/` for reference.

## Tool References

- Syft: https://github.com/anchore/syft
- Grype: https://github.com/anchore/grype
- SPDX specification: https://spdx.dev/
