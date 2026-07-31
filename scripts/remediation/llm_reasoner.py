import json
import urllib.request
import os
import sys
from datetime import datetime, timezone


def get_llm_recommendation(candidate, context, ecosystem, is_retry=False, failure_logs=""):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("[ERROR] GEMINI_API_KEY not found.")
        sys.exit(1)

    system_prompt = """You are a Senior DevSecOps AI Agent. Your objective is to eradicate software supply chain vulnerabilities within dependency ecosystems.
You must critically evaluate the topological subgraph. Provide comprehensive reasoning on why the vulnerability exists.
Evaluate all technically feasible remediation strategies, including native upgrades, dependency overrides, dependency resolutions, package replacement, or manual intervention. Recommend the safest strategy that preserves compatibility and explain why alternative strategies were rejected.
Do not hallucinate package versions. Recommend versions that actually exist and solve the CVE."""

    scenario_id = os.environ.get('SCENARIO_ID', 'UNKNOWN')
    application = "Apache Airflow" if ecosystem == "python" else "OWASP Juice Shop"

    # Intelligence retrieval date: use the EPSS snapshot date rather than a hardcoded value
    # so the prompt accurately reflects when enrichment data was captured.
    intelligence_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        snapshot_path = "scripts/remediation/snapshots/epss_snapshot.json"
        with open(snapshot_path, "r") as f:
            epss_data = json.load(f)
            intelligence_date = epss_data.get("metadata", {}).get("snapshot_date", intelligence_date)
    except Exception:
        pass  # fallback to today

    fixed_versions_display = candidate['fixed_versions']
    if scenario_id == 'JS-09':
        fixed_versions_display = "[HIDDEN INTENTIONALLY - YOU MUST DETERMINE THE SAFEST VERSION TO AVOID BREAKING THE BUILD]"

    user_prompt = f"""Scenario ID: {scenario_id}
Prompt Version: v1.1

### Vulnerability Intelligence
* Target Package: {candidate['package_name']}
* Vulnerable Version: {candidate['vulnerable_version']}
* CVE ID: {candidate['cve_id']}
* CVSS Score: {candidate['cvss']}
* EPSS Probability: {candidate['epss']}
* CISA KEV Status: {candidate['kev']}
* Intelligence Retrieved On: {intelligence_date}
* Fixed Versions: {fixed_versions_display}

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
            "reasoning": {"type": "STRING", "description": "Comprehensive reasoning for the strategy chosen."},
            "strategy": {"type": "STRING", "description": "The exact strategy chosen (e.g., direct_upgrade, transitive_override, dependency_resolution, replacement)."},
            "remediation_type": {"type": "STRING", "description": "Must be one of: Direct Upgrade, Transitive Override, Dependency Resolution, Replacement, Manual Review."},
            "recommended_package_version": {"type": "STRING", "description": "The specific semantic version to enforce."},
            "manifest_patch": {
                "type": "OBJECT",
                "description": "The structured intermediate representation of the manifest patch.",
                "properties": {
                    "operation": {"type": "STRING", "description": "The operation to perform (e.g., 'replace', 'add_override', 'bump')."},
                    "package": {"type": "STRING", "description": "The target package name to modify."},
                    "constraint": {"type": "STRING", "description": "The new version constraint to enforce (e.g., '>=42.0.0' or '3.9.18')."}
                },
                "required": ["operation", "package", "constraint"]
            }
        },
        "required": ["reasoning", "strategy", "remediation_type", "recommended_package_version", "manifest_patch"]
    }

    api_payload = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            # Zero temperature ensures the model generates the most deterministic and consistent output possible, preventing random variations.
            "temperature": 0.0,
            # Full probability mass considered, but combined with temperature=0.0, this restricts generation to the highest-probability token.
            "topP": 1.0,
            # Only the single top token is considered at each step, further enforcing determinism for structured schema compliance.
            "topK": 1,
            # Static seed parameter to ensure reproducibility of results across runs.
            "seed": 42,
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
    }

    experiment_label = "Supplementary Experiment" if scenario_id == 'JS-09' else "2026-final"

    # Save the request for evidence, enriched with additional metadata for thesis audit trails
    evidence_payload = {
        "scenario_id": scenario_id,
        "experiment_id": experiment_label,
        "application": application,
        "ecosystem": ecosystem,
        "prompt_version": "v1.1",
        "api_payload": api_payload
    }

    # Fallback model list: primary → stable fallback → legacy fallback
    # Note: gemini-3.6-flash injected per user request
    models = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    result = None

    print(f"[LLM] Requesting recommendation for {candidate['package_name']}...")

    print("\n--- LLM Request Prompt ---")
    print(user_prompt)
    print("--------------------------\n")

    with open('llm-request.json', 'w') as f:
        json.dump(evidence_payload, f, indent=2)

    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        req = urllib.request.Request(
            url,
            data=json.dumps(api_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'x-goog-api-key': api_key}
        )
        print(f"[LLM] Attempting request using model: {model_name}...")
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                print(f"[LLM] Successfully retrieved response using model: {model_name}")
                # Save the FULL API response for complete audit trail (includes usageMetadata, modelVersion, etc.)
                with open('llm-response-full.json', 'w') as f:
                    json.dump(result, f, indent=2)
                break
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            print(f"[WARNING] Model {model_name} failed with HTTP Error {e.code} {e.reason}: {err_body}. Attempting fallback model...")
            continue
        except Exception as e:
            print(f"[WARNING] Model {model_name} failed with error: {e}. Attempting fallback model...")
            continue

    if not result:
        print("[ERROR] All candidate LLM models failed to return a response.")
        sys.exit(1)

    llm_text = result['candidates'][0]['content']['parts'][0]['text']

    # Save the structured JSON response content for evidence (for compatibility with downstream scripts)
    with open('llm-response.json', 'w') as f:
        f.write(llm_text)

    try:
        llm_json = json.loads(llm_text)
        print("\n=================== LLM REASONING LAYER ===================")
        print(llm_json.get("reasoning", "No reasoning block provided in output."))
        print("============================================================\n")

        print("=================== STRUCTURED RESOLUTION ===================")
        print(json.dumps(llm_json, indent=2))
        print("=============================================================\n")
        return llm_json
    except json.JSONDecodeError:
        print("\n--- Raw Response (Failed to parse JSON) ---")
        print(llm_text)
        print("-------------------------------------------\n")
        print("[ERROR] Failed to parse LLM response as JSON.")
        sys.exit(1)
