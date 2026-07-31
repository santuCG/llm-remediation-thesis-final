import urllib.request, json, zipfile, io, os

TOKEN = os.environ["GITHUB_TOKEN"]
run_ids = [30133490467, 30133472098, 30133471466]

for run_id in run_ids:
    print(f"--- Fetching for run {run_id} ---")
    req = urllib.request.Request(f'https://api.github.com/repos/santuCG/llm-remediation-thesis-final/actions/runs/{run_id}/artifacts')
    req.add_header('Authorization', f'Bearer {TOKEN}')
    try:
        with urllib.request.urlopen(req) as res:
            artifacts = json.loads(res.read())['artifacts']
            evidence_artifact = next(a for a in artifacts if a['name'] == 'remediation-evidence')
            
            # Use curl to download the zip artifact because urllib struggles with github's redirected S3 links
            import os
            os.system(f'curl.exe -sL -H "Accept: application/vnd.github+json" -H "Authorization: Bearer {TOKEN}" -H "X-GitHub-Api-Version: 2022-11-28" {evidence_artifact["archive_download_url"]} -o evidence_{run_id}.zip')
            
            with zipfile.ZipFile(f'evidence_{run_id}.zip', 'r') as zip_ref:
                with zip_ref.open('metrics.json') as f:
                    metrics = json.loads(f.read())
                    print(f"Strategy: {metrics.get('strategy')}")
                    print(f"JSON Valid on Attempt 1: {metrics.get('retry_count') == 1}")
                    print(f"Failure Stage: {metrics.get('failure_stage')}")
                    print(f"Remediation Type: {metrics.get('remediation_type')}")
                    print(f"Confidence: {metrics.get('confidence')}")
    except Exception as e:
        print('Failed:', e)
