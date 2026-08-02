# AF-01 `llm-request.json` Correction (2026-08-03)

## 1. What was found

During the repository-wide `llm-request.json`/`llm-response.json` verification against recovered CI logs, AF-01 was the one scenario (of 18) whose committed `llm-request.json` did not byte-match the GitHub Actions log of its own recovered provenance run (`workflow_run_id 30574548185`, executed 2026-07-30T19:26:54Z). The committed prompt text differed from the log in exactly two places, both inside `api_payload.contents[0].parts[0].text`:

| Location in prompt | Log (true payload sent) | Committed file (before this fix) |
|---|---|---|
| Scenario identifier line | `Scenario ID: UNKNOWN` | `Scenario ID: AF-01` |
| CVE line | `* CVE ID: GHSA-29h4-r29x-hchv` | `* CVE ID: GHSA-29h4-r29x-hchv (CVE-2026-8838)` |

Everything else in the ~1600-character prompt, and the entire response, was already byte-identical.

## 2. Root cause

Traced via `git log --follow` on `results/execution_evidence/AF-01/llm-request.json` to commit `96b156814866060dce848b14cad4d71dd27c2b51` ("docs: finalize model tracking to strictly use gemini-2.5-flash and inject actual CVE IDs to evidence", 2026-07-30T21:41:34Z). This commit's diff shows it directly edited the embedded prompt *text string* inside the committed JSON — it did not touch `llm_reasoner.py`'s prompt-construction logic (that commit's only code change was to the model URL and fallback list). This confirms the edit was a manual, disclosed, post-hoc enrichment of already-committed evidence, not a pipeline re-execution.

Two supporting checks confirm this was a hand-edit rather than a live rerun:
- **No pipeline write path exists for this change.** `scripts/remediation/llm_reasoner.py:125` is the only place in the codebase that writes `llm-request.json`, and it writes once, from the same in-memory `user_prompt` string that is printed to the log immediately beforehand — there is no code path that rewrites this file after the fact. `scripts/rebuild_manifests.py` reads `llm-request.json` (for hash computation and prompt extraction) but its only file write targets `experiment_manifest.json` — confirmed via direct inspection, it never writes to `llm-request.json`.
- **Timing.** AF-01's true run (19:26:54Z) executed *before* the hand-edit commit (21:41:34Z), so nothing after that edit ever regenerated AF-01's evidence to reconcile it. By contrast, JS-01 — whose `llm-request.json` this same commit also hand-edited — was not left inconsistent, because JS-01's own true run executed *after* the hand-edit (created_at 2026-07-30T23:00:10Z) and a later commit (`9ca4b8d898`, 2026-07-31T09:02:47Z) overwrote JS-01's file with that run's genuine live output, which organically included the enrichment already present in the source data by then. AF-01 never received an equivalent later overwrite, so its hand-edited state persisted uncorrected until now.

## 3. Verification

**Byte-for-byte re-comparison** against the GitHub Actions log for run `30574548185`, using the same script and methodology already applied to all 18 scenarios (`verify_llm_io.py`, last-occurrence extraction, GH annotation/timestamp stripping):

```
prompt_extracted_len=1635 json_prompt_len=1635 MATCH=True
response_extracted=parsed OK MATCH=True
```

**Diff verification** — confirmed via character-level diff (`difflib.SequenceMatcher`) against the archived pre-correction file that exactly two substrings changed in `llm-request.json`, nothing else:
```
replace 'AF-01' -> 'UNKNOWN'
delete ' (CVE-2026-8838)' -> ''
```
The file's separate, legitimate wrapper-level metadata field (`scenario_id: "AF-01"`, outside `api_payload`, added by the 2026-07-30 restructuring commit) was correctly left untouched — it labels which scenario the file belongs to and was never part of the payload sent to Gemini.

**Hash dependency check.** `experiment_manifest.json`'s `artifact_hashes.llm-request.json` field was verified, before this fix, to hold the exact current SHA-256 of the (uncorrected) file (`68ea389ec71f7b9a2022923e89aa7cd9e00daa2adc8df40c60d117164ae1757b` — confirmed by direct recomputation). Since this is a genuine, mechanically-derived hash of the file's bytes, correcting the file necessarily invalidated it. Recomputed post-correction hash: `19598ede197bd2b10d06e6041eb95ac0698840e23385e6b05674fd6afabc5b72`. Updated in both places this value appears inside `experiment_manifest.json` — the JSON body (`artifact_hashes.llm-request.json`) and its duplicated copy inside the appended `EMPIRICAL EVIDENCE` trailer — confirmed via diff to be exactly the 2 lines changed, nothing else in the manifest touched.

## 4. What changed and what did not

**Changed:** `results/execution_evidence/AF-01/llm-request.json` (2 substrings inside the embedded prompt text); `results/execution_evidence/AF-01/experiment_manifest.json` (`artifact_hashes.llm-request.json`, both occurrences, updated to match the corrected file).

**Not changed:** `llm-response.json`, `metrics.json`, all other artifact hashes, `workflow_commit`/`workflow_url`/`repository_commit` (already corrected in the prior provenance-correction round and not touched again here), the wrapper-level `scenario_id`/`experiment_id`/`application`/`ecosystem`/`prompt_version` fields, and any other scenario. Pre-correction state archived at `archive/af01_llm_request_correction_20260803_pre_state/`.

## 5. Original conclusion / New evidence / Why changed / Why supersedes

**Original conclusion** (established during the repository-wide LLM I/O verification pass): AF-01's `llm-request.json` and its GitHub Actions log were treated as the file being correct evidence with an unexplained two-point divergence from the log, pending a decision on which one represents "true" provenance.

**New evidence:** Direct diff of commit `96b156814866060dce848b14cad4d71dd27c2b51` shows the divergence was introduced by a manual, disclosed edit to the committed JSON's embedded prompt text (not a pipeline behavior), made one minute after a related restructuring commit, and never reconciled by a subsequent rerun — unlike JS-01, which received exactly the same hand-edit but was independently overwritten by its own later live execution.

**Why the conclusion changed:** With the write path fully traced (`llm_reasoner.py` as sole, one-shot writer; `rebuild_manifests.py` confirmed read-only with respect to this file) and the CI log confirmed as the byte-exact record of what was actually transmitted to Gemini (`print(user_prompt)` immediately preceding `json.dump` of the same in-memory string), there is no remaining ambiguity about which side is authoritative: the log is ground truth, and the committed file was the outlier.

**Why this correction supersedes the previous state:** The two corrected substrings are metadata-adjacent (a scenario-identifier label duplicated from a separate wrapper field, and a CVE cross-reference suffix) and do not touch any vulnerability data, dependency graph, or LLM output — `llm-response.json` and every metric were already, and remain, unaffected. Restoring the exact transmitted text makes AF-01 consistent with the same standard already verified for the other 17 scenarios, without changing any scientific result.

## 6. Trailer consistency — completed 2026-08-03 (same correction, not a new one)

The item flagged above as open has been resolved as part of this same AF-01 evidence-consistency correction.

**Verified the trailer is intended to be a verbatim duplicate.** `scripts/rebuild_manifests.py:extract_prompt_text()` (line 289-294) returns exactly `llm_request['api_payload']['contents'][0]['parts'][0]['text']` — the identical string used to populate `llm-request.json`. The manifest-building template (`scripts/rebuild_manifests.py:536-539`) then writes:
```
--- LLM PROMPT ---
Scenario ID: {sid}
Prompt Version: {prompt_version}

{prompt_text}
```
i.e., a script-generated header line (`{sid}`, `{prompt_version}` — the scenario's own label, not derived from the prompt content) followed by the verbatim extracted prompt text. This confirms the trailer's embedded copy is designed to be byte-identical to `llm-request.json`'s prompt string, distinct from the header line immediately above it.

**What was corrected.** Only the second occurrence of the `Scenario ID: AF-01` / CVE-suffix text — the one belonging to the embedded verbatim copy, not the script's own header line one line above it — was updated to match the now-corrected `llm-request.json`:
- `Scenario ID: AF-01` → `Scenario ID: UNKNOWN` (embedded-copy occurrence only; the header line's `Scenario ID: AF-01` was left untouched, since it correctly labels which scenario this manifest belongs to, exactly analogous to the wrapper-level `scenario_id` field in `llm-request.json`)
- `* CVE ID: GHSA-29h4-r29x-hchv (CVE-2026-8838)` → `* CVE ID: GHSA-29h4-r29x-hchv`

**Verification performed:**
1. **Trailer matches `llm-request.json` byte-for-byte.** Extracted the trailer's embedded prompt text and compared it directly against `llm-request.json`'s `api_payload.contents[0].parts[0].text`: length 1635 both sides, `MATCH=True`.
2. **JSON body unchanged.** Parsed the manifest's JSON-body prefix (via `json.JSONDecoder().raw_decode`) before and after this edit: identical object, byte-identical raw prefix.
3. **No additional hash requires updating.** `artifact_hashes` lists only real artifact filenames (`package-before.json`, `metrics.json`, `llm-request.json`, etc.) and contains no self-referential entry for `experiment_manifest.json` — there is no hash of the manifest file stored anywhere for this trailer edit to invalidate.
4. **Diff isolation.** Diffed the file against the snapshot taken immediately before this edit (`archive/af01_llm_request_correction_20260803_pre_state/experiment_manifest.json.round1_hashfixed`): exactly 2 lines changed, matching the two intended substrings, nothing else.

No commentary, metrics, hashes, timestamps, or response data were touched. This closes the AF-01 evidence-consistency correction: `llm-request.json`, its dependent hash in `experiment_manifest.json`, and the manifest's own human-readable duplicate of the same prompt are now mutually consistent and all verified against the GitHub Actions log of AF-01's true run.
