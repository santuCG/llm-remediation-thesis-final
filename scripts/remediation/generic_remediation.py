import sys
import os
import json
import time

from discover import discover_vulnerabilities
from prioritize import prioritize_vulnerabilities
from context_builder import get_context
from llm_reasoner import get_llm_recommendation
from manifest_editor import apply_remediation

def main():
    if len(sys.argv) < 3:
        print("Usage: python generic_remediation.py <ecosystem> <app_dir>")
        sys.exit(1)
        
    ecosystem = sys.argv[1].lower()
    app_dir = sys.argv[2]
    
    start_time = time.time()
    
    print("=== Phase 1: Discovery ===")
    matches = discover_vulnerabilities("grype.json")
    if not matches:
        print("No vulnerabilities to process.")
        sys.exit(0)
        
    print("\n=== Phase 2: Prioritization ===")
    candidate = prioritize_vulnerabilities(matches, ecosystem)
    if not candidate:
        print("No automatically remediable candidates found.")
        sys.exit(0)
        
    # Write candidate to evidence
    with open('selected-candidate.json', 'w') as f:
        json.dump(candidate, f, indent=2)
        
    print("\n=== Phase 3: Context Collection ===")
    context = get_context(ecosystem, candidate['package_name'], app_dir)
    
    print("\n=== Phase 4: LLM Reasoning (Attempt 1) ===")
    recommendation = get_llm_recommendation(candidate, context, ecosystem, is_retry=False)
    
    print(f"\n[ORCHESTRATOR] Strategy Selected: {recommendation.get('strategy')}")
    print(f"[ORCHESTRATOR] Remediation Type: {recommendation.get('remediation_type')}")
    print(f"[ORCHESTRATOR] Confidence: {recommendation.get('confidence_score')}")
    
    print("\n=== Phase 5: Applying Recommendation ===")
    apply_remediation(ecosystem, app_dir, recommendation)
    
    print("\n=== Phase 6: Orchestration Complete for Attempt 1 ===")
    print("The pipeline will now proceed with native package manager resolution and validation.")
    
    # Generate initial metrics.json skeleton
    metrics = {
        "application": app_dir,
        "ecosystem": ecosystem,
        "selected_package": candidate['package_name'],
        "selected_cve": candidate['cve_id'],
        "severity": candidate['severity'],
        "cvss": candidate['cvss'],
        "epss": candidate['epss'],
        "kev": candidate['kev'],
        "dependency_type": "nested" if "node_modules" in candidate['package_name'] else "direct",
        "strategy": recommendation.get('strategy', ''),
        "confidence": recommendation.get('confidence_score', 0),
        "remediation_type": recommendation.get('remediation_type', ''),
        "build_success": False,
        "test_success": False,
        "dependency_verified": False,
        "rescan_success": False,
        "runtime_success": False,
        "lockfile_regenerated": False,
        "execution_time_seconds": int(time.time() - start_time),
        "retry_count": 0,
        "llm_iteration": 1,
        "failure_stage": "none"
    }
    
    with open('metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)

if __name__ == "__main__":
    main()
