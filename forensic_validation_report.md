# FINAL FORENSIC VALIDATION — ALL 18 SCENARIOS

Read-only investigation except for the specific, logged auto-remediation actions below (9 manifest fields + 1 script bug — both explicitly authorized "safe fix" categories: incorrect commit SHAs, missing/stale generated metadata). No raw log, LLM response, SBOM, Grype output, or execution-produced package manifest was modified anywhere in this pass.

---

## 1. Scenario-by-scenario validation matrix

| Scenario | Structure | Hashes | Provenance | Cross-file consistency | Package before/after | Verdict |
|---|---|---|---|---|---|---|
| AF-01 | ✅ 13/13 (+bonus `pipeline_logs/`) | ✅ 12/12 raw-match | ✅ commit matches run's real `head_sha` | ✅ clean | ✅ genuine version change | **CLEAN** |
| AF-02 | ✅ | ✅ | ⚠️ commit real & matches run, but run is shared with 5 other scenarios | ✅ clean | ✅ | **MINOR** |
| AF-03 | ✅ | ✅ | ⚠️ same as AF-02 | ✅ clean | ✅ | **MINOR** |
| AF-04 | ✅ | ✅ | ⚠️ same as AF-02 | ✅ clean | ✅ (case-sensitive match, verified) | **MINOR** |
| AF-05 | ✅ | ✅ | 🔧 commit was fabricated — **fixed this pass** | ✅ clean | ✅ | **FIXED** |
| AF-06 | ✅ | ✅ | 🔧 commit was fabricated — **fixed this pass**; independent, separate issue: executed target (werkzeug/CVE-2024-34069) duplicates AF-09, does not match pre-registered jinja2/CVE-2024-56326 (already disclosed in README/preregistration from the prior remediation pass) | ✅ clean | ✅ | **MAJOR (pre-existing, disclosed)** |
| AF-07 | ✅ | ✅ | 🔧 commit was fabricated — **fixed this pass** | ✅ clean | ✅ | **FIXED** |
| AF-08 | ✅ | ✅ | 🔧 commit was fabricated — **fixed this pass** | ✅ clean | ✅ | **FIXED** |
| AF-09 | ✅ | ✅ | 🔧 commit was fabricated — **fixed this pass** (note: `workflow_url` itself was already correct — only `repository_commit` was fake) | ✅ clean | ✅ | **FIXED** |
| JS-01 | ✅ | ✅ | ✅ commit matches run's real `head_sha` | ⚠️ `build_success=true` + `failure_stage="build"` contradiction (M2, root-caused) | 🔴 **`package-before.json` override already shows the fixed version (`vm2: 3.9.18`), not the vulnerable `3.9.17` declared in `selected-candidate.json`** | **CRITICAL** |
| JS-02 | ✅ | ✅ | ⚠️ run shared with 5 others (see AF-02) | ⚠️ same build_success/failure_stage contradiction | 🔴 same "before" issue (`handlebars: 4.7.9` in both before/after; vulnerable version was `4.7.7`) | **CRITICAL** |
| JS-03 | ✅ | ✅ | ⚠️ run shared | 🔴 **`build_success=true` while `build.log` contains a real, fatal `npm error EINVALIDTAGNAME`** (C4, root-caused, script fixed) | ✅ (override correctly shows the new nested entry added) | **CRITICAL** |
| JS-04 | ✅ | ✅ | ⚠️ run shared | ⚠️ `remediation_type` stale ("Transitive Override" vs LLM's actual "Direct Upgrade") + build_success/failure_stage contradiction, both root-caused this pass | ✅ (verified: `pdfkit` genuinely bumped 0.11.0→0.13.0, matching the LLM's actual alternate-package strategy) | **MAJOR** |
| JS-05 | ✅ | ✅ | 🔧 commit fabricated — **fixed** | ⚠️ same two metrics staleness issues as JS-04 | ✅ genuine change (jsonwebtoken 0.4.0→4.2.2) | **MAJOR (partly fixed)** |
| JS-06 | ✅ | ✅ | 🔧 commit fabricated — **fixed**; independent, separate, already-disclosed issue: executed target (lodash/CVE-2021-23337) doesn't match pre-registered flatted/CVE-2026-33228 | ⚠️ same two metrics staleness issues | 🔴 same "before already fixed" issue as JS-01/02 (`lodash: 4.17.21` in both; vulnerable version was `2.4.2`) | **CRITICAL** |
| JS-07 | ✅ | ✅ | 🔧 commit fabricated — **fixed** | ⚠️ build_success/failure_stage contradiction (remediation_type happened to already match here) | 🔴 same issue (`ws` override already `7.5.10`-class in "before"; vulnerable version was `7.4.6`) | **CRITICAL** |
| JS-08 | ✅ | ✅ | 🔧 commit fabricated — **fixed** | ⚠️ both metrics staleness issues | ✅ genuine change (body-parser 1.20.2→1.20.3) | **MAJOR (partly fixed)** |
| JS-09 | ✅ | ✅ | ✅ own unique, correctly-linked run — but that run is the branch commit (`b9cb78f9`, "fix: use gemini-3.6-flash") already disclosed in README/preregistration from the prior pass | 🔴 **missing the entire `=== EMPIRICAL EVIDENCE ===` block** (47 lines vs. 170–385 for every other scenario) + `remediation_type` mismatch + already-disclosed model/prompt deviations | ✅ genuine change (multer 1.4.5-lts.1→lts.2) | **CRITICAL (already flagged, now more precisely characterized)** |

