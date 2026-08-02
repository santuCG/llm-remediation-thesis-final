# Pre-Correction State — `repository_commit` Correction (2026-08-03)

These 8 `experiment_manifest.json` files are the exact pre-correction state of `results/execution_evidence/{AF-05,06,07,08,JS-05,06,07,08}/experiment_manifest.json`, preserved before correcting their `repository_commit` field.

**What was wrong:** all 8 files carried the identical `repository_commit` (`241b549e07430f9520d1a116360ae194d1ba84f6`) — AF-02's real commit, not their own.

**Root cause:** the earlier "9 fabricated `repository_commit` hashes" fix (`docs/audit/docs_group_b_evaluation.md`, pre-freeze) queried the `head_sha` of the `workflow_url` recorded at the time for these scenarios — which was itself wrong (see `docs/audit/workflow_url_provenance_correction_2026-08-03.md`), pointing to AF-02's run rather than each scenario's own. That earlier fix correctly replaced a *fabricated* hash with a *real* one, but the real one it fetched was for the wrong run, because the wrong run was the only one available to query at the time.

**Recovery method:** now that each scenario's true `workflow_run_id` is known and corrected, each one's genuine `head_sha` was queried directly from the GitHub Actions API for that specific run, then independently cross-checked against git history: each recovered commit was confirmed to exist, with a commit date that precedes its corresponding run's `created_at` and falls in the correct chronological position relative to the other commits and runs in this sequence (two independent sources, per the repository owner's request).

**What did not change:** artifact hashes, metrics, prompts, responses, logs, and the already-corrected `workflow_commit`/`workflow_url` fields were not touched — confirmed via diff (exactly 4 lines changed per file: 2 removed, 2 added, both being the same `repository_commit` field in its two locations).
