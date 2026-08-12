import os
import subprocess
import time
import json
import sys

SCENARIOS_FILE = "experiment/archive/final_18_scenarios.json"
GH_BIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "gh_cli", "bin", "gh.exe"))

def run_command(cmd_args, capture=True):
    env = os.environ.copy()
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    env["GH_TOKEN"] = line.split("=", 1)[1].strip().strip('"').strip("'")
                    
    result = subprocess.run(cmd_args, env=env, capture_output=capture, text=True)
    return result

def main():
    if not os.path.exists(SCENARIOS_FILE):
        print(f"[ERROR] Cannot find scenarios file at {SCENARIOS_FILE}")
        sys.exit(1)

    with open(SCENARIOS_FILE, 'r') as f:
        scenarios = json.load(f)

    # Filter out scenarios that don't have IDs
    valid_scenarios = [s for s in scenarios if s.get("scenario_id") and s.get("vulnerability", {}).get("cve_id")]
    
    print("=============================================")
    print("DISPATCHING GRYPE BASELINE SCENARIOS")
    print("=============================================")
    
    for scenario in valid_scenarios:
        s_id = scenario.get("scenario_id")
        cve_id = scenario.get("vulnerability", {}).get("cve_id")
        
        trigger_cmd = [GH_BIN, "workflow", "run", "grype-baseline.yml", "-f", f"target_cve={cve_id}"]
        res = run_command(trigger_cmd)
        if res.returncode == 0:
            print(f"[+] Dispatched Grype Baseline workflow for {s_id} ({cve_id})")
        else:
            print(f"[-] Failed to dispatch {s_id}: {res.stderr}")
            
        time.sleep(5)  # Slight delay to avoid workflow dispatch rate limits

    print("\n[!] All baseline scenarios dispatched. Please check GitHub Actions UI for results.")

if __name__ == "__main__":
    main()
