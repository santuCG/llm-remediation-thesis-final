# Context-Aware Dependency Remediation in SBOM-Driven CI Pipelines Using a Large Language Model

This repository is the reproducibility, implementation, and evidence artifact accompanying a Master's thesis. It contains the pipeline that was evaluated, the scenarios it was run against, and the complete recorded evidence for every run.

> **The university-submitted thesis is the authoritative academic document.** This repository supports and substantiates the thesis's claims with runnable code and verifiable evidence; it is not itself a second copy of the thesis narrative, and where any supporting document in `docs/` differs from the thesis, the thesis governs.

> **Repository status.** This repository contains a single finalized snapshot: all results, evidence, and analysis below are self-contained in this snapshot, and every citation in this repository resolves locally — no other branch needs to be checked out to verify anything cited here. This snapshot was extracted from a private development history that also contained exploratory and superseded work; that development history is not part of this repository and is not required to reproduce or verify anything reported.
>
> **A note on the CI-run links cited throughout this repository** (e.g. in `FINAL_DATASET.md`, `REGENERATION_LOG.md`, `preregistration/PRE_REGISTRATION_AMENDMENT.md`, and individual `experiment_manifest.json` files): these are `github.com/.../actions/runs/<id>` links captured as provenance at the time each scenario was generated, recording exactly which CI execution produced that evidence. They point at the original private development environment's CI history and are not expected to resolve for a reader outside that environment — they are retained as an audit trail (proof that a specific, timestamped, non-fabricated CI run produced the cited fields) rather than as live, clickable links.

---

## 1. What this research is

This work evaluates whether a Large Language Model (LLM), supplied with structured vulnerability intelligence (CVSS, EPSS, KEV) and dependency-graph context, can generate dependency remediation strategies that succeed where a deterministic vulnerability scanner's direct-upgrade recommendation does not — specifically for vulnerabilities in transitive (nested) dependencies. The comparison is against a deterministic baseline workflow running on the same preregistered targets.

## 2. The evaluated system

The evaluated pipeline generates a Software Bill of Materials (SBOM), scans it for vulnerabilities, selects a target, builds a structured prompt from vulnerability and dependency-graph evidence, sends it to an LLM under a fixed schema and generation configuration, applies the returned recommendation to the manifest, and independently re-verifies the result (install, dependency-graph check, SBOM regeneration, rescan) before recording an outcome. Every recommendation is treated as a hypothesis, never as evidence, until it passes deterministic validation.

## 3. Pre-registration

The 18 vulnerability scenarios were locked before execution:
* [preregistration/MASTER_METHODOLOGY_RECORD.md](preregistration/MASTER_METHODOLOGY_RECORD.md)
* [preregistration/JUICESHOP_PREREGISTRATION.md](preregistration/JUICESHOP_PREREGISTRATION.md)
* [preregistration/AIRFLOW_PREREGISTRATION.md](preregistration/AIRFLOW_PREREGISTRATION.md)
* [preregistration/PRE_REGISTRATION_AMENDMENT.md](preregistration/PRE_REGISTRATION_AMENDMENT.md)
* [preregistration/tool_versions.md](preregistration/tool_versions.md)

## 4. Active workflows

The two evaluated GitHub Actions pipelines:
* [.github/workflows/generic-remediation.yml](.github/workflows/generic-remediation.yml) — the LLM-assisted remediation pipeline
* [.github/workflows/grype-baseline.yml](.github/workflows/grype-baseline.yml) — the deterministic baseline comparison pipeline

Running `generic-remediation.yml` requires a `GEMINI_API_KEY` repository secret (Settings → Secrets and variables → Actions) for the Google Generative Language API; `grype-baseline.yml` requires no secrets.

## 5. Remediation logic and prompts

* [scripts/remediation/llm_reasoner.py](scripts/remediation/llm_reasoner.py) — prompt construction, model call, generation configuration
* [scripts/remediation/retry_remediation.py](scripts/remediation/retry_remediation.py) — the single-retry mechanism
* [scripts/remediation/generic_remediation.py](scripts/remediation/generic_remediation.py), [prioritize.py](scripts/remediation/prioritize.py), [validator.py](scripts/remediation/validator.py) — candidate selection, prioritisation, and deterministic post-remediation validation
* [scripts/remediation/prompts/PROMPT_CHANGELOG.md](scripts/remediation/prompts/PROMPT_CHANGELOG.md) — prompt/schema version history
* Exact prompt and response schema, per run: `results/execution_evidence/<ID>/llm-request.json` / `llm-response.json`

