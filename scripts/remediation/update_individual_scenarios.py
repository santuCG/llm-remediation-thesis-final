import json
import os

def main():
    final_scenarios_path = "results/scenarios/final_18_scenarios.json"
    scenarios_dir = "results/scenarios"
    
    if not os.path.exists(final_scenarios_path):
        print(f"[ERROR] Master scenarios file not found at {final_scenarios_path}")
        return
        
    with open(final_scenarios_path, "r", encoding="utf-8") as f:
        master_scenarios = json.load(f)
        
    for item in master_scenarios:
        scenario_id = item["scenario_id"]
        filepath = os.path.join(scenarios_dir, f"{scenario_id}.json")
        
        # Load or generate skeleton
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                scen_data = json.load(f)
        else:
            print(f"[WARNING] Individual scenario file {filepath} not found, skipping.")
            continue
            
        # Update metadata Snaps and Vulnerability details from final_18_scenarios.json
        scen_data["pre_registration"]["scenario_metadata"]["application_version"] = item["package"]["current_version"]
        
        cve_data = scen_data["pre_registration"]["vulnerability_enrichment"]["cve"]
        cve_data["id"] = item["vulnerability"]["cve_id"]
        cve_data["description"] = item["vulnerability"]["description"]
        cve_data["cvss_score"] = item["vulnerability"]["cvss_score"]
        cve_data["cvss_vector"] = item["vulnerability"].get("cvss_vector", "")
        
        # Derive severity
        cvss = item["vulnerability"]["cvss_score"]
        if cvss is not None:
            if cvss >= 9.0:
                cve_data["severity"] = "Critical"
            elif cvss >= 7.0:
                cve_data["severity"] = "High"
            elif cvss >= 4.0:
                cve_data["severity"] = "Medium"
            else:
                cve_data["severity"] = "Low"
                
        scen_data["pre_registration"]["vulnerability_enrichment"]["epss"]["score"] = item["vulnerability"]["epss_probability"]
        scen_data["pre_registration"]["vulnerability_enrichment"]["kev"]["listed"] = item["vulnerability"]["kev_status"]
        
        grype_rec = scen_data["pre_registration"]["scanner_recommendation"]["grype"]
        grype_rec["package"] = item["package"]["name"]
        grype_rec["installed_version"] = item["package"]["current_version"]
        grype_rec["recommended_fixed_version"] = item["package"]["grype_recommended_version"]
        
        # Save updated scenario file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(scen_data, f, indent=2)
            
        print(f"[INFO] Updated individual scenario metadata for {scenario_id}")

if __name__ == "__main__":
    main()
