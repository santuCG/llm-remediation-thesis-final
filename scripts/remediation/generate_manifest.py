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

    # -----------------------------------------------------------------------
    # SCENARIO ID: read from SCENARIO_ID env var (set by the workflow per-run).
    # Falls back to deriving from APP_DIR as a last resort.
    # -----------------------------------------------------------------------
    scenario_id = os.environ.get('SCENARIO_ID', '')
    if not scenario_id:
        metrics_file = os.path.join(evidence_dir, 'metrics.json')
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
                app_dir = metrics.get('application', '')
                # This fallback should never be needed if SCENARIO_ID is set correctly
                # but is kept as a safety net to avoid producing "UNKNOWN"
                scenario_id = metrics.get('scenario_id', 'UNKNOWN')
        if not scenario_id:
            scenario_id = 'UNKNOWN'

    # -----------------------------------------------------------------------
    # PROOF FIELDS: repository commit and workflow run ID are distinct.
    # GITHUB_SHA   = the git commit hash of the checked-out code
    # GITHUB_RUN_ID = the GitHub Actions workflow run identifier
    # -----------------------------------------------------------------------
    repo_commit = os.environ.get('GITHUB_SHA', 'unknown')
    workflow_run_id = os.environ.get('GITHUB_RUN_ID', 'unknown')
    repo_slug = os.environ.get('GITHUB_REPOSITORY', 'santuCG/llm-remediation-thesis-final')

    workflow_url = (
        f"https://github.com/{repo_slug}/actions/runs/{workflow_run_id}"
        if workflow_run_id != 'unknown'
        else 'unknown'
    )

    # -----------------------------------------------------------------------
    # ARTIFACT HASHES: SHA256 of every file in the evidence folder provides
    # post-hoc integrity verification. Reviewers can recompute and confirm.
    # -----------------------------------------------------------------------
    artifact_hashes = {}
    for filename in sorted(os.listdir(evidence_dir)):
        filepath = os.path.join(evidence_dir, filename)
        if os.path.isfile(filepath) and filename != 'experiment_manifest.json':
            artifact_hashes[filename] = hash_file(filepath)

    # -----------------------------------------------------------------------
    # SNAPSHOT HASHES: EPSS and KEV snapshots are cryptographically anchored
    # so the LLM's enrichment input is verifiable and temporally immutable.
    # -----------------------------------------------------------------------
    epss_path = "scripts/remediation/snapshots/epss_snapshot.json"
    kev_path = "scripts/remediation/snapshots/kev_snapshot.json"
    epss_hash = hash_file(epss_path)
    kev_hash = hash_file(kev_path)

    # Read snapshot date from epss_snapshot metadata if available
    snapshot_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        with open(epss_path, 'r') as f:
            epss_data = json.load(f)
            snapshot_date = epss_data.get('metadata', {}).get('snapshot_date', snapshot_date)
    except Exception:
        pass  # fallback to today's date

    manifest = {
        "schema_version": "2.0",
        "scenario": scenario_id,
        "repository_commit": repo_commit,
        "workflow_run_id": workflow_run_id,
        "workflow_url": workflow_url,
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "llm": {
            # Read the model actually used from LLM_MODEL_USED if the calling
            # process set it (e.g. after a fallback-model retry); otherwise
            # fall back to the configured primary model. This field must
            # reflect what actually responded, not just what was requested
            # first, since llm_reasoner.py can fall back to a different
            # model in its retry list.
            "model": os.environ.get("LLM_MODEL_USED", "gemini-2.5-flash"),
            "temperature": 0.0,
            "seed": 42,
            "topP": 1.0,
            "topK": 1
        },
        "snapshots": {
            "epss_snapshot": {
                "file": "epss_snapshot.json",
                "date": snapshot_date,
                "sha256": epss_hash
            },
            "kev_snapshot": {
                "file": "kev_snapshot.json",
                "date": snapshot_date,
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
    print(f"[MANIFEST] Generated experiment manifest at {manifest_path}")
    print(f"[MANIFEST] Scenario: {scenario_id} | Run: {workflow_run_id} | Commit: {repo_commit}")


if __name__ == "__main__":
    main()
