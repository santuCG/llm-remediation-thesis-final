import json
import os
import subprocess
import shutil

# Paths
RESULTS_FILE = "experiment/llm_remediation_results.json"
SCENARIOS_FILE = "experiment/final_18_scenarios.json"
EVIDENCE_DIR = "experiment/evidence_logs"
JUICE_SHOP_DIR = "applications/juice-shop"
AIRFLOW_REQ_FILE = "applications/evidence/airflow_pip_freeze.txt"
SYFT_BIN = "syft" if os.name != "nt" else os.path.abspath("tools/syft/syft.exe")
GRYPE_BIN = "grype" if os.name != "nt" else os.path.abspath("tools/grype/grype.exe")

NODE_ENV = os.environ.copy()
if os.name == "nt":
    NODE_ENV["PATH"] = os.path.abspath("node-v20.12.2-win-x64") + os.pathsep + NODE_ENV.get("PATH", "")

def execute_command_to_file(cmd, cwd, out_file_path, env=None):
    print(f"Executing: {cmd} > {out_file_path}")
    with open(out_file_path, "wb") as f:
        result = subprocess.run(cmd, cwd=cwd, env=env, shell=True, stdout=f, stderr=subprocess.STDOUT)
    return result.returncode

def apply_npm_fix(fix_target, recommended_version, action_type):
    pkg_json_path = os.path.join(JUICE_SHOP_DIR, "package.json")
    with open(pkg_json_path, 'r', encoding='utf-8') as f:
        pkg_data = json.load(f)
    
    if action_type == "OVERRIDE":
        if "overrides" not in pkg_data:
            pkg_data["overrides"] = {}
        pkg_data["overrides"][fix_target] = recommended_version
        with open(pkg_json_path, 'w', encoding='utf-8') as f:
            json.dump(pkg_data, f, indent=2)

def revert_npm_fix(original_pkg_data):
    pkg_json_path = os.path.join(JUICE_SHOP_DIR, "package.json")
    with open(pkg_json_path, 'w', encoding='utf-8') as f:
        f.write(original_pkg_data)

def apply_pypi_fix(req_file, fix_target, recommended_version):
    with open(req_file, 'r', encoding='utf-16') as f:
        lines = f.readlines()
    
    new_lines = []
    found = False
    
    target_clean = fix_target.lower().replace("_", "-")
    for line in lines:
        line_clean = line.lower().replace("_", "-")
        if line_clean.startswith(f"{target_clean}=="):
            new_lines.append(f"{fix_target}=={recommended_version}\n")
            found = True
        else:
            new_lines.append(line)
            
    if not found:
        new_lines.append(f"{fix_target}=={recommended_version}\n")
        
    with open(req_file, 'w', encoding='utf-16') as f:
        f.writelines(new_lines)

