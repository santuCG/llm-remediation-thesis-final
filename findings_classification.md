# FINDINGS CLASSIFICATION — READ-ONLY PASS

Source: `audit_progress.md` (the final audit report), findings C1-C7 (Critical) and M1-M9 (Major).
No file was modified to produce this pass. One additional code-level check was performed (`scripts/remediation/generate_manifest.py:94`) because it directly changes the classification of C3 from "possible one-off" to "structural code bug" — this is disclosed inline rather than silently upgrading the finding.

---

FINDING: C1 — Baseline failure mechanism does not match documented ERESOLVE/ResolutionImpossible claim
CATEGORY: Documentation mismatch
EVIDENCE BASIS: Requires external evidence: GitHub API query (unauthenticated `GET /repos/santuCG/llm-remediation-thesis-final/actions/workflows/320934778/runs` and `/actions/runs/{id}/jobs`, 11 of 36 runs sampled). What would need to be imported into this repo as a committed file to make this repo-defensible on its own: the raw `build.log`/`test.log` (or at minimum a `jobs.json` step-conclusion export) for a representative sample of baseline runs, saved under e.g. `results/execution_evidence/baseline_reference/<run-id>/`.
REMEDIATION TYPE: Documentation only (rewrite `preregistration/PRE_REGISTRATION_AMENDMENT.md:186,192` to match the observed mechanism). Importing evidence (above) is not a code fix or a rerun — the runs already happened; it is an evidence-import step, listed separately in the Minimum Fix Set below.
REWRITTEN CONCLUSION: FACT: `grype-baseline.yml` genuinely executed 36 times on 2026-07-26, split 27 failure/9 success, confirmed via GitHub's public API. FACT: in 11 of 11 sampled runs, the step that installs the scanner's recommended version succeeded; the failure, where present, occurred at a later build/test/rescan step. FACT: `preregistration/PRE_REGISTRATION_AMENDMENT.md:186` states the npm failure mode is "a fatal `ERESOLVE unable to resolve dependency tree` error, immediately crashing the build," and `:192` states the PyPI failure mode is "`ResolutionImpossible`... the build never starts." INTERPRETATION: these two descriptions describe a different failure point (package-manager resolution) than the one observed in the sampled runs (later build/test/rescan). CANNOT DETERMINE: whether a genuine `ERESOLVE`/`ResolutionImpossible` occurred in any of the 25 unsampled runs, or whether the confirmed `tee`-without-`pipefail` bug in this same workflow (see M2/C4 mechanism) silently converted a real resolver failure into a false "success" at the install step — this requires the raw log text, which requires authentication not used in this audit.
VIVA DEFENSIBILITY: YES. The API query is reproducible by anyone (no auth needed for this level of data), the sample is consistent across all 11 runs checked including both ecosystems' scenario batches, and the one caveat (pipefail masking) is stated as an open question rather than papered over.

---

FINDING: C2 — AF-06 and JS-06's executed evidence does not match their pre-registered targets
CATEGORY: Repository bug (the mismatch itself, i.e. execution not matching the locked design). NOTE: the upstream *mechanism* that produced the bug is separately addressed in the dedicated "AF-06/JS-06 ROOT CAUSE" section below and is classified there as partially Cannot determine — this CATEGORY field describes the finding, not the mechanism.
EVIDENCE BASIS: Repo-only defensible. Files: `results/scenarios/final_18_scenarios.json` (pre-registered AF-06 = jinja2/CVE-2024-56326, JS-06 = flatted/CVE-2026-33228), `results/execution_evidence/AF-06/metrics.json` (executed = werkzeug/CVE-2024-34069), `results/execution_evidence/JS-06/metrics.json` (executed = lodash/CVE-2021-23337), and git commit `8d6d40e3` (traced via `git log --diff-filter=A -- results/execution_evidence/AF-06/` and `.../JS-06/`, both first appearing in this single commit with the mismatch already present — no prior version exists in history to compare).
REMEDIATION TYPE: Requires rerunning TWO scenarios — AF-06 (target: jinja2/CVE-2024-56326) and JS-06 (target: flatted/CVE-2026-33228) — against their actual pre-registered targets. Alternative, non-rerun remediation: a dated pre-registration amendment explicitly disclosing and justifying the substitution, if the current data is to be kept.
REWRITTEN CONCLUSION: FACT: the pre-registered and executed identities disagree for exactly 2 of 18 scenarios, verified programmatically against all 18. FACT: both AF-06 and JS-06's evidence folders were created in a single commit (`8d6d40e3`, 2026-07-31) with no earlier, differently-identified version in this repository's history. INTERPRETATION: because both files were created new (not modified from a prior correct state) in this repo's own history, the deviation most likely originated upstream of this repository — either in how the CI workflow was dispatched (wrong `target_cve` input) or in a local scenario-selection/aggregation step not preserved in a way that shows its logic — rather than as a documented, deliberate swap recorded in a later commit. CANNOT DETERMINE: the precise upstream mechanism from committed history alone (see dedicated section).
VIVA DEFENSIBILITY: YES for the mismatch itself (clean file-to-file comparison). The upstream-mechanism claim is appropriately hedged as interpretation, not fact, so it would survive hostile questioning without overreaching.

