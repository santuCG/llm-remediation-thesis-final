# Finding: Two Independent CVE-Detection Gaps During Regeneration (AF-06, JS-06)

**Status:** Investigation complete for AF-06 (fully root-caused) and substantially advanced
for JS-06 (root-caused to Syft's SBOM cataloging stage, deterministic and reproducible, but
the exact per-package inclusion/exclusion rule is **not** fully characterized despite an
extended investigation — see "Extended investigation" below). The pipeline defect that let
both scenarios select the wrong CVE **silently** has been fixed (`prioritize.py`, Fix #10 in
`CHANGELOG_V2.md`; commits `a7606850`/`36cc51fd`) and both scenarios re-dispatched: AF-06 now
correctly targets its preregistered CVE end-to-end; JS-06 correctly fails loudly rather than
substituting a different CVE, since the underlying Syft gap is a separate, unresolved problem
— see "Decisions needed" at the end.

**Context:** During regeneration of the 18 pre-registered scenarios under Pipeline v2.0 /
prompt v1.2, two scenarios (AF-06, JS-06) silently selected a different CVE/package than
the one pre-registered. Both were caught only because the resulting `metrics.json` was
cross-checked against the pre-registered scenario data (`results/scenarios/final_18_scenarios.json`)
and against NVD directly — the pipeline itself gave no warning or error in either case. A
subsequent cross-check against the *original* (pre-this-session) `results/execution_evidence/`
confirmed the substitution is not new — see "Historical scope" below.

This document investigates *why*, following a specific evidence checklist, before any
decision is made about whether or how to fix it.

---

## Scenario 1: AF-06 (jinja2, CVE-2024-56326) — CVSS version disagreement

### What was pre-registered
`applications/airflow`, `jinja2@3.1.4`, `CVE-2024-56326` (`GHSA-q2x7-8rv6-6q7h`),
recorded CVSS score **7.8**, fix version `3.1.5`, upgrade type "patch".

### What the pipeline actually selected on regeneration
`werkzeug`/`CVE-2024-34069` — a completely different package and CVE (which happens to be
AF-09's own pre-registered target).

### Root cause, evidence-traced

1. **The vulnerability is still genuinely present.** A fresh Grype scan of the current
   `applications/airflow` dependency tree detects `GHSA-q2x7-8rv6-6q7h` on `jinja2@3.1.4`,
   exactly matching the pre-registered package/version/GHSA ID, with `relatedVulnerabilities`
   correctly containing `CVE-2024-56326`.

2. **Grype reports this vulnerability's severity as `"Medium"`**, not High/Critical:
   ```json
   {"id": "GHSA-q2x7-8rv6-6q7h", "severity": "Medium", "related": ["CVE-2024-56326"], "fix.state": "fixed"}
   ```

3. **`scripts/remediation/prioritize.py:100-102`** filters candidates before anything else:
   ```python
   if severity not in ['high', 'critical']:
       continue
   ```
   This runs *before* the `TARGET_CVE` override logic ever executes (`prioritize.py:161-178`).
   A vulnerability filtered out here is invisible to the override, which then silently falls
   back to `candidates[0]` — whichever unrelated vulnerability ranks highest overall.

4. **Why Grype says "Medium" when the pre-registered CVSS score is 7.8**: confirmed directly
   from GitHub's own advisory record (`gh api advisories/GHSA-q2x7-8rv6-6q7h`):
   ```
   severity: medium
   cvss_v3: {vector: 'CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H', score: 7.8}
   cvss_v4: {vector: 'CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N', score: 5.4}
   ```
   **The same advisory carries two different CVSS scores from two different scoring
   standards for the same vulnerability**: 7.8 under CVSS v3.1 (which conventionally maps
   to "High", 7.0–8.9), and 5.4 under CVSS v4.0 (which maps to "Medium"). GitHub's own
   `severity` field — the field Grype ingests and exposes verbatim — is derived from the
   **v4.0** score, not the v3.1 score.

5. **A data inconsistency in the original pre-registration is also exposed by this**: the
   pre-registered scenario recorded `"cvss_score": 7.8` paired with
   `"cvss_vector": "CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P"` — a
   v4.0 *vector string* attached to the v3.1 *numeric score*. The two don't belong together;
   the v4.0 vector's actual score is 5.4, not 7.8. This mismatch predates this session's
   engineering work and was not introduced by anything done here — it was present in the
   original 2026-07-08 scenario snapshot.

### Interpretation

This is not a data-freshness problem (nothing changed about the vulnerability itself) and
not a Grype bug. It's a genuine, real-world instance of **CVSS version disagreement**: NVD
and GHSA increasingly publish both v3.1 and v4.0 scores for the same CVE, and these two
standards can and do disagree on qualitative severity for the same vulnerability, because
v4.0 changed how several metrics (notably attack complexity/requirements and scope) are
weighted. A scanner or pipeline that keys its "high/critical" filter off a single
scanner-reported severity string is exposed to whichever CVSS version that scanner's
upstream data source treats as authoritative for the severity label — which may not match
the version a researcher had in mind when originally recording a CVSS score for
pre-registration.

---

## Scenario 2: JS-06 (flatted, CVE-2026-33228) — Failure Category A: SBOM cataloging limitation

Syft omitted `flatted` during SBOM cataloging. Classified here as **Failure Category A** to distinguish it explicitly from JS-07's failure, discovered later during regeneration (`CHANGELOG_V2.md`, "Finding: `manifest_editor.py` only patches the root `package.json`"): Category A is about what the pipeline can *see* (the vulnerability never reaches the SBOM); JS-07 is **Failure Category B** — what the pipeline can *reach* (the vulnerability is seen and a fix attempted, but a copy of the package sits outside the manifest editor's scope). Different failure category, different underlying fix, not conflated.

