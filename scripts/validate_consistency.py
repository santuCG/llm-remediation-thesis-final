#!/usr/bin/env python3
"""
validate_consistency.py
=======================
Cross-checks all 18 scenario JSON files against their metrics.json ground truth.
Prints a PASS/FAIL for every check. All must PASS for submission.
"""
import json, os, sys

BASE = r'C:\Users\HP\Downloads\llm-remediation-thesis-final'
SCENARIOS_DIR = os.path.join(BASE, 'results', 'scenarios')
EVIDENCE_DIR  = os.path.join(BASE, 'results', 'execution_evidence')

ALL = ['AF-01','AF-02','AF-03','AF-04','AF-05','AF-06','AF-07','AF-08','AF-09',
       'JS-01','JS-02','JS-03','JS-04','JS-05','JS-06','JS-07','JS-08','JS-09']

errors = []
checks_passed = 0
checks_total  = 0

def check(condition, msg):
    global checks_passed, checks_total
    checks_total += 1
    if condition:
        checks_passed += 1
        print(f"  [PASS] {msg}")
    else:
        errors.append(msg)
        print(f"  [FAIL] {msg}")

def find_json_end(raw):
    bc = 0; ins = False; esc = False; je = 0
    for i, ch in enumerate(raw):
        if esc: esc = False; continue
        if ch == '\\' and ins: esc = True; continue
        if ch == '"' and not esc: ins = not ins
        if not ins:
            if ch == '{': bc += 1
            elif ch == '}':
                bc -= 1
                if bc == 0: je = i+1; break
    return je

for sid in ALL:
    print(f"\n--- {sid} ---")
    sp = os.path.join(SCENARIOS_DIR, f'{sid}.json')
    mp = os.path.join(EVIDENCE_DIR, sid, 'metrics.json')

    check(os.path.exists(sp), f"{sid}.json exists in results/scenarios/")

    if not os.path.exists(sp):
        continue

    with open(sp, 'r', encoding='utf-8') as f:
        raw = f.read()
    je = find_json_end(raw)
    try:
        scenario = json.loads(raw[:je])
    except json.JSONDecodeError as e:
        check(False, f"{sid}.json is valid JSON: {e}")
        continue

    check(True, f"{sid}.json is valid JSON")

    # Check scenario_id matches filename
    actual_sid = scenario.get('pre_registration',{}).get('scenario_metadata',{}).get('scenario_id','')
    check(actual_sid == sid, f"scenario_id field == '{sid}' (found: '{actual_sid}')")

    # Check status
    status = scenario.get('pre_registration',{}).get('scenario_metadata',{}).get('status','')
    expected_status = 'Completed' if sid != 'JS-09' else 'Pre-Registered — Evidence Pending'
    check(status == expected_status, f"status == '{expected_status}' (found: '{status}')")

    # No placeholder git commit (skip JS-09 which has no evidence folder)
    if sid != 'JS-09':
        git_commit = scenario.get('execution',{}).get('llm_pipeline',{}).get('git_commit','')
        check(git_commit not in ('e987f6d','a1b2c3d','placeholder',''), f"git_commit is not a placeholder (found: '{git_commit[:16]}...')")

    # Check no duplicate inline comments in empirical block
    empirical = raw[je:]
    if '=== EMPIRICAL EVIDENCE ===' in empirical:
        dup_found = False
        for line in empirical.split('\n'):
            if '//' in line:
                p = line.find('//')
                comment = line[p:]
                p2 = comment.find('//', 2)
                if p2 != -1 and comment[:p2].strip() == comment[p2:].strip():
                    dup_found = True
                    break
        check(not dup_found, "No duplicate inline comments in EMPIRICAL block")

    if not os.path.exists(mp):
        print(f"  [INFO] No metrics.json for {sid} (JS-09 has no evidence)")
        continue

    with open(mp, 'r') as f:
        metrics = json.load(f)

    # Check validation block matches metrics
    val = scenario.get('execution',{}).get('llm_pipeline',{}).get('validation',{})
    check(val.get('tests',{}).get('passed') == metrics.get('test_success'),
          f"tests.passed == metrics.test_success ({metrics.get('test_success')})")
    check(val.get('build',{}).get('passed') == metrics.get('build_success'),
          f"build.passed == metrics.build_success ({metrics.get('build_success')})")
    check(val.get('grype_rescan',{}).get('vulnerability_removed') == metrics.get('rescan_success'),
          f"vulnerability_removed == metrics.rescan_success ({metrics.get('rescan_success')})")

    # strategy/remediation_type consistency
    strat = metrics.get('strategy','')
    rtype = metrics.get('remediation_type','')
    check(bool(strat) and bool(rtype), f"strategy ('{strat}') and remediation_type ('{rtype}') are both set")

print(f"\n{'='*50}")
print(f"RESULTS: {checks_passed}/{checks_total} checks passed")
if errors:
    print(f"\nFAILED CHECKS:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED - Repository is internally consistent and ready for review.")
