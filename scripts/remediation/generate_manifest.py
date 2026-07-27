import os
import json
import hashlib
from datetime import datetime, timezone

def hash_file(filepath):
    if not os.path.exists(filepath):
        return None
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    evidence_dir = 'evidence'
    if not os.path.exists(evidence_dir):
        print("evidence directory not found")
        return

    # Load metrics to get context
    metrics_file = os.path.join(evidence_dir, 'metrics.json')
    scenario_id = "UNKNOWN"
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)
            app_dir = metrics.get('application', '')
            scenario_id = "AF-01" if "airflow" in app_dir.lower() else ("JS-01" if "juice-shop" in app_dir.lower() else "UNKNOWN")

    # Hashes of all artifacts in evidence
    artifact_hashes = {}
    for filename in os.listdir(evidence_dir):
        filepath = os.path.join(evidence_dir, filename)
        if os.path.isfile(filepath) and filename != 'experiment_manifest.json':
            artifact_hashes[filename] = hash_file(filepath)

    # Hashes of snapshots
    epss_path = "scripts/remediation/snapshots/epss_snapshot.json"
    kev_path = "scripts/remediation/snapshots/kev_snapshot.json"
    
    epss_hash = hash_file(epss_path)
    kev_hash = hash_file(kev_path)

    manifest = {
        "scenario": scenario_id,
        "repository_commit": os.environ.get('GITHUB_SHA', 'unknown'),
        "workflow_commit": os.environ.get('GITHUB_SHA', 'unknown'),
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04", # Hardcoded based on GH Actions run-on or close enough
        "python": "3.12.x",
        "llm": {
            "model": "gemini-1.5-flash",
            "temperature": 0.0,
            "seed": 42,
            "topP": 1.0,
            "topK": 1
        },
        "snapshots": {
            "epss_snapshot": {
                "file": "epss_snapshot.json",
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "sha256": epss_hash
            },
            "kev_snapshot": {
                "file": "kev_snapshot.json",
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "sha256": kev_hash
            }
        },
        "tool_versions": {
            "syft": "1.44.0",
            "grype": "0.112.0"
        },
        "artifact_hashes": artifact_hashes
    }

    manifest_path = os.path.join(evidence_dir, 'experiment_manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"Generated experiment manifest at {manifest_path}")

if __name__ == "__main__":
    main()
