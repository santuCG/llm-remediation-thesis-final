# Deterministic Baseline — Non-Fatal Build Check, Supplementary Validation

Evidence for the supplementary study reported in thesis sections 3.8a, 4.13, and 5.10.

**What this is.** `.github/workflows/grype-baseline.yml`'s npm branch originally called
`check_npm_build.sh ... --fatal`, which aborts the workflow step immediately on an npm build
failure (under GitHub Actions' default `set -e`), before the shared SBOM-regeneration/rescan/
validation lines later in the same step ever run. This meant the deterministic baseline never
reached rescan for any of the nine npm scenarios, all of which fail this build check for a
pre-existing, remediation-unrelated reason (`TS1005`, thesis section 3.7). Section 3.8
disclosed this as a scope limitation on the npm comparison rather than resolving it.

This directory holds the evidence from re-dispatching all nine npm scenarios (commit
`288dd403`, which removes `--fatal` from that one call site) to test what the baseline
actually does once given the same opportunity to reach rescan that the LLM pipeline
(`generic-remediation.yml`) always had.

**Per-scenario contents**, mirroring the primary dataset's evidence schema
(`docs/METRIC_FIELD_OWNERSHIP.md`, `results/execution_evidence/<ID>/`):
`metrics.json`, `baseline-patch.json`, `baseline-grype.json`, `baseline-sbom.json`,
`rescan.json`, `build.log`, `experiment_manifest.json`.

**Dispatch run URLs** (`santuCG/llm-remediation-thesis-reproducibility`):
JS-01: [32639983970](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/32639983970) ·
JS-02: [32639987499](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/32639987499) ·
JS-03: [32639991447](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/32639991447) ·
JS-04: [32639995104](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/32639995104) ·
JS-05: [32639998006](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/32639998006) ·
JS-06: [32640001893](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/32640001893) ·
JS-07: [32640005511](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/32640005511) ·
JS-08: [32640008016](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/32640008016) ·
JS-09: [32640010858](https://github.com/santuCG/llm-remediation-thesis-reproducibility/actions/runs/32640010858)

**Scope.** This is supplementary evidence explaining a disclosed limitation of the primary
dataset. It does not replace or alter `results/reproducibility_verification/<ID>/`, the
frozen baseline evidence the primary dataset (Table 5, Table 6) is drawn from.
