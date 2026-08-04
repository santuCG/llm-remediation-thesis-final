# Final Dataset Manifest — Pipeline v2.0

Canonical, single-table manifest for all 18 scenarios' final evidence. Every field below is
quoted directly from that scenario's own `results/execution_evidence/<ID>/experiment_manifest.json`,
`llm-request.json`, and `metrics.json` — none is inferred or reconstructed from logs. Use this
table instead of searching `REGENERATION_LOG.md` or CI logs when the question is simply "what
produced this scenario's evidence, and what was the outcome."

**Column definitions.**
- **Pipeline version** — `experiment_manifest.json.pipeline_version` (the orchestration code: `generic_remediation.py`, `prioritize.py`, `validator.py`, `retry_remediation.py`, `.github/workflows/generic-remediation.yml`).
- **Prompt version** — `llm-request.json.prompt_version` (the LLM system/user prompt and response schema, `scripts/remediation/llm_reasoner.py`; independent of pipeline version — see `scripts/remediation/prompts/PROMPT_CHANGELOG.md`).
- **Run ID** — the GitHub Actions `workflow_run_id` that produced this evidence, linked to its run page.
- **Commit SHA** — `repository_commit`, the repository state actually checked out for that run (short form; full SHA in each scenario's `experiment_manifest.json`).
- **Evidence SHA** — the SHA-256 of that scenario's `metrics.json` (`artifact_hashes."metrics.json"`, truncated to 12 hex chars here), i.e. a content fingerprint of the canonical result file. `N/A` where no `metrics.json` was produced.
- **Result** — `PASS (clean)` if `dependency_verified` and `rescan_success` are both `true`; otherwise the specific failure category from Table 4 of `THESIS_DRAFT_V3.md`.

## Table

| Scenario | Pipeline version | Prompt version | Run ID | Commit SHA | Evidence SHA | Result |
|---|---|---|---|---|---|---|
| AF-01 | v2.0 | v1.2 | [30948616416](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30948616416) | `5392ee7e` | `16a32ed11997` | PASS (clean) |
| AF-02 | v2.0 | v1.2 | [30865157364](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30865157364) | `8916b395` | `e66752aa4df9` | PASS (clean) |
| AF-03 | v2.0 | v1.2 | [30866015290](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30866015290) | `bfd07488` | `bf541f1893b1` | PASS (clean) |
| AF-04 | v2.0 | v1.2 | [30866826162](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30866826162) | `259d6b65` | `86a1eb1319a7` | PASS (clean) |
| AF-05 | v2.0 | v1.2 | [30875173695](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30875173695) | `857af446` | `398550153940` | PASS (clean) |
| AF-06 | v2.0 | v1.2 | [30942956346](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30942956346) | `36cc51fd` | `f4d5ee5a74ca` | PASS (clean) |
| AF-07 | v2.0 | v1.2 | [30943518765](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30943518765) | `36cc51fd` | `12ed5d689de3` | PASS (clean) |
| AF-08 | v2.0 | v1.2 | [30945587353](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30945587353) | `36cc51fd` | `59232f02836c` | PASS (clean) |
| AF-09 | v2.0 | v1.2 | [30948331316](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30948331316) | `febf62e0` | `979174def86a` | PASS (clean) |
| JS-01 | v2.0 | v1.2 | [30948623108](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30948623108) | `5392ee7e` | `28f302e2d33a` | PASS (clean signals; job-level `failure` is the known, unrelated `TS1005` build issue) |
| JS-02 | v2.0 | v1.2 | [30950066148](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30950066148) | `7ea29841` | `c61ebd3e7178` | PASS (clean signals; same `TS1005` note) |
| JS-03 | v2.0 | v1.2 | [30866019450](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30866019450) | `bfd07488` | `a2f54b3a4d3f` | PASS (clean signals; same `TS1005` note) |
| JS-04 | v2.0 | v1.2 | [30866830764](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30866830764) | `259d6b65` | `18f4d0326eda` | PASS (clean signals; same `TS1005` note) |
| JS-05 | v2.0 | v1.2 | [30875177735](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30875177735) | `857af446` | `1701131d8405` | PASS (clean signals; same `TS1005` note) |
| JS-06 | v2.0 | *N/A — never reached the LLM step* | [30941710255](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30941710255) | `a7606850` | *N/A — no `metrics.json` produced* | **Failure Category A** — SBOM cataloging limitation (`flatted` absent from Syft's SBOM); no candidate matched, pipeline correctly refused to substitute |
| JS-07 | v2.0 | v1.2 | [30943524500](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30943524500) | `36cc51fd` | `0eadee073411` | **Failure Category B** — pipeline applicability limitation (`ws`'s vulnerable copy lives in Juice Shop's independently-installed `frontend/` tree, outside `manifest_editor.py`'s reach) |
| JS-08 | v2.0 | v1.2 | [30948318473](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30948318473) | `febf62e0` | `288c48bd0c9a` | PASS (clean signals; same `TS1005` note) |
| JS-09 | v2.0 | v1.2 | [30948325107](https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30948325107) | `febf62e0` | `86fe3b78d1dd` | PASS (clean signals; same `TS1005` note) |

## Notes

- **All 18 rows share `pipeline_version: v2.0` and (where an LLM call occurred) `prompt_version: v1.2`** — this is the single, final, homogeneous pipeline state the dataset was generated under. No scenario in this table reflects an earlier pipeline or prompt version; scenarios that needed regeneration to reach this state (all 18, ultimately — see `REGENERATION_LOG.md`) were fully re-run, not patched in place.
- **Commit SHA reflects the code actually checked out for that specific CI run**, not the commit the evidence was later filed under. Several scenarios share a commit (e.g. AF-06/AF-07/AF-08/JS-07 all show `36cc51fd`) because they were dispatched back-to-back against the same repository state before the next fix (`febf62e0`, the Fix #11 range-prefix follow-up) landed — this is expected, not a data error.
- **16 of 18 scenarios are `PASS (clean)`.** The 9 npm `PASS` rows carry a job-level `failure` conclusion in GitHub Actions caused by a pre-existing, unrelated `TS1005` TypeScript compilation issue (§3.7 of `THESIS_DRAFT_V3.md`) — `dependency_verified`/`rescan_success` are unaffected and both `true` for all of them; this is noted per-row rather than silently normalized away.
- **Full CVE-level cross-check** (preregistered vs. executed target, for every scenario including the two negative results) is in `docs/CVE_MATCH_VERIFICATION.md` — this manifest and that table are companions: this one answers "what produced this evidence and did it pass," that one answers "did it target the right vulnerability."
- **Evidence SHA** is a fingerprint for integrity checking, not a substitute for reading `metrics.json` directly — it changes if the file changes even by one byte, so it can confirm two copies of a scenario's evidence are identical without a full diff.