### What was pre-registered
`applications/juice-shop`, `flatted@3.2.9`, `CVE-2026-33228` (`GHSA-rf6f-7fwh-wjgh`),
CVSS v4.0 score 8.9, fix version `3.4.2`, marked `"is_direct_dependency": true`.

### What the pipeline actually selected on regeneration
`lodash`/`CVE-2021-23337` — again, a completely different package and CVE.

### Investigation, following the requested checklist

**1. Grype DB version.** From `grype-db-metadata.json` captured during the actual CI run:
```
schemaVersion: v6.1.9
built:         2026-08-03T07:21:25Z
from:          vulnerability-db_v6.1.9_2026-08-03T00:38:44Z...
```
The database was built **less than 24 hours before the scan**. This rules out staleness —
if anything, this is about as fresh as a Grype DB can be.

**2. Is the advisory itself recent enough to plausibly be missing from any DB?** Checked
directly against GitHub's advisory API (`gh api advisories/GHSA-rf6f-7fwh-wjgh`):
```
type: reviewed (GitHub-curated, not a raw OSV import)
published_at:     2026-03-19T17:43:54Z
nvd_published_at: 2026-03-20T23:16:46Z
withdrawn_at:     null
severity: high
cvss_v4: {score: 8.9, vector: 'CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P'}
```
Published and NVD-indexed over **4.5 months** before this scan, GitHub-reviewed, not
withdrawn. This is a mature, well-established advisory by any reasonable standard — not a
same-week disclosure a database could plausibly not have ingested yet.

**3. Syft SBOM contents — does the package appear at all?** Checked directly:
```python
# baseline-sbom.json from the actual CI run
packages = [p for p in sbom['packages'] if p['name'].lower() == 'flatted']
# -> 0 matches
```
**No.** The package that Grype would need to check against its database is never given to
it in the first place — the SBOM the pipeline generates does not list `flatted` at all.
This is the actual root cause; everything downstream of this (Grype's DB, Grype's matching)
is irrelevant to what actually happened.

**4. Reproduced outside the CI pipeline**, per your request, using the *exact* pipeline
binary versions (Syft v1.44.0, Grype v0.112.0 — downloaded and version-verified to match
`grype-db-metadata.json` byte-for-byte) against the real, locally-installed
`applications/juice-shop/node_modules`:
```
Full syft dir:. scan (same --exclude flags as the workflow): 2125 packages total.
express: 2 entries (4.18.2, 4.22.2)  <- correctly detected, proves the cataloger works
flatted: 0 entries                   <- reproduces the CI gap exactly, outside CI
```
This rules out anything CI-runner-specific (Linux vs. Windows, container filesystem
quirks, GitHub Actions environment variables) — the exact same omission reproduces on a
completely different machine.