---

FINDING: C3 — JS-09's manifest misstates the LLM model used, and the code makes this a structural risk for every scenario
CATEGORY: Repository bug.
EVIDENCE BASIS: Split finding. (a) The underlying code defect is **repo-only defensible**: `scripts/remediation/generate_manifest.py:94` contains the literal, hardcoded line `"model": "gemini-2.5-flash",` — this field is never populated from the actual model string returned by the LLM call in `llm_reasoner.py`'s fallback loop (`models = [...]`). This alone proves the manifest's `llm.model` field is structurally incapable of reflecting a fallback event, for any scenario, independent of any external evidence. (b) Proving that this specific defect actually fired for JS-09 (i.e., that `gemini-3.6-flash` really was used) requires external evidence: the untracked `js09_pipeline_logs.txt` file (found only in a second, separately-cloned checkout, not part of the git repository) and the `santuCG/llm-remediation-thesis-final` remote's unmerged `test-js-09` branch (fetched via `git fetch`, not present in `origin`'s default clone history). What would need to be imported into this repo to make (b) repo-defensible on its own: the decoded raw log content as a committed file (e.g. `results/execution_evidence/JS-09/raw_ci_log.txt`), and a note reconciling it against the branch commit `b9cb78f9` already cited in `JS-09/experiment_manifest.json`'s own `repository_commit` field.
REMEDIATION TYPE: Pipeline code fix (make `generate_manifest.py` read the actual model string dynamically, e.g. from an environment variable or file written by `llm_reasoner.py` at call time) AND requires rerunning ONE scenario — JS-09 — under the intended, undisclosed-deviation-free protocol (real fixed-versions list, `gemini-2.5-flash`, no forced-retry framing on attempt 1) to produce a comparable 18th data point, or explicit disclosure if it is to remain a labeled supplementary result instead.
REWRITTEN CONCLUSION: FACT: `generate_manifest.py:94` hardcodes the model string; it does not read it from the actual API response. FACT: `JS-09/experiment_manifest.json`'s `repository_commit` field cites `b9cb78f9`, the exact commit on the unmerged `test-js-09` branch that changes the model fallback order to try `gemini-3.6-flash` first. FACT: the raw CI log for this run (decoded from `js09_pipeline_logs.txt`) records `Successfully retrieved response using model: gemini-3.6-flash` for both the first attempt and the retry. FACT: the same raw log shows `Fixed Versions: [HIDDEN INTENTIONALLY - YOU MUST DETERMINE THE SAFEST VERSION...]` in both prompts, matching the committed `llm-request.json`. INTERPRETATION: taken together, these establish that the manifest's `"gemini-2.5-flash"` entry for this scenario is not merely imprecise but factually contradicted by the run's own execution record. CANNOT DETERMINE: whether any other scenario besides JS-09 ever triggered the fallback path (the code bug means this cannot be ruled out purely from the other 17 manifests, though no other raw log was available to check, and no other scenario's `llm-response.json` reasoning text mentions a model change).
VIVA DEFENSIBILITY: YES, and this is the strongest-evidenced finding in the whole audit — a hardcoded line of code plus a self-citing commit hash plus a raw execution log all agree with each other and against the manifest.

---

FINDING: C4 — JS-03's `build_success: true` is a false positive
CATEGORY: Repository bug.
EVIDENCE BASIS: Repo-only defensible. Files: `results/execution_evidence/JS-03/build.log` (contains `npm error code EINVALIDTAGNAME`), `results/execution_evidence/JS-03/metrics.json` (`build_success: true`), `scripts/remediation/manifest_editor.py:27-29` (writes a flat, non-nested override key), `.github/workflows/generic-remediation.yml:88` (`npm install 2>&1 | tee ../../build.log || (...)` with no `set -o pipefail`), and the raw `AF-01/pipeline_logs/.../6_Phase 1...txt` log confirming the shell invocation is `bash -e {0}` (no `-o pipefail`).
REMEDIATION TYPE: Pipeline code fix (add `set -o pipefail` before the affected `run:` blocks in `generic-remediation.yml`; fix `manifest_editor.py` to nest scoped override paths) AND requires rerunning ONE scenario — JS-03 — to obtain a genuine result once both fixes are in place.
REWRITTEN CONCLUSION: FACT: `JS-03/build.log` contains a fatal, uncaught npm error. FACT: `JS-03/metrics.json` records `build_success: true` for the same run. FACT: `manifest_editor.py` writes the LLM's scoped-path package name (`"request > form-data"`) as a single flat JSON key rather than a nested object, which is what npm rejects. FACT: the workflow step that would catch this failure pipes through `tee` without `pipefail`, so the pipeline's reported exit status reflects `tee` (typically 0), not `npm install`. INTERPRETATION: these three facts together fully explain the false positive; no fabrication is implied or needed as an explanation.
VIVA DEFENSIBILITY: YES — every element is independently visible in committed files; the root cause chain is complete without needing any external evidence.

