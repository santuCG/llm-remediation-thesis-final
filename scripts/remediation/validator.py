import json

def validate_remediation(grype_json_path, target_cve_id):
    try:
        with open(grype_json_path, 'r') as f:
            data = json.load(f)
            
        matches = data.get('matches', [])
        for match in matches:
            vuln_id = match.get('vulnerability', {}).get('id', '')
            related = [r.get('id', '') for r in match.get('relatedVulnerabilities', [])]
            
            if vuln_id == target_cve_id or target_cve_id in related:
                print(f"[VALIDATOR] FAILED: {target_cve_id} is still present.")
                return False
                
        print(f"[VALIDATOR] SUCCESS: {target_cve_id} has been eradicated.")
        return True
    except Exception as e:
        print(f"[ERROR] Validator failed to read JSON: {e}")
        return False
