# `repository_commit` Correction (2026-08-03)

## 1. What was found

While verifying that the just-corrected `workflow_url` fields were now fully consistent, a second, related field was checked: `repository_commit`. Eight scenarios (`AF-05, AF-06, AF-07, AF-08, JS-05, JS-06, JS-07, JS-08`) carried the identical `repository_commit` (`241b549e07430f9520d1a116360ae194d1ba84f6`) — the real commit for AF-02's run, not their own.

## 2. Root cause

This is a direct consequence of the `workflow_url` bug (`docs/audit/workflow_url_provenance_correction_2026-08-03.md`), not a separate, independent error. The earlier "9 fabricated `repository_commit` hashes" fix (`docs/audit/docs_group_b_evaluation.md` Item 1, pre-freeze) queried each scenario's `head_sha` from whatever `workflow_url` was recorded for it at the time. For these 8 scenarios, that recorded `workflow_url` was already wrong (pointing at AF-02's run), so the "real" hash that fix correctly fetched was AF-02's real commit — a genuine, git-verified hash, but for the wrong run. The fix was procedurally correct (it replaced fabrication with a real, verified value) but operated on already-corrupted input.

## 3. Verification — two independent sources per scenario, per repository owner's requirement

For each of the 8 scenarios: (1) the corrected `workflow_run_id`'s own `head_sha`, queried directly from the GitHub Actions API; (2) independent cross-check that the recovered commit hash exists in this repository's git history, with a commit date preceding that run's `created_at`, in the correct chronological position relative to the surrounding commit/run sequence.

| Scenario | Previous `repository_commit` | Correct `repository_commit` | Source 1 (GH API `head_sha`) | Source 2 (git history) | Status |
|---|---|---|---|---|---|
| AF-05 | `241b549e...` | `796ba575b26a4038bd2393d9f09c6328f06661b1` | Run `30617428694` | Commit exists, dated 2026-07-31 08:44:34 UTC, 48s before run | ✅ |
| AF-06 | `241b549e...` | `796ba575b26a4038bd2393d9f09c6328f06661b1` | Run `30618200840` | Same commit, 14 min before run | ✅ |
| AF-07 | `241b549e...` | `d3766873fa30b70396cbdcc7c78f9cd203f0b3ed` | Run `30619246825` | Commit exists, ~4 min before run | ✅ |
| AF-08 | `241b549e...` | `15177533346e3240f5b419c9b7cf9568603b0664` | Run `30627246921` | Commit exists, same-day sequence before run | ✅ |
| JS-05 | `241b549e...` | `796ba575b26a4038bd2393d9f09c6328f06661b1` | Run `30617435445` | Same commit family as AF-05 | ✅ |
| JS-06 | `241b549e...` | `796ba575b26a4038bd2393d9f09c6328f06661b1` | Run `30618206648` | Same commit family as AF-06 | ✅ |
| JS-07 | `241b549e...` | `d3766873fa30b70396cbdcc7c78f9cd203f0b3ed` | Run `30619254609` | Same commit family as AF-07 | ✅ |
| JS-08 | `241b549e...` | `15177533346e3240f5b419c9b7cf9568603b0664` | Run `30627253658` | Same commit family as AF-08 | ✅ |

The recovered commits fall in strict chronological order (`241b549e` → `796ba575` → `d3766873` → `15177533`), each one's associated runs occurring after that commit and before the next — internally consistent across the whole sequence, not just per-scenario.

## 4. What changed and what did not

**Changed:** `repository_commit` field only, in both its JSON-body location and its duplicate copy in the `EMPIRICAL EVIDENCE` trailer — confirmed via diff to be exactly 4 lines per file (2 removed, 2 added), for all 8 files.

**Not changed:** artifact hashes, `metrics.json`, `llm-request.json`, `llm-response.json`, logs, and the already-corrected `workflow_commit`/`workflow_url` fields (fixed in the prior commit, not touched again here). Pre-correction state archived at `archive/repository_commit_correction_20260803_pre_state/`.

This does not affect any experimental result, metric, or conclusion — it corrects which specific commit the evidence's own provenance record cites, nothing about what the evidence itself contains.