**Legend:** ✅ verified clean · ⚠️ Major, root-caused, does not fabricate/lose data · 🔴 Critical · 🔧 fixed this pass (safe-category fix only)

---

## 2. Files repaired (this pass)

| File | Problem | Root cause | Fix | Why safe | Verified |
|---|---|---|---|---|---|
| `results/execution_evidence/{AF-05,AF-06,JS-05,JS-06}/experiment_manifest.json` | `repository_commit` = `796ba575b26a403844d23af9c5e00e7f4d9e48f9` does not exist as a Git object | A real 8-char short-hash prefix (`796ba575`, a genuine commit) padded with non-corresponding hex characters to look like a full 40-char SHA | Replaced with the verified real full SHA `796ba575b26a4038bd2393d9f09c6328f06661b1` (2 occurrences per file: JSON header + EMPIRICAL EVIDENCE block copy) | This is generated provenance metadata, not raw pipeline output; the correction is independently verifiable via `git log --all` | `python3 -m json` header re-parse OK on all 4; no leftover fake string; `git status` confirms only these files changed |
| `results/execution_evidence/{AF-07,JS-07}/experiment_manifest.json` | Same defect, prefix `d3766873` | Same mechanism | → `d3766873fa30b70396cbdcc7c78f9cd203f0b3ed` | Same | Same |
| `results/execution_evidence/{AF-08,JS-08}/experiment_manifest.json` | Same defect, prefix `15177533` | Same mechanism | → `15177533346e3240f5b419c9b7cf9568603b0664` | Same | Same |
| `results/execution_evidence/AF-09/experiment_manifest.json` | Same defect, prefix `16a551ed` | Same mechanism | → `16a551ed6c7569848711da6f431cae58d4d008fe` | Same | Same |
| `scripts/remediation/retry_remediation.py` | `remediation_type` never updated on retry (sibling bug to the already-fixed `failure_stage` issue) | Missing assignment in the same metrics-update block | Added `metrics['remediation_type'] = recommendation.get('remediation_type', ...)` alongside the existing `strategy` update | Pipeline code, not evidence; prospective only, changes no existing scenario's recorded data | `py_compile` passes; mirrors the already-verified pattern of the `failure_stage` fix |

**Nine manifest edits + one script edit. Nothing under `results/execution_evidence/**` besides these 9 `experiment_manifest.json` files was touched — confirmed via `git status --porcelain` showing exactly these 10 paths.**

---

## 3. Files requiring manual intervention (not fixed — would require rewriting evidence)

- **`JS-01/JS-02/JS-06/JS-07`'s `package-before.json`.** The override entry for the target package already shows the *fixed* version in the "before" snapshot, not the vulnerable version each scenario's own `selected-candidate.json` declares. This cannot be corrected without regenerating the actual pre-remediation state — i.e., rerunning the scenario — which is out of scope for this pass (per the explicit instruction to stop rather than rewrite historical evidence).
- **`JS-03`'s `build.log`/`metrics.json` mismatch** (`build_success:true` despite a real fatal npm error) — root cause fixed in the pipeline code (prior pass), but the existing JS-03 evidence itself still shows the false positive. Requires a rerun to produce a corrected record.
- **`JS-09`'s missing EMPIRICAL EVIDENCE block** — regenerating it from the existing `metrics.json`/`llm-request.json`/`llm-response.json` would be straightforward mechanically, but doing so risks papering over the scenario's other already-disclosed irregularities (hidden prompt, model discrepancy) by making it look structurally "complete" like the other 17. Recommend leaving this as an open manual decision tied to the broader JS-09 rerun-vs-supplementary decision already on record, not fixing it in isolation.
- **The 6 scenarios sharing `workflow_url` 30592634834** (AF-02/03/04, JS-02/03/04) and the 8 that shared the now-corrected-commit runs — the *specific* CI run that produced each individual scenario's evidence cannot be independently proven from what's committed or from the public API (per-run `workflow_dispatch` input values, i.e. which `target_cve` a given run actually processed, are not exposed without authenticated log access). Per the explicit "do not guess" instruction, no `workflow_url` was invented or altered for these — only the independently-verifiable `repository_commit` values were fixed.

---

## 4. Evidence that could not be verified

