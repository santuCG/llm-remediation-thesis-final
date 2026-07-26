# Deterministic Baseline Application Policy

This document defines the methodological policy for the "scanner-directed" baseline experiment.

## Purpose
The baseline evaluates the efficacy of naive scanner recommendations when applied directly to a project, without the orchestration or semantic reasoning provided by an LLM agent.

## Core Policy
For the scanner-directed baseline, the scanner-recommended version is applied to the project's existing dependency declaration prior to dependency installation. 
- No alternative versions are considered.
- No dependency conflict resolution is performed.
- No semantic modifications beyond the scanner recommendation are executed.

## Ecosystem-Specific Application Rules

### Python (`requirements.txt`)
The baseline explicitly replaces the matching package version in `requirements.txt` with the recommended version.
- **Example**: If Grype recommends `2.1.14` for `redshift-connector`, any line starting with `redshift-connector==` or `redshift-connector>=` is replaced with `redshift-connector==2.1.14`.

### NPM (`package.json`)
The baseline modifies `package.json` depending on the dependency type:
1. **Direct Dependencies**: If the vulnerable package is explicitly listed in `dependencies`, `devDependencies`, or `optionalDependencies`, its declared version is updated directly to the scanner recommendation.
2. **Transitive Dependencies**: If the vulnerable package is not directly declared, the scanner-directed baseline uses `npm overrides` to express the scanner-recommended version. It injects an `overrides` block into `package.json` forcing resolution to the recommended version.

## Evidence Generation
Every baseline remediation attempt generates a `baseline-patch.json` artifact documenting:
- The package name
- The original version (if directly declared)
- The recommended version applied
- The target manifest file
- The application method (e.g., `direct_replacement`, `override_added`)

This ensures complete traceability for the experimental dataset.
