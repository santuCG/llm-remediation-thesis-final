# Scenario Definitions — Which File Is Authoritative

This directory contains three representations of the 18 pre-registered scenarios. They exist for different purposes; this note states which one is authoritative for what, per the Run B publication audit (`docs/audit/`).

- **`final_18_scenarios.json`** — the authoritative scenario list used by the live pipeline. `.github/workflows/grype-baseline.yml` looks up a scenario from this file by CVE ID at dispatch time. Its contents were verified during this audit to match `preregistration/PRE_REGISTRATION_AMENDMENT.md`'s locked scenario tables exactly.
- **`AF-01.json` … `JS-09.json`** — one file per scenario, carrying pre-registration metadata (registration timestamp, selection rationale) plus an appended `EMPIRICAL EVIDENCE` plaintext trailer. **Known issue:** at least `AF-01.json` does not parse as valid JSON due to that appended trailer (confirmed during the Run A publication audit; the other 17 were not individually re-verified). Treat these as historical/registration records, not as a machine-readable data source.
- **`pre_registered/scenarios.json`** — an earlier-format snapshot of the scenario set, superseded by `final_18_scenarios.json` for pipeline purposes.

If you need the scenario set programmatically, use `final_18_scenarios.json`. If you need the original pre-registration record for a specific scenario, use `preregistration/PRE_REGISTRATION_AMENDMENT.md`, not the per-scenario files in this directory.
