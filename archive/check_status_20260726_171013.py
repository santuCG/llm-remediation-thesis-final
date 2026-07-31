import urllib.request
import json
import time
import os

def check():
    req = urllib.request.Request('https://api.github.com/repos/santuCG/llm-remediation-thesis-final/actions/runs?per_page=1')
    req.add_header('Authorization', f'Bearer {os.environ["GITHUB_TOKEN"]}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    res = urllib.request.urlopen(req)
    run = json.loads(res.read())['workflow_runs'][0]
    print(f"Status: {run['status']}, Conclusion: {run['conclusion']}")
    return run['status']

if __name__ == '__main__':
    check()
