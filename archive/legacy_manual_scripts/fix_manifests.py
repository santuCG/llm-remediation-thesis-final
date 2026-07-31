import os, json, re

for d in os.listdir('results/execution_evidence'):
    p = os.path.join('results/execution_evidence', d, 'experiment_manifest.json')
    if os.path.exists(p):
        with open(p, 'r') as f:
            content = f.read()
            # Strip trailing comments (// or /*)
            content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            try:
                data = json.loads(content)
                data['scenario'] = d
                with open(p, 'w') as outf:
                    json.dump(data, outf, indent=2)
            except Exception as e:
                print(f"Error parsing {p}: {e}")
