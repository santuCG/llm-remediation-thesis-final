import os
import json
import yaml

evidence_dir = "results/execution_evidence"
profiles_dir = "profiles"

os.makedirs(profiles_dir, exist_ok=True)

for scenario in os.listdir(evidence_dir):
    if not (scenario.startswith("AF-") or scenario.startswith("JS-")):
        continue

    metrics_path = os.path.join(evidence_dir, scenario, "metrics.json")
    if not os.path.exists(metrics_path):
        print(f"Skipping {scenario}, no metrics.json")
        continue

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    ecosystem = metrics.get("ecosystem", "npm")
    application = metrics.get("application", "applications/juice-shop")
    if scenario.startswith("AF-"):
        ecosystem = "python"
        application = "applications/airflow"

    template = f"{ecosystem}-remediation.yml"
    
    # tool_versions logic based on JS vs AF
    if ecosystem == "npm":
        tools = {
            "node": "20.x",
            "syft": "v1.11.0" if scenario in ["JS-08", "JS-09", "JS-01"] else "v1.44.0", # we'll default to 1.44
            "grype": "v0.80.0" if scenario in ["JS-08", "JS-09", "JS-01"] else "v0.112.0"
        }
    else:
        tools = {
            "python": "3.11.x",
            "syft": "v1.44.0",
            "grype": "v0.112.0"
        }

    profile = {
        "scenario_id": scenario,
        "application": application,
        "ecosystem": ecosystem,
        "repository": {
            "url": "https://github.com/santuCG/llm-remediation-thesis-final",
            "commit": "HEAD"
        },
        "pipeline": {
            "version": "2.0",
            "template": template,
            "profile_version": "1.0"
        },
        "llm": {
            "provider": "Gemini",
            "model": "gemini-1.5-pro",
            "prompt_version": "v1.1",
            "temperature": 0,
            "top_p": 1,
            "top_k": 1
        },
        "tool_versions": tools,
        "target_package": metrics.get("selected_package", ""),
        "target_cve": metrics.get("api_cve_id", ""),
        "dependency_type": metrics.get("dependency_type", "direct"),
        "expected": {
            "strategy": metrics.get("strategy", "direct_upgrade"),
            "retry": metrics.get("retry_count", 0),
            "build": metrics.get("build_success", False),
            "rescan": metrics.get("rescan_success", False)
        }
    }

    profile_path = os.path.join(profiles_dir, f"{scenario}.yaml")
    with open(profile_path, "w") as f:
        yaml.dump(profile, f, sort_keys=False)
        print(f"Generated {profile_path}")