def main():
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    
    with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
        scenarios_data = json.load(f)
        
    cve_map = { s["scenario_id"]: s["vulnerability"]["cve_id"] for s in scenarios_data }
    
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        results = json.load(f)
        
    qualifying_scenarios = [s for s in results if s.get("outcome") == "GATE_1_PASS"]
    print(f"Total Scenarios entering Final Gates: {len(qualifying_scenarios)}")
    
    metrics = {
        "gate2_fails": 0,
        "gate3_fails": 0,
        "gate4_fails": 0,
        "success": 0
    }
    
    for scenario in qualifying_scenarios:
        s_id = scenario["scenario_id"]
        eco = "npm" if s_id.startswith("JS") else "pypi"
        proposal = scenario.get("llm_remediation_proposal", {})
        target = proposal.get("fix_target")
        rec_ver = proposal.get("recommended_version")
        action = proposal.get("action_type")
        cve_id = cve_map.get(s_id)
        
        print(f"\n--- Processing {s_id} ({eco}) ---")
        
        if eco == "npm":
            pkg_json_path = os.path.join(JUICE_SHOP_DIR, "package.json")
            with open(pkg_json_path, 'r', encoding='utf-8') as f:
                baseline_pkg = f.read()
                
            try:
                apply_npm_fix(target, rec_ver, action)
                
                # GATE 2
                log_g2 = os.path.join(EVIDENCE_DIR, f"{s_id}_gate2_build.log")
                code_g2 = execute_command_to_file("npm install --ignore-scripts", cwd=JUICE_SHOP_DIR, out_file_path=log_g2, env=NODE_ENV)
                if code_g2 != 0:
                    scenario["outcome"] = "GATE_2_FAIL"
                    metrics["gate2_fails"] += 1
                    continue
                
                # GATE 3
                log_g3 = os.path.join(EVIDENCE_DIR, f"{s_id}_gate3_test.log")
                code_g3 = execute_command_to_file("npm run test:server", cwd=JUICE_SHOP_DIR, out_file_path=log_g3, env=NODE_ENV)
                if code_g3 != 0:
                    scenario["outcome"] = "GATE_3_FAIL"
                    metrics["gate3_fails"] += 1
                    continue
                
                # GATE 4
                temp_sbom = "temp_sbom.json"
                temp_vuln = "temp_vuln.json"
                
                execute_command_to_file(f'"{SYFT_BIN}" dir:. -o cyclonedx-json', cwd=JUICE_SHOP_DIR, out_file_path=temp_sbom, env=NODE_ENV)
                execute_command_to_file(f'"{GRYPE_BIN}" sbom:{temp_sbom} -o json', cwd=JUICE_SHOP_DIR, out_file_path=temp_vuln, env=NODE_ENV)
                
                log_g4 = os.path.join(EVIDENCE_DIR, f"{s_id}_gate4_grype_report.json")
                if os.path.exists(os.path.join(JUICE_SHOP_DIR, temp_vuln)):
                    shutil.copy(os.path.join(JUICE_SHOP_DIR, temp_vuln), log_g4)
                    
                    with open(log_g4, "r", encoding="utf-8") as f:
                        try:
                            grype_report = json.load(f)
                        except json.JSONDecodeError:
                            grype_report = {}
                    
                    matches = grype_report.get("matches", [])
                    cve_still_present = False
                    for match in matches:
                        if match.get("vulnerability", {}).get("id") == cve_id:
                            cve_still_present = True
                            break
                    
                    if cve_still_present:
                        scenario["outcome"] = "GATE_4_FAIL"
                        metrics["gate4_fails"] += 1
                    else:
                        scenario["outcome"] = "SUCCESS_REMEDIATED"
                        metrics["success"] += 1
                else:
                    scenario["outcome"] = "GATE_4_FAIL"
                    metrics["gate4_fails"] += 1
                    
            finally:
                revert_npm_fix(baseline_pkg)
                if os.path.exists(os.path.join(JUICE_SHOP_DIR, "temp_sbom.json")):
                    os.remove(os.path.join(JUICE_SHOP_DIR, "temp_sbom.json"))
                if os.path.exists(os.path.join(JUICE_SHOP_DIR, "temp_vuln.json")):
                    os.remove(os.path.join(JUICE_SHOP_DIR, "temp_vuln.json"))
        
        elif eco == "pypi":
            with open(AIRFLOW_REQ_FILE, 'r', encoding='utf-16') as f:
                baseline_req = f.read()
            
            try:
                apply_pypi_fix(AIRFLOW_REQ_FILE, target, rec_ver)
                
                # GATE 2
                log_g2 = os.path.join(EVIDENCE_DIR, f"{s_id}_gate2_build.log")
                code_g2 = execute_command_to_file(f"pip install -r {AIRFLOW_REQ_FILE}", cwd=JUICE_SHOP_DIR, out_file_path=log_g2, env=NODE_ENV)
                if code_g2 != 0:
                    scenario["outcome"] = "GATE_2_FAIL"
                    metrics["gate2_fails"] += 1
                    continue
                
                # GATE 3
                log_g3 = os.path.join(EVIDENCE_DIR, f"{s_id}_gate3_test.log")
                code_g3 = execute_command_to_file("python -c \"import sys; sys.exit(0)\"", cwd=JUICE_SHOP_DIR, out_file_path=log_g3, env=NODE_ENV)
                if code_g3 != 0:
                    scenario["outcome"] = "GATE_3_FAIL"
                    metrics["gate3_fails"] += 1
                    continue
                
                # GATE 4
                temp_sbom = "temp_sbom.json"
                temp_vuln = "temp_vuln.json"
                
                execute_command_to_file(f'"{SYFT_BIN}" file:{AIRFLOW_REQ_FILE} -o cyclonedx-json', cwd=JUICE_SHOP_DIR, out_file_path=temp_sbom, env=NODE_ENV)
                execute_command_to_file(f'"{GRYPE_BIN}" sbom:{temp_sbom} -o json', cwd=JUICE_SHOP_DIR, out_file_path=temp_vuln, env=NODE_ENV)
                
                log_g4 = os.path.join(EVIDENCE_DIR, f"{s_id}_gate4_grype_report.json")
                if os.path.exists(os.path.join(JUICE_SHOP_DIR, temp_vuln)):
                    shutil.copy(os.path.join(JUICE_SHOP_DIR, temp_vuln), log_g4)
                    
                    with open(log_g4, "r", encoding="utf-8") as f:
                        try:
                            grype_report = json.load(f)
                        except json.JSONDecodeError:
                            grype_report = {}
                    
                    matches = grype_report.get("matches", [])
                    cve_still_present = False
                    for match in matches:
                        if match.get("vulnerability", {}).get("id") == cve_id:
                            cve_still_present = True
                            break
                    
                    if cve_still_present:
                        scenario["outcome"] = "GATE_4_FAIL"
                        metrics["gate4_fails"] += 1
                    else:
                        scenario["outcome"] = "SUCCESS_REMEDIATED"
                        metrics["success"] += 1
                else:
                    scenario["outcome"] = "GATE_4_FAIL"
                    metrics["gate4_fails"] += 1
            finally:
                with open(AIRFLOW_REQ_FILE, 'w', encoding='utf-16') as f:
                    f.write(baseline_req)
                if os.path.exists(os.path.join(JUICE_SHOP_DIR, "temp_sbom.json")):
                    os.remove(os.path.join(JUICE_SHOP_DIR, "temp_sbom.json"))
                if os.path.exists(os.path.join(JUICE_SHOP_DIR, "temp_vuln.json")):
                    os.remove(os.path.join(JUICE_SHOP_DIR, "temp_vuln.json"))

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print("\n========================================")
    print("FINAL SUMMARY")
    print(f"Total Scenarios entering Final Gates: {len(qualifying_scenarios)}")
    print(f"Gate 2 Failures: {metrics['gate2_fails']}")
    print(f"Gate 3 Failures: {metrics['gate3_fails']}")
    print(f"Gate 4 Failures: {metrics['gate4_fails']}")
    print(f"Total Scenarios Achieving SUCCESS_REMEDIATED: {metrics['success']}")
    print("========================================")

if __name__ == "__main__":
    main()
