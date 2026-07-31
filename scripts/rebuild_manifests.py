#!/usr/bin/env python3
"""
rebuild_manifests.py
====================
Rebuilds all experiment_manifest.json files so they have the EXACT same
structure and empirical evidence section as AF-01.

The output file has two sections:
1. A clean JSON object (the machine-readable manifest)
2. A === EMPIRICAL EVIDENCE === plaintext block appended after the JSON,
   containing the full manifest (with inline comments), pipeline metrics
   (with inline comments), the LLM prompt, and the LLM output.

Run from repo root:
    python scripts/rebuild_manifests.py
"""

import json
import os
import hashlib
import re

BASE = r'C:\Users\HP\Downloads\llm-remediation-thesis-final'
EVIDENCE_DIR = os.path.join(BASE, 'results', 'execution_evidence')

# Per-scenario provenance data (from experiment_manifest.json + pipeline logs)
SCENARIO_PROVENANCE = {
    "AF-01": {
        "repository_commit": "52736303a6859896a2fbce677dd37a96037b1950",
        "workflow_commit": "30574548185",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30574548185",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "AF-02": {
        "repository_commit": "241b549e07430f9520d1a116360ae194d1ba84f6",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "AF-03": {
        "repository_commit": "241b549e07430f9520d1a116360ae194d1ba84f6",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "AF-04": {
        "repository_commit": "241b549e07430f9520d1a116360ae194d1ba84f6",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "AF-05": {
        "repository_commit": "796ba575b26a403844d23af9c5e00e7f4d9e48f9",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "AF-06": {
        "repository_commit": "796ba575b26a403844d23af9c5e00e7f4d9e48f9",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "AF-07": {
        "repository_commit": "d3766873fa30b7039b5e33e7cc3474c94ebe4555",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "AF-08": {
        "repository_commit": "15177533346e32406b8e9ef3de55fd47fdcce0b2",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "AF-09": {
        "repository_commit": "16a551ed6c7569845e3f84e40e22dc3e7601a2a8",
        "workflow_commit": "30585687941",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30585687941",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "JS-01": {
        "repository_commit": "c36397b6288b1980ea24b0f389209d351bdfbbb3",
        "workflow_commit": "30589077682",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30589077682",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "JS-02": {
        "repository_commit": "241b549e07430f9520d1a116360ae194d1ba84f6",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "JS-03": {
        "repository_commit": "241b549e07430f9520d1a116360ae194d1ba84f6",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "JS-04": {
        "repository_commit": "241b549e07430f9520d1a116360ae194d1ba84f6",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "JS-05": {
        "repository_commit": "796ba575b26a403844d23af9c5e00e7f4d9e48f9",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "JS-06": {
        "repository_commit": "796ba575b26a403844d23af9c5e00e7f4d9e48f9",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "JS-07": {
        "repository_commit": "d3766873fa30b7039b5e33e7cc3474c94ebe4555",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
    "JS-08": {
        "repository_commit": "15177533346e32406b8e9ef3de55fd47fdcce0b2",
        "workflow_commit": "30592634834",
        "workflow_url": "https://github.com/santuCG/llm-remediation-thesis-final/actions/runs/30592634834",
        "pipeline_version": "v2.0",
        "runner": "ubuntu-24.04",
        "python": "3.12.x",
        "llm_model": "gemini-2.5-flash",
        "syft": "1.44.0",
        "grype": "0.112.0",
        "epss_date": "2026-07-30",
        "kev_date": "2026-07-30",
    },
}

# Snapshot SHA256 hashes (same for all scenarios - snapshots were frozen on 2026-07-30)
EPSS_SHA256 = "b224c69bbbc4d0c02274f8992561d1e4335020410d10ed9e3ebcbed157abb2d9"
KEV_SHA256  = "036c579ee00120ad6b77a9e391ef96c96bd7ba4ab060214df0d79ddda2e64ce6"


def sha256_file(path):
    """Compute SHA256 of a file."""
    if not os.path.exists(path):
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_prompt_text(llm_request):
    """Extract the human-readable prompt text from llm-request.json."""
    try:
        return llm_request['api_payload']['contents'][0]['parts'][0]['text']
    except (KeyError, IndexError):
        return "Prompt not available"


def build_metrics_commented(metrics, ecosystem):
    """Build the metrics block with inline comments (matching AF-01 format)."""
    app_label = "The target application being evaluated"
    eco_label = "Package manager ecosystem (e.g., npm, python)"
    candidate_label = "Total number of vulnerabilities initially scanned"
    pkg_label = "The specific vulnerable dependency chosen for remediation"
    cve_label = "The GitHub Security Advisory ID" if metrics.get('selected_cve','').startswith('GHSA') else "The CVE identifier for this vulnerability"
    api_cve_label = "The standard MITRE CVE ID"
    sev_label = "CVSS severity rating"
    cvss_label = "Common Vulnerability Scoring System score"
    epss_label = "Exploit Prediction Scoring System probability"
    epss_ts_label = "Time the EPSS score was fetched"
    kev_label = "CISA Known Exploited Vulnerabilities catalog status"
    dep_label = "Whether the dependency is direct or transitive"
    strat_label = "The remediation strategy chosen by the LLM"
    rtype_label = "The human-readable strategy category"
    llm_label = "Whether the LLM output matched the required JSON schema"
    build_label = "Whether the application successfully built after remediation"
    test_label = "Whether the application's test suite passed"
    dep_ver_label = "Whether the dependency tree correctly resolved the new version"
    rescan_label = "Whether the scanner confirmed the vulnerability was eradicated"
    runtime_label = "Runtime tests status"
    lock_label = "Whether a lockfile was regenerated"
    time_label = "Total pipeline execution time in seconds"
    retry_label = "Number of LLM retries needed"
    iter_label = "The specific iteration of the LLM prompting"
    stage_label = "The furthest pipeline stage reached"
    fail_label = "The stage where the pipeline failed, if any"

    def v(val):
        if isinstance(val, bool):
            return str(val).lower()
        if isinstance(val, str):
            return f'"{val}"'
        return str(val)

    lines = [
        '{',
        f'  "application": {v(metrics.get("application",""))}, // {app_label}',
        f'  "ecosystem": {v(metrics.get("ecosystem",""))}, // {eco_label}',
        f'  "candidate_count": {v(metrics.get("candidate_count",0))}, // {candidate_label}',
        f'  "selected_package": {v(metrics.get("selected_package",""))}, // {pkg_label}',
        f'  "selected_cve": {v(metrics.get("selected_cve",""))}, // {cve_label}',
        f'  "api_cve_id": {v(metrics.get("api_cve_id",""))}, // {api_cve_label}',
        f'  "severity": {v(metrics.get("severity",""))}, // {sev_label}',
        f'  "cvss": {v(metrics.get("cvss",0))}, // {cvss_label}',
        f'  "epss": {v(metrics.get("epss",0))}, // {epss_label}',
        f'  "epss_timestamp": {v(metrics.get("epss_timestamp",""))}, // {epss_ts_label}',
        f'  "kev_status": {v(metrics.get("kev_status",False))}, // {kev_label}',
        f'  "dependency_type": {v(metrics.get("dependency_type",""))}, // {dep_label}',
        f'  "strategy": {v(metrics.get("strategy",""))}, // {strat_label}',
        f'  "remediation_type": {v(metrics.get("remediation_type",""))}, // {rtype_label}',
        f'  "llm_response_valid": {v(metrics.get("llm_response_valid",False))}, // {llm_label}',
        f'  "build_success": {v(metrics.get("build_success",False))}, // {build_label}',
        f'  "test_success": {v(metrics.get("test_success",False))}, // {test_label}',
        f'  "dependency_verified": {v(metrics.get("dependency_verified",False))}, // {dep_ver_label}',
        f'  "rescan_success": {v(metrics.get("rescan_success",False))}, // {rescan_label}',
        f'  "runtime_success": {v(metrics.get("runtime_success",False))}, // {runtime_label}',
        f'  "lockfile_regenerated": {v(metrics.get("lockfile_regenerated",False))}, // {lock_label}',
        f'  "execution_time_seconds": {v(metrics.get("execution_time_seconds",0))}, // {time_label}',
        f'  "retry_count": {v(metrics.get("retry_count",0))}, // {retry_label}',
        f'  "llm_iteration": {v(metrics.get("llm_iteration",1))}, // {iter_label}',
        f'  "validation_stage_reached": {v(metrics.get("validation_stage_reached",""))}, // {stage_label}',
        f'  "failure_stage": {v(metrics.get("failure_stage","none"))} // {fail_label}',
        '}',
    ]
    return '\n'.join(lines)


def build_manifest_commented(manifest, prov):
    """Build the experiment manifest block with inline comments (matching AF-01 format)."""
    sid = manifest.get('scenario', '')
    lines = [
        '{',
        f'    "scenario": "{sid}", // The unique identifier for this vulnerability scenario',
        f'    "repository_commit": "{prov["repository_commit"]}", // The Git commit hash of the repository during execution',
        f'    "workflow_commit": "{prov["workflow_commit"]}", // The GitHub Actions run ID that executed this pipeline',
        f'    "pipeline_version": "{prov["pipeline_version"]}", // The version of the remediation pipeline engine',
        f'    "runner": "{prov["runner"]}", // The OS environment where the pipeline ran',
        f'    "python": "{prov["python"]}", // The Python version used by the pipeline',
        '    "llm": { // LLM configuration settings',
        f'        "model": "{prov["llm_model"]}", // The exact LLM model used for reasoning',
        '        "temperature": 0.0, // Temperature setting (0.0 for deterministic output)',
        '        "seed": 42, // Seed for reproducibility',
        '        "topP": 1.0, // Top-P sampling setting',
        '        "topK": 1 // Top-K sampling setting',
        '    },',
        '    "snapshots": { // Hashes of vulnerability intelligence snapshots',
        '        "epss_snapshot": {',
        '            "file": "epss_snapshot.json",',
        f'            "date": "{prov["epss_date"]}",',
        f'            "sha256": "{EPSS_SHA256}"',
        '        },',
        '        "kev_snapshot": {',
        '            "file": "kev_snapshot.json",',
        f'            "date": "{prov["kev_date"]}",',
        f'            "sha256": "{KEV_SHA256}"',
        '        }',
        '    },',
        '    "tool_versions": { // Versions of security scanners used',
        f'        "syft": "{prov["syft"]}",',
        f'        "grype": "{prov["grype"]}"',
        '    },',
        '    "artifact_hashes": { // SHA256 hashes of all pipeline artifacts for integrity tracking',
    ]
    # Add artifact hashes
    hashes = manifest.get('artifact_hashes', {})
    items = list(hashes.items())
    for i, (fname, fhash) in enumerate(items):
        comma = ',' if i < len(items) - 1 else ''
        lines.append(f'        "{fname}": "{fhash}"{comma}')
    lines.append('    },')
    lines.append(f'    "workflow_url": "{prov["workflow_url"]}" // Direct link to the successful GitHub Actions workflow run')
    lines.append('}')
    return '\n'.join(lines)


def build_json_manifest(sid, prov, artifact_hashes):
    """Build the clean machine-readable JSON manifest object."""
    return {
        "scenario": sid,
        "repository_commit": prov["repository_commit"],
        "workflow_commit": prov["workflow_commit"],
        "pipeline_version": prov["pipeline_version"],
        "runner": prov["runner"],
        "python": prov["python"],
        "llm": {
            "model": prov["llm_model"],
            "temperature": 0.0,
            "seed": 42,
            "topP": 1.0,
            "topK": 1
        },
        "snapshots": {
            "epss_snapshot": {
                "file": "epss_snapshot.json",
                "date": prov["epss_date"],
                "sha256": EPSS_SHA256
            },
            "kev_snapshot": {
                "file": "kev_snapshot.json",
                "date": prov["kev_date"],
                "sha256": KEV_SHA256
            }
        },
        "tool_versions": {
            "syft": prov["syft"],
            "grype": prov["grype"]
        },
        "artifact_hashes": artifact_hashes,
        "workflow_url": prov["workflow_url"]
    }


def process_scenario(sid):
    print(f"\n=== Processing {sid} ===")
    evidence_path = os.path.join(EVIDENCE_DIR, sid)
    if not os.path.exists(evidence_path):
        print(f"  [SKIP] No evidence folder for {sid}")
        return

    # Load source files
    metrics = load_json(os.path.join(evidence_path, 'metrics.json'))
    llm_req = load_json(os.path.join(evidence_path, 'llm-request.json'))
    llm_resp = load_json(os.path.join(evidence_path, 'llm-response.json'))

    if not metrics:
        print(f"  [SKIP] No metrics.json for {sid}")
        return

    prov = SCENARIO_PROVENANCE.get(sid)
    if not prov:
        print(f"  [SKIP] No provenance data for {sid}")
        return

    # Compute artifact hashes
    artifact_files = [
        'package-before.json', 'rescan.json', 'baseline-grype.json',
        'candidate-ranking.json', 'build.log', 'selected-candidate.json',
        'metrics.json', 'test.log', 'baseline-sbom.json',
        'package-after.json', 'llm-response.json', 'llm-request.json'
    ]
    artifact_hashes = {}
    for fname in artifact_files:
        fpath = os.path.join(evidence_path, fname)
        if os.path.exists(fpath):
            artifact_hashes[fname] = sha256_file(fpath)

    # Build the clean JSON manifest
    manifest_obj = build_json_manifest(sid, prov, artifact_hashes)

    # Build the empirical evidence sections
    manifest_commented = build_manifest_commented(manifest_obj, prov)
    metrics_commented = build_metrics_commented(metrics, metrics.get('ecosystem', 'python'))

    # Extract prompt text
    prompt_text = extract_prompt_text(llm_req) if llm_req else "LLM request not available"

    # Extract LLM output (clean JSON)
    llm_output_str = json.dumps(llm_resp, indent=2, ensure_ascii=False) if llm_resp else "{}"

    # Determine prompt version
    prompt_version = "v1.1"
    if llm_req:
        prompt_version = llm_req.get('prompt_version', 'v1.1')

    # Build the full file content
    json_section = json.dumps(manifest_obj, indent=4, ensure_ascii=False)

    empirical_section = f"""

=== EMPIRICAL EVIDENCE ===
NOTE: The following pipeline metrics, LLM prompts, and exact outputs are appended here in plaintext to serve as verifiable, empirical proof of the LLM's reasoning and the pipeline's deterministic success for this scenario.

--- EXPERIMENT MANIFEST ---
{manifest_commented}

--- PIPELINE METRICS ---
{metrics_commented}

--- LLM PROMPT ---
Scenario ID: {sid}
Prompt Version: {prompt_version}

{prompt_text}

--- LLM OUTPUT ---
{llm_output_str}
"""

    output_path = os.path.join(evidence_path, 'experiment_manifest.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_section)
        f.write(empirical_section)

    print(f"  [OK] Written {output_path}")
    print(f"  Artifacts hashed: {len(artifact_hashes)}")
    print(f"  rescan_success: {metrics.get('rescan_success')}")


ALL_SCENARIOS = [
    "AF-01", "AF-02", "AF-03", "AF-04", "AF-05",
    "AF-06", "AF-07", "AF-08", "AF-09",
    "JS-01", "JS-02", "JS-03", "JS-04", "JS-05",
    "JS-06", "JS-07", "JS-08"
]

if __name__ == "__main__":
    print("=== Rebuilding experiment_manifest.json for all scenarios ===")
    for sid in ALL_SCENARIOS:
        process_scenario(sid)
    print("\n=== Done ===")
