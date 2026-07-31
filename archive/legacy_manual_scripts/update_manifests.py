import os
import json

def append_to_manifest(s, run_id):
    manifest_path = f'results/execution_evidence/{s}/experiment_manifest.json'
    
    if not os.path.exists(manifest_path):
        data = {
            'scenario': s,
            'workflow_commit': run_id,
            'workflow_url': f'https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/{run_id}',
            'pipeline_version': 'v2.0',
            'llm': {'model': 'gemini-2.5-flash'}
        }
    else:
        content = open(manifest_path, 'r', encoding='utf-8').read()
        json_part = content.split('=== EMPIRICAL EVIDENCE ===')[0].strip()
        data = json.loads(json_part)
        data['workflow_url'] = f'https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/{run_id}'
        
    metrics_file = f'results/execution_evidence/{s}/metrics.json'
    req_file = f'results/execution_evidence/{s}/llm-request.json'
    resp_file = f'results/execution_evidence/{s}/llm-response.json'
    
    metrics = json.loads(open(metrics_file, 'r', encoding='utf-8').read())
    req = json.loads(open(req_file, 'r', encoding='utf-8').read())
    resp = json.loads(open(resp_file, 'r', encoding='utf-8').read())
    
    if 'api_payload' in req:
        prompt_text = req['api_payload']['contents'][0]['parts'][0]['text']
    else:
        prompt_text = req['contents'][0]['parts'][0]['text']
        
    response_json_str = json.dumps(resp, indent=2)
    metrics_json_str = json.dumps(metrics, indent=2)
    
    note = "NOTE: The following pipeline metrics, LLM prompts, and exact outputs are appended here in plaintext to serve as verifiable, empirical proof of the LLM's reasoning and the pipeline's deterministic success for this scenario."
    append_str = f'\n\n\n=== EMPIRICAL EVIDENCE ===\n{note}\n\n--- PIPELINE METRICS ---\n{metrics_json_str}\n\n--- LLM PROMPT ---\n{prompt_text}\n\n--- LLM OUTPUT ---\n{response_json_str}\n'
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4) + append_str)
    print(f'Updated {manifest_path}')

append_to_manifest('AF-01', '30574548185')
append_to_manifest('JS-01', '30215612850')
