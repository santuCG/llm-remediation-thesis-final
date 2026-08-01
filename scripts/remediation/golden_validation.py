import json
import yaml
import sys
import os

def main(profile_path, metrics_path):
    if not os.path.exists(profile_path) or not os.path.exists(metrics_path):
        print(f"Error: Missing profile or metrics. {profile_path} {metrics_path}")
        sys.exit(1)
        
    with open(profile_path, 'r') as f:
        profile = yaml.safe_load(f)
        
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
        
    expected = profile.get('expected', {})
    if not expected:
        print("Warning: No expected golden values in profile. Skipping validation.")
        with open('validation-report.json', 'w') as f:
            json.dump({"status": "SKIPPED"}, f)
        return
        
    actual = {
        "candidate": metrics.get('selected_package'),
        "strategy": metrics.get('strategy')
    }
    
    status = "PASS"
    if expected.get('candidate') != actual.get('candidate') or expected.get('strategy') != actual.get('strategy'):
        status = "FAIL"
        
    report = {
        "expected": expected,
        "actual": actual,
        "status": status
    }
    
    with open('validation-report.json', 'w') as f:
        json.dump(report, f, indent=2)
        
    print(f"Golden Validation Status: {status}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: golden_validation.py <profile_path> <metrics_path>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
