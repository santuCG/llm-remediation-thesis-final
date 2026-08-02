# Case Study — AF-01: `redshift-connector` (CVE-2026-8838) in Apache Airflow

> **Post-freeze documentation artifact (2026-08-02).** Derived entirely from the frozen evidence in `results/execution_evidence/AF-01/`. Every figure is quoted from those files; nothing is re-run. AF-01 is the **clean-reference** companion to the JS-01 case study: where JS-01 exposes the hard transitive/toolchain edge case, AF-01 shows the pipeline executing end-to-end with internally consistent metrics and a first-attempt success. Read the two together — they bound the behaviour of the system.

---

## 1. Why this scenario is worth a case study

AF-01 is the pipeline's "happy path" reference: a critical vulnerability in a **direct** Python dependency, remediated by a clean version bump that installs, resolves, and eradicates the advisory on the first attempt, with a `metrics.json` that is internally consistent end-to-end. It is the correct baseline against which the harder JS-01 case should be read.

It also carries one honest limitation that must be stated up front (§12): **for this pip scenario the deterministic scanner baseline also succeeds**, so AF-01 demonstrates the *pipeline operating correctly*, not the LLM's distinctive advantage over deterministic SCA. That advantage is what the transitive npm scenarios (e.g. JS-01) exist to show.

---

## 2. Original vulnerability

*(Source: `results/execution_evidence/AF-01/selected-candidate.json`)*

| Field | Value |
|---|---|
| Package | `redshift-connector` |
| Vulnerable version | `2.1.1` |
| Advisory | `GHSA-29h4-r29x-hchv` (alias `CVE-2026-8838`) |
| Severity | Critical |
| CVSS | 9.8 |
| EPSS | 0.00808 |
| CISA KEV | No |
| Fixed version | `2.1.14` |

Unlike JS-01's transitive `vm2`, `redshift-connector` is a **direct** dependency, declared in `requirements.txt` and required by `apache-airflow-providers-amazon`:

```
apache-airflow-providers-amazon  →  redshift-connector==2.1.1   ← vulnerable, directly pinned
```

Python's flat resolution model (one installed version per package, no nested duplication) is what makes this case tractable by a simple bump — the structural contrast with npm's nested graph is the heart of the ecosystem-dependent story.

---

## 3. Baseline Grype findings

*(Source: `results/execution_evidence/AF-01/baseline-grype.json`)*

- `redshift-connector @ 2.1.1` → `GHSA-29h4-r29x-hchv` **present**.
- Total match entries in the baseline report: **583**.

This established the experimental control.

---

## 4. Candidate ranking (prioritisation)

*(Source: `results/execution_evidence/AF-01/candidate-ranking.json` — 62 ranked candidates)*

The prioritisation stage ranks all discovered vulnerabilities by **KEV → EPSS → CVSS (descending)**. The top of the ranking was, for example:

| Rank | Package | KEV | EPSS | CVSS |
|---|---|---|---|---|
| 1 | `werkzeug` | No | 0.03397 | 7.5 |
| 2 | `urllib3` | No | 0.02667 | 7.5 |
| 3 | `apache-airflow` | No | 0.01979 | 7.5 |

As in every scenario, `redshift-connector` is not the top-ranked item; JS-/AF- scenarios are **pre-registered**, so the orchestrator overrides the ranking to select the pre-registered target. The ranking is retained as evidence of the prioritisation policy while the scenario definition fixes the studied vulnerability.

---

## 5. LLM prompt (abridged)

*(Source: `results/execution_evidence/AF-01/llm-request.json`; user content excerpted)*

The system instruction and generation config are identical to every scenario (Senior DevSecOps agent; `temperature 0.0, topP 1.0, topK 1, seed 42`; strict JSON `responseSchema`). The user content supplied:

- Vulnerability intelligence (§2).
- Dependency context: `pip show redshift-connector` (version `2.1.1`, `Required-by: apache-airflow-providers-amazon`) and the full `pip freeze`.

