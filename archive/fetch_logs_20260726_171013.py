import urllib.request, json, os
TOKEN = os.environ["GITHUB_TOKEN"]

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

req = urllib.request.Request("https://api.github.com/repos/santuCG/llm-remediation-thesis-final/actions/runs")
req.add_header("Authorization", f"Bearer {TOKEN}")
with urllib.request.urlopen(req) as res:
    runs = json.loads(res.read())["workflow_runs"]
for run in runs:
    if run["name"] == "Generic LLM Remediation Pipeline":
        req_jobs = urllib.request.Request(run["jobs_url"])
        req_jobs.add_header("Authorization", f"Bearer {TOKEN}")
        with urllib.request.urlopen(req_jobs) as res_jobs:
            jobs = json.loads(res_jobs.read())["jobs"]
            for job in jobs:
                log_url = f"https://api.github.com/repos/santuCG/llm-remediation-thesis-final/actions/jobs/{job['id']}/logs"
                req_log = urllib.request.Request(log_url)
                req_log.add_header("Authorization", f"Bearer {TOKEN}")
                try:
                    with urllib.request.urlopen(req_log) as res_log:
                        with open("failed_log.txt", "wb") as f:
                            f.write(res_log.read())
                    print("Logs saved to failed_log.txt")
                except Exception as e:
                    print("Error fetching logs:", e)
        break
