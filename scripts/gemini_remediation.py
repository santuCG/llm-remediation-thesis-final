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

    # Read the dynamic pipeline failure context
    pipeline_failure_context = "No specific failure context provided."
    try:
        with open('../../pipeline_failure_context.txt', 'r') as f:
            pipeline_failure_context = f.read().strip()
    except Exception as e:
        print(f"Could not read pipeline_failure_context.txt: {e}")
    
    # Run npm ls
    print(f"Extracting dependency subgraph for {package_name}...")
    try:
        ls_output = subprocess.check_output(['npm', 'ls', package_name, '--json'], text=True)
    except subprocess.CalledProcessError as e:
        ls_output = e.output

    # Construct the prompt
    system_prompt = """You are a Senior DevSecOps AI Agent. Your objective is to eradicate software supply chain vulnerabilities within legacy node ecosystems.

Your task is to analyze the vulnerability intelligence and the nested dependency subgraph. You must deduce the correct architectural strategy to enforce a secure, stable version across the entire tree without breaking compilation. You must recommend a version that actually exists on the public npm registry. Do not hallucinate."""

    user_prompt = f"""### Vulnerability Intelligence
* Target Package: {package_name}
* Vulnerable Version: {vulnerable_version}
* CVE ID: {cve_id}
* CVSS Score: {cvss_score}

### Pipeline Execution Context
{pipeline_failure_context}

### Dependency Graph
```json
{ls_output}
```

### Security Engineering Challenge
You must critically evaluate the topological subgraph. Provide comprehensive reasoning on why the previous pipeline failed. Furthermore, before recommending your resolution, briefly discuss whether migrating to entirely different modern alternative packages is topologically feasible here (without modifying parent source code), and use that reasoning to justify your final, safest configuration strategy.

Based on the pipeline failure context, the topological subgraph, and the architectural constraint above:
1. Deduce the safest semantic version to deploy that actually exists on the public npm registry.
2. Deduce the exact package.json configuration key required to force this topological resolution natively without breaking the build."""

    print("=== DYNAMIC PROMPT FOR LLM LAYER ===")
    print("SYSTEM PROMPT:")
    print(system_prompt)
    print("\nUSER PROMPT:")
    print(user_prompt)
    print("======================================")

    # Response Schema for Gemini
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "reasoning": { "type": "STRING", "description": "Provide a comprehensive architectural analysis. Explain why the naive fix failed, evaluate the topological feasibility of substituting with alternative packages entirely, and justify your final constraint strategy." },
            "confidence_score": { "type": "INTEGER", "description": "Confidence score from 0 to 100." },
            "action_type": { "type": "STRING", "description": "The exact package.json key to use (e.g. overrides, resolutions)." },
            "recommended_package_version": { "type": "STRING", "description": "The specific semantic version to enforce. Must exist on the npm registry." },
            "senior_devsecops_recommendation": { "type": "STRING", "description": "A comprehensive message to junior devs explaining the methodology, the failure of naive updates, and the importance of backward compatibility." }
        },
        "required": ["reasoning", "confidence_score", "action_type", "recommended_package_version", "senior_devsecops_recommendation"]
    }

    # Call Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "temperature": 0.0,
            "topP": 1.0,
            "topK": 1,
            "responseMimeType": "application/json",
            "responseSchema": response_schema
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
        llm_json = json.loads(llm_text)
    except json.JSONDecodeError:
        print("Failed to parse LLM response as JSON.")
        sys.exit(1)

    print("\n*** DevSecOps Reasoning & Recommendations ***")
    print(f"Confidence Score: {llm_json.get('confidence_score')}/100")
    print(f"Reasoning: {llm_json.get('reasoning')}")
    print(f"Recommendation for Juniors: {llm_json.get('senior_devsecops_recommendation')}")
    print("*********************************************\n")
        
    # Update package.json
    action_type = llm_json.get('action_type', 'overrides')
    target_version = llm_json.get('recommended_package_version')

    if not target_version:
        print("Error: The LLM did not provide a recommended_package_version.")
        sys.exit(1)
        
    # Standardize action_type in case the LLM capitalizes or formats it weirdly
    action_type = action_type.lower().strip()
    if action_type not in ['overrides', 'resolutions']:
        action_type = 'overrides' # fallback to standard npm mechanism if hallucinated

    print(f"Applying {action_type} for {package_name}@{target_version} to package.json...")
    with open('package.json', 'r') as f:
        pkg = json.load(f)
        
    pkg[action_type] = pkg.get(action_type, {})
    pkg[action_type][package_name] = target_version
        
    with open('package.json', 'w') as f:
        json.dump(pkg, f, indent=2)
        
    print("Successfully applied LLM fix to package.json.")

if __name__ == "__main__":
    main()
