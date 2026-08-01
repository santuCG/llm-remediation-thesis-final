# PHASE 2 — METHODOLOGY VERIFICATION

Every stage below was verified by reading the actual current script/workflow content on `main` (not assumed from documentation). Classification: **FACT** = directly read from code; **OBSERVATION** = a pattern noticed while reading; **INFERENCE** = my own judgment, marked as such.

---

## Syft

**Purpose:** Generate a Software Bill of Materials (SBOM) — a structured inventory of every package and version present in the application's dependency tree — as the deterministic input to vulnerability scanning.
**Input:** The application source directory (`dir:.` inside `applications/juice-shop/` or `applications/airflow/`), after dependencies have just been installed (`node_modules` or Python site-packages present on disk).
**Output:** `baseline-sbom.json` (SPDX-JSON format), later `post-sbom.json` for the rescan.
**Command (from `generic-remediation.yml:74`):**
```bash
./bin/syft dir:. --exclude "**/bin" --exclude "**/build" --exclude "**/.eggs" \
  --exclude "**/*.egg-info" --exclude "**/dist" --exclude "**/.pytest_cache" \
  -o spdx-json > ../../baseline-sbom.json
```
**Plain English:** "Scan every file in the current directory tree, skip build artifacts and caches so they don't get misidentified as packages, and write out a standard SPDX-format inventory of every package and version found."
**Why required:** Grype (the next stage) scans an SBOM, not the filesystem directly — Syft is the bridge between "what's actually installed" and "what can be checked against a vulnerability database."
**Repository location:** `tools/syft_bin/syft.exe` (Windows binary, vendored for local use); the actual CI workflow downloads a fresh Linux binary at run time (`curl ... syft_1.44.0_linux_amd64.tar.gz`) rather than using the vendored one — **OBSERVATION**: this means the vendored `tools/syft_bin/` binary is not actually what CI runs; it exists for local/manual use only.
**Version:** 1.44.0, consistently pinned by exact download URL in both `generic-remediation.yml:72` and `grype-baseline.yml`. **FACT**, confirmed identical in both files.

---

## Grype

