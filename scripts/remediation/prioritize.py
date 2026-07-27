import urllib.request
import json
import ssl
from datetime import datetime, timezone

def get_epss_score(cve_id):
    try:
        url = f"https://api.first.org/data/v1/epss?cve={cve_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if res_data.get('status') == 'OK' and res_data.get('data'):
                return float(res_data['data'][0].get('epss', 0.0))
    except Exception as e:
        print(f"[WARN] Failed to fetch live EPSS for {cve_id}: {e}")
        
    try:
        snapshot_path = "scripts/remediation/snapshots/epss_snapshot.json"
        with open(snapshot_path, "r") as f:
            data = json.load(f)
            for item in data.get('data', []):
                if item.get('cve') == cve_id:
                    return float(item.get('epss', 0.0))
    except Exception as e:
        print(f"[WARN] Failed to fetch EPSS for {cve_id} from snapshot fallback: {e}")
    return 0.0

def get_kev_status(cve_id):
    try:
        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            for vuln in data.get('vulnerabilities', []):
                if vuln.get('cveID') == cve_id:
                    return True
    except Exception as e:
        print(f"[WARN] Failed to fetch live KEV status: {e}")
        
    try:
        snapshot_path = "scripts/remediation/snapshots/kev_snapshot.json"
        with open(snapshot_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for vuln in data.get('vulnerabilities', []):
                if vuln.get('cveID') == cve_id:
                    return True
    except Exception as e:
        print(f"[WARN] Failed to fetch KEV status from snapshot fallback: {e}")
    return False

def prioritize_vulnerabilities(matches, ecosystem):
    candidates = []
    
    kev_cache = {}
    epss_cache = {}
    
    print("[ORCHESTRATOR] Picking from pre-registered scenario...")
    for match in matches:
        vuln = match.get('vulnerability', {})
        artifact = match.get('artifact', {})
        
        cve_id = vuln.get('id', '')
        severity = vuln.get('severity', 'Unknown').lower()
        
        # 1. Severity >= High (High or Critical)
        if severity not in ['high', 'critical']:
            continue
            
        # 2. Fixed Version Exists
        fix = vuln.get('fix', {})
        if not fix or fix.get('state') != 'fixed':
            continue
            
        # 3. Supported Ecosystem
        pkg_type = artifact.get('type', '').lower()
        if ecosystem == 'npm' and pkg_type != 'npm':
            continue
        if ecosystem == 'python' and pkg_type != 'python':
            continue
            
        # Extract CVSS
        cvss_metrics = vuln.get('cvss', [])
        cvss_score = 0.0
        if cvss_metrics:
            cvss_score = cvss_metrics[0].get('metrics', {}).get('baseScore', 0.0)
            
        # Find explicit CVE ID for API queries if the primary is GHSA
        api_cve_id = cve_id
        if not cve_id.startswith('CVE-'):
            for rel in match.get('relatedVulnerabilities', []):
                rel_id = rel.get('id', '')
                if rel_id.startswith('CVE-'):
                    api_cve_id = rel_id
                    break
            
        if api_cve_id not in kev_cache:
            kev_cache[api_cve_id] = get_kev_status(api_cve_id)
        if api_cve_id not in epss_cache:
            epss_cache[api_cve_id] = get_epss_score(api_cve_id)
            
        candidates.append({
            'cve_id': cve_id,
            'api_cve_id': api_cve_id,
            'package_name': artifact.get('name'),
            'vulnerable_version': artifact.get('version'),
            'severity': severity,
            'cvss': cvss_score,
            'epss': epss_cache[api_cve_id],
            'epss_timestamp': datetime.now(timezone.utc).isoformat(),
            'kev': kev_cache[api_cve_id],
            'fixed_versions': fix.get('versions', [])
        })

    if not candidates:
        print("[PRIORITIZE] No automatically remediable candidates found.")
        return None, candidates

    # Sorting Logic: KEV (True) -> EPSS (Descending) -> CVSS (Descending)
    candidates.sort(key=lambda x: (x['kev'], x['epss'], x['cvss']), reverse=True)
    
    with open('candidate-ranking.json', 'w') as f:
        json.dump(candidates, f, indent=2)
    
    import os
    target_cve = os.environ.get('TARGET_CVE')
    top_candidate = candidates[0]
    
    if target_cve:
        for c in candidates:
            if c['cve_id'] == target_cve or c['api_cve_id'] == target_cve or c['package_name'] == target_cve:
                if target_cve.startswith('CVE-') and c['api_cve_id'] != target_cve:
                    c['api_cve_id'] = target_cve
                    c['epss'] = get_epss_score(target_cve)
                    c['kev'] = get_kev_status(target_cve)
                top_candidate = c
                print(f"[PRIORITIZE] Overriding selection with TARGET_CVE: {target_cve}")
                break
                
    print(f"[PRIORITIZE] Selected Top Candidate: {top_candidate['package_name']} ({top_candidate['cve_id']})")
    
    return top_candidate, candidates
