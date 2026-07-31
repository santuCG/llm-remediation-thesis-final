# ZERO-TRUST AUDIT — FINAL REPORT

**Repository:** `llm-remediation-thesis-final` (origin: `github.com/santuCG/llm-remediation-thesis-final`)
**Audit stance:** hostile committee reviewer. Objective is correctness, not volume of findings.
**Scope:** everything except `.git/`, `applications/airflow/af_venv/`, `applications/juice-shop/node_modules/` (vendored/compiled, not thesis-authored).
**Method:** read-only throughout. No file in the repository was created, moved, deleted, renamed, or modified. No `git commit`/`push`/`add` was run. This file is the only artifact written. Two local checkouts were examined (a working copy and a second, independently-cloned checkout that turned out to contain one additional untracked file with decisive evidence — see Section 8 and Addendum material folded in below); both point at the same commit history and the same `origin`.
**External verification performed:** the original author's GitHub remote was fetched (branches/commits only — no push), and the public GitHub Actions REST API was queried unauthenticated (job/step metadata only — no log or artifact download, and the leaked credential found in Section 13 was never used to authenticate anything).

---

## 1. Executive Summary

This repository documents a Master's thesis testing whether an LLM (Gemini) can generate working dependency-remediation strategies across 18 pre-registered CVE scenarios (9 OWASP Juice Shop/npm, 9 Apache Airflow/pip), where the thesis's central claim is that a naive application of a vulnerability scanner's recommended fix fails 100% of the time (the "0% baseline"), and that LLM-assisted remediation does meaningfully better.

The engineering is real and mostly sophisticated: genuine SBOM generation (Syft), genuine vulnerability scanning (Grype), a genuine structured-output LLM integration, genuine CI automation, and — where it was possible to independently verify via GitHub's own API — genuine, non-fabricated pipeline executions. That is an important finding in its own right and is stated plainly so it isn't lost under the issues below.

However, the audit surfaced a set of **Critical findings that materially undermine the specific claims made about the results**, most importantly:
- The "0% baseline" claim's specific failure mechanism (package manager rejects the install with `ERESOLVE`/`ResolutionImpossible`) does not match what actually happened in 11 of 11 sampled real CI runs of the dedicated baseline workflow — in every one, the install succeeded and a later build/test/rescan step failed instead.
- Two of the 18 "pre-registered, locked" scenarios (`AF-06`, `JS-06`) do not correspond to what was pre-registered; one is an exact duplicate of another scenario's target, the other is an unregistered CVE substituted in without disclosure.
- `JS-09`'s official experiment manifest states the LLM model used was `gemini-2.5-flash`; the scenario's own raw CI execution log and the commit hash the manifest itself cites both independently prove `gemini-3.6-flash` was actually used for both attempts, with the ground-truth "fixed version" answer deliberately hidden from the prompt — a deviation that applies to no other scenario and is disclosed nowhere outside a buried JSON field.
- A hardcoded GitHub Personal Access Token is committed in plaintext across 6 files.
- Several metrics/log self-contradictions exist, most precisely root-caused to a missing `set -o pipefail` in the CI workflow and a stale field in the retry script — genuine bugs, not evidence of intentional fabrication, but they mean the pipeline's own success/failure determination cannot currently be trusted at face value.

None of this means the underlying research idea is unsound — the enrichment-signal thinking (CVSS/EPSS/KEV), the four-gate validation design, and the retry/re-prompt mechanism (confirmed genuine) are reasonable. The problem is a gap between what is claimed in the narrative documents and what the primary evidence — including evidence outside this repository that the audit went and fetched — actually supports.

---

## 2. Critical Issues

