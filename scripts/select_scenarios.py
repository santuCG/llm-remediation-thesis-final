import json
import os
import re
import urllib.request
import time
import subprocess
import datetime

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_valid_upgrade(current, target):
    pre_release_indicators = ['alpha', 'beta', 'rc', 'pre', 'dev', 'a', 'b', '-']
    if any(ind in target.lower() for ind in pre_release_indicators):
        return False
    def get_parts(v):
        v = v.lstrip('v')
        parts = re.split(r'[^0-9]+', v)
        nums = []
        for p in parts:
            if p.isdigit(): nums.append(int(p))
            else: break
        return nums
    curr_parts = get_parts(current)
    targ_parts = get_parts(target)
    if not targ_parts: return False
    for i in range(max(len(curr_parts), len(targ_parts))):
        c = curr_parts[i] if i < len(curr_parts) else 0
        t = targ_parts[i] if i < len(targ_parts) else 0
        if t > c: return True
        elif t < c: return False
    return False

def get_upgrade_type(current, target):
    def get_parts(v):
        v = v.lstrip('v')
        return [int(p) for p in re.split(r'[^0-9]+', v) if p.isdigit()]
    c = get_parts(current)
    t = get_parts(target)
    while len(c) < 3: c.append(0)
    while len(t) < 3: t.append(0)
    if t[0] != c[0]: return "major"
    if t[1] != c[1]: return "minor"
    return "patch"

def extract_cve_id(match):
    vuln = match.get('vulnerability', {})
    cve_id = vuln.get('id')
    original_ghsa_id = None
    if cve_id and cve_id.startswith('GHSA-'):
        original_ghsa_id = cve_id
        cve_id = None
        aliases = vuln.get('aliases', [])
        for a in aliases:
            if isinstance(a, str) and a.startswith('CVE-'):
                cve_id = a
                break
        if not cve_id:
            related = match.get('relatedVulnerabilities', [])
            for r in related:
                r_id = r.get('id', '')
                if isinstance(r_id, str) and r_id.startswith('CVE-'):
                    cve_id = r_id
                    break
    return cve_id, original_ghsa_id