Notably, **there is no "Previous Attempt Failure" section** in this prompt — confirming AF-01 succeeded on the *first* LLM attempt (`retry_count: 0`, `llm_iteration: 1`). Contrast JS-01, whose recorded prompt was a retry carrying the prior build failure.

---

## 6. LLM response

*(Source: `results/execution_evidence/AF-01/llm-response.json`, verbatim reasoning)*

> **reasoning:** "The package redshift-connector at version 2.1.1 contains a critical vulnerability (GHSA-29h4-r29x-hchv, CVSS 9.8). The dependency is explicitly specified in requirements.txt. Performing a direct upgrade of redshift-connector from 2.1.1 to 2.1.14 satisfies downstream dependencies like apache-airflow-providers-amazon while completely remediating the vulnerability. Alternative strategies like package replacement or manual review are unnecessary as a official patch exists in version 2.1.14."
>
> **strategy:** `direct_upgrade` · **remediation_type:** `Direct Upgrade` · **recommended_package_version:** `2.1.14` · **manifest_patch:** `{ operation: bump, package: redshift-connector, constraint: 2.1.14 }`

The reasoning is correct and appropriately economical: it identifies the genuine fixed version (`2.1.14`, no hallucination), confirms the dependency is direct, checks that the bump satisfies the downstream provider (`apache-airflow-providers-amazon`), and explicitly rejects the heavier strategies (replacement, manual review) as unnecessary because an official patch exists. This is the *simple* end of the strategy space — and the LLM correctly recognised it as such rather than over-engineering.

---

## 7. Manifest diff

*(Source: `results/execution_evidence/AF-01/package-before.json` vs `package-after.json` — pip-freeze text despite the `.json` extension; see §12)*

A genuine, clean one-line delta:

```diff
- redshift-connector==2.1.1
+ redshift-connector==2.1.14
```

Unlike JS-01, AF-01's recorded before/after files are **uncontaminated** — the "before" shows the true vulnerable pin and the "after" shows the fix, so the manifest delta is directly visible in the evidence.

---

## 8. Dependency resolution

*(Source: `results/execution_evidence/AF-01/build.log`)*

The install log confirms a clean in-place upgrade of the direct dependency:

```
Collecting redshift-connector==2.1.14 (from -r requirements.txt (line 300))
Installing collected packages: redshift-connector
  Attempting uninstall: redshift-connector
    Found existing installation: redshift-connector 2.1.1
    Uninstalling redshift-connector-2.1.1
```

`2.1.1` is uninstalled and `2.1.14` installed with no unresolved-conflict errors — the flat pip resolution model needs no override, unlike JS-01's transitive case. `dependency_verified: true` in the metrics records that the intended version is what actually resolved.

---

## 9. Rescan results

*(Source: `results/execution_evidence/AF-01/rescan.json` vs `baseline-grype.json`)*

| | Baseline | Post-remediation |
|---|---|---|
| `redshift-connector` target advisory `GHSA-29h4-r29x-hchv` | **present** (`2.1.1`) | **absent (eradicated)** |
| Total Grype match entries | 583 | 581 |

The target advisory is eradicated. The aggregate count barely moves (583→581) — consistent with the thesis's point that aggregate scanner counts are not a proportional measure of single-vulnerability remediation; the load-bearing result is the target eradication.

---

## 10. Build and test validation

*(Source: `results/execution_evidence/AF-01/build.log`, `test.log`)*

- Dependency **install** succeeded (§8).
- No build/compile failure — unlike the npm scenarios, the Airflow (pip) target does not carry the pre-existing TypeScript toolchain incompatibility. `build_success: true`, `failure_stage: none`.
- `test_success: false` — attributable to the runner's test-environment limitations (missing runner-level packages such as `sentry_sdk`), **not** a remediation defect; it did not gate the scenario (`failure_stage: none`, `validation_stage_reached: validator`).

---

## 11. Final metrics

