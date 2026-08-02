# Workflow URL Provenance Correction (2026-08-03)

## 1. What was found

`THESIS_LIMITATIONS.md` Item 5 stated: *"Eight scenarios (AF-05/06/07/08, JS-05/06/07/08) share one CI `workflow_url`... AF-09 and all other scenarios have uniquely-attributable provenance."*

Direct inspection of all 18 `experiment_manifest.json` files found this understated the problem: **13 scenarios** (`AF-03,04,05,06,07,08`, `JS-02,03,04,05,06,07,08`) — not 8 — carried the identical `workflow_url`/`workflow_commit` (`30592634834`), which independently verified as **AF-02's own genuine CI run** (dispatched with `TARGET_CVE=CVE-2025-43859`, matching h11). `AF-03` and `JS-02`, previously described as "uniquely-attributable," were also affected.

## 2. Root cause — proven, not inferred

**Where `workflow_url` is correctly populated:** `scripts/remediation/generate_manifest.py:46-51` reads `os.environ.get('GITHUB_RUN_ID')` — GitHub's own unique-per-run identifier — at the moment a manifest is generated live during CI. This path cannot produce a duplicate across different runs by construction.

**Where it went wrong:** `scripts/rebuild_manifests.py` contains a hand-authored, static `SCENARIO_PROVENANCE` dictionary (lines 27-245) that was used to *rebuild* all 18 manifests post-hoc (git history: introduced in commits `8d6d40e309`/`15177533346e`, 2026-07-31 11:24-11:25, *"Fix workflow_commit and add workflow_url to experiment_manifest.json... to all scenarios"*; reapplied in `987d1e4500`, same day 15:07, *"chore: rebuild all experiment manifests"*). Whoever authored this table correctly varied `repository_commit` per scenario but left `workflow_commit`/`workflow_url` at the AF-02 value for most entries — a copy-paste error. Internal proof: `AF-07`'s own `repository_commit` differs from `AF-02`'s in this same table, yet both were assigned the identical `workflow_url` — impossible if genuinely from the same run.

**Confirmed NOT a design decision.** There is no "parent orchestration" concept anywhere in this codebase; `generic-remediation.yml` dispatches exactly one scenario per invocation.

