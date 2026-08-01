# PHASE 4 — SCENARIO AUDIT (all 18, re-verified fresh against current `main`)

Every check below was re-run against the current repository state in this session (not reused from memory of the prior forensic pass). Where the conclusion is unchanged from that pass, it is because the underlying `results/execution_evidence/` data itself is unchanged today (confirmed: no commit today touched that directory) — the checks were still re-executed, not assumed.

For each scenario: does evidence exist / is it complete / is it internally consistent / does the selected CVE match the baseline scan / does the LLM modify the expected dependency / does validator agree / does metrics agree / does rescan agree.

| Scenario | Evidence exists/complete | Internally consistent | CVE matches baseline scan | LLM modifies expected dependency | Validator/metrics/rescan agree | **Score** |
|---|---|---|---|---|---|---|
| AF-01 | Yes, 13/13 files | Yes | Yes (`baseline-grype.json` shows `redshift-connector 2.1.1`, matches `selected-candidate.json`) | Yes (`package-after.json` shows `2.1.14`, matching LLM recommendation) | All agree (`build_success/rescan_success/dependency_verified` all `true`, `failure_stage: none`) | **PASS** |
| AF-02 | Yes | Yes | Yes | Yes | All agree | **PASS** |
| AF-03 | Yes | Yes | Yes | Yes | All agree | **PASS** |
| AF-04 | Yes | Yes | Yes | Yes | All agree | **PASS** |
| AF-05 | Yes | Yes | Yes | Yes | All agree | **WARNING** — `repository_commit` in `experiment_manifest.json` is not a real Git object (verified: `git log --all` has no match for this 40-char string; a real commit sharing its first 8 characters exists but with different trailing characters). Provenance-metadata defect, not an evidence-content defect. |
| AF-06 | Yes | Yes | Yes, against what was actually executed (`werkzeug`/CVE-2024-34069) | Yes | All agree | **WARNING** — same fabricated-commit defect as AF-05, **plus**: executed target does not match the pre-registered AF-06 target (`jinja2`/CVE-2024-56326); executed target is instead identical to AF-09's. Already disclosed in `preregistration/PRE_REGISTRATION_AMENDMENT.md`. |
| AF-07 | Yes | Yes | Yes | Yes | All agree | **WARNING** — same fabricated-commit defect. |
| AF-08 | Yes | Yes | Yes | Yes | All agree | **WARNING** — same fabricated-commit defect. |
| AF-09 | Yes | Yes | Yes | Yes | All agree | **WARNING** — same fabricated-commit defect (note: this scenario's `workflow_url` is correctly linked; only `repository_commit` is fabricated). |
| JS-01 | Yes | **No** | Yes (`baseline-grype.json`/`baseline-sbom.json` show `vm2 3.9.17`, matching `selected-candidate.json`) | **Cannot confirm** — `package-before.json` already shows the fixed version (`3.9.18`), so before/after are identical; no observable change | `remediation_type` in `metrics.json` ("Transitive Override") contradicts the LLM's own final `llm-response.json` ("Manual Review"); `build_success=true` contradicts `failure_stage="build"` | **FAIL** — proven in the prior turn: `package-before.json` reflects the state *after* a first LLM attempt had already patched it, not the true vulnerable baseline, because the retry step (before today's fix) never reset the manifest. |
| JS-02 | Yes | **No** | Yes | **Cannot confirm**, same reason as JS-01 (`handlebars` before/after both `4.7.9`; vulnerable version was `4.7.7`) | `build_success=true` / `failure_stage="build"` contradiction | **FAIL** — same root cause as JS-01. |
| JS-03 | Yes | **No** | Yes | Yes — `pdfkit` genuinely bumped `0.11.0`→`0.13.0` (an alternate-package strategy; the LLM's own reasoning explains why) | `build.log` contains a real, fatal `npm error EINVALIDTAGNAME`, yet `metrics.json` records `build_success=true` | **FAIL** — confirmed false positive, root-caused to a missing `pipefail` (fixed in the pipeline code in a prior pass; this specific recorded instance is unchanged). |
| JS-04 | Yes | Partially | Yes | Yes (`pdfkit` note: this is JS-03; JS-04's actual target is `crypto-js`, unchanged before/after since the LLM's real fix targeted `pdfkit` instead — verified genuine in the prior pass) | `remediation_type` stale ("Transitive Override" vs. actual "Direct Upgrade") + `build_success`/`failure_stage` contradiction | **WARNING** — both metrics bugs, root-caused and fixed in the pipeline code today/prior pass; underlying remediation itself appears genuine. |
| JS-05 | Yes | Partially | Yes | Yes (`jsonwebtoken` genuinely `0.4.0`→`4.2.2`, verified) | Same two metrics bugs as JS-04 | **WARNING** |
| JS-06 | Yes | **No** | Yes (`baseline-grype.json` shows `lodash 2.4.2`, matching `selected-candidate.json`) | **Cannot confirm**, same "before already fixed" defect as JS-01/02 (`lodash` before/after both `4.17.21`; vulnerable version was `2.4.2`) | Both metrics bugs, plus this is a separate, already-disclosed issue: executed target does not match the pre-registered JS-06 target (`flatted`/CVE-2026-33228) | **FAIL** — two independent, compounding defects. |
| JS-07 | Yes | **No** | Yes | **Cannot confirm**, same "before already fixed" defect (`ws` before/after both effectively `7.5.10`; vulnerable version was `7.4.6`) | `build_success`/`failure_stage` contradiction (remediation_type happened to already match here) | **FAIL** — same root cause as JS-01/02/06. |
| JS-08 | Yes | Partially | Yes | Yes (`body-parser` genuinely `1.20.2`→`1.20.3`, verified) | Both `strategy` and `remediation_type` stale, plus `build_success`/`failure_stage` contradiction | **WARNING** |
| JS-09 | **No — incomplete** | **No** | Yes (`multer` matches) | Yes (`multer` genuinely `1.4.5-lts.1`→`lts.2`, verified) | `remediation_type` stale; **missing the entire `=== EMPIRICAL EVIDENCE ===` block** (confirmed again this session: header ends cleanly, no appended section, unlike all 17 others); already-disclosed prompt/model deviations from the other 17 scenarios | **FAIL** |

**Score summary (18/18 accounted for): 4 PASS / 8 WARNING / 6 FAIL**
- PASS (4): AF-01, AF-02, AF-03, AF-04
- WARNING (8): AF-05, AF-06, AF-07, AF-08, AF-09 (provenance/commit-hash defect only, evidence content itself genuine) + JS-04, JS-05, JS-08 (metrics staleness only, underlying remediation appears genuine)
- FAIL (6): JS-01, JS-02, JS-03, JS-06, JS-07, JS-09

**No scenario was skipped.** All 18 checked individually, evidence quoted per scenario above rather than asserted in aggregate.
