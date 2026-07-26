import json
scenarios = json.load(open('experiment/archive/final_18_scenarios.json'))
print('| ID | App | Package | Current | Grype Target | CVE | CVSS |')
print('|---|---|---|---|---|---|---|')
for s in scenarios:
    if 'scenario_id' in s and 'vulnerability' in s:
        print(f"| {s['scenario_id']} | {s['application']} | {s['package']['name']} | {s['package']['current_version']} | {s['package']['grype_recommended_version']} | {s['vulnerability']['cve_id']} | {s['vulnerability'].get('cvss_score', 'N/A')} |")
