import os
import json
import subprocess
import shutil

repo_dir = r"C:\Users\HP\Downloads\llm-remediation-thesis-final\applications\juice-shop-repo"
evidence_lockfile = r"C:\Users\HP\Downloads\llm-remediation-thesis-final\applications\evidence\juice_shop_package-lock.json"
scenarios_file = r"C:\Users\HP\Downloads\llm-remediation-thesis-final\experiment\archive\final_18_scenarios.json"
output_dir = r"C:\Users\HP\Downloads\llm-remediation-thesis-final\experiment\raw_outputs"
results_file = r"C:\Users\HP\Downloads\llm-remediation-thesis-final\experiment\manual_validation_results.csv"

# Make sure output exists
os.makedirs(output_dir, exist_ok=True)

with open(scenarios_file, 'r', encoding='utf-8') as f:
    scenarios = json.load(f)

js_scenarios = [s for s in scenarios if s['scenario_id'].startswith('JS-')]

results = []

def run_cmd(cmd, cwd):
    # Setup PATH for grype, syft, node, etc.
    env = os.environ.copy()
    env["PATH"] = r"C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0;C:\Program Files\Git\cmd;C:\Program Files\nodejs;C:\Users\HP\Downloads\grype;C:\Users\HP\Downloads\MSc-LLM-Remediation-Experiment\tools\syft;" + env.get("PATH", "")
    
    print(f"Running: {cmd}")
    process = subprocess.run(cmd, cwd=cwd, shell=True, env=env, capture_output=True, text=True)
    return process.returncode, process.stdout, process.stderr

for s in js_scenarios:
    scen_id = s['scenario_id']
    pkg = s['package']['name']
    cve = s['vulnerability']['cve_id']
    target_version = s['package']['grype_recommended_version']
    
    print(f"\n======================\nProcessing {scen_id}: {pkg} -> {target_version}\n======================")
    
    # 1. Reset Lockfile (Baseline)
    target_lockfile = os.path.join(repo_dir, "package-lock.json")
    shutil.copy2(evidence_lockfile, target_lockfile)
    
    # 2. Baseline generation
    run_cmd("npm ci --ignore-scripts", cwd=repo_dir)
    
    sbom_baseline = os.path.join(output_dir, f"{scen_id}-baseline-sbom.json")
    grype_baseline = os.path.join(output_dir, f"{scen_id}-baseline-grype.json")
    
    run_cmd(f"syft file:package-lock.json -o spdx-json={sbom_baseline}", cwd=repo_dir)
    run_cmd(f"grype sbom:{sbom_baseline} -o json --file {grype_baseline}", cwd=repo_dir)
    
    # 3. LLM Remediation Simulation
    # Strategy: "npm install pkg@version --ignore-scripts"
    llm_cmd = f"npm install {pkg}@{target_version} --ignore-scripts"
    print(f"Executing LLM Remediation: {llm_cmd}")
    code, out, err = run_cmd(llm_cmd, cwd=repo_dir)
    
    eresolve_triggered = False
    if code != 0 or "ERESOLVE" in err or "ERESOLVE" in out:
        eresolve_triggered = True
        print(f"{scen_id} Triggered ERESOLVE!")
        
    # 4. LLM Generation
    sbom_llm = os.path.join(output_dir, f"{scen_id}-llm-sbom.json")
    grype_llm = os.path.join(output_dir, f"{scen_id}-llm-grype.json")
    
    run_cmd(f"syft file:package-lock.json -o spdx-json={sbom_llm}", cwd=repo_dir)
    run_cmd(f"grype sbom:{sbom_llm} -o json --file {grype_llm}", cwd=repo_dir)
    
    # 5. Check if still vulnerable
    still_vulnerable = False
    try:
        with open(grype_llm, 'r', encoding='utf-8') as f:
            grype_data = json.load(f)
            
        vulns = [m['vulnerability']['id'] for m in grype_data.get('matches', []) if m['artifact']['name'] == pkg]
        if len(vulns) > 0:
            still_vulnerable = True
            print(f"{scen_id} is STILL VULNERABLE to {len(vulns)} issues.")
        else:
            print(f"{scen_id} is FIXED.")
    except Exception as e:
        print(f"Error parsing grype output: {e}")
        still_vulnerable = True
        
    outcome = "Failed" if (eresolve_triggered or still_vulnerable) else "Success"
    
    results.append(f"{scen_id},{pkg},{llm_cmd},{outcome},{eresolve_triggered},{still_vulnerable}")
    
# Write CSV
csv_header = "Scenario_ID,Target_Package,Basic_LLM_Remediation_Step,Outcome,ERESOLVE_Triggered,Still_Vulnerable\n"
with open(results_file, 'w', encoding='utf-8') as f:
    f.write(csv_header)
    f.write("\n".join(results))
    
print("\nValidation completed. Results written to manual_validation_results.csv")
