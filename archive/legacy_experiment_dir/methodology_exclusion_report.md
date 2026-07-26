# Methodology Exclusion Report

## Overview
This document records the methodological exclusions and constraints discovered during the deterministic baseline and pilot LLM remediation phases. These constraints govern the final experimental dataset.

## Exclusions Applied

### 1. OS-Level Packages Disqualified
OS-level packages have been formally disqualified from the experimental dataset. The experimental parameters strictly require isolated application-level dependency resolution using native package managers (npm, pip). Attempting to remediate OS-level dependencies introduces system-wide state changes that violate the reproducibility requirement of the CI validation environment. 

### 2. Ghost Application Disqualified
The Ghost application scenarios were fully disqualified due to inherent instability in its dependency lockfiles and an undocumented constraint model that prevents deterministic, isolated version bumping. Only Juice Shop (npm) and Airflow (pypi) have been retained, yielding a final dataset of 18 verifiable scenarios.

### 3. Local Execution vs. CI Parity
During the pilot LLM generation phase, all validation gates (Gate 2: Build, Gate 3: Test, Gate 4: Rescan) were strictly enforced inside GitHub Actions CI. Local execution is considered a violation of the methodological baseline because it relies on the local node/python binaries rather than the public, isolated GitHub runners that were used to establish the baseline failure states. The `run_pilot_orchestration.py` script automatically dispatches GitHub Actions workflows to ensure strict CI parity.

### 4. JSON Generation Truncation Limitations
During the pilot runs with the `gemini-3.5-flash` endpoint, severe output truncation issues were encountered specifically when requesting strict JSON outputs. This resulted in `PARSE_ERROR` outcomes, logging `HALLUCINATED_VERSION` for these pilot scenarios. This technical limitation in the LLM provider's API backend is formally logged as a confounding variable that contributes to the "Hallucinated / Parse Error" metric in the remediation generation phase.
