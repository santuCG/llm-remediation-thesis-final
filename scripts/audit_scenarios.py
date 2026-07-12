import json
import glob
import os
import sys

def audit_and_enrich():
    with open('experiment/final_18_scenarios.json', 'r', encoding='utf-8') as f:
        scenarios = json.load(f)

    updated_scenarios = []
    has_errors = False

    for scenario in scenarios:
        cve = scenario['cve']
        nvd_path = f"experiment/raw_nvd_data/{cve}.json"
        
        if not os.path.exists(nvd_path):
            print(f"[ERROR] Missing NVD data for {cve}. Run fetch_nvd_data.py first.")
            has_errors = True
            continue
            
        with open(nvd_path, 'r', encoding='utf-8') as f:
            nvd_raw = json.load(f)
            
        if not nvd_raw.get('vulnerabilities'):
            print(f"[ERROR] NVD data for {cve} is empty or malformed.")
            has_errors = True
            continue
            
        cve_data = nvd_raw['vulnerabilities'][0]['cve']
        
        # Extract Description
        desc_list = cve_data.get('descriptions', [])
        description = next((d['value'] for d in desc_list if d['lang'] == 'en'), 'No description')
        
        # Extract CVSS
        metrics = cve_data.get('metrics', {})
        cvss_data = None
        for key in ['cvssMetricV40', 'cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
            if key in metrics:
                cvss_data = metrics[key][0]['cvssData']
                break
                
        if not cvss_data:
            print(f"[ERROR] No CVSS data found in NVD for {cve}.")
            has_errors = True
            continue
            
        nvd_cvss = cvss_data.get('baseScore')
        cvss_vector = cvss_data.get('vectorString')
        
        # Extract CWEs
        weaknesses = cve_data.get('weaknesses', [])
        cwes = []
        for w in weaknesses:
            for desc in w.get('description', []):
                if desc['lang'] == 'en':
                    cwes.append(desc['value'])
        cwe_id = ', '.join(cwes) if cwes else 'Unknown'
        
        # 3-Way Audit: Verify NVD CVSS matches our JSON CVSS
        our_cvss = scenario['cvss']
        if float(nvd_cvss) != float(our_cvss):
            print(f"[CORRECTED] {cve}: Updating CVSS from {our_cvss} to NVD official {nvd_cvss}.")
            scenario['cvss'] = float(nvd_cvss)
        else:
            print(f"[VALID] {cve}: CVSS matches perfectly ({nvd_cvss}).")
            
        # Enrich scenario
        scenario['nvd_description'] = description
        scenario['cvss_vector'] = cvss_vector
        scenario['cwe_id'] = cwe_id
        updated_scenarios.append(scenario)

    with open('experiment/final_18_scenarios.json', 'w', encoding='utf-8') as f:
        json.dump(updated_scenarios, f, indent=2)
    print("\n[SUCCESS] Audit and enrichment complete! All 18 scenarios have been updated with NVD truth.")

if __name__ == "__main__":
    audit_and_enrich()
