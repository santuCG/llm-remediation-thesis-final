# Case Study — JS-01: `vm2` (CVE-2023-32314) in OWASP Juice Shop

> **Post-freeze documentation artifact (2026-08-02).** Derived entirely from the frozen evidence in `results/execution_evidence/JS-01/`. Every figure below is quoted from those files; nothing is re-run or re-computed. This case study illustrates the pipeline end-to-end and is deliberately honest about the evidence's known imperfections (see §12), because JS-01 is one of the scenarios the audit flagged as internally inconsistent — and its scientific story is *more* compelling for it.

---

## 1. Why this scenario is worth a case study

JS-01 is the thesis's most instructive scenario. It is not a clean "bump the version and win" — it is a case where an LLM, given a critical vulnerability and a real toolchain constraint, performed graph-aware reasoning, recognised that a mechanical override could not safely fix the application, and **recommended manual review rather than over-claiming success.** It simultaneously exposes the central methodological distinction of the thesis: *scanner-level vulnerability eradication* and *full application build success* are different properties, and this scenario achieves the first without the second.

---

## 2. Original vulnerability

*(Source: `results/execution_evidence/JS-01/selected-candidate.json`)*

| Field | Value |
|---|---|
| Package | `vm2` |
| Vulnerable version | `3.9.17` |
| Advisory | `GHSA-whpj-8f3w-67p5` (alias `CVE-2023-32314`) |
| Severity | Critical |
| CVSS | 9.8 |
| EPSS | 0.08127 |
| CISA KEV | No |
| Fixed version | `3.9.18` |

`vm2` is a sandbox library with a critical sandbox-escape / remote-code-execution class vulnerability. Crucially, it is **not a direct dependency** of Juice Shop — it enters transitively:

```
juice-shop@15.3.0
└─ juicy-chat-bot@0.8.0
   └─ vm2@3.9.17        ← vulnerable, nested one level down
```

This transitive placement is the entire reason the scenario is interesting: a naive `npm install vm2@3.9.18` at the top level does not govern a version required by an intermediate parent.

---

## 3. Baseline Grype findings

*(Source: `results/execution_evidence/JS-01/baseline-grype.json`)*

The baseline scan of the unmodified, vulnerable application confirmed the target advisory against the installed transitive version:

- `vm2 @ 3.9.17` → `GHSA-whpj-8f3w-67p5` **present**.
- Total match entries in the baseline report: **383**.

This established the experimental control.

---

## 4. Candidate ranking (prioritisation)

*(Source: `results/execution_evidence/JS-01/candidate-ranking.json` — 111 ranked candidates)*

The prioritisation stage ranks all discovered vulnerabilities by the pre-registered policy **KEV → EPSS → CVSS (descending)**. The top of the ranking for this application was, for example:

| Rank | Package | Advisory | KEV | EPSS | CVSS |
|---|---|---|---|---|---|
| 1 | `lodash` | GHSA-35jh-r3h4-6jhm | No | 0.21333 | 7.2 |
| 2 | `jsonwebtoken` | GHSA-c7hr-j4mj-j2w6 | No | 0.08655 | 0.0 |

`vm2` is **not** the top-ranked candidate. JS-01 is a *pre-registered* scenario, so the orchestrator overrides the ranking to select the pre-registered target (`vm2` / `CVE-2023-32314`) — the ranking is retained as evidence of the prioritisation logic, while the scenario definition fixes which vulnerability is studied. This separation (ranking policy vs. pre-registered target) is deliberate and keeps the 18 scenarios controlled rather than scanner-order-dependent.

---

## 5. LLM prompt (abridged)

*(Source: `results/execution_evidence/JS-01/llm-request.json`; system instruction and generation config verbatim, dependency context abridged)*

**System instruction (verbatim):**

> "You are a Senior DevSecOps AI Agent... You must critically evaluate the topological subgraph. Provide comprehensive reasoning on why the vulnerability exists. Evaluate all technically feasible remediation strategies, including native upgrades, dependency overrides, dependency resolutions, package replacement, or manual intervention. Recommend the safest strategy that preserves compatibility and explain why alternative strategies were rejected. Do not hallucinate package versions. Recommend versions that actually exist and solve the CVE."

**Generation config:** `temperature 0.0, topP 1.0, topK 1, seed 42`, `responseMimeType application/json` with a strict `responseSchema` (required fields: `reasoning`, `strategy`, `remediation_type`, `recommended_package_version`, `manifest_patch`).

