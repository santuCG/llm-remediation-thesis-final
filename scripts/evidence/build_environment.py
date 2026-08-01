import os
import json

def main():
    whitelist = [
        'RUNNER_OS',
        'RUNNER_ARCH',
        'GITHUB_WORKFLOW',
        'GITHUB_RUN_ID',
        'GITHUB_SHA',
        'SCENARIO_ID',
        'APP_DIR',
        'TARGET_CVE',
        'NODE_VERSION',
        'PYTHON_VERSION',
        'SYFT_VERSION',
        'GRYPE_VERSION'
    ]
    
    env_data = {}
    for key in whitelist:
        env_data[key] = os.environ.get(key, 'NOT_SET')
        
    os.makedirs('provenance', exist_ok=True)
    with open('provenance/environment.json', 'w') as f:
        json.dump(env_data, f, indent=2)
        
    with open('provenance/environment.txt', 'w') as f:
        for k, v in env_data.items():
            f.write(f"{k}={v}\n")
            
if __name__ == "__main__":
    main()
