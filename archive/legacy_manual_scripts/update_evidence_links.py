import os
import json
import re

def update_scenario(s, run_id):
    scenario_file = f'results/scenarios/{s}.json'
    if os.path.exists(scenario_file):
        content = open(scenario_file, 'r', encoding='utf-8').read()
        
        # Replace github_run_id with actual run id
        content = re.sub(r'"github_run_id":\s*"\d+"', f'"github_run_id": "{run_id}"', content)
        
        # Replace workflow_url with actual URL
        content = re.sub(r'"workflow_url":\s*".*?"', f'"workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/{run_id}"', content)
        
        # Inject the note if not already injected
        if "NOTE: The following pipeline metrics" not in content:
            content = content.replace('=== EMPIRICAL EVIDENCE ===', '=== EMPIRICAL EVIDENCE ===\nNOTE: The following pipeline metrics, LLM prompts, and exact outputs are appended here in plaintext to serve as verifiable, empirical proof of the LLM\'s reasoning and the pipeline\'s deterministic success for this scenario.')
            
        with open(scenario_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {scenario_file}")

update_scenario('AF-01', '30574548185')
update_scenario('JS-01', '30215612850')

# Update experiment_manifest.json (AF-01)
manifest_path = 'results/execution_evidence/AF-01/experiment_manifest.json'
if os.path.exists(manifest_path):
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['workflow_commit'] = '30574548185' # Set to run id for clarity or keep SHA, let's keep it as run id since they asked for it
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Updated {manifest_path}")

