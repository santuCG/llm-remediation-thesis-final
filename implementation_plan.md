# Phase A: Core Engine Overhaul & Profile Refactoring

We will completely refactor the repository pipelines to be fully generic, purely profile-driven, mathematically verifiable, and reproducible without external decay. We will implement these changes using a single test scenario (JS-08) to validate the new architecture before rolling it out to all 36 scenarios.

## Proposed Changes

### Scripts & Utilities
#### [NEW] `scripts/profiles/load_profile.py`
A Python script to parse a given profile YAML and inject its values (scenario ID, target CVE, tool versions, application dir, lockfile path, validation steps) safely into `$GITHUB_ENV`. This replaces the inline Python commands.

#### [NEW] `scripts/evidence/build_environment.py`
A Python script to securely dump only whitelisted environment variables (like `RUNNER_OS`, tool versions, pipeline state) into `provenance/environment.txt`, avoiding secret leakage.

#### [NEW] `scripts/remediation/golden_validation.py`
A validator that compares the actual LLM choice and strategy (`metrics.json`) against the expected baseline defined in the profile. It will output `validation-report.json` with a PASS/FAIL status.

### Pipeline Templates
#### [MODIFY] `.github/workflows/baseline-npm-remediation.yml`
#### [MODIFY] `.github/workflows/baseline-python-remediation.yml`
#### [MODIFY] `.github/workflows/npm-remediation.yml`
#### [MODIFY] `.github/workflows/python-remediation.yml`
- Replace hardcoded `package-lock.json` restoration with generic profile-driven logic.
- Replace manual `syft` and `grype` downloads with `actions/cache` backed by specific versions.
- Replace `python -c` profile loading with `load_profile.py`.
- Replace hardcoded `jq` build/test scripts with a generic loop over `profile.validation.build` and `profile.validation.test`.
- Upgrade provenance bundling to include `package.json`, lockfiles, and run `build_environment.py`.
- Update artifact names to `${{ env.SCENARIO_ID }}-baseline-${{ github.run_id }}` (and `-llm-`).

### Artifact Verification
#### [NEW] `.github/workflows/verify-run.yml`
A standalone GitHub Actions workflow designed to take a Run ID, download its artifact ZIP, recalculate its SHA-256, and mathematically compare the results against the original dataset's expected hashes. This provides independent Golden Validation of any future re-runs.

### Profiles & Launchers (Phase B Implementation)
#### [MODIFY] `profiles/JS-08.yaml`
Update the JS-08 profile to include the new generic schemas:
```yaml
baseline:
  restore_lockfile: true
  lockfile: "evidence/juice_shop_package-lock.json"
validation:
  build:
    - npm run build:frontend
    - npm run build:server
    - npm run build
  test:
    - npm test
expected:
  candidate: "body-parser"
  strategy: "direct_upgrade"
```

#### [MODIFY] `.github/workflows/baseline-js-08.yml`
#### [MODIFY] `.github/workflows/llm-js-08.yml`
Update the launchers to pass `scenario: JS-08` instead of the full path.

## Verification Plan
1. Commit all architectural changes.
2. Trigger `baseline-js-08.yml` and `llm-js-08.yml`.
3. Verify they dynamically load their profile, cache tools, run the generic build/validate steps, output proper golden validation, and package secure evidence.
4. Once verified, roll out the changes to the remaining 35 scenarios (Phase D).
