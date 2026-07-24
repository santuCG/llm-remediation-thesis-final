## LLM Remediation Thesis Methodology Rules

1. **Lockfile Integrity:** Only package managers should generate lockfiles. The pipeline must NEVER perform AST editing or lockfile surgery in Python. Phase 1 applies changes to the manifest and runs native resolution. Phase 2 (Fallback) deletes the lockfile/node_modules and regenerates it purely via package manager, documenting the fallback in evidence.

2. **Filtering Logic:** Vulnerabilities must be filtered by: Severity >= High AND Automatically Remediable (Fixed version available AND Supported ecosystem AND Package manager supports upgrade path AND No manual source code modification required AND Not Ignored).

3. **Prioritization:** Sort strictly by KEV (True) -> EPSS (Descending) -> CVSS (Descending). Select the Top 1 Remediable Candidate.

4. **Unbiased Reasoning:** LLM prompts must NOT bias the model towards any specific fix (e.g., do not suggest a specific alternative package like isolated-vm). Ask the model to evaluate all technically feasible strategies (native upgrades, overrides, replacements, etc.) and recommend the safest compatible strategy.

5. **Strict Retries:** Maximum ONE retry. Flow: LLM Recommendation #1 -> Apply -> Verify/Build/Test. If failure occurs at any stage -> Capture Logs -> LLM Recommendation #2 (Refined) -> Apply -> Verify/Build/Test. If failure again -> Fail Experiment.

6. **Enriched Context:** Always collect deep context for the LLM: 
pm ls --json, 
pm explain, package.json, package-lock.json, grype.json, SBOM, and build logs.

7. **Enriched Metrics:** Ensure metrics.json captures Application, Ecosystem, Selected Package, CVE, Severity, CVSS, EPSS, KEV, Dependency Type, Strategy, Confidence, Remediation Type, Boolean Success Flags, lockfile_regenerated, execution_time_seconds, retry_count, llm_iteration, and failure_stage.
