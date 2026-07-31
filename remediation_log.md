# REMEDIATION LOG

Scope: `findings_classification.md` Minimum Fix Set, items 1-12 (Documentation only / Pipeline code fix / Repository cleanup only) plus the Security item (token removal, item 13, handled per its own explicit instructions — no history rewrite, no functionality removed, secret never reprinted).
Explicitly out of scope for this pass: items 14-16 (reruns), 17 (evidence import), 18 (M3, open question), and any finding/issue not already named in the approved list — including Minor findings from the original audit that were never assigned a Minimum Fix Set item number (e.g. the `progress-reports/` path reference), which are intentionally left untouched here.
Immutable zone respected throughout: nothing under `results/execution_evidence/**`, `archive/legacy_*`, or any historical log/manifest/SBOM/metrics file was opened for writing.

This log is written incrementally, one entry per file, as each change completes.

---

File: `archive/check_status_20260726_171013.py`
Reason: Hardcoded GitHub Personal Access Token in plaintext.
Audit Finding: C5.
Summary of Changes: Added `import os`; replaced the literal token string in the `Authorization` header with `os.environ["GITHUB_TOKEN"]`. No other logic changed; script still requires a token to function, now supplied via environment variable instead of being embedded in source.
Risk: Low. The script will now raise `KeyError` if `GITHUB_TOKEN` is unset, which is correct fail-fast behavior for a manual debug script — no silent fallback was introduced.
Evidence Preserved? YES — this file is a utility script, not an experimental-evidence artifact; nothing under `results/execution_evidence/**` was touched.

File: `archive/compare_metrics_20260726_171013.py`
Reason: Hardcoded GitHub Personal Access Token in plaintext.
Audit Finding: C5.
Summary of Changes: Added `os` to the existing import line; replaced `TOKEN = 'ghp_...'` with `TOKEN = os.environ["GITHUB_TOKEN"]`. (Note: the script already contains a redundant `import os` further down inside the loop — left as-is; removing it is outside the scope of this fix.)
Risk: Low, same rationale as above.
Evidence Preserved? YES.

File: `archive/fetch_logs_20260726_171013.py`
Reason: Hardcoded GitHub Personal Access Token in plaintext.
Audit Finding: C5.
Summary of Changes: Added `os` to the import line; replaced the literal token assignment with `os.environ["GITHUB_TOKEN"]`.
Risk: Low.
Evidence Preserved? YES.

File: `archive/poll_pipeline_20260726_171013.py`
Reason: Hardcoded GitHub Personal Access Token in plaintext.
Audit Finding: C5.
Summary of Changes: Replaced `TOKEN = "ghp_..."` with `TOKEN = os.environ["GITHUB_TOKEN"]` (this file already imported `os`).
Risk: Low.
Evidence Preserved? YES.

File: `archive/scratch_fetch_runs_20260726_171013.py`
Reason: Hardcoded GitHub Personal Access Token in plaintext.
Audit Finding: C5.
Summary of Changes: Added `os` to the import line; replaced the literal token assignment with `os.environ["GITHUB_TOKEN"]`.
Risk: Low.
Evidence Preserved? YES.

File: `archive/temp_files/get_artifacts.py`
Reason: Hardcoded GitHub Personal Access Token in plaintext.
Audit Finding: C5.
Summary of Changes: Replaced `token = 'ghp_...'` with `token = os.environ["GITHUB_TOKEN"]` (this file already imported `os`).
Risk: Low.
Evidence Preserved? YES.

**Verification:** re-grepping for the leaked token pattern (referenced by file/line in C5 — not reprinted here) confirms the string no longer appears in any of the 6 named files.

**⚠ New discovery during this fix, flagged not fixed (out of the explicitly named scope):** the same token string was also found, while verifying the fix, in 4 additional files: `archive/temp_scripts/check_gh.py:7`, `fetch_logs.py:6`, `fetch_logs_fixed.py:6`, `fetch_logs_to_file.py:6`. These are **untracked by git** (`git ls-files archive/temp_scripts/` returns empty — the folder is listed in `.gitignore` and these files have never been committed). This is a materially different risk than the 6 named C5 files: it is a local-disk-only exposure, not a git-history/public-remote exposure. Because my authorization for this pass named exactly 6 specific files, I did not edit these 4 without confirmation — listed under Requires Manual Decision in the final report.

---

