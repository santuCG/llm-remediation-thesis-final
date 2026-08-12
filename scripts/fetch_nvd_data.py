import json
import urllib.request
import time
import os
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_cve_data():
    with open('experiment/final_18_scenarios.json', 'r', encoding='utf-8') as f:
        scenarios = json.load(f)

    for scenario in scenarios:
        cve = scenario['cve']
        out_path = f"experiment/raw_nvd_data/{cve}.json"
        
        if os.path.exists(out_path):
            print(f"Skipping {cve}, already downloaded.")
            continue
            
        print(f"Fetching {cve} from NVD...")
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve}"
        
        success = False
        retries = 3
        while not success and retries > 0:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                    data = json.loads(response.read().decode())
                    with open(out_path, 'w', encoding='utf-8') as out_f:
                        json.dump(data, out_f, indent=2)
                    print(f"  -> Successfully saved {cve}")
                    success = True
            except Exception as e:
                retries -= 1
                print(f"  -> [ERROR] {cve}: {e}. Retrying in 6s...")
                time.sleep(6)
                
        time.sleep(6.5) # Rate limit protection

if __name__ == "__main__":
    fetch_cve_data()
