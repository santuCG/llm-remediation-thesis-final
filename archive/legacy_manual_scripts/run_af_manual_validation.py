import os
import json
import subprocess
import shutil

repo_dir = r"C:\Users\HP\Downloads\llm-remediation-thesis-final\applications\airflow-repo"
evidence_freeze = r"C:\Users\HP\Downloads\llm-remediation-thesis-final\applications\evidence\airflow_pip_freeze.txt"
scenarios_file = r"C:\Users\HP\Downloads\llm-remediation-thesis-final\experiment\archive\final_18_scenarios.json"
output_dir = r"C:\Users\HP\Downloads\llm-remediation-thesis-final\experiment\raw_outputs"
results_file = r"C:\Users\HP\Downloads\llm-remediation-thesis-final\experiment\manual_validation_results.csv"

os.makedirs(output_dir, exist_ok=True)

with open(scenarios_file, 'r', encoding='utf-8') as f:
    scenarios = json.load(f)

af_scenarios = [s for s in scenarios if s['scenario_id'].startswith('AF-')]

results = []

def run_cmd(cmd, cwd):
    env = os.environ.copy()
    env["PATH"] = r"C:\Users\HP\AppData\Local\Programs\Python\Python311\;C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0;C:\Users\HP\Downloads\grype;C:\Users\HP\Downloads\MSc-LLM-Remediation-Experiment\tools\syft;" + env.get("PATH", "")
    
    print(f"Running: {cmd}")
    process = subprocess.run(cmd, cwd=cwd, shell=True, env=env, capture_output=True, text=True)
    return process.returncode, process.stdout, process.stderr

# Create an isolated python environment for airflow testing to avoid mutating global Python
venv_dir = os.path.join(repo_dir, "af_venv")
run_cmd(f"python -m venv {venv_dir}", cwd=repo_dir)
pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")

for s in af_scenarios:
    scen_id = s['scenario_id']
    pkg = s['package']['name']
    cve = s['vulnerability']['cve_id']
    target_version = s['package']['grype_recommended_version']
    
    print(f"\n======================\nProcessing {scen_id}: {pkg} -> {target_version}\n======================")
    
    # 1. Baseline Generation (just from freeze file directly)
    sbom_baseline = os.path.join(output_dir, f"{scen_id}-baseline-sbom.json")
    grype_baseline = os.path.join(output_dir, f"{scen_id}-baseline-grype.json")
    
    # Copy freeze file to standard requirements.txt for syft
    baseline_req = os.path.join(output_dir, f"{scen_id}-baseline-requirements.txt")
    shutil.copy2(evidence_freeze, baseline_req)
    
    run_cmd(f"syft file:{baseline_req} -o spdx-json={sbom_baseline}", cwd=output_dir)
    run_cmd(f"grype sbom:{sbom_baseline} -o json --file {grype_baseline}", cwd=output_dir)
    
    # 2. LLM Remediation Simulation
    # Re-install baseline
    run_cmd(f"{pip_exe} install --no-deps -r {baseline_req}", cwd=repo_dir) # no deps since freeze has everything
    
    # LLM Command
    llm_cmd = f"{pip_exe} install {pkg}=={target_version}"
    print(f"Executing LLM Remediation: {llm_cmd}")
    code, out, err = run_cmd(llm_cmd, cwd=repo_dir)
    
    eresolve_triggered = False
    if code != 0 or "ERROR:" in err:
        eresolve_triggered = True
        print(f"{scen_id} Triggered Conflict/Error!")
        
    # Generate LLM freeze
    llm_req = os.path.join(output_dir, f"{scen_id}-llm-requirements.txt")
    run_cmd(f"{pip_exe} freeze > {llm_req}", cwd=repo_dir)
    
    # Generate LLM SBOM & Grype
    sbom_llm = os.path.join(output_dir, f"{scen_id}-llm-sbom.json")
    grype_llm = os.path.join(output_dir, f"{scen_id}-llm-grype.json")
    
    run_cmd(f"syft file:{llm_req} -o spdx-json={sbom_llm}", cwd=output_dir)
    run_cmd(f"grype sbom:{sbom_llm} -o json --file {grype_llm}", cwd=output_dir)
    
    # 3. Check if still vulnerable
    still_vulnerable = False
    try:
        with open(grype_llm, 'r', encoding='utf-8') as f:
            grype_data = json.load(f)
            
        vulns = [m['vulnerability']['id'] for m in grype_data.get('matches', []) if m['artifact']['name'].lower() == pkg.lower()]
        if len(vulns) > 0:
            still_vulnerable = True
            print(f"{scen_id} is STILL VULNERABLE to {len(vulns)} issues.")
        else:
            print(f"{scen_id} is FIXED.")
    except Exception as e:
        print(f"Error parsing grype output: {e}")
        still_vulnerable = True
        
    outcome = "Failed" if (eresolve_triggered or still_vulnerable) else "Success"
    
    results.append(f"{scen_id},{pkg},{pkg}=={target_version},{outcome},{eresolve_triggered},{still_vulnerable}")
    
# Append to CSV
with open(results_file, 'a', encoding='utf-8') as f:
    f.write("\n".join(results) + "\n")
    
print("\nValidation completed. Results appended to manual_validation_results.csv")
