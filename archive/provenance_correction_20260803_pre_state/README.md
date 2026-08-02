# Pre-Correction State — `workflow_url`/`workflow_commit` Provenance Fix (2026-08-03)

These 13 `experiment_manifest.json` files are the exact pre-correction state of `results/execution_evidence/{AF-03,04,05,06,07,08,JS-02,03,04,05,06,07,08}/experiment_manifest.json`, preserved before correcting their `workflow_commit`/`workflow_url` fields.

**What was wrong:** all 13 files carried the identical, incorrect value (`workflow_commit: 30592634834`, pointing to AF-02's real CI run) instead of each scenario's own actual run.

**Root cause:** a hardcoded, hand-authored `SCENARIO_PROVENANCE` lookup table in `scripts/rebuild_manifests.py` (introduced 2026-07-31, commits `8d6d40e309`/`15177533346e`) copy-pasted AF-02's run ID into most other scenarios' entries instead of each one's genuine `GITHUB_RUN_ID`. The live, per-run generation code (`scripts/remediation/generate_manifest.py`) is correct by construction; this hardcoded post-hoc "rebuild" table is where the error was introduced.

**Recovery method:** each scenario's true run ID was independently confirmed via two signals: (1) the actual `[PRIORITIZE] Selected Top Candidate` package name in that run's own CI log matches the scenario's own `metrics.json.selected_package` exactly, and (2) the run's internal timestamp falls within seconds to under a minute of that scenario's own recorded `epss_timestamp`. Full mapping and evidence: see the corresponding audit report in `docs/audit/`.

**What did not change:** `metrics.json`, `llm-request.json`, `llm-response.json`, `build.log`, `test.log`, `rescan.json`, `selected-candidate.json`, and `candidate-ranking.json` were not touched by this correction — only the `workflow_commit`/`workflow_url` fields (and their duplicate copy in the `EMPIRICAL EVIDENCE` trailer) inside `experiment_manifest.json` were corrected, confirmed via diff (exactly 8 lines changed per file: 4 removed, 4 added, all four occurrences of the same field pair).