## 6. Primary evidence

The complete recorded evidence for all 18 preregistered scenarios — SBOMs, scans, LLM request/response, manifest before/after, build/test logs, rescans, and metrics — is the sole basis for the thesis's primary dataset and research-question conclusion:
* [results/execution_evidence/](results/execution_evidence/)
* [results/reproducibility_verification/](results/reproducibility_verification/) — the deterministic baseline's own evidence
* [results/scenarios/](results/scenarios/) — the scenario manifest

## 7. Supplementary evidence

Additional evidence explaining, not replacing, the primary dataset:
* [results/execution_evidence_lockfile_preserved/](results/execution_evidence_lockfile_preserved/) — controlled lockfile-preservation validation
* [results/execution_evidence_no_hint/](results/execution_evidence_no_hint/) and [results/execution_evidence_no_hint_lockfile_preserved/](results/execution_evidence_no_hint_lockfile_preserved/) — no-hint ablation study and its extension

## 8. Scenarios and target applications

18 scenarios across two applications: OWASP Juice Shop ([applications/juice-shop/](applications/juice-shop/), npm) and Apache Airflow ([applications/airflow/](applications/airflow/), pip). Raw vulnerability-intelligence snapshots (EPSS, MITRE, baseline SBOM/scan) used for scenario selection are in [applications/evidence/](applications/evidence/). The canonical per-scenario manifest (pipeline version, prompt version, CI run ID, commit, evidence hash, result) is [FINAL_DATASET.md](FINAL_DATASET.md).

## 9. Reproducibility

* [docs/06-reproducibility.md](docs/06-reproducibility.md) — step-by-step reproduction commands
* [REGENERATION_LOG.md](REGENERATION_LOG.md) — record of the field-by-field reproducibility re-dispatch (all 18 scenarios, zero mismatches) that the thesis cites
* [docs/CVE_MATCH_VERIFICATION.md](docs/CVE_MATCH_VERIFICATION.md) — confirms every executed scenario matched its preregistered target CVE
* [docs/METRIC_FIELD_OWNERSHIP.md](docs/METRIC_FIELD_OWNERSHIP.md) — definitions and write-sites for every recorded outcome field
* [PIPELINE_V2_RELEASE_NOTES.md](PIPELINE_V2_RELEASE_NOTES.md) — the engineering-fix history behind the frozen dataset, with scientific impact stated per fix
* [CHANGELOG.md](CHANGELOG.md) — earlier repository changes, including the prompt-schema fix cited in the thesis

Supporting implementation documentation elaborates specific aspects of the pipeline: [docs/02-experimental-environment.md](docs/02-experimental-environment.md) (platform and tool choices), [docs/03-llm-configuration.md](docs/03-llm-configuration.md) (LLM mechanics — system prompt, schema, retry augmentation), and [docs/04-experimental-methodology.md](docs/04-experimental-methodology.md) (the 12-stage pipeline walkthrough). These describe the implementation; they are not the thesis and are not the canonical methodology/results account (§ note at the top of this document) — where a specific number, version, or model identifier matters, the authoritative source is always the thesis or the evidence in `results/execution_evidence/<ID>/`, never these documents.

## 10. Local tool requirements

This repository does not commit tool binaries (`tools/**/bin/`, `tools/**/*.exe` are gitignored). Both CI workflows download these exact pinned versions at run time; any local reproduction should use the same versions:
*   **Syft v1.44.0** — [anchore/syft releases](https://github.com/anchore/syft/releases/tag/v1.44.0)
*   **Grype v0.112.0** — [anchore/grype releases](https://github.com/anchore/grype/releases/tag/v0.112.0)
*   **GitHub CLI (`gh`)** — used locally for workflow dispatch and log retrieval; any current release is compatible.
