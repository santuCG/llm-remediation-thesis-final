import os
import yaml

def update_profiles():
    profiles_dir = 'profiles'
    workflows_dir = '.github/workflows'
    
    scenarios = [f"JS-0{i}" for i in range(1, 10)] + [f"AF-0{i}" for i in range(1, 10)]
    
    for scenario in scenarios:
        profile_path = os.path.join(profiles_dir, f"{scenario}.yaml")
        if not os.path.exists(profile_path):
            continue
            
        with open(profile_path, 'r') as f:
            profile = yaml.safe_load(f)
            
        is_npm = profile.get('ecosystem') == 'npm'
        
        # Add baseline config
        profile['baseline'] = {
            'restore_lockfile': True,
            'lockfile': 'evidence/juice_shop_package-lock.json' if is_npm else 'evidence/airflow_pip_freeze.txt'
        }
        
        # Add validation config
        if is_npm:
            profile['validation'] = {
                'build': [
                    'npm run build:frontend',
                    'npm run build:server',
                    'npm run build'
                ],
                'test': [
                    'npm test'
                ]
            }
        else:
            profile['validation'] = {
                'build': [],
                'test': [
                    'if [ -d "tests/core" ]; then pip install pytest==7.4.4 pytest-asyncio sentry-sdk || true && python3 -m pytest tests/core; fi'
                ]
            }
            
        with open(profile_path, 'w') as f:
            yaml.dump(profile, f, sort_keys=False, default_flow_style=False)
            
        # Create baseline workflow
        baseline_wf = f"""name: Baseline {scenario}
on:
  workflow_dispatch:
jobs:
  run-scenario:
    uses: ./.github/workflows/{"baseline-npm-remediation.yml" if is_npm else "baseline-python-remediation.yml"}
    with:
      scenario: {scenario}
    secrets: inherit
"""
        with open(os.path.join(workflows_dir, f"baseline-{scenario.lower()}.yml"), 'w') as f:
            f.write(baseline_wf)
            
        # Create LLM workflow
        llm_wf = f"""name: LLM {scenario}
on:
  workflow_dispatch:
jobs:
  run-scenario:
    uses: ./.github/workflows/{"npm-remediation.yml" if is_npm else "python-remediation.yml"}
    with:
      scenario: {scenario}
    secrets: inherit
"""
        with open(os.path.join(workflows_dir, f"llm-{scenario.lower()}.yml"), 'w') as f:
            f.write(llm_wf)

if __name__ == "__main__":
    update_profiles()
