import urllib.request
import json
import ssl

def get_epss_score(cve_id):
    try:
        url = f"https://api.first.org/epss?cve={cve_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=context) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('data'):
                epss = float(data['data'][0].get('epss', 0.0))
                return epss
    except Exception as e:
        print(f"[WARN] Failed to fetch EPSS for {cve_id}: {e}")
    return 0.0

def get_kev_status(cve_id):
    try:
        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=context) as response:
            data = json.loads(response.read().decode('utf-8'))
            for vuln in data.get('vulnerabilities', []):
                if vuln.get('cveID') == cve_id:
                    return True
    except Exception as e:
        print(f"[WARN] Failed to fetch KEV status: {e}")
    return False

def prioritize_vulnerabilities(matches, ecosystem):
    candidates = []
    
    # Pre-fetch KEV once if possible, or fetch per CVE
    kev_cache = {}
    epss_cache = {}
    
    print("[PRIORITIZE] Filtering for automatically remediable candidates...")
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
            
        if cve_id not in kev_cache:
            kev_cache[cve_id] = get_kev_status(cve_id)
        if cve_id not in epss_cache:
            epss_cache[cve_id] = get_epss_score(cve_id)
            
        candidates.append({
            'cve_id': cve_id,
            'package_name': artifact.get('name'),
            'vulnerable_version': artifact.get('version'),
            'severity': severity,
            'cvss': cvss_score,
            'epss': epss_cache[cve_id],
            'kev': kev_cache[cve_id],
            'fixed_versions': fix.get('versions', [])
        })

    if not candidates:
        print("[PRIORITIZE] No automatically remediable candidates found.")
        return None

    # Sorting Logic: KEV (True) -> EPSS (Descending) -> CVSS (Descending)
    candidates.sort(key=lambda x: (x['kev'], x['epss'], x['cvss']), reverse=True)
    
    top_candidate = candidates[0]
    print(f"[PRIORITIZE] Selected Top Candidate: {top_candidate['package_name']} ({top_candidate['cve_id']})")
    
    return top_candidate
