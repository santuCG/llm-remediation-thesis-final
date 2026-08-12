import os
import subprocess
import time
import json
import sys
import shutil

SCENARIOS_FILE = "results/scenarios/pre_registered/scenarios.json"
RESULTS_BASE_DIR = "results"
GH_BIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "gh_cli", "bin", "gh.exe"))

def run_command(cmd_args, capture=True):
    env = os.environ.copy()
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
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
    print("DISPATCHING SCENARIOS (BATCHED TO AVOID API RATE LIMITS)")
    print("=============================================")
    
    tracking_map = {} # CVE -> Scenario ID
    BATCH_SIZE = 3
    
    for i in range(0, len(valid_scenarios), BATCH_SIZE):
        batch = valid_scenarios[i:i+BATCH_SIZE]
        
        for scenario in batch:
            s_id = scenario.get("scenario_id")
            cve_id = scenario.get("vulnerability", {}).get("cve_id")
            tracking_map[cve_id] = s_id
            
            trigger_cmd = [GH_BIN, "workflow", "run", "generic-remediation.yml", "-f", f"target_cve={cve_id}"]
            res = run_command(trigger_cmd)
            if res.returncode == 0:
                print(f"[+] Dispatched workflow for {s_id} ({cve_id})")
            else:
                print(f"[-] Failed to dispatch {s_id}: {res.stderr}")
                
        if i + BATCH_SIZE < len(valid_scenarios):
            print(f"\n[*] Waiting 60 seconds to respect Gemini API rate limits (15 RPM)...")
            time.sleep(60)

    print("\n[!] All batches dispatched. Polling GitHub Actions for completion...")
    
    # 2. Poll and Download
    completed_runs = set()
    all_dispatched = len(tracking_map)
    
    while len(completed_runs) < all_dispatched:
        print(f"[*] Polling GitHub Actions... ({len(completed_runs)}/{all_dispatched} completed)")
        
        # Fetch the most recent 100 runs
        list_cmd = [GH_BIN, "run", "list", "--workflow=generic-remediation.yml", "-L", "100", "--json", "databaseId,status"]
        res = run_command(list_cmd)
        
        if res.returncode == 0:
            try:
                runs = json.loads(res.stdout)
                for run in runs:
                    run_id = run["databaseId"]
                    status = run["status"]
                    
                    if status == "completed" and run_id not in completed_runs:
                        temp_dir = os.path.join(RESULTS_BASE_DIR, "temp_downloads", str(run_id))
                        os.makedirs(temp_dir, exist_ok=True)
                        dl_cmd = [GH_BIN, "run", "download", str(run_id), "-D", temp_dir]
                        dl_res = run_command(dl_cmd)
                        
                        metrics_path = os.path.join(temp_dir, "remediation-evidence", "metrics.json")
                        if os.path.exists(metrics_path):
                            with open(metrics_path, 'r') as mf:
                                metrics_data = json.load(mf)
                                cve = metrics_data.get("selected_cve")
                                
                                if cve in tracking_map:
                                    s_id = tracking_map[cve]
                                    target_dir = os.path.join(RESULTS_BASE_DIR, s_id, "automated")
                                    os.makedirs(target_dir, exist_ok=True)
                                    
                                    evidence_dir = os.path.join(temp_dir, "remediation-evidence")
                                    for file_name in os.listdir(evidence_dir):
                                        shutil.move(os.path.join(evidence_dir, file_name), os.path.join(target_dir, file_name))
                                        
                                    print(f"[SUCCESS] Downloaded evidence for {s_id} ({cve}) from Run {run_id}")
                                    completed_runs.add(run_id)
                                    del tracking_map[cve]
                        
                        shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                pass
                
        if len(tracking_map) > 0:
            time.sleep(30)

    print("\n[SUCCESS] ALL SCENARIOS COMPLETED AND DOWNLOADED!")

if __name__ == "__main__":
    main()
