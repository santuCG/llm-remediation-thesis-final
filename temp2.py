with open('logs.txt', encoding='utf-8') as f:
    lines = f.readlines()
    start=1000
    end=1020
    for l in lines[start:end]: print(l.strip())
