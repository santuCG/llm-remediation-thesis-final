lines = open('logs.txt', encoding='utf-8').readlines()
in_llm=False
for l in lines:
    if '=== LLM RAW RESPONSE ===' in l:
        in_llm=True
    if in_llm:
        print(l.strip())
    if '*********************************************' in l:
        break
