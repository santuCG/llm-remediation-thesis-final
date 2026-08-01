import os
import sys
import json
import yaml
import datetime

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_reports.py <profile_path> <evidence_dir>")
        sys.exit(1)

    profile_path = sys.argv[1]
    evidence_dir = sys.argv[2]
    
    with open(profile_path, 'r') as f:
        profile = yaml.safe_load(f)
        
    metrics_path = os.path.join(evidence_dir, 'metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
    else:
        metrics = {}

    expected = profile.get('expected', {})
    
    # Validation Report
    actual_strategy = metrics.get('strategy', 'none')
    actual_build = "PASS" if metrics.get('build_success') else "FAIL"
    actual_rescan = "PASS" if metrics.get('rescan_success') else "FAIL"
    actual_retry = metrics.get('retry_count', 0)
    
    validations = {
        "strategy": {"expected": expected.get('strategy'), "actual": actual_strategy},
        "retry": {"expected": expected.get('retry'), "actual": actual_retry},
        "build": {"expected": expected.get('build') == True or expected.get('build') == "PASS", "actual": metrics.get('build_success')},
        "rescan": {"expected": expected.get('rescan') == True or expected.get('rescan') == "PASS", "actual": metrics.get('rescan_success')}
    }
    
    all_pass = True
    for key, v in validations.items():
        v['match'] = (str(v['expected']).lower() == str(v['actual']).lower())
        if not v['match']:
            all_pass = False
            
    validation_report = {
        "overall_status": "PASS" if all_pass else "FAIL",
        "checks": validations
    }
    
    with open(os.path.join(evidence_dir, 'validation-report.json'), 'w') as f:
        json.dump(validation_report, f, indent=2)
        
    # Scenario Manifest
    scenario_manifest = {
        "scenario_id": profile.get("scenario_id"),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "repository": profile.get("repository", {}),
        "pipeline": profile.get("pipeline", {}),
        "llm": profile.get("llm", {}),
        "tool_versions": profile.get("tool_versions", {}),
        "validation_status": validation_report["overall_status"]
    }
    with open(os.path.join(evidence_dir, 'scenario-manifest.json'), 'w') as f:
        json.dump(scenario_manifest, f, indent=2)
        
    # Pipeline Summary
    pipeline_summary = {
        "scenario": profile.get("scenario_id"),
        "metrics": metrics,
        "validation": validation_report
    }
    with open(os.path.join(evidence_dir, 'pipeline-summary.json'), 'w') as f:
        json.dump(pipeline_summary, f, indent=2)

    # Pipeline Report MD
    report_md = f"""# Pipeline Report: {profile.get("scenario_id")}

## Scenario Details
- **Repository Commit**: {profile.get('repository', {}).get('commit', 'HEAD')}
- **Target Package**: {profile.get('target_package')}
- **Target CVE**: {profile.get('target_cve')}

## Execution
- **Strategy Selected**: {actual_strategy}
- **Retry Count**: {actual_retry}

## Validation Gates
- **Build**: {actual_build}
- **Rescan**: {actual_rescan}

## Golden Scenario Verification
- **Status**: {validation_report['overall_status']}
"""
    with open(os.path.join(evidence_dir, 'pipeline-report.md'), 'w') as f:
        f.write(report_md)
        
if __name__ == "__main__":
    main()
