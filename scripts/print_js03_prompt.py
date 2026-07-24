import json

scenarios = json.load(open('c:/Users/HP/Downloads/llm-remediation-thesis-final/experiment/archive/final_18_scenarios.json', encoding='utf-8'))
baselines = json.load(open('c:/Users/HP/Downloads/llm-remediation-thesis-final/experiment/archive/deterministic_baseline_results.json', encoding='utf-8'))

s = next(s for s in scenarios if s['scenario_id'] == 'JS-03')
b = next(b for b in baselines if b['scenario_id'] == 'JS-03')

prompt = f"""You are a software dependency security analyst. Your task is to recommend a remediation strategy for a known vulnerability in a CI/CD pipeline.
A static vulnerability scanner has identified a vulnerable dependency and recommended a fix version. However, applying that version directly has been shown to cause a dependency resolution failure. You must analyze the situation and recommend the most appropriate remediation strategy.

=== VULNERABILITY CONTEXT ===
Application: {s['application']}
Ecosystem: {s['package']['ecosystem']}
Package: {s['package']['name']}
Current Version: {s['package']['current_version']}
Scanner Recommended Fix Version: {s['package']['grype_recommended_version']}
Upgrade Type: {s['package']['upgrade_type']}

=== VULNERABILITY DETAILS ===
CVE ID: {s['vulnerability']['cve_id']}
CVSS Score: {s['vulnerability']['cvss_score']}
EPSS Probability: {s['vulnerability']['epss_probability']}
KEV Status: {s['vulnerability']['kev_status']}
CWE: {s['vulnerability']['cwe_id']}
Description: {s['vulnerability']['description']}

=== DEPENDENCY CONTEXT ===
Dependency Path: {s['dependency_context']['dependency_path']}
Manifest File: {s['dependency_context']['manifest_file']}

=== BASELINE FAILURE ===
Applying the scanner-recommended version directly caused a fatal dependency resolution failure.
Error:
{b.get('failure_details', 'Unknown Error')}

=== YOUR TASK ===
Based on the vulnerability severity, exploitation probability, and dependency constraints, recommend the most appropriate remediation strategy. Do not rely on external tools. Reason about the constraints and propose a concrete version fix or an alternative package.

Respond with a strictly valid JSON object adhering to the following schema:
{{
  "rationale": "Analysis of the vulnerability and why this strategy was chosen",
  "action_type": "DIRECT_BUMP | OVERRIDE | CONSTRAINT_RELAXATION | PACKAGE_REPLACEMENT | DEFER",
  "recommended_version": "exact semantic version, alternative package name, or null if DEFER",
  "fix_target": "the package to modify in the manifest — may differ from the vulnerable package",
  "prioritisation_reasoning": "how CVSS and EPSS scores influenced the prioritisation decision"
}}

Do not reference any external URLs, documentation links, or real-time data in your response. Base your analysis solely on the vulnerability context provided in this prompt. Keep rationale under 2 sentences. Keep prioritisation_reasoning under 2 sentences. Output only the JSON object with no markdown formatting or additional text.

The fix_target field must contain ONLY the exact package name as it appears in the package registry. Never put a filename, sentence, or description in this field. Example: fix_target should be 'cryptography' not 'requirements.txt'.
"""

print(prompt)
