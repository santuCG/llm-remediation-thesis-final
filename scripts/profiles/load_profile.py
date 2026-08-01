import yaml
import os
import sys

def main(profile_path):
    if not os.path.exists(profile_path):
        print(f"Error: Profile {profile_path} not found.")
        sys.exit(1)
        
    with open(profile_path, 'r') as f:
        profile = yaml.safe_load(f)

    env_file = os.environ.get('GITHUB_ENV')
    if not env_file:
        print("Error: GITHUB_ENV not set.")
        sys.exit(1)

    with open(env_file, 'a') as ef:
        ef.write(f"SCENARIO_ID={profile.get('scenario_id', 'UNKNOWN')}\n")
        ef.write(f"APP_DIR={profile.get('application', '')}\n")
        ef.write(f"TARGET_CVE={profile.get('target_cve', '')}\n")
        
        # Tool versions
        tool_versions = profile.get('tool_versions', {})
        ef.write(f"NODE_VERSION={tool_versions.get('node', '20.x')}\n")
        ef.write(f"PYTHON_VERSION={tool_versions.get('python', '3.11.x')}\n")
        ef.write(f"SYFT_VERSION={tool_versions.get('syft', 'v1.44.0')}\n")
        ef.write(f"GRYPE_VERSION={tool_versions.get('grype', 'v0.112.0')}\n")
        
        # Baseline variables
        baseline = profile.get('baseline', {})
        if baseline.get('restore_lockfile'):
            ef.write(f"RESTORE_LOCKFILE=true\n")
            ef.write(f"LOCKFILE_SOURCE={baseline.get('lockfile', '')}\n")
        else:
            ef.write(f"RESTORE_LOCKFILE=false\n")
            
        print(f"Successfully loaded profile {profile.get('scenario_id')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: load_profile.py <path_to_profile.yaml>")
        sys.exit(1)
    main(sys.argv[1])
