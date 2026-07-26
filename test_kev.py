import urllib.request
url = 'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as r:
        print("Mozilla/5.0 OK:", len(r.read()))
except Exception as e:
    print("Mozilla/5.0 ERROR:", e)

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
    with urllib.request.urlopen(req) as r:
        print("curl OK:", len(r.read()))
except Exception as e:
    print("curl ERROR:", e)