---

FINDING: C5 — Hardcoded GitHub Personal Access Token committed in 6 files
CATEGORY: Repository bug (closest available category; this is fundamentally a secrets-hygiene/security defect, not a functional-logic bug — noted explicitly since none of the six offered categories name "security exposure").
EVIDENCE BASIS: Repo-only defensible. `archive/check_status_20260726_171013.py:7`, `archive/compare_metrics_20260726_171013.py:3`, `archive/fetch_logs_20260726_171013.py:2`, `archive/poll_pipeline_20260726_171013.py:7`, `archive/scratch_fetch_runs_20260726_171013.py:2`, `archive/temp_files/get_artifacts.py:6`, each containing a hardcoded GitHub Personal Access Token (referenced here by file/line only — not reprinted), plus `git log -1 -- <path>` confirming commit `797562b2` as the introduction point.
REMEDIATION TYPE: Repository cleanup only, for the in-repo half of the problem (remove the token from these files and, if a clean history matters, rewrite git history and force-push — a destructive operation requiring the repo owner's explicit decision, not something this audit performs or recommends doing lightly). The other half of the remediation — **rotating/revoking the token on GitHub's own account settings** — is outside any of the six listed remediation types entirely, because it is an action on a system this repository does not control. Stated plainly so it isn't lost: file deletion alone, with or without history rewrite, does not revoke the credential.
REWRITTEN CONCLUSION: FACT: the string matches GitHub's classic PAT format exactly, in 6 named locations, committed in a specific, named commit. CANNOT DETERMINE (deliberately not attempted by this audit): whether the token is still valid — testing it would mean using a credential already flagged as compromised, which this audit will not do.
VIVA DEFENSIBILITY: YES for the exposure fact itself. The recommendation to rotate is not contingent on proving the token still works — the correct posture is to treat any committed credential as compromised regardless.

---

FINDING: C6 — `run_deterministic_baseline.py` cannot execute against the current repository layout
CATEGORY: Repository bug.
EVIDENCE BASIS: Repo-only defensible, and independently re-confirmed in a second checkout. `scripts/run_deterministic_baseline.py:9-12` (`scenarios_path = 'experiment/final_18_scenarios.json'`, `if not os.path.exists(scenarios_path): sys.exit(1)`), and direct confirmation that `experiment/` does not exist with content in either checkout audited (in the second checkout it exists as a fully empty directory).
REMEDIATION TYPE: Pipeline code fix (update the hardcoded paths to `results/scenarios/final_18_scenarios.json` and appropriate output locations under `results/`/`docs/`), then optionally re-run it to actually produce the missing baseline artifact described in C1.
REWRITTEN CONCLUSION: FACT: the script's required input path does not exist in either checkout examined. FACT: in the second checkout, `experiment/` exists as a directory but contains zero files. CANNOT DETERMINE: whether this script was ever runnable in some earlier repository layout that has since been restructured, or whether it was always aspirational/incomplete — no historical commit was found where `experiment/final_18_scenarios.json` exists.
VIVA DEFENSIBILITY: YES — this is a simple, directly reproducible "does the file exist" check, confirmed twice independently.

---

FINDING: C7 — README's "17 executed scenarios, 17/17 rescan_success" claim does not match the data
CATEGORY: Documentation mismatch.
EVIDENCE BASIS: Repo-only defensible. `README.md:138` vs. `rescan_success` field across all 18 `results/execution_evidence/*/metrics.json` (18/18 `true`, including `JS-09` which is `build_success: false`).
REMEDIATION TYPE: Documentation only.
REWRITTEN CONCLUSION: FACT: `README.md:138` states 17 scenarios were executed and 17 achieved `rescan_success: true`. FACT: all 18 committed `metrics.json` files show `rescan_success: true`. INTERPRETATION: the "17" figure appears to be stale, most plausibly written before JS-09 (or whichever scenario was originally intended as the 17th/18th) was added, and never updated. CANNOT DETERMINE: which scenario, if any, the original "17" was meant to exclude — no document anywhere reconciles this.
VIVA DEFENSIBILITY: YES — a direct count comparison, fully reproducible.

---

FINDING: M1 — Undisclosed LLM retry/re-prompt loop
CATEGORY: Documentation mismatch.
EVIDENCE BASIS: Repo-only defensible. `results/execution_evidence/JS-0{3,4,5,6,7,8,9}/metrics.json` (`retry_count: 1, llm_iteration: 2`) and the same scenarios' `llm-response.json` reasoning text explicitly referencing "the previous attempt failed"; absence of any retry/iteration/re-prompt language across `README.md` and `docs/*.md` (grepped, zero hits).
REMEDIATION TYPE: Documentation only.
REWRITTEN CONCLUSION: FACT: 7 of 9 JS scenarios' committed evidence shows a genuine second LLM attempt following a genuine first-attempt build failure (the JS-09 raw log independently confirms this is a real mechanism, not a fabricated field). FACT: no methodology document describes this loop. INTERPRETATION: presenting aggregate "success" numbers without disclosing that most of them required a second, failure-informed attempt describes a different (weaker, but still real) result than a single-shot design would.
VIVA DEFENSIBILITY: YES.

---

FINDING: M2 — Stale `failure_stage` field bug in the retry script
CATEGORY: Repository bug.
EVIDENCE BASIS: Repo-only defensible. `scripts/remediation/retry_remediation.py:64-71` (never resets `failure_stage` to `"none"` after a successful retry) and the resulting `build_success: true` / `failure_stage: "build"` co-occurrence in 7 of 9 JS `metrics.json` files.
REMEDIATION TYPE: Pipeline code fix (reset `failure_stage` to `"none"` on a successful retry outcome).
REWRITTEN CONCLUSION: FACT: the code path that would clear this field on success does not exist. FACT: the contradictory field pair appears in exactly the scenarios that underwent a retry. INTERPRETATION: this fully explains the anomaly as a stale-field bug, not a fabrication or a separate unexplained failure.
VIVA DEFENSIBILITY: YES.

---

FINDING: M3 — Templated/duplicated frontend build logs across 8 JS scenarios
CATEGORY: Cannot determine — state exactly what evidence would resolve it: independent confirmation of whether the Juice Shop Angular frontend bundle is genuinely insensitive to backend-only dependency version changes (e.g. crypto-js, lodash) such that identical webpack content hashes across differing dependency graphs would be *expected* rather than anomalous. This audit could not rule out that explanation, and did not have access to re-run the build with controlled inputs to test it directly.
EVIDENCE BASIS: Repo-only defensible for the raw *observation* (identical `Hash: eec0da7fb4f70cee` and byte-identical bundle sizes across `JS-01,02,04-09/build.log`, all committed, reproducible via `grep -E "Hash:|vendor.js" */build.log`). NOT repo-only defensible for the *conclusion* that this indicates templating/reuse rather than genuine build determinism — that requires either an independent rebuild with deliberately varied dependencies, or a reference (external) explanation of Angular/webpack's hashing behavior for this specific project configuration.
REMEDIATION TYPE: Requires rerunning ALL scenarios on the JS side with instrumentation added (e.g. logging the actual installed `crypto-js`/`lodash` version alongside the frontend build hash) to directly test whether the hash tracks the dependency change or not — this is the only way to convert this from an open question into a confirmed finding either way.
REWRITTEN CONCLUSION: FACT: the fingerprint (hash + bundle sizes) is identical across 8 scenarios' `build.log` files. CANNOT DETERMINE: whether this reflects genuine, expected build determinism (backend-only packages not being bundled into the frontend) or non-independent/templated log capture. This finding should be treated as an open question, not a confirmed defect, until the evidence above is gathered.
VIVA DEFENSIBILITY: NO, as currently framed in the "Major" severity of the original report. Under hostile questioning ("prove these logs are templated and not just deterministic"), this audit could not, with what's currently committed, definitively rule out the innocent explanation. **Recommend downgrading this from a stated Major finding to an explicitly-flagged open question** pending the evidence described above — the underlying observation (identical hashes) stays in the record as FACT; only the "templated/duplicated, therefore not independently captured" conclusion should be softened to CANNOT DETERMINE.

---

FINDING: M4 — Non-verifying SHA256 integrity hashes (missing `.gitattributes`)
CATEGORY: Repository bug.
EVIDENCE BASIS: Repo-only defensible. Absence of `.gitattributes` at repo root; `git config --get core.autocrlf` = `true` on this checkout; `git show HEAD:<path>` (LF) vs. working-tree file (CRLF) for a sampled artifact; declared hash in `experiment_manifest.json` matches `sha256(file.replace(CRLF,LF))` exactly.
REMEDIATION TYPE: Repository cleanup only (add a `.gitattributes` pinning `results/execution_evidence/**` to LF or binary as appropriate).
REWRITTEN CONCLUSION: FACT: no `.gitattributes` exists. FACT: the committed blob is LF; a standard Windows checkout with `autocrlf=true` (git's own recommended default) produces a CRLF working-tree copy. FACT: the declared hash matches the LF version, not the checked-out CRLF version. INTERPRETATION: this is a checkout/tooling gap, not evidence of tampering — the content is very likely unchanged, only line-ending bytes differ.
VIVA DEFENSIBILITY: YES.

---

FINDING: M5 — `.json`-named files that are not valid JSON
CATEGORY: Repository bug.
EVIDENCE BASIS: Repo-only defensible. `json.load()` failure on all 18 `experiment_manifest.json` (appended plaintext block) and all 9 Airflow `package-before.json`/`package-after.json` (plain-text `pip freeze` output).
REMEDIATION TYPE: Pipeline code fix (adjust the generation scripts — `append_evidence.py`/manifest-append tooling for the manifest issue; the AF-side evidence-capture step for the package-before/after issue — rather than a one-time manual rename, since these files are regenerated by scripts on each run).
REWRITTEN CONCLUSION: FACT, verified programmatically across all instances, no sampling involved.
VIVA DEFENSIBILITY: YES.

---

FINDING: M6 — `manifest_editor.py` does not handle nested/scoped override paths
CATEGORY: Repository bug.
EVIDENCE BASIS: Repo-only defensible. `scripts/remediation/manifest_editor.py:27-29`, cross-checked against `results/execution_evidence/JS-03/package-after.json`'s literal `"request > form-data"` key.
REMEDIATION TYPE: Pipeline code fix.
REWRITTEN CONCLUSION: FACT — this is the same code cited under C4; listed separately here because it is a standalone, independently fixable defect regardless of the pipefail issue.
VIVA DEFENSIBILITY: YES.

---

FINDING: M7 — `results/THESIS_DRAFT.md` is stale and unindexed
CATEGORY: Documentation mismatch.
EVIDENCE BASIS: Repo-only defensible. Direct comparison of its Chapter 3 results table against current `metrics.json` values for the same scenario IDs; absence from `README.md`'s key-documents table.
REMEDIATION TYPE: Documentation only.
REWRITTEN CONCLUSION: FACT for every specific table-cell comparison performed (AF-06/JS-06 identities match pre-registration rather than execution, consistent with this document predating commit `8d6d40e3`; most "Failed" LLM-outcome cells contradict current `build_success`/`rescan_success: true` values). INTERPRETATION: this reads as an abandoned/superseded draft rather than a maintained one, given the mismatch is total rather than partial.
VIVA DEFENSIBILITY: YES.

---

FINDING: M8 — README's "golden execution evidence... proving the automated POC succeeded" is overstated
CATEGORY: Thesis wording issue.
EVIDENCE BASIS: Repo-only defensible as a synthesis of C1-C7/M1-M7, all of which are independently repo-defensible or clearly marked where they are not.
REMEDIATION TYPE: Documentation only.
REWRITTEN CONCLUSION: INTERPRETATION (explicitly, not FACT): "golden" and "proving success" are value-laden characterizations; the underlying facts (C1-C7, M1-M7) support a more qualified description. This finding is a framing critique, not an independent factual claim, and should be read as such.
VIVA DEFENSIBILITY: YES, provided it is presented as interpretation/framing critique rather than as a standalone factual finding — which is how it is now labeled.

---

FINDING: M9 — `THESIS_DRAFT.md`'s attribution of JS-03's failure to "the LLM hallucinated Yarn resolutions syntax"
CATEGORY: Thesis wording issue.
EVIDENCE BASIS: Repo-only defensible. `results/THESIS_DRAFT.md:70` vs. `results/execution_evidence/JS-03/llm-response.json` (the LLM's actual stated intent) vs. `manifest_editor.py:27-29` (the apply-layer's handling of that intent).
REMEDIATION TYPE: Documentation only.
REWRITTEN CONCLUSION: FACT: the LLM's `manifest_patch.package` field value was `"request > form-data"`, plain text describing a scoped path, not Yarn-specific syntax token-for-token. FACT: the apply-layer code does not parse or nest this. INTERPRETATION: attributing the resulting failure primarily to "LLM syntax fidelity" rather than to the apply-layer's handling is a defensible-but-contestable framing choice — reasonable reviewers could weigh this differently, which is why this remains a wording issue rather than a factual-error finding.
VIVA DEFENSIBILITY: YES, precisely because it's presented as a contestable interpretation rather than an assertion that the thesis is "wrong."

---

## JS-09 OFFICIAL STATUS

Grepped `README.md`, all of `docs/`, all of `preregistration/`, `results/THESIS_DRAFT.md`, `SCENARIOS_LIST.md`, `CHANGELOG.md` for "JS-09" and for "17 scenarios"/"18 scenarios"/"17/18"/"18/18" style counts.

**Is JS-09 currently counted in any stated total anywhere?** Yes. `README.md:61` lists "Juice Shop | JS-01 to JS-09 | npm" as part of the 18. `README.md:64,175,176,179,203` and every "18 scenarios" reference in `preregistration/MASTER_METHODOLOGY_RECORD.md`, `preregistration/PRE_REGISTRATION_AMENDMENT.md`, and `preregistration/README.md` treat all 18 (implicitly including JS-09) as one undifferentiated set. `SCENARIOS_LIST.md:17` and `preregistration/scenario_selection_log.md` both list JS-09 identically to every other scenario, with no annotation. `results/THESIS_DRAFT.md:90` lists it as "Pending | Pending" (this draft predates JS-09's execution entirely).

**Is it described as "supplementary" anywhere a reader would see it (not just its own manifest's internal field)?** No. The only occurrence of the word "supplementary" adjacent to JS-09 in any form is: (a) the git commit message `b2227787 "docs(evidence): add JS-09 supplementary experiment results"` (visible only via `git log`, not in any rendered document), and (b) the internal `"experiment_id": "Supplementary Experiment"` field inside `results/execution_evidence/JS-09/llm-request.json` (visible only by opening and parsing that specific raw JSON file). `docs/05-results-and-discussion.md` does contain the word "supplementary," but in an unrelated sentence about Grype-finding diff analysis, not about JS-09's status.

**Conclusion, from what's written only, no inference:** JS-09 is presented, in every reader-facing document, as an ordinary member of the 18 pre-registered scenarios. Its internal, non-reader-facing labeling as a "Supplementary Experiment" does not surface anywhere a reader consulting the README, docs, or pre-registration materials would encounter it.

---

## AF-06 / JS-06 ROOT CAUSE

Traced via `git log --follow --diff-filter=A -- results/execution_evidence/AF-06/` and `.../JS-06/`: both scenario folders were created in their entirety, for the first time, in a single commit — `8d6d40e3`, "Fix workflow_commit and add workflow_url to experiment_manifest.json and re-append EMPIRICAL EVIDENCE block to all scenarios," 2026-07-31 11:24:47 +0200, author `santuCG`. `git show --stat 8d6d40e3` confirms the commit's actual diff, despite its "to all scenarios" wording, is scoped almost entirely to these two scenarios (13 new files each) plus a 4-line edit to `results/THESIS_DRAFT.md`. `git show 8d6d40e3^:results/execution_evidence/AF-06/metrics.json` (and the JS-06 equivalent) both error with "exists on disk, but not in" the parent commit — there is no earlier, differently-identified version of either file anywhere in this repository's history to compare against or to have been "swapped from."

Evaluating the five options:
- **(a) wrong folder/upload mapping:** consistent with the evidence for AF-06 specifically — its executed identity (werkzeug/CVE-2024-34069) is an exact duplicate of AF-09's, which is the kind of outcome a copy-paste or mislabeled-artifact-upload error into the wrong scenario folder would produce.
- **(b) a scenario-selection script bug:** consistent with the evidence for JS-06 specifically — its executed identity (lodash/CVE-2021-23337) is not a duplicate of any other locked scenario, but does appear in `JS-03/candidate-ranking.json`'s discovery pool, consistent with a selection script reading from the broader candidate pool instead of the locked `final_18_scenarios.json` entry for this one slot.
- **(c) a pre-registration document that was never updated after a deliberate swap:** **not supported** — there is no earlier commit establishing a "correct," pre-registration-matching version of either scenario that was later replaced; the mismatched version is the only version that has ever existed in this repo.
- **(d) something else:** cannot be ruled out (e.g., a GitHub Actions `workflow_dispatch` triggered with the wrong `target_cve` input value, which would be invisible from repository files alone and would require the actual dispatch-event history from GitHub's API to check — not attempted in this pass).
- **(e) cannot determine:** applies to the precise upstream trigger in both cases.

**Verdict:** AF-06 and JS-06 most likely have **two different, non-identical mechanisms** (a duplicate-target error for AF-06, a wrong-source-pool selection error for JS-06), both occurring upstream of this repository (at dispatch time or in an unpreserved local script), both first landing in this repo already mismatched, in a single late commit. This is stated as the most evidence-consistent reconstruction, not a proven mechanism — the audit does not have direct access to the workflow-dispatch trigger history or any local script's runtime state that would confirm either explanation over the other.

---

## BASELINE CLAIM: EXACT WORDING COMPARISON

**`preregistration/PRE_REGISTRATION_AMENDMENT.md:186`** (npm/ERESOLVE):
> "All nine npm scenarios exited with code 1. Modern npm (v8+) enforces strict peer dependency checks. When `npm install <package>@<version>` is run for a nested package, the package manager detects a conflict between the requested version and the constraints defined by the parent package in the root `package-lock.json`. This triggers a fatal `ERESOLVE unable to resolve dependency tree` error, **immediately crashing the build**."

**`preregistration/PRE_REGISTRATION_AMENDMENT.md:192`** (PyPI/ResolutionImpossible):
> "All nine PyPI scenarios exited with code 1. Apache Airflow enforces strict version constraints across its dependency tree. When pip attempts to install a newer version of a package than the constraints allow, the resolver raises `ResolutionImpossible` and fails immediately. **The build never starts.**"

**`README.md:66-67`**:
> "npm failures: `ERESOLVE` — peer dependency conflict, package manager rejects the installation"
> "PyPI failures: `ResolutionImpossible` — strict version bounds in the constraints file prevent the upgrade"

**Exact behavior implemented by `grype-baseline.yml`, in order** (quoting the step names and their function directly from the workflow file):
1. `Phase 1 - Establish Baseline & Install Dependencies` — installs the *existing, currently-pinned* `requirements.txt`/lockfile (the known-vulnerable state), not the recommended fix.
2. `Phase 2 - Generate SBOM & Scan` — Syft + Grype against that baseline.
3. `Phase 3 & 4 - Apply Grype Recommendation (Logged)` — runs `update_manifest.py` then `npm install` / `pip install --no-deps -r requirements.txt` against the scanner-recommended version. (Sampled via GitHub API: this step's conclusion is `success` in 11 of 11 runs checked.)
4. `Phase 5 - Build / Tests / Rescan` — runs `npm run build:frontend`/`build:server`/`test` (npm) or `pytest tests/core` (Python) if present, then re-scans and runs `validator.py` to confirm CVE eradication. (Sampled via API: this is the step whose conclusion is `failure` in every sampled failing run.)

**Comparison:** the documentation describes the failure as occurring *at* step 3 (the package manager itself refusing to resolve/install — "immediately crashing," "never starts"). The workflow's own step structure and the sampled run outcomes place the failure at step 4, *after* step 3 has already reported success. These are not two readings of ambiguous language — the documentation names a specific, different failure point (dependency resolution) than what the workflow's step boundaries and the sampled step-level conclusions show (build/test/rescan, after resolution already succeeded). Stated as a comparison only: **the two descriptions do not agree on which phase fails**, for the 11 runs checked; whether they agree for the other 25 runs is not established either way.

---

## RETRY LOOP: PRE-REGISTRATION STATUS

Searched all of `preregistration/` (every file: `MASTER_METHODOLOGY_RECORD.md`, `PRE_REGISTRATION_AMENDMENT.md`, `protocol.md`, `README.md`, `JUICESHOP_PREREGISTRATION.md`, `scenario_selection_log.md`, and any others present) for "retry," "re-prompt," "reprompt," "iteration," "second attempt," "multi-attempt," "attempt 2."

**Result:** the only match anywhere in `preregistration/` is `JUICESHOP_PREREGISTRATION.md:290`, an unrelated note about retrying NVD REST API calls after HTTP 429 rate-limit responses — nothing to do with LLM remediation attempts. `preregistration/protocol.md:71-83` ("Phase 3: LLM Execution") describes the experimental condition as a single request/response cycle: "The LLM receives a structured input payload... It returns a JSON response with its recommended action and version." No branching, retry, or multi-attempt language appears anywhere in this description.

**Conclusion: retrying was not pre-registered. It is silent — neither described nor prohibited — in every locked methodology document.** It is also not described in any post-hoc amendment (`PRE_REGISTRATION_AMENDMENT.md` covers the Ghost CMS removal and the ecosystem-split restructure, not the LLM-execution protocol's retry behavior).

**Does this change what the "success rate" numbers mean relative to what was pre-registered?** Yes. The pre-registered design describes one LLM call per scenario, evaluated once. The actual, genuinely-executed pipeline (confirmed via the JS-09 raw log, not just inferred from metrics fields) gives 7 of 9 JS scenarios a second, failure-informed attempt before recording a result. A reported "success" under the pre-registered single-shot design and a reported "success" under the actual two-shot design are not measuring the same thing; the pre-registration does not license aggregating them without disclosing which scenarios needed the second attempt.

---

## EVIDENCE IMMUTABILITY LIST

**NEVER EDIT** (historical evidence — touching these without an actual rerun would falsify the record):
- Every file under `results/execution_evidence/<SCENARIO>/` for any scenario not being deliberately rerun: `baseline-grype.json`, `baseline-sbom.json`, `build.log`, `candidate-ranking.json`, `experiment_manifest.json`, `llm-request.json`, `llm-response.json`, `metrics.json`, `package-after.json`, `package-before.json`, `rescan.json`, `selected-candidate.json`, `test.log`.
- `results/execution_evidence/manual_baselines/JS-01_manual_remediation.diff`.
- `archive/**` (historical/legacy runs — editing these to "fix" them would misrepresent what actually happened at the time; if a file here must change for security reasons — the leaked token, C5 — that is a deletion/history-rewrite decision for the owner, not an edit-in-place "fix").
- `js09_pipeline_logs.txt` (raw log; if imported into the repo per C3's remediation, it must be imported verbatim, not edited).
- Any GitHub Actions run history, job logs, or artifacts (external to this repo entirely; not ours to edit under any circumstance).

**MAY UPDATE** (documentation — describing current or intended behavior, not asserting a specific run's outcome):
- `README.md`, all of `docs/`, `preregistration/*.md` (methodology/wording, not the locked scenario definitions themselves — see note below), folder-level `README.md` files (proposed or existing), `CHANGELOG.md`, `SCENARIOS_LIST.md` (if a scenario is genuinely rerun and its identity needs updating to match), `results/THESIS_DRAFT.md` (draft, explicitly not evidence).
- **Note on `preregistration/final_18_scenarios.json` / `results/scenarios/final_18_scenarios.json` specifically:** these are borderline — they are the *locked pre-registration record*, not narrative documentation, and are meant to be immutable by design (that is the entire point of pre-registration). They belong in **NEVER EDIT** in spirit; the correct fix for C2 is not to edit this file to match what was executed, but to either amend it via a dated, disclosed pre-registration amendment (adding new text, not silently changing the original entries) or to rerun AF-06/JS-06 to match what's already locked.

**Cross-check against the Minimum Fix Set below:** every remediation proposed anywhere in this document either (a) touches only files in the MAY UPDATE list, (b) proposes rerunning a specific named scenario (which produces new files under a scenario folder — not an edit of the existing ones, which stay in place until the rerun's output is deliberately substituted in with disclosure), or (c) proposes a pipeline code fix (which lives in `scripts/`/`.github/workflows/`, not evidence). No proposed remediation requires editing a NEVER EDIT file without an accompanying rerun. **No reclassification needed.**

---

## MINIMUM FIX SET

Grouped by REMEDIATION TYPE. This is the smallest set of changes such that no remaining Critical finding fails its own viva-defensibility test.

**Documentation only:**
1. Correct `README.md:138` to state 18/18 (or explicitly name and justify whichever scenario is excluded) — resolves C7.
2. Correct `preregistration/PRE_REGISTRATION_AMENDMENT.md:186,192` to describe the failure as occurring at build/test/rescan, not at package-manager resolution — resolves C1's documentation half (pairs with evidence import, below).
3. Add explicit disclosure of the retry/re-prompt loop's existence and observed frequency to `README.md`'s methodology description — resolves M1.
4. Mark `results/THESIS_DRAFT.md` as stale/superseded at the top, or regenerate its Chapter 3 table from current data — resolves M7 (and softens M8/M9 by removing the specific contestable claims from a document presented as current).
5. Add a dated pre-registration amendment note addressing AF-06/JS-06 (if their current data is to be kept rather than rerun) — partially resolves C2 as an alternative to a rerun.
6. Add explicit, reader-facing disclosure of JS-09's deviations (model, hidden prompt) wherever the 18-scenario results are presented, or explicitly carve it out of the "18" framing — resolves the documentation half of C3.

**Pipeline code fix:**
7. Add `set -o pipefail` (or equivalent explicit exit-code checks) to every `... | tee ...` step in `.github/workflows/generic-remediation.yml` and `grype-baseline.yml` — resolves C4's and (partially) C1's mechanism, and M2 is independent of this but should be fixed alongside.
8. Fix `scripts/remediation/retry_remediation.py` to reset `failure_stage` to `"none"` on a successful retry — resolves M2.
9. Fix `scripts/remediation/manifest_editor.py` to nest scoped/transitive override paths instead of writing them as flat keys — resolves M6 (part of C4's chain).
10. Fix `scripts/remediation/generate_manifest.py:94` to read the actual model used at runtime instead of a hardcoded string — resolves the structural half of C3, independent of whether JS-09 itself is rerun.
11. Fix `scripts/run_deterministic_baseline.py`'s hardcoded `experiment/`/`documentation/` paths — resolves C6.

**Repository cleanup only:**
12. Add a `.gitattributes` pinning `results/execution_evidence/**` to consistent line endings — resolves M4.
13. Remove the leaked token from the 6 named files (and decide separately, with the owner's explicit input, whether a full history rewrite is warranted) — resolves the in-repo half of C5. **Rotate the token on GitHub regardless — this is outside repo scope entirely and should not wait for anything else on this list.**

**Requires rerunning ONE scenario:**
14. **JS-03** — after fixes #7 and #9, to obtain a genuine (not falsely-positive) result.
15. **JS-09** — after fix #10, under the undisclosed-deviation-free protocol (or keep as an explicitly-labeled supplementary result per #6, in which case a rerun is optional rather than required).

**Requires rerunning scenarios by name (not "all"):**
16. **AF-06 and JS-06** — against their actual pre-registered targets (jinja2/CVE-2024-56326 and flatted/CVE-2026-33228), unless remediated via #5 instead.

**Evidence import (not a code fix, not a rerun — a one-time addition of already-existing external evidence into the repo):**
17. Import representative raw logs / job-step conclusions for a sample of the 36 `grype-baseline.yml` runs into `results/execution_evidence/baseline_reference/` — needed for C1 to become fully repo-defensible on its own, without relying on this audit's external GitHub API queries being re-run by a future reader.

**Open question, not yet a fix (requires new evidence before any remediation type applies):**
18. Resolve M3 (templated frontend build logs) by re-running with instrumentation that logs the actual bundled dependency version alongside the build hash — until then, M3 should be carried as a flagged open question, not a stated Major defect.

**Nothing outside items 1-18 is in scope for the next write-enabled pass.**
