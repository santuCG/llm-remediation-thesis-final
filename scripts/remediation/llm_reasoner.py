import json
import urllib.request
import os
import sys

def get_llm_recommendation(candidate, context, ecosystem, is_retry=False, failure_logs=""):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("[ERROR] GEMINI_API_KEY not found.")
        sys.exit(1)
        
    system_prompt = """You are a Senior DevSecOps AI Agent. Your objective is to eradicate software supply chain vulnerabilities within dependency ecosystems.
You must critically evaluate the topological subgraph. Provide comprehensive reasoning on why the vulnerability exists.
Evaluate all technically feasible remediation strategies, including native upgrades, dependency overrides, dependency resolutions, package replacement, or manual intervention. Recommend the safest strategy that preserves compatibility and explain why alternative strategies were rejected.
Do not hallucinate package versions. Recommend versions that actually exist and solve the CVE."""

    user_prompt = f"""### Vulnerability Intelligence
* Target Package: {candidate['package_name']}
* Vulnerable Version: {candidate['vulnerable_version']}
* CVE ID: {candidate['cve_id']}
* CVSS Score: {candidate['cvss']}
* EPSS Probability: {candidate['epss']}
* CISA KEV Status: {candidate['kev']}
* Fixed Versions: {candidate['fixed_versions']}

### Dependency Context
```json
{json.dumps(context, indent=2)}
```
"""

    if is_retry:
        user_prompt += f"""
### Previous Attempt Failure Logs
The previous remediation attempt failed during validation/build. Please analyze these logs, refine your recommendation, and provide a new strategy.
```
{failure_logs}
```
"""

    user_prompt += """
Based on the vulnerability intelligence and context:
1. Recommend the safest strategy.
2. Provide the exact manifest configuration (e.g., overrides block for package.json, or line for requirements.txt) required to enforce this without breaking the build."""

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "reasoning": { "type": "STRING", "description": "Comprehensive reasoning for the strategy chosen." },
            "confidence_score": { "type": "INTEGER", "description": "Confidence score from 0 to 100." },
            "strategy": { "type": "STRING", "description": "The exact strategy chosen (e.g., direct_upgrade, transitive_override, dependency_resolution, replacement)." },
            "remediation_type": { "type": "STRING", "description": "Must be one of: Direct Upgrade, Transitive Override, Dependency Resolution, Replacement, Manual Review." },
            "recommended_package_version": { "type": "STRING", "description": "The specific semantic version to enforce." },
            "manifest_patch": {
                "type": "OBJECT",
                "description": "The structured intermediate representation of the manifest patch.",
                "properties": {
                    "operation": { "type": "STRING", "description": "The operation to perform (e.g., 'replace', 'add_override', 'bump')." },
                    "package": { "type": "STRING", "description": "The target package name to modify." },
                    "constraint": { "type": "STRING", "description": "The new version constraint to enforce (e.g., '>=42.0.0' or '3.9.18')." }
                },
                "required": ["operation", "package", "constraint"]
            }
        },
        "required": ["reasoning", "confidence_score", "strategy", "remediation_type", "recommended_package_version", "manifest_patch"]
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "temperature": 0.0,
            "topP": 1.0,
            "topK": 1,
            "seed": 42,
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
    }

    print(f"[LLM] Requesting recommendation for {candidate['package_name']}...")
    
    # Save the request for evidence
    with open('llm-request.json', 'w') as f:
        json.dump(payload, f, indent=2)

    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"[ERROR] LLM HTTP Error: {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
        sys.exit(1)
        
    llm_text = result['candidates'][0]['content']['parts'][0]['text']
    
    # Save response for evidence
    with open('llm-response.json', 'w') as f:
        f.write(llm_text)
        
    try:
        llm_json = json.loads(llm_text)
        return llm_json
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse LLM response as JSON.")
        sys.exit(1)
