import json
import sys

def discover_vulnerabilities(grype_json_path):
    try:
        with open(grype_json_path, 'r') as f:
            data = json.load(f)
        matches = data.get('matches', [])
        print(f'[DISCOVER] Found {len(matches)} vulnerabilities in {grype_json_path}')
        return matches
    except Exception as e:
        print(f'[ERROR] Failed to parse Grype JSON: {e}')
        sys.exit(1)