**Purpose:** Deterministically scan the SBOM against a vulnerability database (Anchore's) to identify known CVEs/GHSAs affecting the installed packages.
**Input:** `baseline-sbom.json` (or `post-sbom.json` for the rescan).
**Output:** `grype.json` (renamed to `baseline-grype.json` at evidence-gathering time) / `rescan.json`.
**Command:**
```bash
GRYPE_DB_VALIDATE_AGE=false ./bin/grype sbom:../../baseline-sbom.json -o json > ../../grype.json
```
**Plain English:** "Take the SBOM, check every package/version in it against the vulnerability database, and write the list of matches as JSON. `GRYPE_DB_VALIDATE_AGE=false` disables Grype's normal refusal to run with a stale local DB — meaning if the runner's cached DB is old, Grype will use it anyway rather than erroring out."
**Why required:** This is the actual, deterministic "what's vulnerable" measurement the whole thesis is built on — the LLM never decides what's vulnerable, only how to fix what Grype found.
**Repository location:** `tools/grype_bin/grype.exe` (same vendored-vs-CI-fresh-download distinction as Syft).
**Version:** 0.112.0, consistently pinned. **FACT.**
**Documented but not implemented — OBSERVATION, Phase 2 finding:** `docs/06-reproducibility.md:47` documents a **"Cold Start Database Clause"** requiring researchers to import a specific Grype DB snapshot from **2026-07-08** via `grype db import` *before* scanning, "to ensure exact reproducibility of the scanner findings... with auto-updates disabled." No such DB snapshot file exists anywhere in this repository (checked: no `.tar.gz`/`.db` file matching this description under `applications/evidence/`, `tools/`, or elsewhere), and neither workflow YAML runs `grype db import` or disables auto-update — both rely on whatever DB the runner happens to have cached, only guarded by `GRYPE_DB_VALIDATE_AGE=false` (which suppresses an error, it does not pin the DB version). **This is a direct, checkable gap between documented methodology and actual implementation** — the one thing the reproducibility doc calls essential for "exact reproducibility of scanner findings" is not actually implemented anywhere.

---

## Gemini Prompt (LLM Reasoning)

**Purpose:** Given the vulnerability's context, ask the LLM to recommend a remediation strategy and a concrete manifest patch.
**Input:** `candidate` (selected CVE/package/version data), `context` (dependency-graph snippet), `ecosystem`, and on retry, `failure_logs`.
**Output:** `llm-request.json` (the exact payload sent), `llm-response.json` (the parsed structured JSON reply), `llm-response-full.json` (the raw API response, written locally but **not** part of the 13-file evidence set gathered by the "Gather Evidence" step — **OBSERVATION**: this file is generated but discarded, never uploaded as an artifact).
**Command:** not a shell command — an HTTPS POST to `https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent`, tried in order down a fallback list (`scripts/remediation/llm_reasoner.py:116`, currently `["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]` as of today's commit `72a1a848` — noted factually, not further assessed per your instruction).
**Plain English:** "Send a fixed system prompt plus a per-scenario user prompt (vulnerability details + dependency context + JSON schema) to Gemini with temperature 0 and a fixed seed, asking for a structured recommendation; if the first model in the list fails, try the next one."
**Why required:** This is the actual object of study — the "decision-support" reasoning layer being evaluated.
**Repository location:** `scripts/remediation/llm_reasoner.py`.
**Config, per `AGENTS.md` rule 4 ("Unbiased Reasoning... do not suggest a specific alternative package"):** the system prompt (`llm_reasoner.py:14-17`) reads "Evaluate all technically feasible remediation strategies... Recommend the safest strategy that preserves compatibility and explain why alternative strategies were rejected." **FACT: this matches the documented rule** — no specific alternative package is named in the system prompt.

---

## Candidate Ranking

**Purpose:** From all vulnerabilities Grype found, filter down to automatically-remediable ones and rank them to select the single scenario target.
**Input:** `grype.json`'s `matches` array, `TARGET_CVE` env var (when overriding for a specific pre-registered scenario).
**Output:** `candidate-ranking.json` (the full filtered/sorted list), `selected-candidate.json` (the top pick).
**Command:** not a shell command — `scripts/remediation/prioritize.py:prioritize_vulnerabilities()`.
**Plain English:** "Keep only vulnerabilities that are High/Critical severity, have a fixed version available, and match the current ecosystem (npm or python). Sort what's left by KEV status first, then EPSS score, then CVSS score, all descending. If a specific `TARGET_CVE` was requested, override the automatic pick with that one instead (used to force a specific pre-registered scenario)."
**Verification against `AGENTS.md` rule 2 ("Severity >= High AND ... Fixed version available AND Supported ecosystem...")**: **FACT, confirmed exactly** — `prioritize.py:101-114` implements precisely this filter (severity check, `fix.get('state') == 'fixed'` check, ecosystem-type check). One documented sub-clause not separately implemented as its own check: "No manual source code modification required" and "Not Ignored" (from `AGENTS.md` rule 2) have no corresponding code-level check in `prioritize.py` — **OBSERVATION**: these two conditions appear to be enforced only implicitly (a manual-fix-required case would presumably surface later as an LLM `manual_review` strategy or a build failure, not filtered out at this stage).
**Verification against `AGENTS.md` rule 3 ("KEV -> EPSS -> CVSS descending")**: **FACT, confirmed exactly** — `prioritize.py:156`: `candidates.sort(key=lambda x: (x['kev'], x['epss'], x['cvss']), reverse=True)`.

---

## Validator

**Purpose:** Deterministically confirm whether the target CVE is actually gone after remediation, independent of the LLM's own claim.
**Input:** `rescan.json`, the target CVE ID, `metrics.json`.
**Output:** Updates `metrics.json`'s `rescan_success`, `dependency_verified`, `validation_stage_reached`, or `failure_stage` fields; exits 1 on failure (which fails the CI step and triggers the retry path).
**Command:** `python scripts/remediation/validator.py <rescan.json> <cve_id> <metrics.json>`.
**Plain English:** "Open the post-remediation scan, check whether the target CVE (or a related ID) still appears anywhere in it. If it's gone, mark the fix as verified. If it's still there, mark it as failed and exit with an error code."
**Why required:** This is the deterministic ground truth the whole "hypothesis vs. result" distinction (`docs/06-reproducibility.md`'s central principle) depends on — the LLM's recommendation only becomes a "result" after this check passes.
**Repository location:** `scripts/remediation/validator.py`. Its own code comment (lines 29-34) explicitly documents that it deliberately does NOT set `build_success` itself, to avoid masking a genuine build failure — **FACT**, and this is good, self-aware design.

---

## Retry

**Purpose:** Give the LLM one more attempt, informed by what went wrong, if the first attempt fails.
**Input:** The prior `selected-candidate.json`, `metrics.json` (to recover the failure stage), and the last 2000 characters of the relevant failure log.
**Output:** A refreshed `llm-request.json`/`llm-response.json`, updated `metrics.json` (`retry_count`, `llm_iteration`, `strategy`, `remediation_type`, `failure_stage`).
**Command:** `python scripts/remediation/retry_remediation.py <ecosystem> <app_dir> <failure_stage>`, invoked by `generic-remediation.yml`'s "Retry Remediation Strategy" step, itself gated by `if: failure()`.
**Plain English:** "If any earlier step failed, restore the manifest file to its true original state (as of today's fix, copied from the very first `package-before.json` snapshot), read the last attempt's failure log, ask the LLM again with that context, apply whatever it recommends this time, rebuild, rescan, and validate again — with no further retries after this."
**Verification against `AGENTS.md` rule 5 ("Strict Retries: Maximum ONE retry")**: **FACT, confirmed** — the workflow has exactly one retry step; there is no loop or second retry path. All 18 recorded scenarios show `retry_count` of either 0 or 1, never higher — consistent with this rule (verified against `metrics.json` across all 18 in the earlier forensic pass).
**Today's fix (commits `1d70e9b9` → `812c1010`), verified as functionally correct:** the retry step now restores `package.json`/`requirements.txt` from `package-before.json` — the file `manifest_editor.py`'s *first* invocation wrote — before calling `apply_remediation()` a second time. **FACT.** This directly addresses the defect proven in the prior audit turn (retry previously operated on an already-modified manifest, producing an unchanged "before/after" pair for 4 of 9 npm scenarios). This fix is prospective only — the 4 already-recorded scenarios (JS-01, JS-02, JS-06, JS-07) are unaffected by it unless rerun.

---

## SBOM Generation / Dependency Installation / Lock Regeneration

Already covered under Syft (SBOM) above. Dependency installation and lock regeneration:

**"Install Baseline Dependencies" (generic-remediation.yml:55-66):** `npm ci` (npm) / `pip install -r requirements.txt` (python) — **Plain English:** "Install exactly what the lockfile specifies, no resolution, no drift." This is the step that establishes the "known vulnerable baseline" state.
**"Fallback Lockfile Regeneration" (line 100-115), gated by `if: failure()`:** deletes `package-lock.json`/`node_modules` (npm) or `requirements.txt` (python, replaced via `pip install -e .`) and reinstalls from scratch. **Plain English:** "If the native resolution attempt failed, throw away the lockfile entirely and let the package manager regenerate it fresh — and record in `metrics.json` that this fallback happened (`lockfile_regenerated: true`)." **Verification against `AGENTS.md` rule 1** ("Phase 2 (Fallback) deletes the lockfile/node_modules and regenerates it purely via package manager, documenting the fallback in evidence"): **FACT, confirmed exactly** — this is a precise implementation of the documented rule.

---

## Build / Tests / Rescan

**"Apply Fix & Verify" (line 83-98):** `npm install` / `pip install --no-deps -r requirements.txt` — applies the LLM's patched manifest and lets the package manager resolve it. `set -o pipefail` (added in the prior remediation pass) ensures a real resolution failure is no longer silently masked by `tee`.
**"Validate Remediation & Rescan" (line 117-162):** runs `build:frontend`/`build:server`/`build` npm scripts or nothing extra for python; runs `npm test`/`pytest tests/core` and records `test_success` from the actual exit code (`${PIPESTATUS[0]}`, correctly capturing the piped command's real exit code — **FACT, this specific field is captured correctly, unlike the `pipefail`-dependent ones**); regenerates the SBOM (`post-sbom.json`) and rescans (`rescan.json`); finally invokes the validator.
**Plain English:** "Try to build the application and run its test suite (recording pass/fail honestly either way), then regenerate the SBOM from the now-patched dependency tree and rescan it to see if the target vulnerability is really gone."

---

## Artifact Publication

**"Gather Evidence" (line 208-225):** moves the 12 named files into an `evidence/` folder, then runs `generate_manifest.py`, which adds `experiment_manifest.json` as the 13th artifact (containing provenance, tool versions, LLM config, and a SHA256 hash of every other file).
**"Upload Remediation Evidence" (line 227-232):** `actions/upload-artifact@v4`, uploading the `evidence/` folder as a GitHub Actions artifact named `remediation-evidence`.
**Plain English:** "Collect every generated file into one folder, stamp it with a signed manifest describing exactly how it was produced, and attach the whole folder to the workflow run as a downloadable artifact."
**OBSERVATION, not previously documented in this form:** `llm-response-full.json` is generated (`llm_reasoner.py`) but is not in the `mv` list here — it is silently left behind and lost when the runner is torn down. The raw, complete API response (which would include Google's own `modelVersion` field — the most authoritative source for "which model actually answered") is therefore never preserved as evidence, for any of the 18 scenarios.

---

## Summary table (Purpose / Input / Output / Command / Evidence) — quick reference

| Stage | Purpose | Primary command | Artifact |
|---|---|---|---|
| Baseline install | Establish known-vulnerable state | `npm ci` / `pip install -r requirements.txt` | (no direct artifact; feeds SBOM) |
| SBOM (baseline) | Inventory installed packages | `syft dir:. -o spdx-json` | `baseline-sbom.json` |
| Scan (baseline) | Detect known vulnerabilities | `grype sbom:... -o json` | `baseline-grype.json` |
| Discovery | Parse scan matches | (Python, in-process) | — |
| Candidate ranking | Filter + prioritize | (Python, in-process) | `candidate-ranking.json`, `selected-candidate.json` |
| Context building | Gather dependency-graph context | `npm ls/explain`, `pip show/freeze` | (embedded in `llm-request.json`) |
| LLM reasoning | Generate remediation hypothesis | HTTPS POST to Gemini | `llm-request.json`, `llm-response.json` |
| Apply fix | Patch manifest, install | `npm install` / `pip install --no-deps` | `package-before.json`, `package-after.json`, `build.log` |
| Build/Test | Confirm app still works | `npm run build*`, `npm test` / `pytest` | `build.log`, `test.log` |
| Rescan | Regenerate SBOM + scan post-fix | `syft` + `grype` again | `post-sbom.json` → `rescan.json` |
| Validate | Deterministic pass/fail | `validator.py` | updates `metrics.json` |
| Retry (max 1) | One refined attempt on failure | `retry_remediation.py` | overwrites the same evidence files |
| Publish | Package + hash everything | `generate_manifest.py` + `upload-artifact` | `experiment_manifest.json`, GH Actions artifact |
