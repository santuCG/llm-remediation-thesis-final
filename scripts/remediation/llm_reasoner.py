import json
import urllib.request
import os
import sys
from datetime import datetime, timezone

# Fallback model list: primary → stable fallback → legacy fallback
# NOTE: Only real, existing Gemini model identifiers are listed here.
MODELS = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

# Separate fallback list for the search-grounding call only. Tries the
# "-latest" alias first: AI Studio's interactive grounding test used this
# alias rather than the dated "gemini-3.6-flash" ID, and alias vs. dated-ID
# requests can be routed against different quota/entitlement checks even on
# the same API key. Kept separate from MODELS so this experiment doesn't
# change the already-working structured call's model list.
SEARCH_MODELS = ["gemini-pro-latest", "gemini-flash-latest", "gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


def _get_search_grounded_findings(candidate, api_key):
    """Runs a separate, ungrounded-schema Gemini call with the google_search tool
    enabled, to research the actual fixed version(s) for this CVE independent of
    the scanner-supplied hint (which this branch's prompt no longer includes).

    Kept as a distinct call rather than folded into the structured call below:
    the Gemini API does not reliably support responseSchema/responseMimeType
    (required for deterministic manifest_patch parsing) together with tools in
    the same request. This isolates search grounding to a freeform research
    step whose findings are then handed to the unchanged structured call as
    additional prompt context.

    Uses the google-genai SDK's `client.interactions.create(...)` surface
    (not the raw generateContent REST endpoint the structured call below
    uses) -- direct generateContent calls with `tools: [{"google_search": {}}]`
    consistently returned 429 RESOURCE_EXHAUSTED / "check your plan and
    billing details" for every candidate model on this key, while the same
    key's interactions.create() call with `tools: [{"type": "google_search"}]`
    (confirmed working via AI Studio's own "Get Code" export) did not. The two
    surfaces appear to route through different quota/entitlement checks for
    this feature."""
    from google import genai

    search_prompt = (
        f"Search the web for the fixed version(s) of the package "
        f"'{candidate['package_name']}' that resolve {candidate['cve_id']} "
        f"(currently at vulnerable version {candidate['vulnerable_version']}). "
        f"Report exactly what you find: the fixed version number(s), the source "
        f"(e.g. advisory, changelog, registry), and note if sources disagree."
    )
    tools = [{'type': 'google_search'}, {'type': 'url_context'}]
    generation_config = {
        'max_output_tokens': 8192,
        'top_p': 0.95,
    }

    with open('search-grounding-request.json', 'w') as f:
        json.dump({
            "input": search_prompt,
            "tools": tools,
            "generation_config": generation_config,
            "models_tried": SEARCH_MODELS,
        }, f, indent=2)

    client = genai.Client(api_key=api_key)
    result_text = None
    raw_repr = None
    for model_name in SEARCH_MODELS:
        print(f"[SEARCH] Attempting grounded search using model: {model_name}...")
        try:
            interaction = client.interactions.create(
                model=f'models/{model_name}',
                input=search_prompt,
                tools=tools,
                generation_config=generation_config,
            )
            last_step = interaction.steps[-1]
            raw_repr = repr(last_step)
            # Response-shape for interactions.create() isn't fully documented
            # here -- try the plausible attribute names defensively and fall
            # back to the raw repr (saved to evidence either way) if none hit.
            for attr in ('content', 'text', 'output', 'output_text'):
                val = getattr(last_step, attr, None)
                if val:
                    result_text = val if isinstance(val, str) else str(val)
                    break
            if result_text is None:
                result_text = raw_repr
            print(f"[SEARCH] Successfully retrieved grounded findings using model: {model_name}")
            break
        except Exception as e:
            print(f"[WARNING] Search model {model_name} failed with error: {e}. Attempting fallback model...")
            continue

    with open('search-grounding-response-full.json', 'w') as f:
        json.dump({"raw_repr": raw_repr, "extracted_text": result_text}, f, indent=2)

    if not result_text:
        print("[WARNING] Grounded search failed on all candidate models; proceeding without search findings.")
        return "Web search grounding was attempted but returned no result; no external findings available."

    return result_text


def get_llm_recommendation(candidate, context, ecosystem, is_retry=False, failure_logs=""):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("[ERROR] GEMINI_API_KEY not found.")
        sys.exit(1)

    print("\n=== Search Grounding: researching fixed version independently ===")
    search_findings = _get_search_grounded_findings(candidate, api_key)
    print(search_findings)
    print("===================================================================\n")

    system_prompt = """You are a Senior DevSecOps AI Agent. Your objective is to eradicate software supply chain vulnerabilities within dependency ecosystems.
You must critically evaluate the topological subgraph. Provide comprehensive reasoning on why the vulnerability exists.
Evaluate all technically feasible remediation strategies: Direct Upgrade, Transitive Override, Dependency Resolution, Replacement, or Manual Review. Recommend the safest strategy that preserves compatibility and explain why alternative strategies were rejected.
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

    user_prompt = f"""Scenario ID: {scenario_id}
Prompt Version: HintRemoval-SearchGrounding-v1.0

### Vulnerability Intelligence
* Target Package: {candidate['package_name']}
* Vulnerable Version: {candidate['vulnerable_version']}
* CVE ID: {candidate['cve_id']}
* CVSS Score: {candidate['cvss']}
* EPSS Probability: {candidate['epss']}
* CISA KEV Status: {candidate['kev']}
* Intelligence Retrieved On: {intelligence_date}

### Dependency Context
```json
{json.dumps(context, indent=2)}
```

### Web Search Findings (live grounding, this call only -- not scanner-supplied)
{search_findings}
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
            # enum added in v1.2: strategy/remediation_type/operation were
            # previously unconstrained strings, compliance with the prose
            # description was advisory only. manifest_editor.py's own handling
            # logic already confirms at least 5 distinct literal values were
            # produced across historical runs -- constraining to the exact
            # values the pipeline actually understands closes that gap without
            # excluding anything previously valid. See prompts/PROMPT_CHANGELOG.md.
            "strategy": {
                "type": "STRING",
                "enum": ["direct_upgrade", "transitive_override", "dependency_resolution", "replacement", "manual_review"],
                "description": "The exact strategy chosen."
            },
            "remediation_type": {
                "type": "STRING",
                "enum": ["Direct Upgrade", "Transitive Override", "Dependency Resolution", "Replacement", "Manual Review"],
                "description": "The human-readable twin of strategy."
            },
            "recommended_package_version": {"type": "STRING", "description": "The specific semantic version to enforce."},
            "manifest_patch": {
                "type": "OBJECT",
                "description": "The structured intermediate representation of the manifest patch.",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "enum": ["add_override", "transitive_override", "replace", "bump", "direct_upgrade"],
                        "description": "The operation to perform."
                    },
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

    # Save the request for evidence, enriched with additional metadata for thesis audit trails
    evidence_payload = {
        "scenario_id": scenario_id,
        "experiment_id": "2026-final-search-grounding",
        "application": application,
        "ecosystem": ecosystem,
        "prompt_version": "HintRemoval-SearchGrounding-v1.0",
        "api_payload": api_payload
    }

    models = MODELS
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
                # Persist the model that actually responded so generate_manifest.py's
                # experiment_manifest.json reflects reality rather than only the
                # primary configured model. GITHUB_ENV is the standard mechanism for
                # passing a value from one workflow step to a later one -- os.environ
                # alone does not survive the step boundary. No-op outside CI (GITHUB_ENV
                # unset), and safe to write on a retry: the later write wins, which is
                # correct since that's the model that produced the final outcome.
                github_env = os.environ.get('GITHUB_ENV')
                if github_env:
                    with open(github_env, 'a') as env_f:
                        env_f.write(f"LLM_MODEL_USED={model_name}\n")
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
        # raise, not sys.exit -- SystemExit isn't an Exception subclass, so
        # sys.exit here would bypass the caller's `except Exception` and skip
        # writing metrics.json entirely instead of recording
        # llm_response_valid=False as intended.
        raise RuntimeError("All candidate LLM models failed to return a response.")

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
        # raise, not sys.exit -- SystemExit isn't an Exception subclass, so
        # sys.exit here would bypass the caller's `except Exception` and skip
        # writing metrics.json entirely instead of recording
        # llm_response_valid=False as intended.
        raise ValueError("Failed to parse LLM response as JSON.")
