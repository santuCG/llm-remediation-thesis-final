with open('logs.txt', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if 'npm install' in l or 'Phase 10' in l or 'overrides' in l:
            print(f'{i}: {l.strip()[:100]}')
