lines = open('logs.txt', encoding='utf-8').readlines()
in_npm=False
for i, l in enumerate(lines):
    if 'gemini_remediation.py' in l:
        in_npm=True
        start = i
    if in_npm and 'Phase 11' in l:
        for line in lines[start:i]:
            print(line.strip())
        break
