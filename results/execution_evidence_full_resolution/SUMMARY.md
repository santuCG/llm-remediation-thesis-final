# Supplementary validation: pip baseline without `--no-deps`

**Branch:** `research/pip-full-resolution-validation`
**Change:** one line in `.github/workflows/grype-baseline.yml` — `pip install --no-deps -r requirements.txt` → `pip install -r requirements.txt`, at the Apply Fix & Verify step only. No other workflow, script, or the LLM pipeline (`generic-remediation.yml`) was touched.

**Why:** the original deterministic baseline installs the scanner-recommended version with `--no-deps`, which skips pip's own dependency-compatibility check between the recommended version and the other 361 already-pinned packages in `applications/evidence/airflow_pip_freeze.txt`. This validation re-enables that check to test whether the recommendation survives pip's normal resolution behaviour.

**Dispatch:** `grype-baseline.yml`, once per pip scenario (AF-01–AF-09), via `workflow_dispatch` with `target_cve` only (app/package resolved by the workflow from `results/scenarios/final_18_scenarios.json`).

## Result

| Scenario | CVE | Package → recommended | First run | Rerun (confirmation) | Conflict |
|---|---|---|---|---|---|
| AF-01 | CVE-2026-8838 | redshift-connector → 2.1.14 | fail | fail | `redshift-connector 2.1.14` requires `beautifulsoup4>=4.13.5`; frozen set pins `beautifulsoup4==4.12.3` |
| AF-02 | CVE-2025-43859 | h11 → 0.16.0 | fail | fail | `httpcore 0.16.3` (pinned) requires `h11<0.15,>=0.13` |
| AF-03 | CVE-2023-50782 | cryptography → 42.0.0 | fail | fail | `gcloud-aio-auth 4.2.3` (pinned) requires `cryptography<42.0.0` |
| AF-04 | CVE-2026-44307 | mako → 1.3.12 | success | — | no conflicting pin |
| AF-05 | CVE-2026-0994 | protobuf → 5.29.6 | fail | fail | `google-ads 24.0.0` (pinned) requires `protobuf<5.0.0,>=4.25.0` |
| AF-06 | CVE-2024-56326 | jinja2 → 3.1.5 | success | — | no conflicting pin |
| AF-07 | CVE-2024-21272 | mysql-connector-python → 9.1.0 | success | — | no conflicting pin |
| AF-08 | CVE-2026-2473 | google-cloud-aiplatform → 1.133.0 | fail | fail | transitive: requires `google-auth>=2.47.0`, but `google-auth==2.29.0` is pinned separately |
| AF-09 | CVE-2024-34069 | werkzeug → 3.0.3 | fail | fail | `apache-airflow 2.9.2` itself requires `werkzeug<3,>=2.0` |

6 of 9 pip scenarios that appeared clean under `--no-deps` fail pip's own `ResolutionImpossible` check once it is allowed to run. All 6 reruns reproduced the identical conflict (same requested package, same blocking dependency, same error), confirming this is deterministic, not transient CI flakiness. AF-08 is a transitive conflict (the target package's own new dependency requirement collides with an unrelated pinned package) — structurally the same "shadowing" pattern the npm case studies (JS-01) already document, now shown on the pip side. AF-09 is blocked by the application's own core framework pin, not a peripheral dependency.

## Evidence

Each `<SCENARIO>/` directory here is the `remediation-evidence` artifact from that scenario's first-attempt workflow run, containing `build.log` (the literal pip error), `metrics.json`, `baseline-sbom.json`/`baseline-grype.json`, and `experiment_manifest.json` (records `workflow_commit` and runner details for that specific run).

| Scenario | First run | Rerun |
|---|---|---|
| AF-01 | [33890856629](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33890856629) | [33968881025](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33968881025) |
| AF-02 | [33890865123](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33890865123) | [33968885357](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33968885357) |
| AF-03 | [33890873006](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33890873006) | [33968889487](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33968889487) |
| AF-04 | [33890880662](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33890880662) | — |
| AF-05 | [33890888361](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33890888361) | [33968894278](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33968894278) |
| AF-06 | [33890896744](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33890896744) | — |
| AF-07 | [33890904839](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33890904839) | — |
| AF-08 | [33890912103](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33890912103) | [33968898554](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33968898554) |
| AF-09 | [33890919615](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33890919615) | [33968902343](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/33968902343) |

## Scope note

This validation only exercises the deterministic baseline's install step. It does not modify or re-run the LLM pipeline (`generic-remediation.yml`), which still uses `--no-deps` at the equivalent step and was not touched on this branch. A fair, matched comparison against the LLM pipeline under the same full-resolution condition would require the equivalent change there, run separately, not yet done as part of this validation.
