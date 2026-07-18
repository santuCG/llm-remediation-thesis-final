import json
import os
import sys
import urllib.request
import subprocess

def main():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not found.")
        sys.exit(1)
        
    print("Reading Grype output...")
    with open('grype-scanner.json', 'r') as f:
        grype_data = json.load(f)
        
    # Find the target vulnerability
    target_match = None
    for match in grype_data.get('matches', []):
        vuln_id = match.get('vulnerability', {}).get('id', '')
        if vuln_id in ('CVE-2023-32314', 'GHSA-whpj-8f3w-67p5'):
            target_match = match
            break
            
    if not target_match:
        print("Target vulnerability CVE-2023-32314 not found in grype-scanner.json. Assuming already eradicated or not present.")
        sys.exit(0)
        
    package_name = target_match['artifact']['name']
    vulnerable_version = target_match['artifact']['version']
    cve_id = target_match['vulnerability']['id']
    cvss_metrics = target_match['vulnerability'].get('cvss', [])
    cvss_score = cvss_metrics[0].get('metrics', {}).get('baseScore', 'N/A') if cvss_metrics else 'N/A'
    
    print(f"Targeting: {package_name}@{vulnerable_version} ({cve_id})")
    
    # Run npm ls
    print(f"Extracting dependency subgraph for {package_name}...")
    try:
        ls_output = subprocess.check_output(['npm', 'ls', package_name, '--json'], text=True)
    except subprocess.CalledProcessError as e:
        ls_output = e.output

    # Construct the prompt
    system_prompt = """You are an expert DevSecOps AI agent specialized in resolving deep dependency shadowing and supply chain vulnerabilities. Your task is to analyze vulnerability reports and dependency graphs to provide a secure, non-breaking package resolution strategy.

Output ONLY a valid JSON object representing the necessary `overrides` or `resolutions` to be added to the `package.json` file. Do not include markdown formatting, explanations, or conversational text."""

    user_prompt = f"""Analyze the following vulnerability and provide a targeted `package.json` override strategy to eradicate the risk without breaking the build.

### Vulnerability Intelligence
* Target Package: {package_name}
* Vulnerable Version: {vulnerable_version}
* CVE ID: {cve_id}
* CVSS Score: {cvss_score}

### Dependency Graph Context
The vulnerability exists within the following dependency tree. Pay close attention to the parent packages requiring this vulnerable version to avoid ERESOLVE conflicts.

```json
{ls_output}
```

Constraints
Do not hallucinate versions. Determine the most stable, secure version that satisfies the tree.
If the package is deprecated and cannot be updated, provide an override that mitigates the specific CVE while maintaining structural compatibility.
Your output must be strict JSON containing ONLY the overrides block. For example:
{{
  "overrides": {{
    "{package_name}": "X.Y.Z"
  }}
}}
"""

    print("=== DYNAMIC PROMPT FOR LLM LAYER ===")
    print("SYSTEM PROMPT:")
    print(system_prompt)
    print("\nUSER PROMPT:")
    print(user_prompt)
    print("======================================")

    # Call Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "temperature": 0.0,
            "topP": 1.0,
            "topK": 1,
            "responseMimeType": "application/json"
        }
    }
    
    print("Invoking Gemini 2.5 Flash API...")
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
        sys.exit(1)
        
    llm_text = result['candidates'][0]['content']['parts'][0]['text']
    
    print("\n=== LLM RAW RESPONSE ===")
    print(llm_text)
    print("========================\n")
    
    # Parse the LLM response JSON
    try:
        overrides_json = json.loads(llm_text)
    except json.JSONDecodeError:
        print("Failed to parse LLM response as JSON.")
        sys.exit(1)
        
    # Update package.json
    print("Applying overrides to package.json...")
    with open('package.json', 'r') as f:
        pkg = json.load(f)
        
    if 'overrides' in overrides_json:
        pkg['overrides'] = pkg.get('overrides', {})
        pkg['overrides'].update(overrides_json['overrides'])
    else:
        pkg['overrides'] = pkg.get('overrides', {})
        pkg['overrides'].update(overrides_json)
        
    with open('package.json', 'w') as f:
        json.dump(pkg, f, indent=2)
        
    print("Successfully applied LLM overrides to package.json.")

if __name__ == "__main__":
    main()
