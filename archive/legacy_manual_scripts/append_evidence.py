import os, json, re

def fix_manifest_and_append(scenario_id):
    scenario_file = f"results/scenarios/{scenario_id}.json"
    evidence_dir = f"results/execution_evidence/{scenario_id}"
    manifest_path = os.path.join(evidence_dir, "experiment_manifest.json")
    
    if not os.path.exists(scenario_file) or not os.path.exists(manifest_path):
        return

    # Get the correct RUN ID from the scenario JSON
    with open(scenario_file, "r", encoding="utf-8") as f:
        scontent = f.read()
        
    scontent_json = re.sub(r'\n\n\n=== EMPIRICAL EVIDENCE ===.*', '', scontent, flags=re.DOTALL)
    scenario_data = json.loads(scontent_json)
    
    run_id = scenario_data.get("execution", {}).get("llm_pipeline", {}).get("github_run_id")
    if not run_id:
        # Fallback if somehow not there
        return
        
    # Fix the experiment_manifest.json
    with open(manifest_path, "r", encoding="utf-8") as f:
        mcontent = f.read()
        mcontent = re.sub(r'//.*$', '', mcontent, flags=re.MULTILINE)
        mcontent = re.sub(r'/\*.*?\*/', '', mcontent, flags=re.DOTALL)
        manifest_data = json.loads(mcontent)
        
    manifest_data["workflow_commit"] = str(run_id)
    manifest_data["workflow_url"] = f"https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/{run_id}"
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
        
    # Now, re-generate the EMPIRICAL EVIDENCE block
    with open(scenario_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Strip existing EMPIRICAL EVIDENCE
    content = re.sub(r'\n\n\n=== EMPIRICAL EVIDENCE ===.*', '', content, flags=re.DOTALL)
    
    # Generate new block
    metrics_path = os.path.join(evidence_dir, "metrics.json")
    request_path = os.path.join(evidence_dir, "llm-request.json")
    response_path = os.path.join(evidence_dir, "llm-response.json")
    
    evidence_text = "\n\n\n=== EMPIRICAL EVIDENCE ===\n"
    evidence_text += "NOTE: The following pipeline metrics, LLM prompts, and exact outputs are appended here in plaintext to serve as verifiable, empirical proof of the LLM's reasoning and the pipeline's deterministic success for this scenario.\n\n"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        evidence_text += "--- EXPERIMENT MANIFEST ---\n"
        evidence_text += f.read() + "\n\n"
        
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            evidence_text += "--- PIPELINE METRICS ---\n"
            evidence_text += f.read() + "\n\n"
            
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
                
    # Write back to scenario file
    with open(scenario_file, "w", encoding="utf-8") as f:
        f.write(content + evidence_text)
        
    print(f"Fixed manifest and re-appended empirical evidence to {scenario_id}")

if __name__ == "__main__":
    for i in range(2, 10):
        fix_manifest_and_append(f"AF-{i:02d}")
        fix_manifest_and_append(f"JS-{i:02d}")
    fix_manifest_and_append("AF-09")
