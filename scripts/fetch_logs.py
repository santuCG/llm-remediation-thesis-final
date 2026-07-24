import urllib.request
import json
import os
import sys

TOKEN = "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"
REPO = "santuCG/llm-remediation-thesis-final"

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
            print(f"Job {job['name']} failed.")
            print(f"Log URL: {job['html_url']}")
            # The GitHub API for job logs: /repos/{owner}/{repo}/actions/jobs/{job_id}/logs
            log_api_url = f"https://api.github.com/repos/{REPO}/actions/jobs/{job['id']}/logs"
            print(f"\n--- LOGS for {job['name']} ---")
            print(get_logs(log_api_url))
            break

if __name__ == '__main__':
    main()