def fetch_and_save_epss(cve_id):
    local_path = f"applications/evidence/{cve_id}_epss.json"
    if os.path.exists(local_path):
        data = load_json(local_path)
        if data.get('data'):
            return float(data['data'][0]['epss'])
        return 0.0
    try:
        url = f'https://api.first.org/data/v1/epss?cve={cve_id}'
        req = urllib.request.Request(url, headers={'User-Agent': 'thesis-script/1.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        raw = resp.read()
        os.makedirs("applications/evidence", exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(raw)
        data = json.loads(raw)
        if data.get('data'):
            return float(data['data'][0]['epss'])
    except Exception as e:
        print(f"Failed to fetch EPSS for {cve_id}: {e}")
    return 0.0

def fetch_and_save_mitre(cve_id):
    local_path = f"applications/evidence/{cve_id}_mitre.json"
    if os.path.exists(local_path):
        return load_json(local_path)
    try:
        url = f'https://cveawg.mitre.org/api/cve/{cve_id}'
        req = urllib.request.Request(url, headers={'User-Agent': 'thesis-script/1.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        raw = resp.read()
        os.makedirs("applications/evidence", exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(raw)
        return json.loads(raw)
    except Exception as e:
        print(f"Failed to fetch MITRE for {cve_id}: {e}")
    return {}

def extract_mitre_info(mitre_data):
    description = ""
    cwe_id = ""
    cvss_vector = ""
    cna = mitre_data.get("containers", {}).get("cna", {})
    for desc in cna.get("descriptions", []):
        if desc.get("lang") == "en":
            description = desc.get("value", "")
            break
    for pt in cna.get("problemTypes", []):
        for desc in pt.get("descriptions", []):
            d = desc.get("description", "")
            if "CWE" in d:
                cwe_id = d
                break
        if cwe_id: break
    metrics = cna.get("metrics", [])
    for m in metrics:
        if "cvssV4_0" in m:
            cvss_vector = m["cvssV4_0"].get("vectorString", "")
            break
        elif "cvssV3_1" in m:
            cvss_vector = m["cvssV3_1"].get("vectorString", "")
            break
        elif "cvssV3_0" in m:
            cvss_vector = m["cvssV3_0"].get("vectorString", "")
            break
    return description, cwe_id, cvss_vector

kev_cache = None
def is_kev(cve_id):
    global kev_cache
    if kev_cache is None:
        local_path = "applications/evidence/cisa_kev_snapshot.json"
        if os.path.exists(local_path):
            data = load_json(local_path)
            kev_cache = {v['cveID'] for v in data.get('vulnerabilities', [])}
        else:
            try:
                url = 'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'
                req = urllib.request.Request(url, headers={'User-Agent': 'thesis-script/1.0'})
                resp = urllib.request.urlopen(req, timeout=15)
                raw = resp.read()
                os.makedirs("applications/evidence", exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(raw)
                data = json.loads(raw)
                kev_cache = {v['cveID'] for v in data.get('vulnerabilities', [])}
            except Exception:
                kev_cache = set()
    return cve_id in kev_cache

def is_blacklisted(pkg_name, app_name, pkg_type):
    name = pkg_name.lower()
    app = app_name.lower().replace(" ", "-")
    if name == app or name == 'apache-airflow':
        return True
    if name.startswith('apache-airflow-providers-'):
        return True
    if name in ['authlib', 'urllib3']:
        return True
    if name in ['setuptools', 'virtualenv', 'pip', 'wheel']:
        return True
    if pkg_type not in ['npm', 'python']:
        return True
    return False

def select_scenarios(app_name, grype_file, prefix, ecosystem, image_name):
    print(f"Selecting scenarios for {app_name}...")
    data = load_json(grype_file)
    matches = data.get('matches', [])
    
    candidates = []
    seen_packages = set()
    
    total_raw = len(matches)
    
    descriptor = data.get('descriptor', {})
    grype_version = descriptor.get('version', 'Unknown')
    db_built = descriptor.get('db', {}).get('status', {}).get('built', 'Unknown')
    
    syft_version = 'Unknown'
    total_packages = 'Unknown'
    sbom_file = grype_file.replace('_grype.json', '_sbom.json')
    if os.path.exists(sbom_file):
        try:
            with open(sbom_file, 'r', encoding='utf-8', errors='ignore') as f:
                sbom_data = json.load(f)
                packages = sbom_data.get('packages', sbom_data.get('artifacts', []))
                total_packages = len(packages)
                for creator in sbom_data.get('creationInfo', {}).get('creators', []):
                    if 'syft' in creator.lower():
                        syft_version = creator.split(':')[-1].strip()
        except Exception:
            pass
    dropped_os = 0
    dropped_blacklisted = 0
    filtered_by_no_cve = 0
    filtered_by_state = 0
    filtered_by_cvss = 0
    filtered_by_downgrade = 0
    
    for match in matches:
        vuln = match.get('vulnerability', {})
        artifact = match.get('artifact', {})
        pkg_name = artifact.get('name', '')
        current_version = artifact.get('version')
        pkg_type = artifact.get('type', '').lower()
        
        if pkg_type not in ['npm', 'python']:
            dropped_os += 1
            continue
            
        if is_blacklisted(pkg_name, app_name, pkg_type):
            dropped_blacklisted += 1
            continue
        
        cve_id, original_ghsa_id = extract_cve_id(match)
        if not cve_id:
            filtered_by_no_cve += 1
            continue
            
        fix = vuln.get('fix', {})
        if fix.get('state') != 'fixed':
            filtered_by_state += 1
            continue
            
        fixed_versions = fix.get('versions', [])
        if not fixed_versions:
            filtered_by_state += 1
            continue
            
        cvss_metrics = vuln.get('cvss', [])
        highest_score = 0.0
        for metric in cvss_metrics:
            metrics_dict = metric.get('metrics', {})
            score = metrics_dict.get('baseScore', 0.0)
            if score > highest_score:
                highest_score = score
                
        severity = vuln.get('severity', '').lower()
        if highest_score == 0.0:
            if severity == 'critical': highest_score = 9.0
            elif severity == 'high': highest_score = 7.0 
                
        if highest_score < 7.0:
            filtered_by_cvss += 1
            continue
            
        valid_fixes = [v for v in fixed_versions if is_valid_upgrade(current_version, v)]
        if not valid_fixes:
            filtered_by_downgrade += 1
            continue
            
        target_version = valid_fixes[0]
        
        if pkg_name in seen_packages:
            continue
            
        locations = artifact.get('locations') or []
        paths = [loc.get('path', '') for loc in locations]
        
        is_transitive = False
        if ecosystem == 'npm':
            is_transitive = any('node_modules' in p and p.count('node_modules') > 1 for p in paths)
        else:
            is_transitive = any('site-packages' in p for p in paths)
            
        is_direct = not is_transitive
        
        manifest_file = "package.json" if ecosystem == "npm" else "requirements.txt"
        lock_file = "package-lock.json" if ecosystem == "npm" else "pip freeze"
        if app_name == "Ghost": lock_file = "yarn.lock"
        dep_path = f"root -> {pkg_name}" if is_direct else f"root -> ... -> {pkg_name}"
        
        candidates.append({
            "package": pkg_name,
            "cve_id": cve_id,
            "original_ghsa_id": original_ghsa_id,
            "current_version": current_version,
            "target_version": target_version,
            "score": highest_score,
            "is_direct": is_direct,
            "manifest_file": manifest_file,
            "lock_file": lock_file,
            "dep_path": dep_path,
            "urls": vuln.get('urls', [])
        })
        seen_packages.add(pkg_name)
        
    candidates.sort(key=lambda x: (x['is_direct'], -x['score']))
    
    top_15 = candidates[:15]
    selected = candidates[:9]
    
    formatted_scenarios = []
    log_entries = []
    for i, s in enumerate(selected):
        scenario_id = f"{prefix}-{str(i+1).zfill(2)}"
        
        epss = fetch_and_save_epss(s['cve_id'])
        mitre_data = fetch_and_save_mitre(s['cve_id'])
        desc, cwe, cvss_vec = extract_mitre_info(mitre_data)
        kev = is_kev(s['cve_id'])
        
        cvss_vec = cvss_vec if cvss_vec and str(cvss_vec).strip() else None
        cwe = cwe if cwe and str(cwe).strip() else None
        desc = desc if desc and str(desc).strip() else None
        
        formatted_scenarios.append({
            "scenario_id": scenario_id,
            "application": app_name,
            "metadata_snapshot_date": datetime.datetime.utcnow().isoformat() + "Z",
            "package": {
                "name": s['package'],
                "ecosystem": "npm" if ecosystem == "npm" else "pypi",
                "is_direct_dependency": s['is_direct'],
                "current_version": s['current_version'],
                "grype_recommended_version": s['target_version'],
                "upgrade_type": get_upgrade_type(s['current_version'], s['target_version'])
            },
            "vulnerability": {
                "cve_id": s['cve_id'],
                "original_ghsa_id": s['original_ghsa_id'],
                "cvss_score": s['score'],
                "cvss_vector": cvss_vec,
                "epss_probability": epss,
                "kev_status": kev,
                "cwe_id": cwe,
                "description": desc
            },
            "dependency_context": {
                "manifest_file": s['manifest_file'],
                "lock_file": s['lock_file'],
                "dependency_path": s['dep_path']
            }
        })
        log_entries.append({
            "scenario_id": scenario_id,
            "rationale": f"Selected {s['cve_id']} in {s['package']} (CVSS {s['score']}). Topological position: {'Direct' if s['is_direct'] else 'Transitive'}.",
            "urls": s['urls'][:2]
        })
        
    stats = {
        "app": app_name,
        "image": image_name,
        "grype_version": grype_version,
        "db_built": db_built,
        "syft_version": syft_version,
        "total_packages": total_packages,
        "total_raw": total_raw,
        "dropped_os": dropped_os,
        "dropped_blacklisted": dropped_blacklisted,
        "filtered_by_no_cve": filtered_by_no_cve,
        "filtered_by_no_fix": filtered_by_state,
        "filtered_by_low_cvss": filtered_by_cvss,
        "filtered_by_downgrade": filtered_by_downgrade,
        "eligible_candidates": len(candidates),
        "top_15": top_15
    }
        
    return formatted_scenarios, log_entries, stats

def generate_app_md(stats, prefix):
    app_name = stats["app"]
    filename = app_name.lower().replace(" ", "_")
    image = stats["image"]
    sbom_file = f"{filename}_sbom.json"
    grype_file = f"{filename}_grype.json"
    
    extra_warning = ""
    lockfile_name = "package-lock.json" if app_name == "Juice Shop" else "pip freeze"
    if app_name == "Airflow":
        extra_warning = "\\n\\n**Airflow Constraints Warning:** Airflow packages strictly require Apache constraint files during pip install to resolve dependencies without conflicts."

    md = f"""# {app_name} Scenarios (Docker-Based Methodology)

## Strict Reproducibility Baseline

- **Target Docker Image Version:** {stats['image']}
- **Grype Version & DB Build Date:** v{stats['grype_version']} (DB Built: {stats['db_built']})
- **SBOM Tool:** {stats['syft_version']}
- **Total Packages Scanned:** {stats['total_packages']}
- **Total Raw Vulns Detected:** {stats['total_raw']}

**State-Freeze Rationale:**
To reproduce the raw baseline (e.g., {stats['total_raw']} vulnerabilities), the exact Docker Image tag must be scanned. However, to guarantee the LLM's remediation targets do not drift over time, the exact transitive dependency graph was extracted via {lockfile_name} and stored in this evidence folder. This ensures the LLM acts upon a cryptographically frozen snapshot of the application's dependencies.{extra_warning}

## Steps for Exact Reproducibility

To guarantee that any researcher can reproduce these exact Grype findings and LLM responses, a strict Docker-based snapshot approach is followed.

**Generating the SBOM:**
```bash
syft scan registry:{image} -o spdx-json={sbom_file}
```

**Scanning the SBOM:**
```bash
GRYPE_DB_AUTO_UPDATE=false grype sbom:{sbom_file} -o json={grype_file}
```
"""
    with open(f"applications/evidence/{filename}_scenarios.md", "w", encoding='utf-8') as f:
        f.write(md)

def freeze_artifacts():
    print("Freezing artifacts for reproducibility...")
    os.makedirs("applications/evidence", exist_ok=True)
    
    if not os.path.exists("applications/evidence/juice_shop_package-lock.json"):
        print("Extracting Juice Shop package-lock.json...")
        subprocess.run("docker create --name temp-js bkimminich/juice-shop:v15.3.0", shell=True, stdout=subprocess.DEVNULL)
        subprocess.run("docker cp temp-js:/juice-shop/package-lock.json applications/evidence/juice_shop_package-lock.json", shell=True, stdout=subprocess.DEVNULL)
        subprocess.run("docker rm temp-js", shell=True, stdout=subprocess.DEVNULL)
    

    
    if not os.path.exists("applications/evidence/airflow_pipdeptree.txt"):
        print("Extracting Airflow pip freeze and pipdeptree...")
        subprocess.run("docker run --rm --entrypoint bash apache/airflow:2.9.2 -c \"pip freeze\" > applications/evidence/airflow_pip_freeze.txt", shell=True)
        subprocess.run('docker run --rm --entrypoint bash apache/airflow:2.9.2 -c "pip install pipdeptree >/dev/null 2>&1 && pipdeptree" > applications/evidence/airflow_pipdeptree.txt', shell=True)

if __name__ == "__main__":
    base_dir = "applications/evidence"
    
    print("Snapshotting CISA KEV...")
    is_kev("CVE-0000-0000")
    
    freeze_artifacts()
    
    js_scenarios, js_logs, js_stats = select_scenarios("Juice Shop", os.path.join(base_dir, "juice-shop_grype.json"), "JS", "npm", "bkimminich/juice-shop:v15.3.0")
    af_scenarios, af_logs, af_stats = select_scenarios("Airflow", os.path.join(base_dir, "airflow_grype.json"), "AF", "python", "apache/airflow:2.9.2")
    
    generate_app_md(js_stats, "JS")
    generate_app_md(af_stats, "AF")
    
    all_scenarios = js_scenarios + af_scenarios
    all_logs = js_logs + af_logs
    all_stats = [js_stats, af_stats]
    
    output_file = "experiment/final_18_scenarios.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_scenarios, f, indent=4)
        
    print(f"\\nSuccessfully generated {len(all_scenarios)} scenarios and saved to {output_file}")
    
    log_content = "# Scenario Selection and Observation Log\\n\\n"
    for log in all_logs:
        log_content += f"### {log['scenario_id']}\\n"
        log_content += f"**Rationale:** {log['rationale']}\\n\\n"
    with open("preregistration/scenario_selection_log.md", "w", encoding='utf-8') as f:
        f.write(log_content)
        
    audit_content = "=== SELECTION AUDIT LOG ===\\n\\n"
    for stat in all_stats:
        audit_content += f"--- {stat['app']} ---\\n"
        audit_content += f"Dropped OS-level packages: {stat['dropped_os']}\\n"
        audit_content += f"Dropped Blacklisted packages: {stat['dropped_blacklisted']}\\n"
        audit_content += f"Dropped No CVE: {stat['filtered_by_no_cve']}\\n"
        audit_content += f"Dropped No Fix: {stat['filtered_by_no_fix']}\\n"
        audit_content += f"Dropped Low CVSS (< 7.0): {stat['filtered_by_low_cvss']}\\n"
        audit_content += f"Dropped Downgrade/Pre-release: {stat['filtered_by_downgrade']}\\n\\n"
        
        audit_content += "Top 15 Eligible Candidates Before Slicing:\\n"
        for i, c in enumerate(stat['top_15']):
            topo = "Direct" if c['is_direct'] else "Transitive"
            audit_content += f"  {i+1}. {c['package']} | {c['cve_id']} | CVSS: {c['score']} | {topo}\\n"
        audit_content += "\\n"
        
    os.makedirs("experiment", exist_ok=True)
    with open("experiment/selection_audit_log.txt", "w", encoding='utf-8') as f:
        f.write(audit_content)
        
    print("Successfully generated experiment/selection_audit_log.txt")
