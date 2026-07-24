import urllib.request
import json
import os
import time
import sys

TOKEN = "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"
REPO = "santuCG/llm-remediation-thesis-final"

def get_latest_run():
    req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/actions/runs?per_page=1')
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            if not data['workflow_runs']:
                return None
            return data['workflow_runs'][0]
    except Exception as e:
        print(f"Error fetching runs: {e}")
        return None

def get_jobs(jobs_url):
    req = urllib.request.Request(jobs_url)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())['jobs']
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

def main():
    run = get_latest_run()
    if not run:
        print("No runs found.")
        sys.exit(1)
        
    print(f"Latest Run: {run['name']} (ID: {run['id']})")
    print(f"Status: {run['status']}")
    print(f"Conclusion: {run['conclusion']}")
    print(f"URL: {run['html_url']}")
    
    jobs = get_jobs(run['jobs_url'])
    for job in jobs:
        print(f"\nJob: {job['name']} - Status: {job['status']} - Conclusion: {job['conclusion']}")
        for step in job['steps']:
            print(f"  Step: {step['name']} - {step['status']} ({step['conclusion']})")
            
    if run['status'] == 'completed':
        sys.exit(0)
    else:
        sys.exit(2)

if __name__ == '__main__':
    main()
