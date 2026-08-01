# JS-09 RERUN — SUMMARY

**Why:** JS-09's evidence was the only one of 18 scenarios missing its `EMPIRICAL EVIDENCE` trailer block, and its `package-before.json` showed the same "already-fixed-version" contamination documented for other scenarios in Phase 4. Per your earlier direction, JS-09 was regenerated exactly like the other 17, using the pipeline as it exists after this session's reproducibility fixes.

**Archived, not deleted:** the pre-rerun evidence is preserved verbatim at `archive/JS-09_pre_rerun_evidence_20260802_012547/` (with its own README explaining why), so the change is traceable rather than silently overwritten.

## Provenance of the new evidence

- Generated via one real `generic-remediation.yml` dispatch (run `30723203247`, commit `d0748e0ac94fe75227d3c57303dfc59ffac78692` — verified to exist in git history).
- `experiment_manifest.json` was produced entirely through the normal tooling: `generate_manifest.py` wrote the clean JSON header during the CI run itself (confirmed by inspecting the raw CI artifact before any local processing — no `EMPIRICAL EVIDENCE` trailer present at that point, genuine `repository_commit`/`workflow_run_id`/`workflow_url`, no fabrication). `rebuild_manifests.py`'s `process_scenario("JS-09")` function was then invoked directly (not the full script, which iterates all 18 scenarios) to add the `EMPIRICAL EVIDENCE` trailer — confirmed via `git status` that this touched **only** JS-09's manifest, no other scenario. No manual editing of any field at any point.

## Files: added / changed

| | Old (archived) | New |
|---|---|---|
| File count | 13 | 16 |
| Added | — | `dependency-graph.log`, `grype-db-metadata.json`, `llm-response-full.json` (this session's Group A additions, now flowing through to every future run including this one) |
| Changed | — | All 13 original files' *content* changed (genuinely fresh LLM call, fresh scan, fresh timestamps — this is a new experiment run, not an edit) |

## Provenance fields

| Field | Old | New |
|---|---|---|
| `repository_commit` | `b9cb78f9f535eaef4a76d820a0541702dec4a5dc` (genuine commit, but paired with a `workflow_url` pointing to a different run — an inconsistency, though not the same fabrication pattern as the 9 hashes fixed in this session) | `d0748e0ac94fe75227d3c57303dfc59ffac78692` (genuine, verified, and consistent with its own `workflow_url`) |
| `workflow_commit` | `None` (missing) | `30723203247` (populated) |
| `EMPIRICAL EVIDENCE` trailer | Absent | Present |

## Target CVE detection / remediation outcome

**Unchanged in substance — the fix worked both times.** `dependency_verified: true` and `rescan_success: true` in both the old and new evidence. Old and new both used the retry mechanism (`retry_count: 1`) and both correctly resolved `multer`/`GHSA-5528-5vmv-3xc2` (`CVE-2026-3520`).

## Metrics that changed, and why

| Field | Old | New | Why |
|---|---|---|---|
| `remediation_type` | `"Transitive Override"` | `"Direct Upgrade"` | Old value **contradicted** its own `strategy: "direct_upgrade"` — a stale-label bug from an earlier retry-sync issue (already root-caused and fixed in code prior to this session). New value is now internally consistent. |
| `build_success` | `false` | `true` | The universal `build_success` regression fixed in this session (#61) — the retry's install genuinely succeeded and is now correctly recorded as such. |
| `test_success` | `false` | `null` | No test suite runs on the retry path; now correctly recorded as "not executed" instead of a misleading `false`. |
| `runtime_success` | `false` | `null` | No runtime-check stage exists in this pipeline at all; now correctly `null` instead of misleading `false`. |
| `failure_stage` | `"build"` | `"none"` | Old value was frozen from Attempt 1's failure handler; new value correctly reflects the retry's actual successful outcome. |
| `candidate_count` | `111` | `134` | Reflects the total vulnerability count in a fresh baseline scan taken a day later — ordinary package-registry/Grype-DB drift over time, not a defect (see Phase 5's documented Grype-DB timing findings for the general mechanism). |
| `execution_time_seconds` | `45` | `10` | This field measures only Attempt 1's orchestration phase (documented limitation, #60) — not a regression, just normal run-to-run variance in that narrow window. |

## Net effect

JS-09 now has the same evidence schema, same `EMPIRICAL EVIDENCE` trailer, and the same fixed-pipeline metrics semantics as the other 17 scenarios. Its remediation outcome (CVE resolved via retry) is unchanged from before. The one caveat already flagged in `docs/audit/docs_group_b_evaluation.md` item 3 stands: JS-09 was generated under today's fixed pipeline, not the exact pipeline state that produced the other 17 — this should be disclosed alongside the thesis's methodology section, not hidden.
