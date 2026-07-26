import json
import os
import sys
import urllib.request
import subprocess

def get_epss_score(cve_id):
    try:
        url = f"https://api.first.org/epss?cve={cve_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('data'):
                epss = data['data'][0].get('epss', 'N/A')
                percentile = data['data'][0].get('percentile', 'N/A')
                return epss, percentile
    except Exception as e:
        print(f"Failed to fetch EPSS for {cve_id}: {e}")
    return 'N/A', 'N/A'

def get_kev_status(cve_id):
    try:
        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            for vuln in data.get('vulnerabilities', []):
                if vuln.get('cveID') == cve_id:
                    return "TRUE (Actively Exploited)"
    except Exception as e:
        print(f"Failed to fetch KEV status: {e}")
    return "FALSE (Not in CISA KEV)"

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
    
    print("Fetching EPSS and KEV threat intelligence...")
    epss_score, epss_percentile = get_epss_score(cve_id)
    kev_status = get_kev_status(cve_id)

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
* EPSS Probability: {epss_score} (Percentile: {epss_percentile})
* CISA KEV Status: {kev_status}

### Pipeline Execution Context
{pipeline_failure_context}

### Dependency Graph
```json
{ls_output}
```

### Security Engineering Challenge
The vulnerable package `{package_name}` is heavily deprecated and no longer maintained. Modern security standards strongly recommend migrating to `isolated-vm` instead of continuing to use `{package_name}`. 

You must critically evaluate the topological subgraph. Provide comprehensive reasoning on why the previous naive pipeline fix failed. Furthermore, before recommending your resolution, explicitly reason about the feasibility of swapping `{package_name}` out for `isolated-vm` as a drop-in replacement right now in this automated CI/CD pipeline context without modifying parent source code. Use that reasoning to justify your final configuration strategy.

Based on the pipeline failure context, the topological subgraph, and the constraints above:
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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
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

    # Surgical lockfile patch to bypass NPM 10 sync bug
    print("Applying surgical patch to package-lock.json to bypass NPM 10 sync bug...")
    try:
        with open('package-lock.json', 'r') as f:
            lock_json = json.load(f)
        
        patched = False
        if 'packages' in lock_json:
            for node_path, node_data in lock_json['packages'].items():
                if node_path.endswith(f"node_modules/{package_name}"):
                    node_data['version'] = target_version
                    node_data['resolved'] = f"https://registry.npmjs.org/{package_name}/-/{package_name}-{target_version}.tgz"
                    patched = True
                    
        def update_legacy_deps(deps):
            nonlocal patched
            for dep_name, dep_data in deps.items():
                if dep_name == package_name:
                    dep_data['version'] = target_version
                    patched = True
                if 'dependencies' in dep_data:
                    update_legacy_deps(dep_data['dependencies'])
        
        if 'dependencies' in lock_json:
            update_legacy_deps(lock_json['dependencies'])
            
        if patched:
            with open('package-lock.json', 'w') as f:
                json.dump(lock_json, f, indent=2)
            print("Surgically patched package-lock.json.")
        else:
            print("Target package not found in package-lock.json. No surgical patch needed.")
            
    except Exception as e:
        print(f"Failed to patch package-lock.json: {e}")

if __name__ == "__main__":
    main()
