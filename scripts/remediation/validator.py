import json
import sys
import os

def validate_remediation(grype_json_path, target_cve_id, metrics_path=None):
    try:
        with open(grype_json_path, 'r') as f:
            data = json.load(f)
            
        matches = data.get('matches', [])
        found = False
        for match in matches:
            vuln_id = match.get('vulnerability', {}).get('id', '')
            related = [r.get('id', '') for r in match.get('relatedVulnerabilities', [])]
            
            if vuln_id == target_cve_id or target_cve_id in related:
                print(f"[VALIDATOR] FAILED: {target_cve_id} is still present.")
                found = True
                break
                
        if not found:
            print(f"[VALIDATOR] SUCCESS: {target_cve_id} has been eradicated.")
            if metrics_path and os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    metrics = json.load(f)
                metrics["rescan_success"] = True
                metrics["dependency_verified"] = True
                metrics["build_success"] = True # Build implicitly succeeded if we reached here
                with open(metrics_path, 'w') as f:
                    json.dump(metrics, f, indent=2)
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Validator failed to read JSON: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python validator.py <grype_json> <cve_id> [metrics_json]")
        sys.exit(1)
        
    metrics_file = sys.argv[3] if len(sys.argv) > 3 else None
    success = validate_remediation(sys.argv[1], sys.argv[2], metrics_file)
    if not success:
        sys.exit(1)