### C1 — The specific "0% baseline" failure mechanism does not match the real CI history
**Confidence: High** (raised from Medium after directly sampling 11/36 real runs via the GitHub API; would be raised to definitive by sampling the remaining 25, which is the same evidence shape and was not fully exhausted only due to time, not access — nothing blocks a full sample).
The dedicated `Grype Baseline Pipeline` workflow (`.github/workflows/grype-baseline.yml`) genuinely ran 36 times on 2026-07-26 (27 failure, 9 success — confirmed via `GET /actions/workflows/{id}/runs`). In every one of 11 runs sampled, the step that installs the scanner's recommended version (`Phase 3 & 4 - Apply Grype Recommendation`) succeeds; the failure, when it occurs, is always at a later step (`Phase 5 - Build / Tests / Rescan`). This directly contradicts `preregistration/PRE_REGISTRATION_AMENDMENT.md:186,192`'s specific claims ("triggers a fatal `ERESOLVE`... immediately crashing the build"; "the resolver raises `ResolutionImpossible`... **the build never starts**"). Caveat: the same workflow has the pipefail bug described in C5, so a resolver-level failure being silently swallowed cannot be 100% excluded without the raw log text (which requires authentication this audit did not use). What is not in doubt is that GitHub's own recorded step conclusion says "success" for the install step in every sampled case.
*Evidence that would change this finding:* the raw log text for any of these runs (requires an authenticated `gh`/API call) showing an actual `ERESOLVE`/`ResolutionImpossible` string that the exit-code bug masked.

### C2 — Two of 18 "pre-registered, locked" scenarios don't match what was pre-registered
**Confidence: High** (programmatically verified against all 18, not a sample).
`AF-06`'s executed evidence (`results/execution_evidence/AF-06/metrics.json`: `werkzeug`/`CVE-2024-34069`) is an exact duplicate of `AF-09`'s pre-registered *and* executed target, not `jinja2`/`CVE-2024-56326` as pre-registered in `results/scenarios/final_18_scenarios.json` and `SCENARIOS_LIST.md`. `JS-06`'s executed evidence (`lodash`/`CVE-2021-23337`) is not the pre-registered `flatted`/`CVE-2026-33228`, and does not correspond to any of the 18 locked targets — it only appears as a discovery-pool candidate inside `JS-03/candidate-ranking.json`. No amendment document discloses either substitution. This directly undermines the explicit stated purpose of pre-registration ("prevents cherry-picking results after the fact," `README.md:57`).
*Evidence that would change this finding:* a pre-registration amendment specifically covering AF-06/JS-06 (searched for, not found), or evidence this was an innocent mislabeling in the evidence-upload pipeline rather than the scenario selection itself.