**Confirmed metadata-only.** For every affected scenario, `metrics.json`, `llm-request.json`, `llm-response.json`, `build.log`, `test.log`, and `rescan.json` were verified to contain genuinely distinct, scenario-correct content (matching each scenario's own pre-registered package/CVE exactly), added in a single commit with no subsequent modification. No experimental result is affected.

## 3. Recovery method and full mapping

Each true run ID was independently confirmed via **two signals**: (a) the run's own `[PRIORITIZE] Selected Top Candidate` log line matches the scenario's `selected_package` exactly, and (b) the run's internal timestamp falls within seconds to under a minute of that scenario's own `epss_timestamp`.

| Scenario | Wrong value (pre-correction) | Corrected value | Confidence | Verification |
|---|---|---|---|---|
| AF-03 | `30592634834` | `30593627903` | High | `cryptography` @ 00:32:20 vs. `epss_timestamp` 00:32:06 (14s) |
| AF-04 | `30592634834` | `30616404009` | High | `mako` @ 08:32:39 vs. 08:32:23 (16s) |
| AF-05 | `30592634834` | `30617428694` | High | `protobuf` @ 08:49:48 vs. 08:49:20 (28s) |
| AF-06 | `30592634834` | `30618200840` | High | `werkzeug` @ 09:02:46 vs. 09:02:13 (33s) — see §4 |
| AF-07 | `30592634834` | `30619246825` | High | `mysql-connector-python` @ 09:19:50 vs. 09:19:36 (14s) |
| AF-08 | `30592634834` | `30627246921` | High | `google-cloud-aiplatform` @ 11:34:10 vs. 11:34:02 (8s) |
| JS-02 | `30592634834` | `30592636219` | High | `handlebars` @ 00:15:24 vs. 00:14:52 (32s) |
| JS-03 | `30592634834` | `30593629026` | High | `form-data` @ 00:36:15 vs. 00:35:43 (32s) |
| JS-04 | `30592634834` | `30616410559` | High | `crypto-js` @ 08:35:28 vs. 08:35:13 (15s) |
| JS-05 | `30592634834` | `30617435445` | High | `jsonwebtoken` @ 08:52:04 vs. 08:51:29 (35s) |
| JS-06 | `30592634834` | `30618206648` | High | `lodash` @ 09:05:36 vs. 09:05:26 (10s) — see §4 |
| JS-07 | `30592634834` | `30619254609` | High | `ws` @ 09:23:06 vs. 09:22:39 (27s) |
| JS-08 | `30592634834` | `30627253658` | High | `body-parser` @ 11:37:07 vs. 11:37:02 (5s) |

AF-01, AF-02, AF-09, JS-01, JS-09 were already correctly attributed (distinct, verified run IDs each) and were not modified.

## 4. Supersedes a previously-closed finding: AF-06 and JS-06 root cause

This is a **correction to `docs/audit/af06_js06_rerun_attempt_2026-08-02.md`**, presented transparently rather than silently overwritten.

**Original conclusion (2026-08-02, closed with repository owner's sign-off):** the AF-06/JS-06 mismatch (executed evidence showing werkzeug/lodash instead of the pre-registered jinja2/flatted) was attributed to a scenario-profile copy-paste error in `profiles/AF-06.yaml` / `profiles/JS-06.yaml`, artifacts of an earlier, since-replaced per-scenario-workflow architecture. That investigation additionally found — independently and separately — that a *fresh rerun* dispatched this session against the correct targets also fell back to werkzeug/lodash, attributed to live Grype-database severity drift.

**New evidence (2026-08-03):** tracing `workflow_url` provenance recovered run `30618200840` — dispatched on **2026-07-31** (the same day the *original*, currently-committed AF-06 evidence was produced, confirmed by exact timestamp match against AF-06's own `epss_timestamp`) — with `TARGET_CVE=CVE-2024-56326`, the correct pre-registered jinja2 target. That run's own log shows it independently selected werkzeug. The equivalent run for JS-06, `30618206648`, was dispatched with `TARGET_CVE=CVE-2026-33228` (the correct flatted target) and independently selected lodash, again confirmed by exact timestamp match.

**Why the conclusion changed:** the *original*, currently-committed AF-06/JS-06 evidence was generated by a correctly-dispatched, current-architecture (`generic-remediation.yml`) run using the correct target CVE — not by the deprecated per-scenario-workflow files. The profile files could not have produced this evidence, because they belong to an architecture that had already been replaced by 2026-07-31 (the workflow files referencing them were deleted before this date, per the architecture-consolidation history already established). The `profiles.yaml` copy-paste bug is confirmed real (it is byte-identical to `AF-09.yaml`, per the original investigation) but is now understood to be a historical artifact from an even earlier point in the project, not the source of the evidence currently in the repository.

**Why the new explanation supersedes rather than merely supplements the previous one:** the previous conclusion's central causal claim — that the mismatch originated in the deprecated profile files — is directly contradicted by dated, timestamped, independently-verifiable proof that the actual currently-committed evidence came from a different, correctly-dispatched mechanism experiencing the same live-database-drift failure mode already documented for this session's own rerun. The profile-copy-paste bug remains a true, documented fact about the repository's history; it is no longer the correct answer to "why does AF-06's *current* evidence show werkzeug."

**What does not change:** the practical conclusion — that AF-06 and JS-06 are not currently reproducible against their pre-registered targets, for a documented external reason (Grype live-database drift), and that the pre-registration remains correctly unamended — is unaffected and, if anything, more strongly evidenced than before (now proven true as far back as the scenarios' original generation, not only in this session's rerun).

## 5. What changed and what did not

**Changed (this correction):** `workflow_commit`/`workflow_url` fields in 13 `experiment_manifest.json` files (JSON body and their duplicate copy in the `EMPIRICAL EVIDENCE` trailer) — 8 lines per file, verified via diff to be the only change in each file. Pre-correction state archived at `archive/provenance_correction_20260803_pre_state/`.

**Not changed:** any experimental result, any metric, any LLM request/response, any build/test/rescan output, the pre-registration, or the frozen `thesis-freeze-2026-08-02` tag's referenced commit.
