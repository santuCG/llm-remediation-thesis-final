import urllib.request
import json
import os
import sys

TOKEN = "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"
REPO = "santuCG/llm-remediation-thesis-final"

class NoAuthRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req:
            # Remove Authorization header for cross-domain redirects (e.g. to Azure)
            if 'Authorization' in new_req.headers:
                del new_req.headers['Authorization']
            if 'authorization' in new_req.unredirected_hdrs:
                del new_req.unredirected_hdrs['authorization']
        return new_req

opener = urllib.request.build_opener(NoAuthRedirectHandler())
urllib.request.install_opener(opener)

def get_latest_run():
    req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/actions/runs?per_page=1')
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        return data['workflow_runs'][0]

def get_jobs(jobs_url):
    req = urllib.request.Request(jobs_url)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())['jobs']

def get_logs(log_url):
    req = urllib.request.Request(log_url)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8', errors='replace')
    except Exception as e:
        return str(e)

def main():
    run = get_latest_run()
    jobs = get_jobs(run['jobs_url'])
    for job in jobs:
        if job['conclusion'] == 'failure':
            log_api_url = f"https://api.github.com/repos/{REPO}/actions/jobs/{job['id']}/logs"
            print(f"--- LOGS for {job['name']} ---")
            print(get_logs(log_api_url))
            break

if __name__ == '__main__':
    main()
