import sys
import urllib.request
import json
import os
from datetime import datetime, timezone


def get_epss_score_from_snapshot(cve_id):
    """Primary source: local snapshot (ensures reproducibility)."""
    try:
        snapshot_path = "scripts/remediation/snapshots/epss_snapshot.json"
        with open(snapshot_path, "r") as f:
            data = json.load(f)
            for item in data.get('data', []):
                if item.get('cve') == cve_id:
                    return float(item.get('epss', 0.0))
    except Exception as e:
        print(f"[WARN] EPSS snapshot lookup failed for {cve_id}: {e}")
    return None


def get_epss_score_live(cve_id):
    """Supplementary source: live API (used only as fallback if snapshot lacks entry)."""
    try:
        url = f"https://api.first.org/data/v1/epss?cve={cve_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if res_data.get('status') == 'OK' and res_data.get('data'):
                score = float(res_data['data'][0].get('epss', 0.0))
                print(f"[INFO] EPSS fetched from live API for {cve_id}: {score} "
                      f"(snapshot did not contain this CVE)")
                return score
    except Exception as e:
        print(f"[WARN] Live EPSS API call failed for {cve_id}: {e}")
    return 0.0


def get_epss_score(cve_id):
    """Snapshot-first EPSS retrieval to ensure reproducibility."""
    score = get_epss_score_from_snapshot(cve_id)
    if score is not None:
        return score
    return get_epss_score_live(cve_id)


def get_kev_status_from_snapshot(cve_id):
    """Primary source: local KEV snapshot."""
    try:
        snapshot_path = "scripts/remediation/snapshots/kev_snapshot.json"
        with open(snapshot_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for vuln in data.get('vulnerabilities', []):
                if vuln.get('cveID') == cve_id:
                    return True
        return False
    except Exception as e:
        print(f"[WARN] KEV snapshot lookup failed for {cve_id}: {e}")
    return None


def get_kev_status_live(cve_id):
    """Supplementary source: live CISA KEV feed (fallback only)."""
    try:
        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            for vuln in data.get('vulnerabilities', []):
                if vuln.get('cveID') == cve_id:
                    print(f"[INFO] KEV status from live API for {cve_id}: True")
                    return True
        return False
    except Exception as e:
        print(f"[WARN] Live KEV API call failed for {cve_id}: {e}")
    return False


def get_kev_status(cve_id):
    """Snapshot-first KEV retrieval to ensure reproducibility."""
    status = get_kev_status_from_snapshot(cve_id)
    if status is not None:
        return status
    return get_kev_status_live(cve_id)


def _build_structural_candidates(matches, ecosystem, kev_cache, epss_cache):
    """Build candidates applying only the structural filters -- fixed version
    exists, ecosystem matches -- NOT severity. Severity is a ranking/discovery
    concern, not a validity concern: a match that fails these two checks
    genuinely cannot be remediated in this run (no fix to apply, or wrong
    ecosystem's package manager); a match that merely has low severity can
    still be a legitimate, explicitly-requested target."""
    candidates = []
    for match in matches:
        vuln = match.get('vulnerability', {})
        artifact = match.get('artifact', {})

        cve_id = vuln.get('id', '')
        severity = vuln.get('severity', 'Unknown').lower()

        fix = vuln.get('fix', {})
        if not fix or fix.get('state') != 'fixed':
            continue

        pkg_type = artifact.get('type', '').lower()
        if ecosystem == 'npm' and pkg_type != 'npm':
            continue
        if ecosystem == 'python' and pkg_type != 'python':
            continue

        cvss_metrics = vuln.get('cvss', [])
        cvss_score = 0.0
        if cvss_metrics:
            cvss_score = cvss_metrics[0].get('metrics', {}).get('baseScore', 0.0)

        # Resolve CVE ID for API queries (GHSA → CVE)
        api_cve_id = cve_id
        scanner_cve_id = cve_id  # preserve the original scanner-reported ID
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
            'scanner_cve_id': scanner_cve_id,   # original Grype-reported ID (immutable)
            'api_cve_id': api_cve_id,            # resolved CVE ID for enrichment APIs
            'package_name': artifact.get('name'),
            'vulnerable_version': artifact.get('version'),
            'severity': severity,
            'cvss': cvss_score,
            'epss': epss_cache[api_cve_id],
            'epss_timestamp': datetime.now(timezone.utc).isoformat(),
            'kev': kev_cache[api_cve_id],
            'fixed_versions': fix.get('versions', [])
        })
    return candidates


