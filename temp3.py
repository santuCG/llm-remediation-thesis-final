import json
data=json.loads(open('grype-scanner.json', encoding='utf-8').read())
for m in data['matches']:
  if m['vulnerability']['id'] in ('CVE-2023-32314', 'GHSA-whpj-8f3w-67p5'):
    print(json.dumps(m['artifact']['locations']))
