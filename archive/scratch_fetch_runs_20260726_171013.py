import urllib.request, json
TOKEN='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'
req = urllib.request.Request('https://api.github.com/repos/santuCG/llm-remediation-thesis-final/actions/workflows/generic-remediation.yml/runs?per_page=3')
req.add_header('Authorization', f'Bearer {TOKEN}')
try:
    with urllib.request.urlopen(req) as res:
        runs = json.loads(res.read())['workflow_runs']
        for run in runs:
            print(f"ID: {run['id']}, Status: {run['status']}, Conclusion: {run['conclusion']}, Created At: {run['created_at']}")
except Exception as e:
    print('Failed:', e)
