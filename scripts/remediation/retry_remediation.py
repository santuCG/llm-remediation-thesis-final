import sys
import os
import re
import json
import time

from context_builder import get_context
from llm_reasoner import get_llm_recommendation
from manifest_editor import apply_remediation

_ERROR_MARKER = re.compile(r'error TS\d|Error:|npm ERR!|FAILED|Traceback|error:', re.IGNORECASE)


def _extract_build_errors(log_text, max_chars=3000):
    """Extract lines that actually look like errors, plus 2 lines of context
    around each, instead of blindly taking the last N characters of the log.
    Falls back to a tail-truncation if no recognizable error marker is found,
    so this never returns less information than the v1.1 behavior did.
    See scripts/remediation/prompts/PROMPT_CHANGELOG.md (v1.2)."""
    lines = log_text.splitlines()
    matched = [i for i, line in enumerate(lines) if _ERROR_MARKER.search(line)]
    if not matched:
        return log_text[-max_chars:]
    keep = set()
    for i in matched:
        for j in range(max(0, i - 2), min(len(lines), i + 3)):
            keep.add(j)
    excerpt = "\n".join(lines[i] for i in sorted(keep))
    return excerpt[-max_chars:]


def _extract_rescan_summary(target_cve_id):
    """Summarize why the target CVE is still present in the post-remediation
    rescan. build.log contains no information about rescan/validator outcomes
    at all -- a compile failure and 'the CVE is still detected' are two
    different failure modes needing different evidence, and rescan_success=false
    (the dominant retry trigger observed for JS-01 across this session's
    verification runs) previously got no rescan-specific context at all.
    See scripts/remediation/prompts/PROMPT_CHANGELOG.md (v1.2)."""
    try:
        with open('rescan.json', 'r') as f:
            rescan = json.load(f)
    except Exception:
        return ""
    for match in rescan.get('matches', []):
        vuln = match.get('vulnerability', {})
        vuln_id = vuln.get('id', '')
        related = [r.get('id', '') for r in match.get('relatedVulnerabilities', [])]
        if vuln_id == target_cve_id or target_cve_id in related:
            artifact = match.get('artifact', {})
            fix = vuln.get('fix', {})
            return (
                f"Post-remediation rescan still detects {target_cve_id} "
                f"(scanner ID: {vuln_id}) in package '{artifact.get('name')}' "
                f"version '{artifact.get('version')}'. "
                f"Scanner-known fixed versions: {fix.get('versions', [])}."
            )
    return ""


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
            if metrics.get('failure_stage', 'none') != 'none':
                failure_stage = metrics['failure_stage']
    except Exception as e:
        print(f"[ERROR] Could not load candidate or metrics: {e}")
        sys.exit(1)
        
    # Read failure context. build_success=false and rescan_success=false are
    # two different failure modes needing different evidence: a compile error
    # (in build.log) says nothing about why a CVE is still detected, and a
    # rescan.json summary says nothing about a compile error. v1.1 always
    # blindly tail-truncated whichever {failure_stage}.log file was named
    # (in practice always build.log, since the workflow's "Update Metrics on
    # Build Failure" step normalizes failure_stage to "build" regardless of
    # the true cause) -- so a rescan-caused retry (the dominant trigger
    # observed for JS-01 across this session's verification runs) got no
    # rescan-specific context at all. See prompts/PROMPT_CHANGELOG.md (v1.2).
    failure_logs_parts = []
    if not metrics.get('build_success', True):
        log_file = f"{failure_stage}.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                build_excerpt = _extract_build_errors(f.read())
            if build_excerpt.strip():
                failure_logs_parts.append(f"[Build/compile output]\n{build_excerpt}")
    if not metrics.get('rescan_success', True):
        rescan_summary = _extract_rescan_summary(candidate.get('cve_id', ''))
        if rescan_summary:
            failure_logs_parts.append(f"[Post-remediation scan]\n{rescan_summary}")
    if not failure_logs_parts:
        # Fallback: preserve v1.1 behavior for any failure mode not covered
        # by the two checks above, so this never surfaces strictly less
        # information than before.
        log_file = f"{failure_stage}.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                failure_logs_parts.append(f.read()[-2000:])
    failure_logs = "\n\n".join(failure_logs_parts)

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
    # Reset failure_stage once the retry itself completes successfully:
    # leaving the prior attempt's failure_stage in place here was masking
    # whether the *retry* actually succeeded, since downstream build/apply
    # steps ("Update Metrics on Build Failure" / "Update Metrics on Apply
    # Fix Failure") already independently re-set failure_stage if the
    # rebuild that follows this script fails again. Only keep the original
    # failure_stage if the retry itself never produced a usable response.
    metrics['failure_stage'] = failure_stage if not llm_response_valid else 'none'
    metrics['strategy'] = recommendation.get('strategy', '')
    # remediation_type is the human-readable twin of strategy and must be
    # refreshed alongside it -- leaving it unset here was the same class of
    # bug as the failure_stage one above: it silently kept the FIRST
    # attempt's label (e.g. "Transitive Override") even when the retry's
    # strategy changed to something else (e.g. "direct_upgrade"), producing
    # a metrics.json that contradicts the LLM's own llm-response.json.
    metrics['remediation_type'] = recommendation.get('remediation_type', metrics.get('remediation_type', ''))
    metrics['llm_response_valid'] = llm_response_valid
    
    with open('metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
        
    if not llm_response_valid:
        sys.exit(1)
        
    print("\n=== Orchestration Complete for Attempt 2 ===")

if __name__ == "__main__":
    main()
