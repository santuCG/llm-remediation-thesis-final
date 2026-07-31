import os, json
for d in sorted(os.listdir('results/scenarios')):
    if d.endswith('.json'):
        with open(os.path.join('results/scenarios', d), 'r') as f:
            data = json.load(f)
            print(f"{d}: {data['pre_registration']['vulnerability_enrichment']['cve']['id']}")