File: `.github/workflows/generic-remediation.yml`
Reason: `npm install 2>&1 | tee ../../build.log || (echo "NPM Install Failed" && exit 1)` (and the equivalent `pip install` line) cannot detect a real failure, because without `set -o pipefail` the pipeline's reported exit status is `tee`'s (near-always 0), not the install command's — so the `||` fallback that was clearly intended to catch a failure never fires.
Audit Finding: C4 (root cause), M2 (contributing mechanism).
Summary of Changes: Added `set -o pipefail` as the first line of the **"Apply Fix & Verify"** step's `run:` block only (the one step in this file containing this exact existing-but-broken `| tee ... || (echo ... && exit 1)` pattern).
Scoping decision, stated explicitly: I considered adding `set -o pipefail` more broadly (to "Fallback Lockfile Regeneration," "Retry Remediation Strategy," and other `| tee` usages in this file), then reverted those additions. Those other steps contain `| tee` with **no pre-existing `||` failure check at all** (or, in one case, an explicit `|| true` that intentionally swallows failure) — adding pipefail there would not be restoring a broken check, it would be introducing new abort-on-failure behavior in steps that currently always continue regardless of the install outcome. That is a larger behavioral change than "the identified bug" and was excluded per the instruction not to change behavior beyond it.
Risk: Low for the change made. The only behavior difference is that a genuinely failing `npm install`/`pip install` at this exact step will now correctly halt the step and be recorded as a failure, which is what the pre-existing `|| (echo "... Failed" && exit 1)` code already reads as if it does.
Evidence Preserved? YES — this is a workflow definition file, not an evidence artifact; no historical run is affected retroactively (workflow files don't rewrite past runs).

File: `.github/workflows/grype-baseline.yml`
Reason: Same missing-`pipefail` defect, present in two steps in this file that both contain existing-but-broken `|| (echo "... Failed" && exit 1)` checks.
Audit Finding: C1 (contributing mechanism — this is the workflow sampled via the GitHub API in the audit), C4-adjacent.
Summary of Changes: Added `set -o pipefail` as the first line of **"Phase 3 & 4 - Apply Grype Recommendation (Logged)"** (`npm install`/`pip install` with the same broken `||` pattern as above) and **"Phase 5 - Build / Tests / Rescan"** (this step, unlike its counterpart in `generic-remediation.yml`, already has explicit `|| (echo "Build Frontend/Server/... Failed" && exit 1)` checks on the `npm run build:*` lines — so this is squarely "fixing an existing but non-functional check," not adding a new one).
Risk: Low, same rationale — a step whose own code already declares "fail if this build step fails" will now actually do so.
Evidence Preserved? YES.

---

File: `scripts/remediation/generate_manifest.py`
Reason: The `llm.model` field was a hardcoded string literal, structurally incapable of reflecting a fallback-model event, independent of what the LLM call actually returned.
Audit Finding: C3.
Summary of Changes: Changed `"model": "gemini-2.5-flash"` to `"model": os.environ.get("LLM_MODEL_USED", "gemini-2.5-flash")`, with a comment explaining why.
Risk: None to current behavior. No code currently sets `LLM_MODEL_USED`, so every run continues to produce exactly the same manifest value as before ("gemini-2.5-flash") until a future change wires up the source. This is a deliberately conservative, zero-behavior-change-today fix scoped to the one named file.
**Explicitly flagged as incomplete on its own:** this fix alone does not correct the mechanism — `scripts/remediation/llm_reasoner.py` would need to be changed to set `LLM_MODEL_USED` (or write an equivalent artifact) after a successful call, and `.github/workflows/generic-remediation.yml`'s "Gather Evidence" step would need no change since env vars propagate automatically within the same job. Neither `llm_reasoner.py` nor the workflow's evidence-gathering step was named in this pass's authorized fix list, so that wiring was **not done** here — listed under Deferred in the final report.
Evidence Preserved? YES.

File: `scripts/remediation/retry_remediation.py`
Reason: `failure_stage` was set to the prior attempt's value unconditionally, never reset on a successful retry, producing the `build_success: true` / `failure_stage: "build"` contradiction seen in 7 of 9 JS scenarios.
Audit Finding: M2.
Summary of Changes: Changed `metrics['failure_stage'] = failure_stage` to `metrics['failure_stage'] = failure_stage if not llm_response_valid else 'none'`, with a comment explaining the reasoning and noting that downstream steps still independently re-set this field if the post-retry rebuild fails again.
Risk: Low. Behavior only changes for the specific case this was meant to fix (a valid retry response); if a retry never gets a usable response, the exact prior behavior is unchanged.
Evidence Preserved? YES.

File: `scripts/remediation/manifest_editor.py`
Reason: Scoped/transitive override paths like `"request > form-data"` were written as a single flat JSON key containing `>` and spaces, which is what caused JS-03's real `npm error EINVALIDTAGNAME`.
Audit Finding: C4 (contributing bug), M6.
Summary of Changes: Added a small helper, `_apply_override()`, that nests a `>`-delimited path into the correct nested object (`{"request": {"form-data": constraint}}`) and falls back to the previous flat-key behavior for a plain package name with no `>` in it. Replaced both call sites that previously wrote `pkg['overrides'][target_pkg] = constraint` directly (the primary `add_override`/`transitive_override` branch and the "unknown operation" fallback branch) with calls to this helper. The `python`/pip branch of this file was not touched — the bug and the fix are npm-specific.
Risk: Low. For every existing scenario where `target_pkg` has no `>` character (all except JS-03's specific case), the helper produces byte-identical output to before.
Evidence Preserved? YES.

File: `scripts/run_deterministic_baseline.py`
Reason: Hardcoded I/O paths (`experiment/`, `documentation/`) do not exist anywhere in the current repository layout, so the script cannot run at all.
Audit Finding: C6.
Summary of Changes: Changed the input path from `experiment/final_18_scenarios.json` to `results/scenarios/final_18_scenarios.json` (verified this file exists and is a plain JSON list matching the structure the script's `for s in scenarios:` loop expects). Changed the two output paths from `experiment/deterministic_baseline_results.json` and `documentation/deterministic_baseline_report.md` to `results/deterministic_baseline_results.json` and `docs/deterministic_baseline_report.md` respectively (both target directories already exist). No logic, algorithm, or output format was changed — only the three path strings.
Risk: Low for the edit itself. **This script was not executed** — fixing its paths makes it runnable again but running it would constitute rerunning an experiment, which is explicitly out of scope for this pass. Listed under Requires Manual Decision / Requires Rerun in the final report, since actually producing this evidence is a separate decision from making the script capable of producing it.
Evidence Preserved? YES — no experiment was run, no evidence file was created or altered by this change.

---

File: `.gitattributes` (new file)
Reason: No `.gitattributes` existed, so a checkout with `core.autocrlf=true` (git's own Windows-recommended default) converts committed LF line endings to CRLF in the working tree, breaking every SHA256 hash declared in every `experiment_manifest.json` for reasons unrelated to content integrity.
Audit Finding: M4.
Summary of Changes: Added a new `.gitattributes` file pinning `results/execution_evidence/**` to `text eol=lf`.
Risk: Low. This does not retroactively fix hashes for content already checked out with the wrong line endings on someone's machine before this file existed (a fresh clone after this change will be consistent); it does not alter any evidence file's content, only how line endings are normalized on future checkouts.
Evidence Preserved? YES — no file under `results/execution_evidence/` was opened or modified; only a new, previously-absent git-configuration file was added.

---

File: `README.md`
Reason: Three separate documentation corrections, all evidence-justified.
Audit Finding: C7 (scenario count), M1 (undisclosed retry loop), C3 (JS-09 deviations).
Summary of Changes:
1. Line 138 area: corrected "In all 17 executed scenarios... All 17 scenarios achieved rescan_success=true" to "18" in both places — re-verified programmatically across all 18 `metrics.json` files before editing (all 18 show `test_success=false`, all 18 show `rescan_success=true`) rather than trusting the prior audit's number without re-checking.
2. Added a new "Note on the retry mechanism" paragraph in the "How Validation Works" section, disclosing that a real, code-implemented retry/re-prompt loop exists and that 7 of 9 JS scenarios required it.
3. Added a new "Note on JS-09" paragraph in the same section, disclosing the hidden-fixed-versions prompt deviation, the internal `"Supplementary Experiment"` label, the model-field discrepancy (worded as "indicates," not "proves," per the instruction to weaken rather than strengthen uncertain wording), and the `build_success=false`/`rescan_success=true` internal inconsistency.
Risk: None — additive disclosure and a verified numeric correction; no existing claim was strengthened.
Evidence Preserved? YES — README.md is documentation, not an evidence artifact.

File: `preregistration/PRE_REGISTRATION_AMENDMENT.md`
Reason: Two separate, clearly-labeled correction/disclosure notes, both evidence-justified.
Audit Finding: C1 (baseline mechanism wording), C2 (AF-06/JS-06 mismatch).
Summary of Changes:
1. Added a dated "Correction note" after the "What this establishes" paragraph, clarifying that the specific ERESOLVE/ResolutionImpossible mechanism described in this section refers to results in a *different, external repository* (`santuCG/llm-sbom-remediation-experiment`) that was not independently re-verified in this pass, and separately disclosing that this repository's own `grype-baseline.yml` workflow was sampled (11/36 runs) via GitHub's API and shows a different failure point (build/test/rescan, not package-manager resolution). Deliberately did **not** rewrite or delete the original claim, since it pertains to a different, unverified data source — added a clearly dated, clearly labeled qualification instead, per "if uncertain, weaken wording instead."
2. Added a dated "Disclosure note" documenting the AF-06/JS-06 mismatch between locked pre-registration identities and executed evidence, stating plainly that the root cause could not be determined with certainty and that the choice between re-running the two scenarios or formally amending the pre-registration is explicitly left as a decision for the repository owner — not decided here.
Risk: None — both are additive, dated, clearly-labeled notes; no original pre-registration content was altered or removed.
Evidence Preserved? YES — this edits prose in an amendment document, not the locked scenario JSON (`results/scenarios/final_18_scenarios.json` was not touched) and not any execution evidence.

File: `results/THESIS_DRAFT.md`
Reason: This draft's Chapter 3 results table contradicts current execution evidence for most scenarios and uses pre-registered (not executed) identities for AF-06/JS-06.
Audit Finding: M7.
Summary of Changes: Added a `STATUS: STALE — SUPERSEDED, DO NOT CITE AS CURRENT RESULTS` banner at the top of the file, explaining specifically what's stale (the AF-06/JS-06 identity mismatch and the "Failed" cells that don't match current `metrics.json` values) rather than a bare "stale" tag with no explanation.
Risk: None — the chapter text itself was left untouched; only a prepended warning banner was added. No results table cell was edited, added, or removed.
Evidence Preserved? YES — this is a draft thesis chapter, not an evidence artifact.

---

**Mid-pass correction, disclosed:** the first draft of the C5 entries above, and the corresponding entries in `findings_classification.md` and `audit_progress.md`, reprinted the actual leaked token string while documenting where it was found — a direct violation of this pass's own instruction to reference secrets by file/line only. Caught during final verification and corrected in all three files before this report was finalized; the token string does not appear in any file in this repository going forward except inside `results/execution_evidence/` (immutable historical evidence, not touched) and the working-tree copies of the 6 originally-flagged files' **git history** (unchanged, since history was not rewritten, per the rules of this pass).

---

## FINAL REPORT

### Fixed (mapped to finding ID)

| # | File(s) | Finding | Change |
|---|---|---|---|
| 1 | `archive/check_status_20260726_171013.py` | C5 | Hardcoded token → `os.environ["GITHUB_TOKEN"]` |
| 2 | `archive/compare_metrics_20260726_171013.py` | C5 | Same |
| 3 | `archive/fetch_logs_20260726_171013.py` | C5 | Same |
| 4 | `archive/poll_pipeline_20260726_171013.py` | C5 | Same |
| 5 | `archive/scratch_fetch_runs_20260726_171013.py` | C5 | Same |
| 6 | `archive/temp_files/get_artifacts.py` | C5 | Same |
| 7 | `.github/workflows/generic-remediation.yml` | C4, M2 | `set -o pipefail` added to "Apply Fix & Verify" |
| 8 | `.github/workflows/grype-baseline.yml` | C1, C4-adjacent | `set -o pipefail` added to "Phase 3 & 4" and "Phase 5" |
| 9 | `scripts/remediation/retry_remediation.py` | M2 | `failure_stage` now resets to `none` on a successful retry |
| 10 | `scripts/remediation/manifest_editor.py` | C4, M6 | Scoped/transitive override paths now nested correctly instead of written as a flat, invalid key |
| 11 | `scripts/remediation/generate_manifest.py` | C3 | `llm.model` now reads `LLM_MODEL_USED` env var if set, falling back to the prior hardcoded default (zero behavior change today; see Deferred) |
| 12 | `scripts/run_deterministic_baseline.py` | C6 | Hardcoded `experiment/`/`documentation/` paths corrected to `results/scenarios/`, `results/`, `docs/` (script fixed, **not executed**) |
| 13 | `.gitattributes` (new) | M4 | Pins `results/execution_evidence/**` to LF |
| 14 | `README.md` | C7, M1, C3 | 17→18 count correction; retry-loop disclosure; JS-09 deviation disclosure |
| 15 | `preregistration/PRE_REGISTRATION_AMENDMENT.md` | C1, C2 | Dated correction note on baseline mechanism wording; dated disclosure note on AF-06/JS-06 mismatch |
| 16 | `results/THESIS_DRAFT.md` | M7 | Stale/superseded banner added |

### Deferred (intentionally left unchanged, and why)

- **`scripts/remediation/llm_reasoner.py`** and **the "Gather Evidence" step in `generic-remediation.yml`**: fully closing the loop on C3 (item 11 above) requires `llm_reasoner.py` to actually set `LLM_MODEL_USED` after a successful call. Neither file was named in this pass's authorized fix list, so this wiring was not done — `generate_manifest.py`'s fix is real but inert until this follow-up lands.
- **`archive/temp_scripts/{check_gh.py, fetch_logs.py, fetch_logs_fixed.py, fetch_logs_to_file.py}`**: contain the same leaked token, discovered while verifying the C5 fix, but not among the 6 files explicitly named in this pass's authorization, and — importantly — **untracked by git** (never committed), a materially lower-severity, local-only exposure rather than the git-history/public exposure C5 describes. Not edited without confirmation.
- **`.github/workflows/generic-remediation.yml`'s "Fallback Lockfile Regeneration" and "Retry Remediation Strategy" steps, and the `build:frontend`/`build:server`/`build`/`test` lines in "Validate Remediation & Rescan"**: these also pipe through `tee` without `pipefail`, but — unlike the fixed sites — have **no pre-existing explicit failure check at all** (or, in one case, an explicit `|| true` that intentionally ignores failure). Adding `pipefail` there would introduce new abort-on-failure behavior where none currently exists, which is a larger change than "restoring an existing but broken check" and was excluded under "do not change behavior beyond the identified bug." Flagging this as a real, separate, not-yet-authorized gap for a future pass.
- **The Minor findings from the original audit that were never assigned a numbered Minimum Fix Set item** (e.g. `README.md`'s reference to a non-existent `progress-reports/` folder, the UK/US spelling mix, the "double-blind" terminology note): left untouched, strictly per the instruction to execute only items 1-12 (plus the named security item) and not rediscover/act on anything else.
- **M3 (templated frontend build-log hashes)**: explicitly out of scope per the instructions (item 18, an open question, not a fix target).

### Requires Rerun

- **JS-03** — after fixes #7 and #10 above, to obtain a genuine (not falsely-positive) result. Not run in this pass.
- **AF-06 and JS-06** — against their locked pre-registration targets (`jinja2`/CVE-2024-56326 and `flatted`/CVE-2026-33228), if the owner decides against a pre-registration amendment instead. Not run in this pass.
- **JS-09** — under the deviation-free protocol (real fixed-versions list, no forced first-attempt retry framing), if the owner decides against keeping it as an explicitly-labeled supplementary result. Not run in this pass.

No scenario was rerun, no evidence was regenerated, and no external CI/GitHub Actions history was imported into the repository, per the explicit boundary for this pass.

### Requires Manual Decision (repository owner only)

- **Token rotation.** The token found in C5 must be revoked/rotated in GitHub account settings regardless of anything done in this repository — that action is entirely outside this repository and was not, and cannot be, performed by this remediation pass. Removing it from the 6 files' working-tree content does not remove it from git history.
- **Whether to also rewrite git history** to fully scrub the token from past commits. This pass explicitly did **not** do this (per the hard technical guardrail against `filter-branch`/force-push/history rewrites) — it is a destructive operation requiring the owner's own explicit decision and execution.
- **The 4 additional untracked files** in `archive/temp_scripts/` containing the same token — clean up locally or leave as-is; not committed, so not a public-exposure decision, but still worth a conscious choice.
- **AF-06 / JS-06**: rerun against locked targets, or formalize the substitution via pre-registration amendment. A disclosure note was added either way; the underlying decision was deliberately not made in this pass.
- **JS-09**: rerun under the corrected protocol, or keep and prominently present it as the labeled supplementary result its own internal field already calls it. A disclosure note was added; the decision was deliberately not made in this pass.
- **Wiring `LLM_MODEL_USED` through `llm_reasoner.py`**: a small, low-risk follow-up, but touches a file outside this pass's named scope, so left for explicit instruction.

### Not Modified (evidence intentionally preserved)

- Every file under `results/execution_evidence/**` for all 18 scenarios — confirmed via `git status --porcelain -- results/execution_evidence/` returning no output.
- `archive/legacy_experiment_dir/`, `archive/legacy_manual_scripts/`, `archive/legacy_methodology_docs/`, `archive/legacy_results_dir/` (including `baseline_temp/`), and every other archived historical artifact not named in the security fix.
- `results/scenarios/final_18_scenarios.json` and `SCENARIOS_LIST.md` — the locked pre-registration record itself; only prose *about* the discrepancy was added elsewhere, the locked entries were not touched.
- `js09_pipeline_logs.txt` (raw evidence, found in a separate checkout, not part of this repository's git history).
- No `git commit`, `git push`, `git add`, `git filter-branch`, `git rebase`, or any history-rewriting command was run at any point in this pass.

### Verification performed before closing this pass

- Re-grepped for the leaked token string across every file touched — confirmed absent (after also catching and fixing three instances of my own reports having reprinted it, disclosed above).
- Re-ran `git status --porcelain` scoped to `results/execution_evidence/` — confirmed no changes.
- `python3 -m py_compile` on all 10 edited Python files — all pass.
- Manually reviewed the full `git diff` of both edited YAML workflow files and all four edited Python pipeline scripts — indentation and logic changes confirmed minimal and as described above.

---

## READ-ONLY VERIFICATION PASS (2026-08-01)

Independent re-verification of the remediation above. One exception exercised per this pass's own explicit authorization (see Security Verification below); otherwise no further repository changes were made.

### 1. Security verification
Repo-wide sweep (tracked + untracked, not limited to the 6 originally-named files) for GitHub tokens, cloud provider keys, private key blocks, and hardcoded `GEMINI_API_KEY`/password assignments. Method note: ripgrep-backed tools silently skip `.gitignore`d paths by default, which would have produced a false "clean" result for `archive/temp_scripts/` (itself gitignored) — caught by cross-checking with a plain, gitignore-independent `grep` as well.
- **Original 6 named C5 files:** confirmed clean, token absent, `os.environ["GITHUB_TOKEN"]` present in all 6.
- **New finding, same secret, 4 additional files:** `archive/temp_scripts/check_gh.py`, `fetch_logs.py`, `fetch_logs_fixed.py`, `fetch_logs_to_file.py` — untracked (gitignored, never committed), utility/support scripts (ad hoc GitHub API log-fetching helpers), not historical evidence. Per this pass's explicit authorization to remediate exactly this category of finding, fixed using the identical pattern (`TOKEN = os.environ["GITHUB_TOKEN"]`). Verified: secret absent afterward (both ripgrep- and grep-based checks), all 4 files pass `py_compile`, the two remaining files in that folder (`copy_evidence.py`, `print_js03_prompt.py`) checked and contain no secrets. This folder is gitignored so these edits do not appear in `git status`.
- **Vendored third-party source** (`applications/juice-shop/lib/insecurity.ts`, `applications/airflow/tests/providers/{ssh,slack}/hooks/test_*.py`, `applications/juice-shop/ctf.key`, `applications/juice-shop/encryptionkeys/premium.key`): matched generic private-key/token-shaped patterns; inspected and confirmed to be OWASP Juice Shop's and Apache Airflow's own well-known, publicly-shipped demo/test fixtures (e.g. a malformed `"...asdfg..."` placeholder key in an Airflow unit test), not real secrets and not thesis-authored. Not a remediation target, consistent with this whole engagement's scope boundary around vendored application source.
- `.env`: re-confirmed untracked (`git ls-files .env` empty). No `.pem`/`id_rsa`/`credentials.json` files tracked anywhere. No hardcoded `GEMINI_API_KEY` assignment found outside the proper `secrets.` context in `.github/workflows/`.

### 2. Code fix verification
All 6 fixes re-verified with actual execution, not just re-reading the diff:
- `manifest_editor.py`: ran `_apply_override()` in isolation against JS-03's exact input (`"request > form-data"`, pre-existing `{"form-data": "2.5.4"}`) — produced the correct nested `{"form-data": "2.5.4", "request": {"form-data": "2.5.4"}}`, and confirmed the flat-key case (used by all 16 other scenarios) is byte-for-byte unchanged.
- `set -o pipefail` in both workflow files: reproduced the exact bug and fix in an isolated `bash -e` shell (matching GitHub Actions' actual shell invocation exactly) — confirmed the `|| (echo "... Failed" && exit 1)` fallback silently never fires without `pipefail`, and correctly fires and aborts the step with `pipefail`.
- `generate_manifest.py`: confirmed `os.environ.get("LLM_MODEL_USED", "gemini-2.5-flash")` returns the unchanged default when unset (zero behavior change today) and the override value when set; confirmed the script still runs and hits its pre-existing early-return path without error.
- `retry_remediation.py`: confirmed both branches of `failure_stage if not llm_response_valid else 'none'` in isolation.
- `run_deterministic_baseline.py`: confirmed the new input path exists and is a plain JSON list matching the script's expected structure, and confirmed no leftover references to the old `experiment/`/`documentation/` paths remain anywhere in the file.
All 10 touched Python files re-confirmed to pass `python3 -m py_compile`. **All 6 code fixes: Fully Verified, no regressions found.**

### 3. Evidence immutability
Two independent methods, both clean:
- Full, repo-wide `git status --porcelain` (not scoped to any subdirectory) returns exactly the 15 intentionally-modified tracked files and nothing else — no `results/execution_evidence/`, `results/scenarios/`, or `archive/legacy_*` entries anywhere in the output.
- `git hash-object` (working tree) vs `git rev-parse HEAD:<path>` (committed blob) compared directly for 6 sampled files spanning every immutable category (execution evidence metrics/manifest/log, locked scenario JSON, archived legacy metrics, applications evidence SBOM) — all 6 byte-for-byte identical.
**Zero evidence files modified. Fully Verified.**

### 4. Documentation verification
Re-read every documentation diff in full, independently re-verified every factual claim against current repository data (not reused from the prior pass), and scanned every added line for forbidden absolute language.
- **Defect found:** `README.md`'s new "Note on test_success" paragraph says "see the note on JS-09 **below**" — but the "Note on JS-09" paragraph is actually positioned *above* it in the final file (confirmed by direct read of the current file: JS-09 note at line 140, test_success note with the cross-reference at line 142). **This is a real, self-contained documentation defect** — the substantive content of both notes is accurate, but the cross-reference direction is wrong. Not fixed in this pass (out of the explicit read-only + security-only-exception scope) — reported as Remaining Work below.
- All other factual claims independently re-verified from scratch against current `metrics.json`/`final_18_scenarios.json` data: AF-06/AF-09/JS-06 identities, the "14 of 14 'Failed' table cells don't match current data" basis for the THESIS_DRAFT.md banner's "most" claim, and the "11 of 36" baseline-sampling figure — all confirmed accurate.
- No forbidden absolute language (guarantee/impossible/perfect/flawless/proves/always/never) found in any newly-added documentation text; the one incidental match ("never starts") is a verbatim quote of the pre-existing original claim being critiqued, not new language.
**Result: Partially Verified — one real cross-reference defect found and reported, not fixed; all substantive content confirmed accurate.**

### 5. Redaction verification (independently re-done, not reused from the prior pass)
Direct, gitignore-independent `grep` for the exact secret substring across `audit_progress.md`, `findings_classification.md`, `remediation_log.md`, and all three edited documentation files (`README.md`, `PRE_REGISTRATION_AMENDMENT.md`, `THESIS_DRAFT.md`) — zero matches. **Fully Verified.**

### 6. Scope compliance
Every one of the 15 tracked modified files plus the 1 new file (`.gitattributes`) traces to a named finding ID from the approved Minimum Fix Set (items 1-12) or the explicitly-authorized Security item (C5); the 4 additional `archive/temp_scripts/` fixes made during this pass trace to the same C5 finding under this pass's own explicit security-exception authorization. **No unexpected or untraceable modification found. Fully Verified.**

## VERIFICATION TABLE

| Finding ID | Claimed Fix | Status | Evidence | Remaining Work | Risk |
|---|---|---|---|---|---|
| C5 | Token removed from 6 named archive scripts | Fully Verified | Secret absent (grep, gitignore-independent); `os.environ["GITHUB_TOKEN"]` present; all 6 pass `py_compile` | Token rotation on GitHub (manual decision, outside repo) | None remaining in-repo |
| C5 (extension) | Token removed from 4 additional `archive/temp_scripts/` files, found during this pass | Fully Verified | Same checks as above, all 4 pass | Same rotation requirement | None remaining in-repo |
| C5 (residual) | Token in git history (6 originally-tracked files) | Not Applicable / Out of Scope | `git log` still shows commit `797562b2` | Rotate token; history rewrite is a separate owner decision, explicitly not performed | Live until rotated |
| C1 | `set -o pipefail` added at the two sites with a pre-existing broken check in `grype-baseline.yml` | Fully Verified | Isolated `bash -e` reproduction of bug and fix | None for the named sites; steps with no pre-existing check at all remain unfixed by design (see Deferred in prior report) | Low |
| C1 | Correction note on baseline mechanism wording in `PRE_REGISTRATION_AMENDMENT.md` | Fully Verified | Claims re-checked against 11/36 sampled run data; correctly scoped to avoid conflating the external `llm-sbom-remediation-experiment` repo with this repo's `grype-baseline.yml` | None | None |
| C2 | AF-06/JS-06 disclosure note added | Fully Verified | Package/CVE identities independently re-extracted from `metrics.json` and `final_18_scenarios.json` and confirmed to match the note exactly | Owner decision: rerun vs. amend (unchanged, not resolved by design) | None |
| C3 | `generate_manifest.py` model field no longer hardcoded | Fully Verified (fix itself); Deferred (full resolution) | Env-var read confirmed functionally correct and zero-behavior-change-today | `llm_reasoner.py` still needs to set `LLM_MODEL_USED` for this fix to take effect on a future run — explicitly out of this pass's named scope | Low (current runs unaffected either way) |
| C3 | JS-09 deviation disclosure added to README | Partially Verified | Content accurate; **but the paragraph's own internal cross-reference ("see note on JS-09 below") points the wrong direction** | Fix the "below" → "above" wording | Cosmetic only — does not affect the accuracy of either note's content |
| C4 | `manifest_editor.py` nested-override fix | Fully Verified | Executed against JS-03's exact input; correct output confirmed; flat-key case confirmed unchanged | None | None |
| C4 | `set -o pipefail` at "Apply Fix & Verify" in `generic-remediation.yml` | Fully Verified | Same isolated shell reproduction as C1 | None | None |
| C6 | `run_deterministic_baseline.py` paths corrected | Fully Verified | New input path exists and is structurally compatible; no leftover old paths; script not executed | Script still requires a deliberate rerun decision (owner) | None (fix); N/A (rerun) |
| C7 | README 17→18 scenario count | Fully Verified | Recount of all 18 `metrics.json` independently reproduced the 18/18 figures | None | None |
| M1 | Retry-loop disclosure added to README | Fully Verified | 7/9 JS retry claim re-confirmed against `metrics.json` `retry_count` fields | None | None |
| M2 | `retry_remediation.py` `failure_stage` reset | Fully Verified | Both branches tested in isolation | None | None |
| M4 | `.gitattributes` added | Fully Verified | File present, correctly scoped, no evidence file touched | Does not retroactively fix already-checked-out CRLF copies elsewhere | None |
| M6 | Same as C4 `manifest_editor.py` fix | Fully Verified | See C4 | None | None |
| M7 | `THESIS_DRAFT.md` stale banner | Fully Verified | Banner's specific claims (AF-06/JS-06 identities, "most Failed cells don't match") independently re-checked cell-by-cell | None | None |

### Overall Verdict

**FOLLOW-UP REQUIRED.**

One real, self-contained defect was found (the README "below" → should be "above" cross-reference) and one intentional, previously-disclosed gap remains open by design (`generate_manifest.py`'s fix is inert until `llm_reasoner.py` is separately updated, which was never in scope for this pass). Neither affects evidence integrity, security posture, or the substantive accuracy of any claim — both are precisely bounded, already-identified, low-risk items. This does not rise to "NOT READY" or invalidate the remediation work; it means one more small, targeted pass (fix one sentence's direction; decide whether to extend scope to `llm_reasoner.py`) is needed before this can be called fully clean.

---

## FOLLOW-UP ITEMS COMPLETED (2026-08-01)

Both items from the verification pass above were resolved:
1. **README cross-reference fixed** — "see the note on JS-09 below" corrected to "above" (the JS-09 note is positioned before it, not after). Finding: C3 (verification-pass finding). No evidence file touched.
2. **`LLM_MODEL_USED` wiring decided and implemented** — concluded it should be implemented, since `generate_manifest.py`'s existing fix (from the prior remediation pass) is otherwise permanently inert. `scripts/remediation/llm_reasoner.py` now writes the model that actually responded to `$GITHUB_ENV` (the standard, correct mechanism for passing a value across GitHub Actions steps — `os.environ` alone does not survive a step boundary) immediately after a successful API call, with a safe no-op fallback when run outside CI. Verified: both the first-attempt and retry code paths call the same patched function; syntax valid; no-op confirmed when `GITHUB_ENV` is unset; correct `KEY=value` write format confirmed when set. No evidence file touched.

---

## REPOSITORY CLEANUP PASS (2026-08-01)

Scope: file/folder organization only — no methodology, pipeline logic, workflow behavior, or documentation content was edited in this pass. Every action below was checked against two gates first: (1) is it referenced anywhere in active docs/scripts/workflows, and (2) does it touch anything under `results/execution_evidence/**` or another immutable-evidence path. Anything failing either check was left alone or flagged for approval rather than acted on.

### Archived (moved into the existing `archive/legacy_manual_scripts/`, not deleted)
Verified unreferenced (`grep` across `.github/`, `scripts/`, `tools/`, `docs/`, `preregistration/`, `README.md`, `CHANGELOG.md`, `SCENARIOS_LIST.md` — zero hits for all 8) before moving. All are one-off, already-executed migration/inspection scripts, several hardcoding specific scenario IDs and run IDs, not part of the repeatable pipeline (`scripts/remediation/`, `scripts/baseline/`):
- `append_evidence.py`, `check_cves.py`, `check_scenarios.py`, `fix_manifest_empirical.py`, `fix_manifests.py` (were loose at repo root)
- `scratch/add_json_comments.py`, `scratch/update_evidence_links.py`, `scratch/update_manifests.py` (were in `scratch/`, which is now empty and removed)

### Removed (not archived — confirmed genuine duplicates or pure build artifacts, nothing of value lost)
- `archive/evidence_20260726_171013.zip` — hash-compared every file inside it against the loose files already sitting beside it in `archive/`: `build.log`, `llm-request.json`, `llm-response.json`, `metrics.json`, `baseline-grype.json`, `baseline-sbom.json`, `rescan.json`, `selected-candidate.json` are all byte-identical to the already-unzipped copies; the zip contains nothing the loose files don't already have. Confirmed unreferenced first.
- `__pycache__/` (untracked Python bytecode cache, regenerable, zero information value)
- `experiment/` and `experiment/evidence_logs/` (untracked, completely empty directory tree — `scripts/run_deterministic_baseline.py` no longer references this path after the earlier remediation pass, so it's also fully vestigial, not just empty)
- `scratch/` (removed after the 3 files inside it were archived, leaving it empty)

### Intentionally left unchanged
- **The other 4 zip files in `archive/`** (`evidence_30133471466_...`, `evidence_30133472098_...`, `evidence_30133490467_...`, `evidence_vm2_...`): checked for matching run-ID content elsewhere in `archive/legacy_results_dir/` — none found. These appear to hold content not duplicated in loose form anywhere else in the repo. Left as-is.
- **The ~30 remaining loose, timestamp-suffixed files directly in `archive/` root** (case-study `.md` files, `session_...md`, various one-off `.py`/`.txt`/`.json`): these already live inside `archive/` (i.e., already out of any active folder), so they don't violate "active folders should only contain X." Not deduplicated further against `archive/legacy_results_dir/` in this pass — would need the same file-by-file hash comparison done for the one zip above, and I didn't have a specific trigger (like the exact-name-match that flagged the zip) to justify spending more time on it without risking a wrong call.
- **`archive/temp_scripts/`** (untracked, gitignored utility scripts, already fixed for the token issue in the prior pass): left in place, already outside any active folder.
- **`.env`**: not touched — credentials file, explicitly out of scope for a cleanup pass, and already correctly gitignored/untracked.

### Requires your approval before any action
- **`results/scenarios/AF-01.json` through `JS-09.json` (18 files, all tracked).** These are a third representation of scenario data — a per-scenario, human-readable dossier combining pre-registration metadata, execution timestamps/run IDs, and the same "EMPIRICAL EVIDENCE" block already present in each scenario's `experiment_manifest.json` — distinct from both `results/scenarios/final_18_scenarios.json` (the pre-registration lock file) and `results/execution_evidence/<ID>/*` (the raw execution artifacts). Checked: not referenced by any script, workflow, or doc — including `README.md`'s own "Key Documents" table, which describes `results/scenarios/` as containing only `pre_registered/scenarios.json` and `final_18_scenarios.json`, with no mention of these 18 files. They are not exact duplicates of anything (the combination of fields is unique to them), so "remove as a duplicate" would be wrong; but they're also undocumented, which is itself worth deciding on rather than me guessing. Three options, your call: (a) keep as-is and add a line to `README.md`'s documents table describing them (a documentation-only fix, not covered by this pass's "don't modify documentation" boundary since it would be *adding* a missing reference, not changing existing content), (b) keep but move somewhere more clearly labeled, (c) treat as superseded/redundant and archive. I did not act on any of these.
- **The zip-vs-`legacy_results_dir` dedup question for the ~30 other archive-root loose files**, noted above — flagging rather than guessing.

### Resolved by owner instruction (2026-08-01)
`results/scenarios/AF-01.json`–`JS-09.json`: owner confirmed these are proper experimental evidence, to be kept and documented, not archived. `README.md`'s `results/scenarios/` table row updated to describe them accurately (contents, and their relationship to the matching `experiment_manifest.json` "EMPIRICAL EVIDENCE" block). No file under `results/execution_evidence/**` or `results/scenarios/*.json` itself was touched — only the README description was added.