*(Source: `results/execution_evidence/AF-01/metrics.json`)*

| Field | Value | Reading |
|---|---|---|
| `strategy` / `remediation_type` | `direct_upgrade` / `Direct Upgrade` | **internally consistent** (contrast JS-01) |
| `dependency_type` | `direct` | **correct** (contrast JS-01's mislabel) |
| `dependency_verified` | `true` | `2.1.14` resolved |
| `rescan_success` | `true` | advisory eradicated |
| `build_success` | `true` | install succeeded, no compile failure |
| `retry_count` / `llm_iteration` | `0` / `1` | first-attempt success |
| `failure_stage` | `none` | clean run |

This is a metrics record with **no internal contradictions** — the reference standard the JS-01 metrics fell short of.

---

## 12. Evidence-integrity notes (honest disclosure)

1. **The deterministic baseline also succeeds here.** In the Phase 5/9 verification sweep, the deterministic scanner-recommendation baseline for AF-01 both built and eradicated the target CVE (`results/reproducibility_verification/AF-01/`). AF-01 therefore demonstrates the pipeline operating correctly, **not** an LLM advantage over deterministic SCA — for flat-resolution pip dependencies a direct bump suffices. The LLM's distinctive contribution is evidenced on the transitive npm scenarios (JS-01). This is the single most important caveat for reading AF-01 in the thesis.
2. **`test_success: false` / `runtime_success: false`** reflect the runner test-toolchain limitation and the absence of a dedicated runtime-check stage respectively; neither indicates a remediation failure (the post-fix pipeline records `runtime_success` as `null` to make this explicit — this historical record predates that change).
3. **`package-before.json` / `package-after.json` are pip-freeze text**, not JSON, despite the `.json` extension (a naming artifact noted in `docs/audit/phase6_evidence_completeness.md`). Their content is authoritative; only the extension is misleading.
4. **Extra `pipeline_logs/` directory.** AF-01 alone carries an additional `pipeline_logs/` sub-directory not present in other scenarios (raw CI log dump; noted in `docs/audit/phase6_evidence_completeness.md`). It is supplementary and does not affect the evidence above.

---

## 13. Interpretation

AF-01 anchors the "clean end" of the system's behaviour and, paired with JS-01, tells the complete story:

- **A correctly-scoped, verifiable success.** A critical CVE in a direct dependency, remediated by the correct fixed version, installed cleanly, verified in the dependency graph, and eradicated in the rescan — on the first attempt, with self-consistent metrics. This is what a passing scenario looks like and it is genuinely reproducible from the frozen files.
- **The reference for reading JS-01.** The contrast is the point: AF-01 (pip, flat, direct) needs no reasoning beyond "bump to the patched version," and the deterministic baseline reaches the same result. JS-01 (npm, transitive, override) is where the LLM must reason about graph topology and downstream toolchain constraints — and where deterministic SCA cannot follow. The thesis's contribution lives in that gap, and AF-01 is the honest control that makes the gap legible.
- **Ecosystem-dependence, stated plainly.** AF-01 is direct evidence that the deterministic baseline is not uniformly ineffective (see `THESIS_LIMITATIONS.md` §1 and `docs/01-overview.md`); the LLM layer is evaluated specifically where deterministic strategies fail, not claimed uniformly.

**Limitations to read alongside this case:** AF-01 does not demonstrate LLM value over deterministic remediation (§12.1); `test_success`/`runtime_success` are environment/stage artifacts, not remediation signals; and, as with every scenario, "target CVE removed" concerns the *selected* advisory, not the package's total security posture. Full list: `THESIS_LIMITATIONS.md`.

---

*Evidence root: [`results/execution_evidence/AF-01/`](../../results/execution_evidence/AF-01/). Companion: [`JS-01_vm2_case_study.md`](JS-01_vm2_case_study.md). Audit context: [`docs/audit/phase4_scenario_audit.md`](../audit/phase4_scenario_audit.md).*
