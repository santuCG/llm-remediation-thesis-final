import os
import json
import re

metrics_comments = {
    '"application":': ' // The target application being evaluated',
    '"ecosystem":': ' // Package manager ecosystem (e.g., npm, python)',
    '"candidate_count":': ' // Total number of vulnerabilities initially scanned',
    '"selected_package":': ' // The specific vulnerable dependency chosen for remediation',
    '"selected_cve":': ' // The GitHub Security Advisory ID',
    '"api_cve_id":': ' // The standard MITRE CVE ID',
    '"severity":': ' // CVSS severity rating',
    '"cvss":': ' // Common Vulnerability Scoring System score',
    '"epss":': ' // Exploit Prediction Scoring System probability',
    '"epss_timestamp":': ' // Time the EPSS score was fetched',
    '"kev_status":': ' // CISA Known Exploited Vulnerabilities catalog status',
    '"dependency_type":': ' // Whether the dependency is direct or transitive',
    '"strategy":': ' // The remediation strategy chosen by the LLM',
    '"remediation_type":': ' // The human-readable strategy category',
    '"llm_response_valid":': ' // Whether the LLM output matched the required JSON schema',
    '"build_success":': ' // Whether the application successfully built after remediation',
    '"test_success":': ' // Whether the application\'s test suite passed',
    '"dependency_verified":': ' // Whether the dependency tree correctly resolved the new version',
    '"rescan_success":': ' // Whether the scanner confirmed the vulnerability was eradicated',
    '"runtime_success":': ' // Runtime tests status',
    '"lockfile_regenerated":': ' // Whether a lockfile was regenerated',
    '"execution_time_seconds":': ' // Total pipeline execution time in seconds',
    '"retry_count":': ' // Number of LLM retries needed',
    '"llm_iteration":': ' // The specific iteration of the LLM prompting',
    '"validation_stage_reached":': ' // The furthest pipeline stage reached',
    '"failure_stage":': ' // The stage where the pipeline failed, if any'
}

manifest_comments = {
    '"scenario":': ' // The unique identifier for this vulnerability scenario',
    '"repository_commit":': ' // The Git commit hash of the repository during execution',
    '"workflow_commit":': ' // The GitHub Actions run ID that executed this pipeline',
    '"pipeline_version":': ' // The version of the remediation pipeline engine',
    '"runner":': ' // The OS environment where the pipeline ran',
    '"python":': ' // The Python version used by the pipeline',
    '"llm": {': ' // LLM configuration settings',
    '"model":': ' // The exact LLM model used for reasoning',
    '"temperature":': ' // Temperature setting (0.0 for deterministic output)',
    '"seed":': ' // Seed for reproducibility',
    '"topP":': ' // Top-P sampling setting',
    '"topK":': ' // Top-K sampling setting',
    '"snapshots": {': ' // Hashes of vulnerability intelligence snapshots',
    '"tool_versions": {': ' // Versions of security scanners used',
    '"artifact_hashes": {': ' // SHA256 hashes of all pipeline artifacts for integrity tracking',
    '"workflow_url":': ' // Direct link to the successful GitHub Actions workflow run'
}

def add_comments(json_str, comments_dict):
    lines = json_str.split('\n')
    for i, line in enumerate(lines):
        for key, comment in comments_dict.items():
            if key in line and not line.strip().startswith('//'):
                lines[i] = line + comment
    return '\n'.join(lines)

def update_file(filepath, is_manifest=False):
    if not os.path.exists(filepath):
        return
        
    content = open(filepath, 'r', encoding='utf-8').read()
    if '=== EMPIRICAL EVIDENCE ===' not in content:
        return
        
    parts = content.split('=== EMPIRICAL EVIDENCE ===')
    json_body = parts[0].strip()
    evidence = parts[1]
    
    # Extract the individual sections
    # They look like:
    # --- PIPELINE METRICS ---
    # { ... }
    # --- LLM PROMPT ---
    # ...
    # --- LLM OUTPUT ---
    # ...
    
    try:
        metrics_part = evidence.split('--- PIPELINE METRICS ---')[1].split('--- LLM PROMPT ---')[0].strip()
        
        # Add comments to metrics
        commented_metrics = add_comments(metrics_part, metrics_comments)
        
        # If this is a manifest, we also want to add comments to the top-level manifest JSON (but as a copy in the evidence to keep the real JSON valid, OR maybe they want it in the appended section?)
        # Let's add a "--- EXPERIMENT MANIFEST ---" section to the evidence with comments!
        if is_manifest:
            manifest_part = json.dumps(json.loads(json_body), indent=4)
            commented_manifest = add_comments(manifest_part, manifest_comments)
            
            # Rebuild evidence string
            new_evidence = evidence.replace(metrics_part, commented_metrics)
            
            # Prepend the commented manifest to the evidence section if not already there
            if '--- EXPERIMENT MANIFEST ---' not in new_evidence:
                injection = f'\n--- EXPERIMENT MANIFEST ---\n{commented_manifest}\n\n--- PIPELINE METRICS ---'
                new_evidence = new_evidence.replace('\n--- PIPELINE METRICS ---', injection)
            else:
                old_manifest = new_evidence.split('--- EXPERIMENT MANIFEST ---')[1].split('--- PIPELINE METRICS ---')[0].strip()
                new_evidence = new_evidence.replace(old_manifest, commented_manifest)
                
        else:
            new_evidence = evidence.replace(metrics_part, commented_metrics)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_body + '\n\n\n=== EMPIRICAL EVIDENCE ===\n' + new_evidence.strip() + '\n')
            
        print(f"Updated {filepath}")
    except Exception as e:
        print(f"Failed to update {filepath}: {e}")


# Also wait, for the scenario files (AF-01.json, JS-01.json), they might also want the manifest included or just the metrics commented.
# The user said: "Okay now all these should have short comments to others to understand ... make sure even this is updates in js-01"
update_file('results/scenarios/AF-01.json', is_manifest=False)
update_file('results/scenarios/JS-01.json', is_manifest=False)
update_file('results/execution_evidence/AF-01/experiment_manifest.json', is_manifest=True)
update_file('results/execution_evidence/JS-01/experiment_manifest.json', is_manifest=True)