**5. Whether the vulnerability namespace changed.** Grype's vulnerability database
organizes records by namespace (e.g., `github:language:javascript`). A namespace mismatch
would prevent Grype from *matching* a package it was given, even if the package were
present in an SBOM. To test this independently of Syft's cataloging gap, a minimal SBOM
containing only `flatted@3.2.9` (with a proper `pkg:npm/flatted@3.2.9` purl) was
constructed by hand and fed directly to Grype:
```
grype sbom:minimal-flatted-sbom.json
-> GHSA-rf6f-7fwh-wjgh | severity: High | related: [CVE-2026-33228] | fix: 3.4.2  (MATCH)
-> GHSA-25h7-pfq9-p65f | severity: High | related: [CVE-2026-32141] | fix: 3.4.0  (bonus: a second, unrelated CVE also affects this version)
```
**Grype correctly matches the package the instant it's given the chance to.** This
conclusively rules out a namespace mismatch, a DB gap, or any Grype-side matching defect —
Grype's database and matcher are functioning exactly as they should.

**6. Candidate mechanism found via Syft's own issue tracker — directionally consistent, but
not a full explanation.** Searched Syft's GitHub repo for prior art and found a documented
mechanism, stated by Syft's own maintainers in [PR #5065](https://github.com/anchore/syft/pull/5065)
("exclude npm devOptional dependencies by default", closing [issue #4982](https://github.com/anchore/syft/issues/4982)):

> "npm records packages that are only reachable through dev dependencies... with
> `"devOptional": true` in `package-lock.json`. Syft already skips `"dev": true` packages
> when dev dependencies are excluded, but `devOptional` ones slipped through..."

This confirms Syft has *some* documented, intentional default behavior around excluding
npm dev-only packages. It does **not**, by itself, prove that behavior is what caused
`flatted` specifically to be omitted — see "Extended investigation" below, which tested
this hypothesis directly against the full dependency set and found it does not cleanly
separate present-vs-omitted packages.

**7. Confirming `flatted`'s position in the dependency tree.** Traced the exact chain in
`package-lock.json`:
```python
# Which package requires flatted?
node_modules/flat-cache -> requires flatted ^3.2.9   (flat-cache itself: "dev": true)
```
`flatted` is pulled in *only* via `flat-cache`, a caching library used internally by
ESLint. It is not listed in either `dependencies` or `devDependencies` directly in
`package.json` — it's transitive, several levels down the lint/type-check tooling chain
(`flat-cache` is itself `"dev": true`). **The pre-registered scenario's
`"is_direct_dependency": true` claim for flatted does not hold in the current dependency
tree** — whether that was ever accurate, or drifted since the 2026-07-08 snapshot, this
investigation cannot determine without the original snapshot's raw SBOM, which wasn't
preserved. (This dependency-type question turned out to be broader than just flatted — see
"Related finding" below.)

### Extended investigation: does `dev:true` alone explain the omission?

The initial conclusion — "Syft excludes dev dependencies by design" — was too strong given
Syft's own SBOM contains dev-only packages that *are* present, which contradicts a clean
"all `dev:true` packages are excluded" rule. This was tested directly rather than assumed
away, following the requested methodology (compare present vs. omitted packages across the
dependency graph, lockfile flags, and SBOM contents; do not stop at a plausible-sounding
partial explanation).

**Determinism check first.** Before investigating *why* packages are omitted, confirmed the
omission itself is not scan noise: a local Windows reproduction (same Syft/Grype binary
versions as the CI run) against the real `node_modules` matched the CI-generated SBOM on
1452 of 1452 packages, differing only in 2–3 platform-path-format entries. The omission
pattern is fully deterministic, not an artifact of a particular run.

**Hypothesis A — production-reachability graph.** Built a full dependency-reachability
graph starting only from `package.json`'s own `dependencies` (i.e., "would this package be
installed if `devDependencies` did not exist at all"). **Disproved**: several packages that
Syft's SBOM *does* include (e.g., `colorette`, `nanoid`) are not reachable via this graph
either — so "reachable from production dependencies" is not the rule Syft is actually
applying.

**Hypothesis B — lockfile `dev`/`optional`/`peer`/`bin` flag profile.** Checked all 373
top-level `"dev": true` entries in `node_modules` against the generated SBOM: 131 are
present, 242 are missing (including `eslint`, `jest`, `mocha`, `cypress`, and `chai`
themselves — i.e., Syft's SBOM does not even fully exclude the packages a developer would
most obviously call "the dev toolchain"). Compared each group's lockfile flag profile
(`dev`, `optional`, `peer`, `bin` presence) looking for a combination that cleanly separates
present from missing. **No clean separating rule was found** — both groups contain
overlapping flag-profile combinations.

**Conclusion of the extended investigation.** The omission of `flatted` is real,
deterministic, and reproducible outside CI, and is directionally consistent with Syft's
documented default dev-dependency exclusion (per PR #5065) — but the precise per-package
rule Syft applies could not be fully characterized from the outside with the evidence
available (lockfile flags and reachability graphs alone), given it does not cleanly account
for the 131/242 split observed across all `dev:true` packages in this project. Established
with confidence: **Syft v1.44.0 consistently omitted `flatted` from the generated SBOM
under the evaluated project configuration.** Since a manually-constructed SBOM containing
the identical package was correctly matched by Grype (checklist item 5, above), **the
detection gap originates during package cataloguing rather than vulnerability matching.**
Not established with confidence: a general, provable rule of the form "Syft excludes dev
dependencies" that would predict this outcome for any given package in advance.

### Interpretation

Unlike AF-06, this has nothing to do with vulnerability data freshness, severity
reclassification, or Grype's matching at all. The fault is isolated to Syft's cataloging
stage: the package the pipeline needed to hand to Grype was never included in the SBOM in
the first place. The CVE is real, current, and would presumably be detected if Syft's SBOM
included `flatted` — but under the pipeline's current default Syft invocation, it is
structurally invisible before Grype, or `prioritize.py`, ever get involved, and the exact
mechanism by which Syft decided to omit this specific package (as opposed to the 131 other
`dev:true` packages it retained) remains unresolved.

---

## Historical scope: this is not new to this session

Cross-checked all 18 scenarios' preregistered CVE (`results/scenarios/final_18_scenarios.json`)
against the **original**, pre-this-session `results/execution_evidence/<ID>/metrics.json` for
each scenario (i.e., the dataset as it existed before any Pipeline v2.0 engineering work
began). 16 of 18 match exactly. AF-06 and JS-06 do not:

- `results/execution_evidence/AF-06/metrics.json` (original) already shows
  `werkzeug`/`CVE-2024-34069` — not jinja2/`CVE-2024-56326`.
- `results/execution_evidence/JS-06/metrics.json` (original) already shows
  `lodash`/`CVE-2021-23337` — not flatted/`CVE-2026-33228`.

This confirms the silent-substitution bug in `prioritize.py` has been present since the
**original** dataset generation, not introduced by any change made this session. It also
means the existing `THESIS_DRAFT_V3.md` was already written around the substituted data:
its own References section cites `CVE-2021-23337` and `CVE-2024-34069` (not the
preregistered CVEs), and its Table 4 JS-06 row matches lodash's actual metrics, not
flatted's. This needs correcting as part of thesis-draft integration — see "Decisions
needed."

## Related finding: `is_direct_dependency` mismatch is broader than JS-06

Checklist item 7 above raised a direct-vs-transitive discrepancy for `flatted`. Cross-checked
the preregistered `is_direct_dependency` field against the current `package.json` for all 9
JS scenarios: **6 of 9 (JS-01, JS-02, JS-03, JS-04, JS-06, JS-07) are recorded as "direct"
but are actually transitive** in the current dependency tree; only JS-05, JS-08, JS-09
match. Spot-checked JS-02/`handlebars` specifically against the *original* historical
evidence (which also claims "direct") vs. the current live pipeline's own
`_get_dependency_type()` computation — the original historical claim is wrong by the same
live computation now used by the pipeline (`handlebars` is confirmed absent from both
`dependencies` and `devDependencies` in the current `package.json`). This suggests the
current code's dependency-type classification is more accurate than the original
pre-registration, but it also means 6 of 9 JS scenarios' preregistered metadata needs a
correction or a disclosed caveat before the thesis treats `is_direct_dependency` as
reliable. Not yet resolved — see "Decisions needed."

---

## Do we have to change our prioritization logic?

**Two different problems, two different decisions. Both have now been decided.**

**AF-06's class of failure (severity reclassification defeating an explicit target): YES,
implemented.** `prioritize.py`'s severity filter (`high`/`critical` only) ran *before* the
`TARGET_CVE` override, so an explicit, deliberate request for a specific pre-registered CVE
could be silently defeated by Grype's current severity label — even when the researcher had
already decided, at pre-registration time, that this specific CVE is the one being studied.
Fixed: an explicit `TARGET_CVE` match now bypasses the severity filter (`prioritize.py`
restructure, `CHANGELOG_V2.md` Fix #10, commits `a7606850`/`36cc51fd`). Re-dispatched AF-06
under the fix: succeeded end-to-end against `jinja2`/`CVE-2024-56326` as originally
preregistered (`build_success`/`test_success`/`dependency_verified`/`rescan_success` all
`true`).

**JS-06's class of failure (Syft omitting the package from the SBOM): NO, confirmed
correctly.** This is not a `prioritize.py` problem, and changing its logic cannot fix it,
because the vulnerability never reaches `prioritize.py` in the first place — it never
reaches Grype either. Re-dispatching JS-06 under the same `prioritize.py` fix confirms this
exactly as predicted: the run correctly fails loudly (`TARGET_CVE=CVE-2026-33228 was not
found among any structurally-valid candidate`) rather than silently substituting `lodash`
again — proving the fix does its job (no silent substitution) without claiming to solve a
problem it structurally cannot solve. Any actual fix for JS-06 belongs upstream, in how the
SBOM is generated (e.g., a Syft cataloger flag to include dev dependencies) — a workflow
change, contingent on the still-open scoping question below.

**The observability fix — implemented, applies to both.** `prioritize.py`'s `TARGET_CVE`
override no longer fails silently. If no candidate matches the requested CVE, the pipeline
now logs every structurally-valid CVE/GHSA ID that *was* available and exits with a hard
failure, instead of falling through to the top-ranked candidate. This is what turned JS-06's
rerun from "silently produces wrong evidence" into "correctly and loudly refuses to
proceed" — the intended outcome given the underlying Syft gap remains unresolved.

---

## Decisions needed (not yet made)

1. ~~Add the loud-failure warning to `prioritize.py`~~ — **Done** (Fix #10).
2. ~~Should `TARGET_CVE` bypass the severity/fix-state filter when explicitly set?~~ —
   **Decided yes, implemented** (Fix #10). Automatic-discovery behavior (no `TARGET_CVE`)
   is unchanged.
3. AF-06 and JS-06 as *originally* regenerated (before Fix #10): superseded by the re-runs
   above — the original wrong-CVE evidence for both should not be used. Per the agreed
   disclosure language (see `CHANGELOG_V2.md`/thesis integration task), state explicitly
   that both were found to have been silently substituted in the original dataset and were
   regenerated against their intended preregistered targets after the pipeline was
   corrected.
4. **Still open**: should the Syft invocation be changed to include dev dependencies for
   JS-06, and if so, does that change what "in scope" means for this thesis's 18 scenarios
   (development-toolchain vulnerabilities vs. only what Juice Shop/Airflow ship)? This is a
   methodology decision, not an engineering one — JS-06 remains unresolved pending it, and
   is not being force-regenerated against a substitute CVE.
5. **Still open**: the `is_direct_dependency` mismatch (6 of 9 JS scenarios — see "Related
   finding" above) needs a decision on how to correct or caveat the preregistered metadata
   before the thesis treats that field as reliable.
6. **Still open**: integrate the corrected AF-06/JS-06 findings, the historical-scope
   finding, and the disclosure statement into `THESIS_DRAFT_V3.md` (Methodology Limitations
   / Findings chapters), including fixing its References section, which currently cites the
   substituted CVEs (`CVE-2021-23337`, `CVE-2024-34069`) rather than the preregistered ones.

Pipeline code has been changed as a result of this investigation — see `CHANGELOG_V2.md`
Fix #10. No changes have been made to the Syft invocation, the severity/fix-state filter's
role in automatic discovery, or any thesis document.
