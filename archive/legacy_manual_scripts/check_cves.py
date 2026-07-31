import os, json
dirs = sorted(os.listdir('results/execution_evidence'))
for d in dirs:
    p = os.path.join('results/execution_evidence', d, 'metrics.json')
    if os.path.exists(p):
        with open(p, 'r') as f:
            try:
                m = json.load(f)
                print(f"{d}: {m.get('api_cve_id')} | run: {m.get('github_run_id', 'none')}")
            except Exception as e:
                pass
