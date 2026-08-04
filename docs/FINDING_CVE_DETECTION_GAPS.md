# Finding: Two Independent CVE-Detection Gaps During Regeneration (AF-06, JS-06)

**Status:** Investigation complete, root-caused with reproducible evidence. No pipeline code
has been changed as a result of this finding — see "Decisions needed" at the end.

**Context:** During regeneration of the 18 pre-registered scenarios under Pipeline v2.0 /
prompt v1.2, two scenarios (AF-06, JS-06) silently selected a different CVE/package than
the one pre-registered. Both were caught only because the resulting `metrics.json` was
cross-checked against the pre-registered scenario data (`results/scenarios/final_18_scenarios.json`)
and against NVD directly — the pipeline itself gave no warning or error in either case.

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

## Scenario 2: JS-06 (flatted, CVE-2026-33228) — Syft excludes dev-only dependencies by design

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

**6. Root cause, confirmed via Syft's own issue tracker.** Searched Syft's GitHub repo for
prior art and found the exact, documented mechanism, stated by Syft's own maintainers in
[PR #5065](https://github.com/anchore/syft/pull/5065) ("exclude npm devOptional
dependencies by default", closing [issue #4982](https://github.com/anchore/syft/issues/4982)):

> "npm records packages that are only reachable through dev dependencies... with
> `"devOptional": true` in `package-lock.json`. **Syft already skips `"dev": true` packages
> when dev dependencies are excluded**, but `devOptional` ones slipped through..."

This is Syft's **documented, intentional default behavior**: npm packages reachable only
through `devDependencies` are excluded from the generated SBOM, because SBOMs conventionally
describe what ships in production, not the full local development toolchain.

**7. Confirming `flatted` is genuinely dev-only in this dependency tree.** Traced the exact
chain in `package-lock.json`:
```python
# Which package requires flatted?
node_modules/flat-cache -> requires flatted ^3.2.9   (flat-cache itself: "dev": true)
```
`flatted` is pulled in *only* via `flat-cache`, a caching library used internally by
ESLint. It is not listed in either `dependencies` or `devDependencies` directly in
`package.json` — it's purely transitive, several levels down the lint/type-check tooling
chain (`flat-cache` is itself `"dev": true`). **The pre-registered scenario's
`"is_direct_dependency": true` claim for flatted does not hold in the current dependency
tree** — whether that was ever accurate, or drifted since the 2026-07-08 snapshot, this
investigation cannot determine without the original snapshot's raw SBOM, which wasn't
preserved.

### Interpretation

Unlike AF-06, this has nothing to do with vulnerability data freshness, severity
reclassification, or Grype at all. **The vulnerable package is a transitive dependency of
the ESLint toolchain, not of the shipped application** — and Syft, by design, does not
include dev-only npm dependencies in its SBOM output. The CVE is real, current, and would
be correctly detected if Syft's cataloger were configured to include dev dependencies (or
if a different SBOM-generation approach were used) — but under the pipeline's current
default Syft invocation, it is structurally invisible before Grype, or `prioritize.py`,
ever get involved.

---

## Do we have to change our prioritization logic?

**These are two different problems requiring two different (and independent) decisions —
neither has been implemented.**

**For AF-06's class of failure (severity reclassification defeating an explicit target):**
`prioritize.py`'s severity filter (`high`/`critical` only) runs *before* the `TARGET_CVE`
override, so an explicit, deliberate request for a specific pre-registered CVE can be
silently defeated by Grype's current severity label — even when the researcher has already
decided, at pre-registration time, that this specific CVE is the one being studied. Arguably
yes, this needs a change: an explicit `TARGET_CVE` match should bypass the severity (and
possibly the fix-state) filter, since those filters exist to guide *automatic* candidate
discovery, not to override a human's explicit, already-made selection. This is a scoped,
well-understood change, but it's a decision about experimental design, not just engineering.

**For JS-06's class of failure (Syft excluding dev dependencies):** No — this is not a
`prioritize.py` problem at all, and changing its logic cannot fix it, because the
vulnerability never reaches `prioritize.py` in the first place; it never reaches Grype
either. Any fix belongs upstream, in how the SBOM is generated (e.g., an
`--select-catalogers` flag or equivalent to include dev dependencies) in
`generic-remediation.yml`/`grype-baseline.yml`'s `syft` invocation — a workflow change, not
a prioritization-logic change. Whether that's the right fix depends on a scoping question
this document does not answer: should this pipeline's scenarios be allowed to target
development-toolchain vulnerabilities at all, or should the scope remain "vulnerabilities in
what Juice Shop/Airflow actually ship"? That's a methodology decision, not an engineering one.

**A third, independent, and probably highest-value fix applies to both:** regardless of
which (if either) of the above is adopted, `prioritize.py`'s `TARGET_CVE` override should
**never fail silently**. Right now, if no candidate matches the requested CVE, the code
falls through to the default top-ranked candidate with zero warning — which is the actual
mechanism that let both AF-06 and JS-06 run to completion producing plausible-looking, but
wrong, evidence. This is a pure observability fix (log/error loudly on no-match), separable
from the two scoping questions above, and it's what prevented this from being caught faster.

---

## Decisions needed (not yet made)

1. AF-06 and JS-06 as already regenerated: discard, or keep with a documented substitution note?
2. Add the loud-failure warning to `prioritize.py` before continuing regeneration? (Low risk, high value, doesn't require deciding the other two questions first.)
3. Should `TARGET_CVE` bypass the severity/fix-state filters when explicitly set? (Methodology decision.)
4. Should the Syft invocation be changed to include dev dependencies, and if so, does that change what "in scope" means for this thesis's 18 scenarios? (Methodology decision.)
5. For AF-06/jinja2 and JS-06/flatted specifically: re-attempt with whichever of the above is adopted, or treat these two as needing a different remediation path entirely?

No code has been changed as a result of this investigation.
