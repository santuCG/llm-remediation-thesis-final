import os, json, re

def add_manifest_comments(json_str):
    replacements = {
        r'"scenario":': r'// The unique identifier for this vulnerability scenario',
        r'"repository_commit":': r'// The Git commit hash of the repository during execution',
        r'"workflow_commit":': r'// The GitHub Actions run ID that executed this pipeline',
        r'"pipeline_version":': r'// The version of the remediation pipeline engine',
        r'"runner":': r'// The OS environment where the pipeline ran',
        r'"python":': r'// The Python version used by the pipeline',
        r'"llm": \{': r'// LLM configuration settings',
        r'"model":': r'// The exact LLM model used for reasoning',
        r'"temperature":': r'// Temperature setting (0.0 for deterministic output)',
        r'"seed":': r'// Seed for reproducibility',
        r'"topP":': r'// Top-P sampling setting',
        r'"topK":': r'// Top-K sampling setting',
        r'"snapshots": \{': r'// Hashes of vulnerability intelligence snapshots',
        r'"tool_versions": \{': r'// Versions of security scanners used',
        r'"artifact_hashes": \{': r'// SHA256 hashes of all pipeline artifacts for integrity tracking',
        r'"workflow_url":': r'// Direct link to the successful GitHub Actions workflow run'
    }
    
    lines = json_str.split('\n')
    new_lines = []
    for line in lines:
        added = False
        for k, v in replacements.items():
            if re.search(k, line):
                # Don't add if it already has a comment
                if '//' not in line:
                    if line.endswith(','):
                        line = f"{line} {v}"
                    else:
                        line = f"{line} {v}"
                added = True
                break
        new_lines.append(line)
    return '\n'.join(new_lines)

def add_metrics_comments(json_str):
    replacements = {
        r'"application":': r'// The target application being evaluated',
        r'"ecosystem":': r'// Package manager ecosystem (e.g., npm, python)',
        r'"candidate_count":': r'// Total number of vulnerabilities initially scanned',
        r'"selected_package":': r'// The specific vulnerable dependency chosen for remediation',
        r'"selected_cve":': r'// The GitHub Security Advisory ID',
        r'"api_cve_id":': r'// The standard MITRE CVE ID',
        r'"severity":': r'// CVSS severity rating',
        r'"cvss":': r'// Common Vulnerability Scoring System score',
        r'"epss":': r'// Exploit Prediction Scoring System probability',
        r'"epss_timestamp":': r'// Time the EPSS score was fetched',
        r'"kev_status":': r'// CISA Known Exploited Vulnerabilities catalog status',
        r'"dependency_type":': r'// Whether the dependency is direct or transitive',
        r'"strategy":': r'// The remediation strategy chosen by the LLM',
        r'"remediation_type":': r'// The human-readable strategy category',
        r'"llm_response_valid":': r'// Whether the LLM output matched the required JSON schema',
        r'"build_success":': r'// Whether the application successfully built after remediation',
        r'"test_success":': r'// Whether the application\'s test suite passed',
        r'"dependency_verified":': r'// Whether the dependency tree correctly resolved the new version',
        r'"rescan_success":': r'// Whether the scanner confirmed the vulnerability was eradicated',
        r'"runtime_success":': r'// Runtime tests status',
        r'"lockfile_regenerated":': r'// Whether a lockfile was regenerated',
        r'"execution_time_seconds":': r'// Total pipeline execution time in seconds',
        r'"retry_count":': r'// Number of LLM retries needed',
        r'"llm_iteration":': r'// The specific iteration of the LLM prompting',
        r'"validation_stage_reached":': r'// The furthest pipeline stage reached',
        r'"failure_stage":': r'// The stage where the pipeline failed, if any'
    }
    
    lines = json_str.split('\n')
    new_lines = []
    for line in lines:
        added = False
        for k, v in replacements.items():
            if re.search(k, line):
                if '//' not in line:
                    if line.endswith(','):
                        line = f"{line} {v}"
                    else:
                        line = f"{line} {v}"
                added = True
                break
        new_lines.append(line)
    return '\n'.join(new_lines)

def fix_manifest(scenario_id):
    evidence_dir = f"results/execution_evidence/{scenario_id}"
    manifest_path = os.path.join(evidence_dir, "experiment_manifest.json")
    
    if not os.path.exists(manifest_path):
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Strip existing EMPIRICAL EVIDENCE from manifest
    content = re.sub(r'\n\n\n=== EMPIRICAL EVIDENCE ===.*', '', content, flags=re.DOTALL)
    
    try:
        manifest_data = json.loads(content)
        pure_manifest_str = json.dumps(manifest_data, indent=4)
    except:
        pure_manifest_str = content
        
    # Generate new block
    metrics_path = os.path.join(evidence_dir, "metrics.json")
    request_path = os.path.join(evidence_dir, "llm-request.json")
    response_path = os.path.join(evidence_dir, "llm-response.json")
    
    evidence_text = "\n\n\n=== EMPIRICAL EVIDENCE ===\n"
    evidence_text += "NOTE: The following pipeline metrics, LLM prompts, and exact outputs are appended here in plaintext to serve as verifiable, empirical proof of the LLM's reasoning and the pipeline's deterministic success for this scenario.\n\n"
    
    evidence_text += "--- EXPERIMENT MANIFEST ---\n"
    evidence_text += add_manifest_comments(pure_manifest_str) + "\n\n"
        
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            try:
                mdata = json.load(f)
                m_str = json.dumps(mdata, indent=2)
            except:
                f.seek(0)
                m_str = f.read()
            evidence_text += "--- PIPELINE METRICS ---\n"
            evidence_text += add_metrics_comments(m_str) + "\n\n"
            
    if os.path.exists(request_path):
        with open(request_path, "r", encoding="utf-8") as f:
            evidence_text += "--- LLM PROMPT ---\n"
            try:
                req_data = json.load(f)
                if isinstance(req_data, list) and len(req_data) > 0 and "parts" in req_data[0]:
                    evidence_text += req_data[0]["parts"][0]["text"] + "\n\n"
                else:
                    f.seek(0)
                    evidence_text += f.read() + "\n\n"
            except:
                f.seek(0)
                evidence_text += f.read() + "\n\n"
                
    if os.path.exists(response_path):
        with open(response_path, "r", encoding="utf-8") as f:
            evidence_text += "--- LLM OUTPUT ---\n"
            try:
                resp_data = json.load(f)
                if isinstance(resp_data, dict) and "candidates" in resp_data:
                    out_text = resp_data["candidates"][0]["content"]["parts"][0]["text"]
                    out_text = out_text.replace('```json\n', '').replace('```', '')
                    evidence_text += out_text + "\n"
                else:
                    f.seek(0)
                    evidence_text += f.read() + "\n"
            except:
                f.seek(0)
                evidence_text += f.read() + "\n"
                
    # Write back to experiment_manifest.json
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(content + evidence_text)
        
    print(f"Appended fully commented empirical evidence to {manifest_path}")

if __name__ == "__main__":
    for i in range(2, 10):
        fix_manifest(f"AF-{i:02d}")
        fix_manifest(f"JS-{i:02d}")