**User content** supplied: the vulnerability intelligence (§2), the full `npm ls` / `npm explain` topological subgraph, and — because this is the **retry** invocation (attempt 2) — the previous attempt's build failure:

> "### Baseline Scanner Build Failure — A deterministic vulnerability scanner previously attempted to fix this by blindly updating the dependency to 3.9.18, but it caused the following compiler/build failure in the legacy application:
> `lib/insecurity.ts(58,51): error TS2531: Object is possibly 'null'.` … `error TS1005: '?' expected (from transitive @types updates)`
> If the version bump caused this compiler mismatch, you must recommend an alternative strategy or a different version that avoids this build breakage."

This is the key experimental design element: the LLM is **told** the naive fix breaks the build, and asked to reason about it.

---

## 6. LLM response

*(Source: `results/execution_evidence/JS-01/llm-response.json`, verbatim reasoning)*

> **reasoning:** "The vulnerability GHSA-whpj-8f3w-67p5 affects vm2 at version 3.9.17. Although vm2 3.9.18 contains the vulnerability fix, attempting to force this update via dependency overrides triggers transitive updates to @types packages (@types/babel__traverse, @types/lodash) containing modern TypeScript syntax unsupported by the project's legacy TypeScript compiler (causing TS1005 errors), alongside nullability errors (TS2531) in lib/insecurity.ts. Because a single package override cannot resolve these multi-package compiler incompatibilities without upgrading the project TypeScript version or refactoring application code, automated remediation is unsafe and manual review is required."
>
> **strategy:** `manual_review` · **remediation_type:** `Manual Review` · **recommended_package_version:** `3.9.18` · **manifest_patch:** `{ operation: add_override, package: vm2, constraint: 3.9.18 }`

