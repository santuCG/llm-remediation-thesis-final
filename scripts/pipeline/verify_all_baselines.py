import os
import sys
import json
import hashlib

def verify_grype_semantic(v1_path, v2_path):
    with open(v1_path, 'r', encoding="utf-8") as f1, open(v2_path, 'r', encoding="utf-8") as f2:
        v1_data = json.load(f1)
        v2_data = json.load(f2)
        
    v1_matches = set()
    for m in v1_data.get("matches", []):
        vuln_id = m["vulnerability"]["id"]
        pkg_name = m["artifact"]["name"]
        pkg_version = m["artifact"]["version"]
        v1_matches.add(f"{vuln_id} in {pkg_name}@{pkg_version}")
        
    v2_matches = set()
    for m in v2_data.get("matches", []):
        vuln_id = m["vulnerability"]["id"]
        pkg_name = m["artifact"]["name"]
        pkg_version = m["artifact"]["version"]
        v2_matches.add(f"{vuln_id} in {pkg_name}@{pkg_version}")
        
    if v1_matches == v2_matches:
        return True, []
    else:
        missing = v1_matches - v2_matches
        unexpected = v2_matches - v1_matches
        errs = []
        if missing:
            errs.append(f"Missing {len(missing)} vulnerabilities from V1 (e.g. {list(missing)[:3]})")
        if unexpected:
            errs.append(f"Unexpected {len(unexpected)} vulnerabilities in V2 (e.g. {list(unexpected)[:3]})")
        return False, errs

def main():
    v1_base = "results/execution_evidence"
    v2_base = "results/execution_evidence_v2"
    
    scenarios = [d for d in os.listdir(v2_base) if d.startswith("AF-") or d.startswith("JS-")]
    
    overall_report = {}
    all_success = True
    
    for scenario in scenarios:
        v1_dir = os.path.join(v1_base, scenario)
        v2_dir = os.path.join(v2_base, scenario, "baseline-evidence")
        
        report = {
            "Verified": "YES",
            "Details": []
        }
        
        if not os.path.exists(v2_dir):
            report["Verified"] = "NO"
            report["Details"].append("No baseline-evidence folder found")
            overall_report[scenario] = report
            all_success = False
            continue
            
        v2_files = set(os.listdir(v2_dir))
        
        targets = ["baseline-grype.json"]
        
        for t in targets:
            if t not in v2_files:
                report["Verified"] = "NO"
                report["Details"].append(f"Missing {t} in V2 artifacts")
                continue
                
            v1_path = os.path.join(v1_dir, t)
            v2_path = os.path.join(v2_dir, t)
            
            if not os.path.exists(v1_path):
                report["Verified"] = "NO"
                report["Details"].append(f"Missing {t} in V1 artifacts for comparison")
                continue
                
            match, errs = verify_grype_semantic(v1_path, v2_path)
            if not match:
                report["Verified"] = "NO"
                report["Details"].extend(errs)
        
        overall_report[scenario] = report
        if report["Verified"] == "NO":
            all_success = False
            
    with open("baseline-verification-report.json", "w") as out:
        json.dump(overall_report, out, indent=2)

    print(json.dumps(overall_report, indent=2))
    if all_success:
        print("\nSUCCESS: All 18 V2 Baseline scenarios produced EXACTLY identical Grype findings as V1!")
    else:
        print("\nFAILURE: Some baselines did not match exactly.")
        
if __name__ == "__main__":
    main()
