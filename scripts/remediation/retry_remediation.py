import sys
import os
import json
import time

from context_builder import get_context
from llm_reasoner import get_llm_recommendation
from manifest_editor import apply_remediation

def main():
    if len(sys.argv) < 4:
        print("Usage: python retry_remediation.py <ecosystem> <app_dir> <failure_stage>")
        sys.exit(1)
        
    ecosystem = sys.argv[1].lower()
    app_dir = sys.argv[2]
    failure_stage = sys.argv[3]
    
    print(f"=== LLM Retry Triggered (Failure Stage: {failure_stage}) ===")
    
    # Load previous candidate and metrics
    try:
        with open('selected-candidate.json', 'r') as f:
            candidate = json.load(f)
        with open('metrics.json', 'r') as f:
            metrics = json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not load candidate or metrics: {e}")
        sys.exit(1)
        
    # Read failure logs (assume saved in build.log or similar based on stage)
    failure_logs = ""
    log_file = f"{failure_stage}.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            failure_logs = f.read()[-2000:] # last 2000 chars
            
    print("\n=== Phase 3: Context Collection (Retry) ===")
    context = get_context(ecosystem, candidate['package_name'], app_dir)
    
    print("\n=== Phase 4: LLM Reasoning (Attempt 2) ===")
    try:
        recommendation = get_llm_recommendation(candidate, context, ecosystem, is_retry=True, failure_logs=failure_logs)
        llm_response_valid = True
    except Exception as e:
        print(f"[ORCHESTRATOR] LLM failed to return valid response on retry: {e}")
        llm_response_valid = False
        recommendation = {}
    
    if llm_response_valid:
        print(f"\n[ORCHESTRATOR] Refined Strategy Selected: {recommendation.get('strategy')}")
        print("\n=== Phase 5: Applying Refined Recommendation ===")
        try:
            apply_remediation(ecosystem, app_dir, recommendation)
        except Exception as e:
            print(f"[ORCHESTRATOR] Failed to apply remediation on retry (likely invalid JSON in manifest_patch): {e}")
            llm_response_valid = False
    else:
        print("\n[ORCHESTRATOR] Skipping apply_remediation on retry due to invalid LLM response.")
    
    # Update metrics
    metrics['retry_count'] = 1
    metrics['llm_iteration'] = 2
    metrics['failure_stage'] = failure_stage
    metrics['strategy'] = recommendation.get('strategy', '')
    metrics['confidence'] = recommendation.get('confidence_score', 0)
    metrics['llm_response_valid'] = llm_response_valid
    
    with open('metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
        
    if not llm_response_valid:
        sys.exit(1)
        
    print("\n=== Orchestration Complete for Attempt 2 ===")

if __name__ == "__main__":
    main()
