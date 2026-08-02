# Repository Freeze Report

**Repository:** `llm-remediation-thesis-final`
**Thesis:** Empirical Evaluation of LLM-Assisted Dependency Remediation in SBOM-Driven CI/CD Pipelines
**Author:** Santosh Nagaraj — SRH University Berlin, MSc (Cybersecurity)
**Freeze date:** 2026-08-02
**Branch:** `main`
**Tag:** `thesis-freeze-2026-08-02`
**Frozen commit SHA:** the commit this tag points to — retrieve with `git rev-list -n 1 thesis-freeze-2026-08-02`. (A commit cannot embed its own hash; git and the tag are the authoritative record.)
**Verdict:** Accept with minor revisions → revisions applied → **FROZEN** (see `FINAL_VERDICT.md`).

---

## 1. Audit timeline (this engagement)

1. Zero-trust forensic audit → `audit_progress.md`, `findings_classification.md`.
2. Scoped remediation of a pre-approved Minimum Fix Set → `remediation_log.md`.
3. Read-only verification pass + follow-up completion.
4. Repository cleanup (obsolete/duplicate archival).
5. Publication-readiness (PR-style per-file) review; staged/committed/pushed.
6. Grounding of docs in real GitHub Actions run history → discovery of fabricated commit-hash provenance.
7. **9-phase independent reproducibility audit** (Phases 1–9, `docs/audit/phase*.md`).
8. Group A additive-provenance improvements + Group B evaluation.
9. `build_success` regression fix; provenance fix; JS-09 regeneration.
10. **4-examiner panel review** (`docs/audit/phase9_examiner_panel_review.md`) — Major revisions → fixed → Accept with minor revisions.
11. Phase 9.5 improvement classification (`docs/THESIS_IMPROVEMENTS.md`).
12. Freeze.

## 2. Bugs fixed (all verified in CI or by primary-evidence re-check)

| Commit | Fix |
|---|---|
| `b9d98fb1` | Pin frontend npm deps — makes the JS baseline reproducible (root cause: `frontend/.npmrc` `package-lock=false` → live-resolved `postinstall`). |
| `cbdd1de1` | Add `--exclude "**/bin"` to `grype-baseline.yml` — the scanner was cataloguing its own `/bin/syft` binary (~274 spurious Go packages, ~67 spurious matches per AF scenario). |
| `f856b891` | Restore `build_success` tracking (regression from an earlier `0cb56095`: implicit `True` removed without replacement → stuck `false` for every scenario); represent `test_success`/`runtime_success` as `null` when not executed; symmetric `validation_stage_reached` fix. |
| `d0748e0a` | Replace 9 fabricated `repository_commit` hashes with real, `git`-verified `head_sha` values. |

## 3. Documentation / integrity corrections (Phase 9 review)

| Commit | Correction |
|---|---|
| `19df65c6` | A1: corrected the false "0% deterministic success rate" claim to the verified ecosystem-split result. A2/D2: relocated the contradictory `THESIS_DRAFT.md` out of `results/` to `archive/`. B3: consolidated the npm build-compilation limitation. C4: corrected the reproducibility-doc layout diagram. |

## 4. Evidence preserved (not modified)

- `results/execution_evidence/` for all 18 scenarios — historical evidence left intact throughout (except JS-09, §5).
- `results/reproducibility_verification/` — the post-fix 18-scenario deterministic-baseline sweep (added, not overwriting).
- `docs/audit/` — full nine-phase + panel-review trail.

## 5. Evidence regenerated

- **JS-09 only.** Regenerated via CI run `30723203247` (commit `d0748e0a`) to add the missing `EMPIRICAL EVIDENCE` block and correct metric semantics. Remediation outcome unchanged (multer/CVE-2026-3520 resolved via retry). Pre-rerun state archived at `archive/JS-09_pre_rerun_evidence_20260802_012547/`. Full comparison: `docs/audit/js09_rerun_summary.md`.

## 6. Additive provenance/traceability (no experiment change)

`30843e65` — future evidence bundles now also capture `llm-response-full.json` (raw model response incl. `modelVersion`), `dependency-graph.log`, and `grype-db-metadata.json` (Grype version, DB schema, DB build timestamp, scan timestamp).

## 7. Remaining limitations

See `THESIS_LIMITATIONS.md` (10 disclosed limitations).

## 8. Future work

See `THESIS_FUTURE_WORK.md` (7 methodology extensions requiring rerun + 5 research directions) and `docs/THESIS_IMPROVEMENTS.md` (full 4-category classification).

## 9. Tool versions (pinned)

| Tool | Version |
|---|---|
| Syft | 1.44.0 (CI Linux; the vendored Windows binary mismatch is documented) |
| Grype | 0.112.0 (live DB; not pinned — see limitation 4) |
| LLM | Gemini (`gemini-3.6-flash` primary, with documented fallback list) |
| CI runner | `ubuntu-latest` / `ubuntu-24.04`, Node 18.x, Python 3.12.x |

## 10. Post-freeze recommendation

The single highest-value post-freeze action (does not modify the experiment): author the **publication-quality JS-01 case study** from the existing frozen evidence, per `docs/THESIS_IMPROVEMENTS.md` Category 2.