- Which specific GitHub Actions run genuinely produced each of AF-02/03/04/05/06/07/08 and JS-02/03/04/05/06/07/08's evidence (14 of 18 scenarios) — the commit is now correct/verified for all of them, but the run-level linkage remains unproven for anything beyond "a run exists that was built from that commit."
- Whether JS-06's `lodash`/CVE-2021-23337 substitution and AF-06's `werkzeug`/CVE-2024-34069 duplication were caused by a dispatch-input error or a local script bug — already flagged as undeterminable from committed history in the prior remediation pass; unchanged by this one.
- The full raw text of any of the 36 `grype-baseline.yml` runs or the 156 `generic-remediation.yml` runs — GitHub's log/artifact download endpoints require authentication not used in this or any prior pass.

---

## 5. Remaining Critical issues

1. **`package-before.json` does not reflect a genuinely vulnerable starting state for JS-01, JS-02, JS-06, JS-07** (4 of 9 npm scenarios — nearly half). This is the most serious finding of this pass: it raises the question of whether the pipeline's "fix" for these four scenarios did any real work, since the override needed was seemingly already present before the run began. Most plausible explanation: the shared `applications/juice-shop/package.json` accumulated overrides across multiple scenario runs in CI without being reset to a clean baseline between them — i.e. cross-scenario contamination in the underlying application checkout, not fabrication of results, but a real reproducibility defect.
2. **JS-03's `build_success: true` remains a confirmed false positive** in the existing evidence (root cause fixed prospectively; this specific record itself is unchanged, per the immutability rule).
3. **JS-09's manifest is missing its EMPIRICAL EVIDENCE block entirely**, on top of its already-disclosed model/prompt deviations.
4. **AF-06 / JS-06's executed targets still do not match their pre-registered identities** (carried over from the prior pass, unchanged, already disclosed in README and the pre-registration amendment).

## 6. Remaining Major issues

1. **`remediation_type` staleness** in `metrics.json` for JS-01, JS-04, JS-05, JS-06, JS-08, JS-09 (6 of 9 JS scenarios) — root cause fixed in `retry_remediation.py` this pass; the 6 existing records are unchanged.
2. **`build_success: true` / `failure_stage: "build"` internal contradiction** persists in the existing evidence for JS-01 through JS-08 (root cause was already fixed in the prior pass; this pass reconfirmed the contradiction is present in 8 of 9 JS scenarios' actual committed data, not 7 as earlier estimated — JS-01 was not previously counted in this specific tally and is included here).
3. **Provenance cannot be individually proven** for 14 of 18 scenarios beyond "built from a verified real commit" — the specific originating CI run is not provable from public, unauthenticated evidence.

---

## 7. Repository consistency score: **5/10**

Structural and hash consistency across all 18 scenarios is excellent (13/13 files, 216/216 hashes, zero exceptions). Cross-file semantic consistency is not: 8/9 JS scenarios carry an internal metrics contradiction, 6/9 carry a second one, and provenance metadata was actively fabricated (not merely stale) in 9 of 18 manifests before this pass.

## 8. Evidence integrity score: **4/10**

The core measurement artifacts (build.log, llm-request/response.json, rescan.json) show no evidence of tampering anywhere sampled, and SHA256 verification is now clean for all 18. But the discovery that nearly half the npm scenarios' "before" state does not represent a genuine vulnerable baseline, combined with fabricated (not just wrong) commit hashes in half the manifests before this pass, means the evidentiary chain cannot be fully trusted end-to-end without the specific caveats documented above.

## 9. Reproducibility score: **4/10**

Tool versions, LLM configuration, and enrichment snapshots are consistently and correctly recorded. But: the specific CI run for 14/18 scenarios cannot be independently re-derived from what's public; the "before" state for 4 scenarios cannot currently be reproduced as claimed; and `run_deterministic_baseline.py` (the baseline-reproduction script) requires a deliberate rerun decision that hasn't been made.

## 10. Supervisor readiness: **NOT YET — specific, listed items, not a wholesale rewrite**

The repository's documentation is now honest about most of what it doesn't know (the correction/disclosure notes from prior passes hold up under this deeper check — nothing found here contradicts them). What's new and unresolved is narrower and more concrete than "not ready" implies: one class of evidence defect (4 scenarios' "before" state) and two already-partially-fixed metrics bugs whose historical instances remain uncorrected by design.

## 11. Would I personally approve this repository for an MSc dissertation?

**NO, not yet — but the remaining gap is specific and small, not systemic.**

The structural, hash, and tool-configuration layers are genuinely solid — that's real, verified engineering, confirmed independently in this pass, not assumed. What blocks approval is one concrete, well-evidenced finding: **four of nine npm scenarios' "before" evidence does not demonstrate a genuine vulnerable starting state**, which undermines the specific claim that a fix was needed and applied for those four. An examiner who checks `JS-01/package-before.json` against `JS-01/selected-candidate.json`'s own declared vulnerable version — a five-minute check, exactly the one performed here — would find the same contradiction. That needs an explicit answer (most likely: a rerun of those four scenarios with a verified-clean application checkout between runs) before this dataset can be presented as 18 independently-demonstrated remediations. Everything else found in this pass was either already disclosed, or has been fixed at the code level with the residual historical instances clearly documented rather than hidden.