### C3 — `JS-09`'s manifest misstates which LLM model was used, and hides ground truth from the prompt
**Confidence: Highest in this audit** (three independent sources agree: unmerged branch code, raw unedited CI console log, and the manifest's own `repository_commit` field).
`results/execution_evidence/JS-09/experiment_manifest.json` records `"model": "gemini-2.5-flash"`. Its own `repository_commit` field is `b9cb78f9f535eaef4a76d820a0541702dec4a5dc` — the exact commit, on the unmerged `test-js-09` branch (fetched from `santuCG/llm-remediation-thesis-final`), titled `"fix: use gemini-3.6-flash"`, which changes the model fallback list to try `gemini-3.6-flash` first. A raw, untracked GitHub Actions log export (`js09_pipeline_logs.txt`, found in the second checkout at `C:\Users\HP\Downloads\llm-remediation-thesis-final`, UTF-16 encoded, decoded and read directly) shows, for **both** the first attempt and the retry: `[LLM] Successfully retrieved response using model: gemini-3.6-flash`, and both prompts contain `* Fixed Versions: [HIDDEN INTENTIONALLY - YOU MUST DETERMINE THE SAFEST VERSION TO AVOID BREAKING THE BUILD]` in place of the real fixed-version list every other scenario receives. The manifest's own `experiment_id` field (in `llm-request.json`) reads `"Supplementary Experiment"`, vs. `"2026-final"` for all 17 other scenarios — an internal acknowledgment this was different, never surfaced in any reader-facing document. The retry mechanism itself is genuine (a real validator failure triggered a real, successful second attempt) — the issue is what was fed to the model and what the manifest says was fed, not that the outcome was faked.
*Evidence that would change this finding:* none plausible — this is a direct, first-party, self-contradicting record.

### C4 — `JS-03`'s `build_success: true` is a false positive, root-caused precisely
**Confidence: High** (code-level root cause identified, not just data anomaly).
`JS-03/build.log` contains a real, fatal `npm error code EINVALIDTAGNAME` (from an invalid override key `"request > form-data"`, itself caused by `scripts/remediation/manifest_editor.py:27-29` writing a flat key instead of nesting it). Yet `JS-03/metrics.json` reports `build_success: true, dependency_verified: true, rescan_success: true`. Root cause: `.github/workflows/generic-remediation.yml:88` runs `npm install 2>&1 | tee ../../build.log || (echo "NPM Install Failed" && exit 1)` without `set -o pipefail` (confirmed via the raw AF-01 log: `shell: /usr/bin/bash -e {0}`, no `-o pipefail`) — so the pipeline's exit status is `tee`'s (almost always 0), and the fallback never fires. This is the same bug present at 6 locations in the workflow (lines 88, 92, 107, 110, 195, 197) and in the separate baseline workflow (C1).
*Evidence that would change this finding:* none needed — fully code-traced and log-confirmed.

### C5 — Hardcoded GitHub Personal Access Token committed in 6 files
**Confidence: High** (pattern-matched to GitHub's exact PAT format; not tested against the live API by this audit, and should not be).
```
archive/check_status_20260726_171013.py:7
archive/compare_metrics_20260726_171013.py:3
archive/fetch_logs_20260726_171013.py:2
archive/poll_pipeline_20260726_171013.py:7
archive/scratch_fetch_runs_20260726_171013.py:2
archive/temp_files/get_artifacts.py:6
```
each containing a hardcoded GitHub Personal Access Token (redacted here — referenced by file/line only). Committed in commit `797562b2`. `archive/` is currently staged for deletion (uncommitted, pre-existing state, not caused by this audit) — this does **not** remediate the exposure; the token remains in git history regardless, and file deletion is not equivalent to revocation.

**[2026-08-01 remediation update]** The token has since been removed from these 6 files' working-tree content (replaced with an environment-variable read) as part of a subsequent remediation pass — see `remediation_log.md`. This does not remove it from git history; rotation on GitHub's side is still required regardless.
*Action required regardless of audit outcome: rotate this token now.*

### C6 — The one script that could produce the missing baseline evidence cannot run, confirmed in two independent checkouts
**Confidence: High.**
`scripts/run_deterministic_baseline.py` reads `experiment/final_18_scenarios.json` and writes to `experiment/` and `documentation/`. Neither directory exists with content in either checkout audited — in the second checkout, `experiment/` exists but is a completely empty directory (`find experiment -type f` → nothing), so the script's first line (`if not os.path.exists(scenarios_path): sys.exit(1)`) would still fire immediately.
*Evidence that would change this finding:* the actual `experiment/final_18_scenarios.json` turning up somewhere, or the script being confirmed as legacy/superseded by the current `results/scenarios/` + `.github/workflows/grype-baseline.yml` path (plausible, but not stated anywhere).

### C7 — README's specific numeric claim ("17 executed scenarios... 17/17 rescan_success") does not match the data
**Confidence: High** (directly counted across all 18 `metrics.json` files).
`README.md:138` states 17 scenarios were executed and all 17 achieved `rescan_success: true`. The actual data shows **18 of 18** scenarios (including `JS-09`, which has `build_success: false`) have `rescan_success: true`. There is no reconciliation anywhere of which scenario is meant to be "the 18th, unexecuted" one.

---

## 3. Major Issues

- **M1 — Undisclosed LLM retry/re-prompt loop.** 7 of 9 JS scenarios required a second LLM attempt after a real build failure (confirmed genuine, not fabricated, via the JS-09 raw log). `retry_count`/`llm_iteration` fields exist for exactly this reason. Not mentioned anywhere in `README.md`'s single-pass "How the Experiment Works" or in `docs/*.md`.
- **M2 — Stale `failure_stage` field bug.** `scripts/remediation/retry_remediation.py:64-71` never resets `failure_stage` to `"none"` after a successful retry, explaining the `build_success: true` + `failure_stage: "build"` contradiction in 7 of 9 JS scenarios' `metrics.json`. A genuine bug, not fabrication — but it means these fields cannot be trusted without cross-referencing logs.
- **M3 — Templated/duplicated frontend build logs across 8 JS scenarios.** Identical webpack hash (`eec0da7fb4f70cee`) and byte-identical bundle sizes across 8 scenarios that each modified a different backend dependency, some of which (crypto-js, lodash) are plausibly bundled into the frontend. Scan-side evidence (`baseline-grype.json`/`rescan.json`) was checked and found genuinely distinct — the concern is scoped to the frontend build-log transcripts only.
- **M4 — Non-verifying SHA256 "integrity" hashes.** No `.gitattributes` exists; on a standard Windows checkout (`core.autocrlf=true`, the git-recommended default), every declared hash in every `experiment_manifest.json` fails to verify because LF blobs become CRLF working-tree files. Root-caused precisely (declared hash matches `sha256(file.replace(CRLF,LF))` exactly).
- **M5 — `.json`-named files that are not JSON.** All 18 `experiment_manifest.json` files fail `json.load()` (a human-readable "EMPIRICAL EVIDENCE" text block is appended after valid JSON). All 9 Airflow `package-before.json`/`package-after.json` are plain-text `pip freeze` output, not JSON.
- **M6 — `manifest_editor.py` doesn't handle nested override paths.** Root cause of C4's underlying bug: writes `"request > form-data"` as a flat key instead of `{"request":{"form-data":...}}`.
- **M7 — `results/THESIS_DRAFT.md` is stale and unindexed.** Its Chapter 3 results table marks most LLM outcomes "Failed" where current data shows success, uses pre-registered (not executed) identities for AF-06/JS-06, and is not referenced anywhere in `README.md`'s key-documents table.
- **M8 — README's "golden execution evidence... proving the automated POC succeeded" is overstated** given C1-C7 and M1-M6 collectively.
- **M9 — `results/THESIS_DRAFT.md:70` attributes JS-03's failure to "the LLM hallucinated Yarn resolutions syntax"** — the code trace (M6/C4) points to an apply-layer bug and a shell-scripting bug, not an LLM output-format failure; the LLM's own instruction was reasonable plain-English intent.

---

## 4. Minor Issues

- UK/US spelling inconsistency across the corpus (predominantly British — `behaviour` ×22, `catalogue` ×5 — with scattered American spellings, concentrated in `results/THESIS_DRAFT.md`: `optimize`, `prioritize(s)`).
- `README.md:225` references a `progress-reports/` folder that does not exist; the actual folder (`27-07-2026/`) sits bare at repo root.
- `results/THESIS_DRAFT.md:21` calls the pipeline "double-blind" — a specific term with no clear referent here (no second human/assessor party is blinded).
- `archive/` root has ~40 loose files sharing a mechanical `_20260726_171013` timestamp suffix with uninformative names (`temp.py`, `temp2.py`, `temp3.py`) — legitimate to keep, but worth a one-line index.
- `results/execution_evidence/manual_baselines/JS-01_manual_remediation.diff` has UTF-16/encoding artifacts (literal null-byte spacing) suggesting a copy-paste mishap when created — content is legible and legitimate once decoded.
- `scratch/` (root) duplicates the purpose of `archive/temp_files/` — three different "misc script" locations exist (`scratch/`, `archive/temp_files/`, loose `archive/*.py`).

---

## 5. Repository Cleanliness Report

`archive/` is by far the largest source of clutter: a root-level dump of ~40 timestamp-suffixed files (scripts, JSON, 5 `.zip` archives, `.md` case studies), plus four organized subfolders (`legacy_experiment_dir/`, `legacy_manual_scripts/`, `legacy_methodology_docs/`, `legacy_results_dir/`) that are thematically named and traceable. `archive/legacy_results_dir/baseline_temp/` holds 13 GitHub-Actions-run-ID-named folders mirroring a subset of the 36 real baseline runs identified in C1, plus several ambiguous loose files (`manual_build_frontend.log`, `post-sbom-utf8.json`, etc.) sitting outside any run-ID folder. `scripts/` and `tools/` themselves are clean and purposeful; `results/` mixes the canonical `scenarios/` + `execution_evidence/` with the stray, unindexed `THESIS_DRAFT.md` (M7).

## 6. Archive Candidates

| Item | Why archived | Superseded by | Referenced by active code? | Safe to keep for traceability? |
|---|---|---|---|---|
| `archive/legacy_experiment_dir/`, `legacy_manual_scripts/`, `legacy_methodology_docs/` | Pre-pipeline-rebuild prototypes | Current `scripts/`/`results/` | No | Yes — keep, shows methodology evolution |
| `archive/legacy_results_dir/` (incl. `baseline_temp/`) | Early/duplicate pipeline runs, incl. real baseline CI mirrors (C1) | `results/execution_evidence/` | No | Yes — this is now known to be genuinely load-bearing evidence for the baseline claim; do not delete without extracting what it corroborates |
| `archive/*_20260726_171013.*` root dump | One-time archival timestamp export | Unclear/none | No | Yes, but rename/index for clarity |
| `archive/temp_files/`, `scratch/` | Ad hoc maintenance scripts | Each other (redundant) | No | Yes — consolidate location, don't delete content |

## 7. Delete Candidates

None identified with high confidence — everything reviewed is either currently referenced as evidence (however messily organized) or is the kind of legacy material a thesis defence benefits from retaining for "show your work" purposes. The 5 `.zip` files in `archive/` (`evidence_20260726_171013.zip` and 4 run-ID-suffixed variants) are plausible **candidates for deduplication** against `archive/legacy_results_dir/` if their contents are confirmed identical, but this was not exhaustively verified (time-scoped) — **do not delete without that verification.**

## 8. Evidence Verification Report (Pass 3, full)

See Sections 2 (C1, C2, C3, C4, C6, C7) above for the complete, resolved findings. Summary of the baseline-contradiction resolution specifically, since it was the seed finding: **the owner's original hypothesis (AF passed, JS failed) is not what the evidence shows.** What the evidence shows, established across three rounds of investigation:
1. No committed file inside `results/execution_evidence/` or `archive/` for any of the 18 scenarios shows an `ERESOLVE`/`ResolutionImpossible` failure.
2. A real, separate CI workflow (`grype-baseline.yml`) genuinely executed this exact experiment 36 times and is independently confirmable via GitHub's public API — so the claim is not fabricated from nothing.
3. But in 11/11 sampled real runs of that workflow, the failure occurs at a later build/test/rescan step, never at the package-manager resolution step the docs specifically describe.
Net: the baseline claim is **substantively different from, and weaker than, what is written** — real failures occurred, but not via the specific mechanism claimed, and the specific evidence is not reproducible from what's committed to the repository alone.

## 9. Broken References

- `README.md:225` → `progress-reports/` (does not exist; see Minor Issues).
- `scripts/run_deterministic_baseline.py` → `experiment/final_18_scenarios.json`, `documentation/deterministic_baseline_report.md` (neither path exists; C6).
- `README.md`'s key-documents table has no entry for `results/THESIS_DRAFT.md` (M7).

## 10. Grammar Corrections

See Minor Issues (UK/US mix) and Section 4. Not exhaustively line-edited across every document given the scope/time budget relative to the Critical findings; the spelling-consistency check is illustrative, not an exhaustive catalogue.

## 11. Pipeline Problems (Pass 6)

- Missing `set -o pipefail` across `generic-remediation.yml` (6 occurrences) and `grype-baseline.yml` (1+ occurrence) — the single highest-leverage fix available, since it likely explains multiple downstream metrics anomalies (C1, C4).
- `retry_remediation.py`'s stale `failure_stage` field (M2).
- `manifest_editor.py`'s flat-key override bug (M6).
- `run_deterministic_baseline.py`'s broken paths (C6).
- `experiment_manifest.json`'s SHA256 hashes fail to verify on any standard Windows checkout (M4).

## 12. Research Risks

- Pre-registration integrity: AF-06/JS-06 substitution (C2) is the single largest risk to the thesis's core "we didn't cherry-pick" claim.
- JS-09's misrecorded model + hidden prompt (C3) is a direct data-integrity problem in the one file meant to be the tamper-evident record.
- The retry loop (M1) changes what "success rate" means (two-shot vs. the single-shot design implied throughout) and is undisclosed.
- `THESIS_DRAFT.md`'s stale results table (M7) risks a supervisor or examiner citing numbers that don't match the actual dataset if this draft isn't clearly marked superseded.

## 13. Security Findings

Hardcoded GitHub PAT in 6 files (C5) — the only credential-exposure finding. `.gitignore` correctly lists `.env`; confirmed untracked in both checkouts (`git ls-files .env` empty). `.github/workflows/*.yml` correctly use `secrets.GEMINI_API_KEY` context, no hardcoded API keys found there. `*.zip` is gitignored but 5 zips remain tracked from before the rule was added (expected git behavior, not a bug, but worth knowing).

## 14. Reproducibility Risks

- `run_deterministic_baseline.py` cannot execute as committed (C6).
- The core baseline claim's primary evidence lives in a workflow whose full logs require GitHub authentication to retrieve (public metadata only is available without a token) — a reviewer without a token can get this far but no further.
- SHA256 artifact-integrity verification fails on a standard Windows git checkout (M4) absent a `.gitattributes`.
- `gh` CLI (vendored in `tools/gh_cli/`) refuses all operations, including public-repo reads, without authentication — a reviewer relying on the vendored tool alone would conclude nothing is verifiable, when in fact `curl` against the plain REST API works for metadata.

## 15. Data Lineage Findings

No live code path in `scripts/`/`tools/` reads from `archive/` — confirmed no runtime risk of legacy data mixing into current results. `preregistration/PRE_REGISTRATION_AMENDMENT.md:237` explicitly and correctly disclaims legacy-schema data ("0 of 18 scenarios have final validated data under the old schema being kept"). The only lineage risk is a human one: `archive/legacy_results_dir/baseline_temp/` is deep and repetitive enough that a reader could mistake an archived run for a current one without careful path-reading.

## 16. Documentation Drift Findings (Pass 13)

- `progress-reports/` referenced but absent (Minor).
- `results/execution_evidence/` called "golden... proving success" (M8) — overstated given the collected findings.
- `THESIS_DRAFT.md` unindexed and stale (M7).
- README's "17 executed / 17-17 rescan_success" claim contradicted by 18/18 in the actual data (C7).

## 17. Research Question Verdict (Pass 14)

*"Can an LLM generate dependency remediation strategies that resolve software supply chain vulnerabilities in cases where applying the scanner's recommendation directly fails?"*

**Verdict: INCONCLUSIVE from the evidence verifiable in and around this repository — neither proven nor disproven**, for two independent reasons: (1) the control condition (scanner's naive fix reliably fails at the package-manager level) is not verified as described — real CI history shows a different failure mechanism (install succeeds, later build/test fails); (2) the treatment condition (LLM succeeds) has at least one confirmed false positive (JS-03), one scenario with a misrecorded model and manipulated prompt (JS-09), two scenarios that don't match pre-registration (AF-06, JS-06), and a 78% undisclosed-retry rate on the npm side. The Python/Airflow side is comparatively clean (single-iteration, internally consistent, no false positives found). The honest, defensible claim the current evidence supports is much narrower than "0% vs. X% success" — closer to "an iterative, LLM-assisted pipeline reached a CVE-absent rescan state for most, not all, attempted scenarios, more reliably on the pip side than the npm side, with the underlying naive-fix failure mode being a build/compile issue rather than a package-manager resolution error."

**KEV sub-question: can be answered, and the thesis's own disclosure is accurate.** `kev_status: false` confirmed across all 18 scenarios, consistent with every doc that states this. No issue.

## 18. Final Repository Score (0-10)

| Dimension | Score | Rationale |
|---|---|---|
| Academic Quality | **3/10** | Sound research design on paper (enrichment signals, 4-gate validation, pre-registration intent), but undermined by an undisclosed model swap recorded incorrectly in its own manifest, an undisclosed prompt manipulation, and two scenarios substituted without amendment. |
| Technical Quality | **5/10** | Real, working SBOM/scan/LLM/CI integration with a genuine (if undisclosed) retry mechanism; undercut by a repeated pipefail bug, a flat-key override bug, and unrunnable baseline tooling. |
| Repository Organisation | **4/10** | Deep, messy `archive/`; a stray unindexed thesis draft in `results/`; three overlapping "misc scripts" locations. |
| Security | **3/10** | A live-format GitHub PAT committed in plaintext across 6 files is a serious, unresolved exposure. |
| Reproducibility | **3/10** | Core baseline claim's primary evidence sits behind GitHub auth outside this repo; the one script meant to reproduce it locally cannot run; integrity hashes don't verify on a standard checkout. |
| Documentation | **5/10** | Extensive and generally well-written, but with specific, checkable numeric/path inaccuracies and a stale draft chapter contradicting the live dataset. |
| **Overall Thesis Readiness** | **3/10** | See verdict below. |

## 19. Verdict

**NOT READY.**

This is not a "tidy up and resubmit" situation — several Critical findings go directly to scientific validity and academic integrity, not polish:
- C2 (two scenarios substituted without disclosure) and C3 (a manifest that misstates its own experimental condition, in the direction of matching the "official" configuration when it didn't) are the kind of findings a thesis committee treats as integrity issues, not formatting notes, regardless of whether they originated from rushed automation rather than intent.
- C1 (the central 0%-baseline claim's own described mechanism doesn't match sampled real CI history) undermines the comparison the entire thesis is built on.
- C5 (leaked credential) is an active, time-sensitive risk independent of the thesis itself.

None of these are unfixable, and the underlying idea and most of the engineering are legitimate — but "READY AFTER MINOR FIXES" would understate work that requires re-running/re-verifying core experimental claims and adding explicit disclosure, not just editing prose. A supervisor should see this report before the next full read-through of the thesis text.

---

## 20. Proposed Corrections — Methodology Docs (output only, not written to any other file)

- **`README.md` step 4** ("Try to fix the vulnerability the basic way... This fails"): revise to explicitly name `grype-baseline.yml` as the mechanism, cite that its actual observed failure mode is "install succeeds, subsequent build/test/rescan step fails" (not `ERESOLVE`/`ResolutionImpossible` package-manager rejection), and either commit representative raw logs into `results/execution_evidence/` or clearly cite the external, authenticated-only GitHub Actions run history as the evidence source.
- **`preregistration/PRE_REGISTRATION_AMENDMENT.md:186,192`**: replace "triggers a fatal `ERESOLVE`... immediately crashing the build" / "the resolver raises `ResolutionImpossible`... the build never starts" with language matching the sampled evidence (install succeeds; failure occurs at build/test/rescan).
- **`README.md:138`**: correct "17 executed scenarios... 17/17 rescan_success" to reflect the actual 18/18, or clearly identify and justify which scenario is excluded and why.
- **Any document describing the LLM protocol as single-pass**: add an explicit description of the retry/re-prompt loop (confirmed genuine), including its actual observed frequency (7/9 JS scenarios).
- **`results/THESIS_DRAFT.md` Chapter 3 table**: either regenerate from current `metrics.json` data or mark the whole document `STALE — SUPERSEDED, DO NOT CITE` at the top.
- **JS-09 specifically**: add an explicit note wherever the 18-scenario results are presented, disclosing the model discrepancy and the hidden-fixed-versions prompt, or exclude it from the "18 uniformly-treated scenarios" framing entirely and present it separately as intended by its own `"Supplementary Experiment"` label.

## 21. Proposed Folder READMEs (output only)

- **`archive/README.md`** (highest value addition): one paragraph explaining the `_20260726_171013` dump and the four `legacy_*` subfolders' purposes, a note that `baseline_temp/<run-id>/` folders mirror specific GitHub Actions runs of `grype-baseline.yml` (now confirmed genuine), and an explicit flag that the loose `.py` scripts here contain a credential requiring rotation.
- **`results/README.md`**: distinguish the canonical `scenarios/` + `execution_evidence/` (18-scenario dataset) from `THESIS_DRAFT.md` (draft chapter, currently stale — mark status).
- **`scripts/README.md`**: distinguish the live pipeline (`remediation/`, `baseline/`) from the ad hoc top-level utility scripts (`fix_*.py`, `rebuild_manifests.py`, etc.).
- **`tools/README.md`**: note these are vendored third-party binaries (Syft, Grype, gh CLI), not project code, and that `gh` requires authentication even for public-repo reads.

## 22. Proposed Root README Skeleton (output only)

```
llm-remediation-thesis-final/
├── applications/       Frozen source snapshots (Juice Shop v15.3.0, Airflow v2.9.2) + pre-registration scan evidence
├── archive/            Superseded prototypes, legacy pipeline runs, one-off scripts — see archive/README.md
├── docs/                Methodology chapters (numbered 01-08) + evolution/validation-protocol notes
├── preregistration/     Locked scenario definitions, selection methodology, amendment log
├── results/
│   ├── scenarios/       Canonical 18-scenario JSON database
│   ├── execution_evidence/  Per-scenario pipeline artifacts (SBOM, scan, LLM I/O, metrics, logs)
│   └── THESIS_DRAFT.md  [STATUS: STALE — see Section 20]
├── scripts/             Pipeline automation (remediation/, baseline/) + maintenance utilities
├── tools/               Vendored binaries: Syft, Grype, gh CLI
├── .github/workflows/   generic-remediation.yml (LLM pipeline), grype-baseline.yml (control-group pipeline)
└── 27-07-2026/          Dated progress note (README currently calls this "progress-reports/" — fix path)
```
