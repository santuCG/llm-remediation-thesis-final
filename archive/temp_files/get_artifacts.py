import urllib.request
import json
import os
import zipfile

token = os.environ["GITHUB_TOKEN"]
req = urllib.request.Request('https://api.github.com/repos/santuCG/llm-remediation-thesis-final/actions/runs/30212986023/artifacts')
req.add_header('Authorization', f'token {token}')
req.add_header('Accept', 'application/vnd.github.v3+json')
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    for artifact in data.get('artifacts', []):
        print(f"Found artifact: {artifact['name']}")
        if artifact['name'] == 'remediation-evidence':
            url = artifact['archive_download_url']
            dl_req = urllib.request.Request(url)
            dl_req.add_header('Authorization', f'token {token}')
            with urllib.request.urlopen(dl_req) as dl_resp:
                with open('remediation-evidence.zip', 'wb') as f:
                    f.write(dl_resp.read())
            print("Downloaded. Unzipping...")
            os.makedirs('results/AF-01/automated/remediation-evidence-latest', exist_ok=True)
            with zipfile.ZipFile('remediation-evidence.zip', 'r') as zip_ref:
                zip_ref.extractall('results/AF-01/automated/remediation-evidence-latest')
            print("Done!")
