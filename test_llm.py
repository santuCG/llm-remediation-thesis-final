import json
import os
import sys
import urllib.request
import re

# Get API key
with open('.env', 'r') as f:
    env_content = f.read()
match = re.search(r'GEMINI_API_KEY\s*=\s*[\"\'\s]?([^\"\'\n]+)', env_content)
if not match:
    print("API Key not found")
    sys.exit(1)
api_key = match.group(1).strip()

ls_output = '''{
  "version": "15.3.0",
  "name": "juice-shop",
  "problems": [
    "extraneous: vm2@3.9.19 C:\\\\Users\\\\HP\\\\Downloads\\\\llm-remediation-thesis-final\\\\applications\\\\juice-shop\\\\node_modules\\\\vm2"
  ],
  "dependencies": {
    "juicy-chat-bot": {
      "version": "0.8.0",
      "resolved": "https://registry.npmjs.org/juicy-chat-bot/-/juicy-chat-bot-0.8.0.tgz",
      "overridden": false,
      "dependencies": {
        "vm2": {
          "version": "3.9.17",
          "resolved": "https://registry.npmjs.org/vm2/-/vm2-3.9.17.tgz",
          "overridden": false
        }
      }
    },
    "vm2": {
      "version": "3.9.19",
      "resolved": "https://registry.npmjs.org/vm2/-/vm2-3.9.19.tgz",
      "overridden": false,
      "extraneous": true,
      "problems": [
        "extraneous: vm2@3.9.19 C:\\\\Users\\\\HP\\\\Downloads\\\\llm-remediation-thesis-final\\\\applications\\\\juice-shop\\\\node_modules\\\\vm2"
      ]
    }
  }
}'''

pipeline_failure_context = "The naive scanner update was applied and exited with code 0, but Grype rescanned the lockfile and the nested CVE is still active."

system_prompt = """You are a Senior DevSecOps AI Agent. Your objective is to eradicate software supply chain vulnerabilities within legacy node ecosystems.

Your task is to analyze the vulnerability intelligence and the nested dependency subgraph. You must deduce the correct architectural strategy to enforce a secure, stable version across the entire tree without breaking compilation. You must recommend a version that actually exists on the public npm registry. Do not hallucinate."""

user_prompt = f"""### Vulnerability Intelligence
* Target Package: vm2
* Vulnerable Version: 3.9.17
* CVE ID: CVE-2023-32314
* CVSS Score: 9.8

### Pipeline Execution Context
{pipeline_failure_context}

### Dependency Graph
```json
{ls_output}
```

Based on the pipeline failure and the topological subgraph, deduce the safest semantic version of vm2 to deploy that actually exists on the public npm registry. Then, deduce the correct package.json configuration key required to force this resolution natively without breaking the build."""

response_schema = {
    "type": "OBJECT",
    "properties": {
        "reasoning": { "type": "STRING", "description": "Explain why the naive fix failed and why your topological fix is correct. Discuss why you recommend this exact version over deprecated or alternative packages." },
        "confidence_score": { "type": "INTEGER", "description": "Confidence score from 0 to 100." },
        "action_type": { "type": "STRING", "description": "The exact package.json key to use (e.g. overrides, resolutions)." },
        "recommended_package_version": { "type": "STRING", "description": "The specific semantic version to enforce. Must exist on the npm registry." },
        "senior_devsecops_recommendation": { "type": "STRING", "description": "A message to junior devs explaining the methodology." }
    },
    "required": ["reasoning", "confidence_score", "action_type", "recommended_package_version", "senior_devsecops_recommendation"]
}

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

for i in range(3):
    print(f"--- RUN {i+1} ---")
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(result['candidates'][0]['content']['parts'][0]['text'])
    except Exception as e:
        print(f"Error: {e}")
