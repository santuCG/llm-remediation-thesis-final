import os
import subprocess
import time
import json
import sys

# We need the 18 scenarios to iterate over. 
# Since final_18_scenarios.json was archived, we can read it from the archive.
SCENARIOS_FILE = "experiment/archive/final_18_scenarios.json"
RESULTS_BASE_DIR = "results"
GH_BIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "gh_cli", "bin", "gh.exe"))
import configparser

def run_command(cmd_args):
    print(f"[CMD] {' '.join(cmd_args)}")
    env = os.environ.copy()
    
    # Check if .env has GH_TOKEN
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    env["GH_TOKEN"] = line.split("=", 1)[1].strip().strip('"').strip("'")
                    
    result = subprocess.run(cmd_args, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Command failed with exit code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    return result

def main():
    if not os.path.exists(SCENARIOS_FILE):
        print(f"[ERROR] Cannot find scenarios file at {SCENARIOS_FILE}")
        sys.exit(1)

    with open(SCENARIOS_FILE, 'r') as f:
        scenarios = json.load(f)

    # If the user wants to test just JS-01 and JS-08 first, we can filter them here if we pass an argument
    test_run = len(sys.argv) > 1 and sys.argv[1] == "--test"
    
    for scenario in scenarios:
        s_id = scenario.get("scenario_id")
        cve_id = scenario.get("vulnerability", {}).get("cve_id")
        
        if not s_id or not cve_id:
            continue
            
        if test_run and s_id not in ["JS-01", "JS-08"]:
            continue
            
        print(f"\n=============================================")
        print(f"Starting Execution for {s_id} ({cve_id})")
        print(f"=============================================")
        
        # 1. Trigger the workflow
        trigger_cmd = [GH_BIN, "workflow", "run", "generic-remediation.yml", "-f", f"target_cve={cve_id}"]
        if run_command(trigger_cmd).returncode != 0:
            print(f"[ERROR] Failed to trigger workflow for {s_id}")
            continue
            
        print(f"[*] Waiting for workflow to register in GitHub Actions queue (15 seconds)...")
        time.sleep(15)
        
        # 2. Fetch Run ID
        list_cmd = [GH_BIN, "run", "list", "--workflow=generic-remediation.yml", "-L", "1", "--json", "databaseId,headSha"]
        res = run_command(list_cmd)
        if res.returncode != 0:
            print(f"[ERROR] Failed to fetch run ID for {s_id}")
            continue
            
        try:
            run_info = json.loads(res.stdout)[0]
            run_id = run_info["databaseId"]
            head_sha = run_info["headSha"]
            print(f"[*] Found RUN_ID: {run_id}")
            print(f"[*] Found Baseline Commit SHA: {head_sha}")
        except Exception as e:
            print(f"[ERROR] Failed to parse run list JSON: {e}")
            continue
            
        # 3. Watch and Wait
        print(f"[*] Watching RUN_ID {run_id} until completion...")
        watch_cmd = [GH_BIN, "run", "watch", str(run_id)]
        run_command(watch_cmd)
        
        # 4. Download Evidence
        target_dir = os.path.join(RESULTS_BASE_DIR, s_id, "automated")
        os.makedirs(target_dir, exist_ok=True)
        
        # Also create the manual baseline directory as scaffolded by the blueprint
        manual_dir = os.path.join(RESULTS_BASE_DIR, s_id, "manual")
        os.makedirs(manual_dir, exist_ok=True)
        
        print(f"[*] Downloading evidence to {target_dir}")
        download_cmd = [GH_BIN, "run", "download", str(run_id), "-D", target_dir]
        run_command(download_cmd)
        
        print(f"[*] Successfully completed automated pipeline loop for {s_id}")
        
    print("\n[SUCCESS] Orchestration loop complete.")

if __name__ == "__main__":
    main()
