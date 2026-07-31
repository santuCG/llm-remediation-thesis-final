import time
import urllib.request
import json
import os
import sys

TOKEN = os.environ["GITHUB_TOKEN"]
REPO = "santuCG/llm-remediation-thesis-final"

class NoAuthRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req:
            if 'Authorization' in new_req.headers:
                del new_req.headers['Authorization']
            if 'authorization' in new_req.unredirected_hdrs:
                del new_req.unredirected_hdrs['authorization']
        return new_req

opener = urllib.request.build_opener(NoAuthRedirectHandler())
urllib.request.install_opener(opener)

def main():
    while True:
        req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/actions/runs?per_page=1')
        req.add_header('Authorization', f'Bearer {TOKEN}')
        req.add_header('Accept', 'application/vnd.github.v3+json')
        try:
            with urllib.request.urlopen(req) as response:
                run = json.loads(response.read())['workflow_runs'][0]
        except Exception as e:
            print("Error checking status:", e)
            time.sleep(30)
            continue
            
        status = run['status']
        print(f"Status: {status}")
        
        if status in ('completed', 'success', 'failure', 'cancelled', 'timed_out'):
            print(f"Pipeline completed with conclusion: {run['conclusion']}")
            break
            
        time.sleep(30)
        
    print("Fetching logs...")
    req = urllib.request.Request(run['jobs_url'])
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    try:
        with urllib.request.urlopen(req) as response:
            jobs = json.loads(response.read())['jobs']
            for job in jobs:
                log_url = f"https://api.github.com/repos/{REPO}/actions/jobs/{job['id']}/logs"
                req_log = urllib.request.Request(log_url)
                req_log.add_header('Authorization', f'Bearer {TOKEN}')
                req_log.add_header('Accept', 'application/vnd.github.v3+json')
                with urllib.request.urlopen(req_log) as response_log:
                    with open('logs.txt', 'wb') as f:
                        f.write(response_log.read())
                print("Logs saved to logs.txt")
                break
    except Exception as e:
        print("Failed to fetch logs:", e)

if __name__ == '__main__':
    main()
