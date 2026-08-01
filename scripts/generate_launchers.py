import os
import yaml
import glob

PROFILES_DIR = "profiles"
WORKFLOWS_DIR = ".github/workflows"

LLM_TEMPLATE = """name: LLM {scenario_id}
on:
  workflow_dispatch:
jobs:
  run-scenario:
    uses: ./.github/workflows/templates/{template}
    with:
      profile: {profile_path}
    secrets: inherit
"""

BASELINE_TEMPLATE = """name: Baseline {scenario_id}
on:
  workflow_dispatch:
jobs:
  run-scenario:
    uses: ./.github/workflows/templates/baseline-{template}
    with:
      profile: {profile_path}
    secrets: inherit
"""

def generate():
    os.makedirs(WORKFLOWS_DIR, exist_ok=True)
    
    for profile_path in glob.glob(os.path.join(PROFILES_DIR, "*.yaml")):
        with open(profile_path, 'r') as f:
            profile = yaml.safe_load(f)
            
        scenario_id = profile['scenario_id']
        template = profile['pipeline']['template']
        
        # LLM Launcher
        llm_workflow = os.path.join(WORKFLOWS_DIR, f"llm-{scenario_id.lower()}.yml").replace('\\', '/')
        with open(llm_workflow, 'w') as f:
            f.write(LLM_TEMPLATE.format(scenario_id=scenario_id, template=template, profile_path=profile_path.replace('\\', '/')))
        print(f"Generated {llm_workflow}")
            
        # Baseline Launcher
        baseline_workflow = os.path.join(WORKFLOWS_DIR, f"baseline-{scenario_id.lower()}.yml").replace('\\', '/')
        with open(baseline_workflow, 'w') as f:
            f.write(BASELINE_TEMPLATE.format(scenario_id=scenario_id, template=template, profile_path=profile_path.replace('\\', '/')))
        print(f"Generated {baseline_workflow}")

if __name__ == "__main__":
    generate()
