import os
import sys
import json
import urllib.request
from datetime import datetime, timezone

def main():
    if len(sys.argv) < 3:
        print("Usage: python graph_orchestrate.py <app_dir> <evidence_dir>")
        sys.exit(1)

    app_dir = sys.argv[1]
    evidence_dir = sys.argv[2]
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("[ERROR] GEMINI_API_KEY not found.")
        sys.exit(1)

    # 1. Load baseline-grype.json to get vulnerability metadata for vm2
    with open(os.path.join(evidence_dir, 'baseline-grype.json'), 'r') as f:
        grype_data = json.load(f)

    target_match = None
    for match in grype_data.get('matches', []):
        vuln = match.get('vulnerability', {})
        pkg = match.get('artifact', {})
        if pkg.get('name') == 'vm2' and vuln.get('id') == 'GHSA-whpj-8f3w-67p5':
            target_match = match
            break
            
    if not target_match:
        print("[ERROR] Could not find vm2 GHSA-whpj-8f3w-67p5 in baseline-grype.json")
        sys.exit(1)
        
    vuln_info = target_match.get('vulnerability', {})
    pkg_info = target_match.get('artifact', {})
    
    # 2. Load manifest (package.json)
    with open(os.path.join(evidence_dir, 'package-before.json'), 'r') as f:
        manifest_data = json.load(f)
        
    # 3. Load dependency graph
    with open(os.path.join(evidence_dir, 'dependency-graph-before.json'), 'r') as f:
        graph_data = json.load(f)

    system_prompt = """You are a Senior DevSecOps AI Agent. Your objective is to eradicate software supply chain vulnerabilities within dependency ecosystems by analyzing the full dependency graph.
You must critically evaluate how the vulnerable package enters the dependency tree. Determine whether it can be safely upgraded or if its parent/introducer needs to change.
Propose the minimum necessary manifest modification to remove the vulnerability without introducing unnecessary changes.
Do not hallucinate packages or versions."""

    user_prompt = f"""Scenario ID: JS-01-GRAPH-EXPLORATORY

### Vulnerability Intelligence
* Target Package: {pkg_info.get('name')}
* Vulnerable Version: {pkg_info.get('version')}
* CVE/GHSA ID: {vuln_info.get('id')}
* Severity: {vuln_info.get('severity')}
* Description: {vuln_info.get('description', 'N/A')}

### Remediation Objective
Analyze the dependency graph below. Identify how `{pkg_info.get('name')}` enters the tree. 
Provide the exact package.json modification necessary to remove this vulnerability. 
The resulting application MUST remain buildable and testable. Do not break the dependency constraints of other packages.

### Package Manifest (package.json)
```json
{json.dumps(manifest_data, indent=2)}
```

### Dependency Graph (npm ls --json)
```json
{json.dumps(graph_data, indent=2)}
```

Based on your analysis:
1. Identify how vm2 enters the dependency tree.
2. Determine whether it can be safely upgraded or if another dependency constraint (e.g. the introducer) needs to change.
3. Propose the minimum necessary manifest modification.
4. Output the exact package.json modification in structured JSON format.
"""

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "reasoning": {"type": "STRING", "description": "Analysis of how vm2 enters the tree and justification for the proposed modification."},
            "manifest_patch": {
                "type": "OBJECT",
                "description": "The exact modification to apply to package.json",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "enum": ["add_override", "replace_dependency", "add_resolution", "bump_dependency"],
                        "description": "The operation to perform on package.json"
                    },
                    "package": {"type": "STRING", "description": "The target package name in package.json to modify (e.g. the parent package or the dependency to override)."},
                    "constraint": {"type": "STRING", "description": "The new version constraint to enforce."}
                },
                "required": ["operation", "package", "constraint"]
            }
        },
        "required": ["reasoning", "manifest_patch"]
    }

    api_payload = {
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
    
    with open(os.path.join(evidence_dir, 'llm-request.json'), 'w') as f:
        json.dump(api_payload, f, indent=2)

    models = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    result = None

    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        req = urllib.request.Request(
            url,
            data=json.dumps(api_payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'x-goog-api-key': api_key
            },
            method='POST'
        )
        try:
            with urllib.request.urlopen(req) as response:
                body = response.read().decode('utf-8')
                result = json.loads(body)
                print(f"[LLM] Success with model: {model_name}")
                break
        except Exception as e:
            print(f"[WARN] API call failed for {model_name}: {e}")

    if not result:
        print("[ERROR] All API calls failed.")
        sys.exit(1)

    try:
        content_text = result['candidates'][0]['content']['parts'][0]['text']
        parsed_response = json.loads(content_text)
    except Exception as e:
        print(f"[ERROR] Failed to parse LLM response: {e}")
        parsed_response = {"error": str(e), "raw_response": result}
        
    with open(os.path.join(evidence_dir, 'llm-response.json'), 'w') as f:
        json.dump(parsed_response, f, indent=2)

if __name__ == "__main__":
    main()
