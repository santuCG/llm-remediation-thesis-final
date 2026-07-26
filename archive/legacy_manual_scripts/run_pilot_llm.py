import json
import time
import os
import re
import urllib.request
import urllib.error
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def check_registry(ecosystem, pkg_name, version):
    if not pkg_name or not version:
        return False
        
    try:
        if ecosystem == "npm":
            url = f"https://registry.npmjs.org/{pkg_name}/{version}"
        else:
            url = f"https://pypi.org/pypi/{pkg_name}/{version}/json"
            
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        print(f"HTTP Error {e.code} for {pkg_name}@{version}")
        return False
    except Exception as e:
        print(f"Error checking registry for {pkg_name}@{version}: {e}")
        return False

def main():
    with open('experiment/final_18_scenarios.json', 'r', encoding='utf-8') as f:
        scenarios = json.load(f)

    with open('experiment/deterministic_baseline_results.json', 'r', encoding='utf-8') as f:
        baselines_data = json.load(f)
        baselines = {b['scenario_id']: b.get('error_trace', 'Unknown Error') for b in baselines_data}

    prompt_template = """You are a software dependency security analyst. Your task is to recommend a remediation strategy for a known vulnerability in a CI/CD pipeline.
A static vulnerability scanner has identified a vulnerable dependency and recommended a fix version. However, applying that version directly has been shown to cause a dependency resolution failure. You must analyze the situation and recommend the most appropriate remediation strategy.

=== VULNERABILITY CONTEXT ===
Application: {application}
Ecosystem: {ecosystem}
Package: {package_name}
Current Version: {current_version}
Scanner Recommended Fix Version: {grype_version}
Upgrade Type: {upgrade_type}

=== VULNERABILITY DETAILS ===
CVE ID: {cve_id}
CVSS Score: {cvss_score}
EPSS Probability: {epss_prob}
KEV Status: {kev_status}
CWE: {cwe_id}
Description: {description}

=== DEPENDENCY CONTEXT ===
Dependency Path: {dep_path}
Manifest File: {manifest_file}

=== BASELINE FAILURE ===
Applying the scanner-recommended version directly caused a fatal dependency resolution failure.
Error: {error_trace}

=== YOUR TASK ===
Based on the vulnerability severity, exploitation probability, and dependency constraints, recommend the most appropriate remediation strategy. Do not rely on external tools. Reason about the constraints and propose a concrete version fix or an alternative package.

Respond with a strictly valid JSON object adhering to the following schema:
{{
  "rationale": "Analysis of the vulnerability and why this strategy was chosen",
  "action_type": "DIRECT_BUMP | OVERRIDE | CONSTRAINT_RELAXATION | PACKAGE_REPLACEMENT | DEFER",
  "recommended_version": "exact semantic version, alternative package name, or null if DEFER",
  "fix_target": "the package to modify in the manifest \u2014 may differ from the vulnerable package",
  "prioritisation_reasoning": "how CVSS and EPSS scores influenced the prioritisation decision"
}}

Do not reference any external URLs, documentation links, or real-time data in your response. Base your analysis solely on the vulnerability context provided in this prompt. Keep rationale under 2 sentences. Keep prioritisation_reasoning under 2 sentences. Output only the JSON object with no markdown formatting or additional text.

The fix_target field must contain ONLY the exact package name as it appears in the package registry. Never put a filename, sentence, or description in this field. Example: fix_target should be 'cryptography' not 'requirements.txt'.
"""

    model = genai.GenerativeModel(
        model_name="gemini-3.5-flash",
        generation_config=genai.GenerationConfig(
            temperature=0.0,
            max_output_tokens=800
        )
    )

    results = []
    traces = {}
    pilot_ids = ["JS-01", "JS-08", "AF-01"]
    
    filtered_scenarios = [s for s in scenarios if s["scenario_id"] in pilot_ids]

    for idx, scenario in enumerate(filtered_scenarios):
        s_id = scenario["scenario_id"]
        print(f"Processing {s_id} ({idx+1}/{len(filtered_scenarios)})...")
        
        eco = scenario["package"]["ecosystem"]
        error_trace = baselines.get(s_id, "No error trace available")
        
        prompt = prompt_template.format(
            application=scenario["application"],
            ecosystem=eco,
            package_name=scenario["package"]["name"],
            current_version=scenario["package"]["current_version"],
            grype_version=scenario["package"]["grype_recommended_version"],
            upgrade_type=scenario["package"]["upgrade_type"],
            cve_id=scenario["vulnerability"]["cve_id"],
            cvss_score=scenario["vulnerability"]["cvss_score"],
            epss_prob=scenario["vulnerability"]["epss_probability"],
            kev_status=scenario["vulnerability"]["kev_status"],
            cwe_id=scenario["vulnerability"]["cwe_id"],
            description=scenario["vulnerability"]["description"],
            dep_path=scenario["dependency_context"]["dependency_path"],
            manifest_file=scenario["dependency_context"]["manifest_file"],
            error_trace=error_trace
        )

        injected_snippet = json.dumps({
            "package": scenario["package"],
            "vulnerability": scenario["vulnerability"],
            "dependency_context": scenario["dependency_context"]
        }, indent=2)

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.0,
                    "maxOutputTokens": 800
                }
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as api_resp:
                raw_response = json.loads(api_resp.read().decode('utf-8'))['candidates'][0]['content']['parts'][0]['text']
            
            raw_response = raw_response.strip()
            if raw_response.startswith("```"):
                raw_response = re.sub(r"^```(?:json)?\s*", "", raw_response, flags=re.IGNORECASE)
                raw_response = re.sub(r"\s*```$", "", raw_response)
                
            proposal = json.loads(raw_response)
        except json.JSONDecodeError:
            print("JSON Decode Error. Raw Response:", raw_response)
            proposal = {
                "action_type": "PARSE_ERROR",
                "recommended_version": None,
                "fix_target": None,
                "rationale": f"Response truncated or malformed: {raw_response[:200]}",
                "prioritisation_reasoning": None
            }
        except Exception as e:
            print(f"Error generating content for {s_id}: {e}")
            proposal = {
                "rationale": "Failed to generate",
                "action_type": "DEFER",
                "recommended_version": None,
                "fix_target": scenario["package"]["name"],
                "prioritisation_reasoning": "Generation failed"
            }
            raw_response = f"ERROR: {e}"

        traces[s_id] = {
            "prompt": prompt,
            "injected_snippet": injected_snippet,
            "raw_response": raw_response
        }

        action_type = proposal.get("action_type")
        recommended_version = proposal.get("recommended_version")
        fix_target = proposal.get("fix_target")

        # Gate 0 Validation
        gate_0_valid = False
        hallucinated = False
        outcome = "DEFERRED"

        if action_type == "DEFER" or action_type == "PARSE_ERROR":
            gate_0_valid = False
            hallucinated = False
            outcome = "DEFERRED" if action_type == "DEFER" else "HALLUCINATED_VERSION"
        elif recommended_version is None:
            gate_0_valid = False
            hallucinated = True
            outcome = "HALLUCINATED_VERSION"
        else:
            is_valid = check_registry(eco, fix_target, recommended_version)
            if is_valid:
                gate_0_valid = True
                hallucinated = False
                outcome = "GATE_0_PASS"
            else:
                gate_0_valid = False
                hallucinated = True
                outcome = "HALLUCINATED_VERSION"

        result_obj = {
            "scenario_id": s_id,
            "ecosystem": eco,
            "package": scenario["package"]["name"],
            "vulnerability": {"cve_id": scenario["vulnerability"]["cve_id"]},
            "llm_remediation_proposal": proposal,
            "gate_0_registry_valid": gate_0_valid,
            "gate_1_resolution_success": None,
            "gate_2_build_success": None,
            "gate_3_test_success": None,
            "gate_4_rescan_clear": None,
            "outcome": outcome,
            "hallucinated": hallucinated
        }
        
        results.append(result_obj)
        print(f"  Action: {action_type}, Gate 0 Valid: {gate_0_valid}, Outcome: {outcome}")
        
        if idx < len(filtered_scenarios) - 1:
            time.sleep(5)

    with open('experiment/pilot_remediation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    with open('experiment/pilot_traces.json', 'w', encoding='utf-8') as f:
        json.dump(traces, f, indent=4)
        
    print("Done. Saved to experiment/pilot_remediation_results.json and experiment/pilot_traces.json")

if __name__ == "__main__":
    main()