Three things make this scientifically notable:
1. **Correct fixed version, no hallucination** — it identified `3.9.18`, the genuine patched release.
2. **Genuine constraint reasoning** — it did not stop at "bump to 3.9.18"; it traced the *downstream* consequence (forcing the update pulls modern `@types` definitions incompatible with the project's pinned legacy TypeScript) and connected it to the specific compiler errors it was shown.
3. **Appropriate self-limitation** — it concluded automated remediation is *unsafe* and flagged manual review, rather than falsely reporting a clean fix. This is exactly the "treat the LLM output as a hypothesis" posture the thesis argues for.

---

## 7. Manifest diff

The recommended patch is a transitive **override** forcing the nested `vm2` to the fixed version:

```jsonc
// package.json (conceptual patch applied by the pipeline)
"overrides": {
  "vm2": "3.9.18"
}
```

This is the correct npm mechanism for governing a transitive version that an intermediate parent (`juicy-chat-bot`) would otherwise pin to `3.9.17`.

> **Evidence caveat:** In the frozen record, both `package-before.json` and `package-after.json` already contain `overrides: { vm2: "3.9.18" }` — i.e., the recorded "before" manifest is contaminated with the applied fix, so the two files do not show a literal delta. This is a documented artifact of a pre-fix retry-restore bug (see §12 and `docs/audit/phase4_scenario_audit.md`), not evidence that no change occurred. The authoritative before/after signal is the **scan** delta in §9 (`vm2 3.9.17` present at baseline → target advisory absent after remediation).

---

## 8. Dependency resolution

*(Source: `npm ls` context embedded in `results/execution_evidence/JS-01/llm-request.json`)*

After the override, npm resolves the transitive node to the enforced version:

```
juice-shop@15.3.0
└─ juicy-chat-bot@0.8.0
   └─ vm2@3.9.18   (overridden: true)   ← was 3.9.17
```

`npm explain vm2` confirms the single install location `node_modules/vm2` at `3.9.18` with `overridden: true`, dependent chain `juicy-chat-bot → juice-shop`. The dependency-graph verification stage therefore confirms the intended version is what actually resolved — not merely what was requested.

---

## 9. Rescan results

*(Source: `results/execution_evidence/JS-01/rescan.json` vs `baseline-grype.json`)*

| | Baseline | Post-remediation |
|---|---|---|
| `vm2` target advisory `GHSA-whpj-8f3w-67p5` | **present** (`3.9.17`) | **absent (eradicated)** |
| Total Grype match entries | 383 | 187 |

The target advisory is eradicated at the scanner level. (The large drop in *aggregate* matches from 383→187 is driven by the override cascading a broader sub-dependency re-resolution and should not be read as a direct measure of remediation quality — consistent with `docs/05` Observation on aggregate counts. The scientifically load-bearing result is the target-advisory eradication.)

---

## 10. Build and test validation

*(Source: `results/execution_evidence/JS-01/build.log`, `test.log`)*

- Dependency **install** succeeded.
- `npm run build:server` (`tsc`) **failed** with the same `TS1005` errors in `@types/babel__traverse` and `@types/lodash` that the LLM predicted — a **pre-existing toolchain incompatibility** present in the baseline and orthogonal to the remediation (no remediation modifies any `@types/*` package).
- Tests did not pass in the runner (`ng` CLI toolchain limitation).

So the application's server does **not** fully compile under its pinned legacy TypeScript toolchain — exactly the outcome the LLM anticipated and the reason it recommended manual review.

---

## 11. Final metrics

*(Source: `results/execution_evidence/JS-01/metrics.json`)*

| Field | Value | Reading |
|---|---|---|
| `selected_cve` | `GHSA-whpj-8f3w-67p5` | target advisory |
| `dependency_verified` | `true` | override resolved to `3.9.18` in the graph |
| `rescan_success` | `true` | target advisory eradicated |
| `build_success` | `true` | *install* succeeded (does not assert `tsc` compilation) |
| `test_success` | `false` | test toolchain failure |
| `retry_count` / `llm_iteration` | `1` / `2` | this is the retry (attempt 2) |
| `strategy` | `manual_review` | LLM's final strategy |

---

## 12. Evidence-integrity notes (honest disclosure)

This frozen record carries known inconsistencies, all documented in the audit trail. They are disclosed here rather than smoothed over:

1. **`remediation_type` mismatch.** `metrics.json` records `"Transitive Override"` while the LLM's own `llm-response.json` says `"Manual Review"`. This is a documented metric-labelling bug (root-caused and fixed in the pipeline code post-audit; not retroactively rewritten into this historical record). *(Ref: `docs/audit/phase4_scenario_audit.md`.)*
2. **`dependency_type: "direct"`** in `metrics.json` is incorrect — `vm2` is transitive (via `juicy-chat-bot`). Same class of historical metric defect.
3. **`build_success: true` with `failure_stage: "build"`** co-occur — an artifact of the pre-fix metric semantics; `build_success` here reflects the install step, not `tsc` compilation.
4. **`package-before.json` contamination** — the recorded "before" manifest already contains the applied override (§7).
5. **Applied-anyway behaviour.** Although the LLM's *strategy* was `manual_review`, it still emitted a `manifest_patch`, and the deterministic apply-layer applied it — which is why the CVE was eradicated in the scan despite the "manual review" recommendation. This gap between the LLM's advisory label and the pipeline's mechanical application is itself a genuine finding.

A re-execution of JS-01 under the post-fix pipeline (with corrected metric semantics) is available in the audit evidence; it reaches the same substantive outcome (target CVE eradicated via retry).

---

## 13. Interpretation

JS-01 is the clearest single demonstration of the thesis's core claims:

- **Graph-aware reasoning, not version-bumping.** The LLM located the vulnerability in the transitive subgraph, chose the correct npm mechanism (override), *and* reasoned about the second-order compiler consequence — behaviour a deterministic SCA "bump to fixed version" cannot exhibit.
- **Honest self-limitation.** Faced with a fix that cannot be made safe without a TypeScript upgrade or code refactor, the LLM recommended manual review instead of falsely claiming success. For a decision-support tool, correctly saying "a human is needed here" is a *feature*, not a failure.
- **The measurement distinction the thesis is built on.** The target vulnerability was eradicated at the scanner level (`rescan_success: true`) while the application did not fully compile (`tsc` toolchain failure). Treating these as one metric would misrepresent both; the pipeline deliberately keeps them separate, and this scenario is why that separation matters.

**Limitations to read alongside this case:** the scanner-level eradication does not imply a compiling, fully-functional application (the `tsc` toolchain failure is pre-existing and unresolved); "target CVE removed" is not "`vm2` is now safe" (`vm2 3.9.18` remains an abandoned package); and the frozen metrics for this specific scenario contain the documented inconsistencies in §12. These are catalogued in `THESIS_LIMITATIONS.md`.

---

*Evidence root: [`results/execution_evidence/JS-01/`](../../results/execution_evidence/JS-01/). Audit context: [`docs/audit/phase4_scenario_audit.md`](../audit/phase4_scenario_audit.md).*