def prioritize_vulnerabilities(matches, ecosystem):
    kev_cache = {}
    epss_cache = {}

    print("[ORCHESTRATOR] Picking from pre-registered scenario...")

    # Build the full structurally-valid pool ONCE (fix exists, ecosystem
    # matches) -- this is the pool an explicit TARGET_CVE is matched against,
    # and also the pool automatic discovery narrows with the severity filter.
    # Severity is deliberately NOT applied here: for a preregistered
    # experiment, TARGET_CVE is the ground truth, not a hint the severity
    # filter should be allowed to override. This is what let AF-06 and JS-06
    # silently drift to a different vulnerability -- their real, preregistered
    # match existed in Grype's output the whole time but never reached the
    # old severity-gated candidate list, so TARGET_CVE had nothing to find.
    all_structural_candidates = _build_structural_candidates(matches, ecosystem, kev_cache, epss_cache)

    target_cve = os.environ.get('TARGET_CVE')

    if target_cve:
        print(f"[PRIORITIZE] TARGET_CVE={target_cve} is set: performing an authoritative lookup "
              f"against all {len(all_structural_candidates)} structurally-valid candidates "
              f"(severity filter not applied to this lookup).")
        for c in all_structural_candidates:
            if c['cve_id'] == target_cve or c['api_cve_id'] == target_cve or c['package_name'] == target_cve:
                if target_cve.startswith('CVE-') and c['api_cve_id'] != target_cve:
                    print(f"[PRIORITIZE] TARGET_CVE override: api_cve_id updated "
                          f"from {c['api_cve_id']} to {target_cve} "
                          f"(scanner reported: {c['scanner_cve_id']})")
                    c['api_cve_id'] = target_cve
                    c['epss'] = get_epss_score(target_cve)
                    c['kev'] = get_kev_status(target_cve)
                with open('candidate-ranking.json', 'w') as f:
                    json.dump([c], f, indent=2)
                print(f"[PRIORITIZE] TARGET_CVE matched: {c['package_name']} ({c['cve_id']}, "
                      f"severity={c['severity']}).")
                return c, [c]

        # No structurally-valid candidate matches the requested TARGET_CVE.
        # Fail loudly instead of silently falling back to a different
        # vulnerability -- this is the exact fix for the AF-06/JS-06 drift.
        with open('candidate-ranking.json', 'w') as f:
            json.dump(all_structural_candidates, f, indent=2)
        available = ", ".join(sorted({c['api_cve_id'] or c['cve_id'] for c in all_structural_candidates})) or "(none)"
        print(f"[ERROR] TARGET_CVE={target_cve} was not found among any structurally-valid "
              f"candidate (fix exists, ecosystem={ecosystem}) in this scan.")
        print(f"[ERROR] Structurally-valid CVE/GHSA IDs that WERE available: {available}")
        print("[ERROR] Refusing to silently substitute a different vulnerability. Failing.")
        sys.exit(1)

    # No explicit target: automatic discovery mode. Severity filter applies
    # here, and only here -- it exists to guide unattended candidate
    # discovery, not to override an explicitly preregistered target.
    print("[PRIORITIZE] No TARGET_CVE set: automatic discovery mode (severity >= high required).")
    candidates = [c for c in all_structural_candidates if c['severity'] in ['high', 'critical']]

    if not candidates:
        print("[PRIORITIZE] No automatically remediable candidates found.")
        return None, candidates

    # Sorting Logic: KEV (True) -> EPSS (Descending) -> CVSS (Descending)
    candidates.sort(key=lambda x: (x['kev'], x['epss'], x['cvss']), reverse=True)

    with open('candidate-ranking.json', 'w') as f:
        json.dump(candidates, f, indent=2)

    top_candidate = candidates[0]
    print(f"[PRIORITIZE] Selected Top Candidate: {top_candidate['package_name']} ({top_candidate['cve_id']})")

    return top_candidate, candidates
