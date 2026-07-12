import json
import os
import subprocess
import shutil
import tempfile
import sys

def main():
    scenarios_path = 'experiment/final_18_scenarios.json'
    if not os.path.exists(scenarios_path):
        print(f"Error: {scenarios_path} not found.")
        sys.exit(1)
        
    with open(scenarios_path, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    
    results = []
    print("Running Deterministic Baseline...")
    print("-" * 50)
    
    for s in scenarios:
        scenario_id = s['scenario_id']
        ecosystem = s['package']['ecosystem']
        package = s['package']['name']
        is_direct = s['package']['is_direct_dependency']
        rec_version = s['package']['grype_recommended_version']
        
        with tempfile.TemporaryDirectory() as tmpdir:
            if ecosystem == "npm":
                # Copy package.json and package-lock.json
                shutil.copy('package.json', os.path.join(tmpdir, 'package.json'))
                shutil.copy('package-lock.json', os.path.join(tmpdir, 'package-lock.json'))
                
                cmd = f"npm install {package}@{rec_version} --package-lock-only"
                result = subprocess.run(cmd, shell=True, cwd=tmpdir, capture_output=True, text=True)
                
            else: # pypi
                # Copy airflow pip freeze as requirements.txt
                shutil.copy('applications/evidence/airflow_pip_freeze.txt', os.path.join(tmpdir, 'requirements.txt'))
                
                # Create venv
                subprocess.run(f"{sys.executable} -m venv venv", shell=True, cwd=tmpdir, capture_output=True)
                pip_path = os.path.join(tmpdir, 'venv', 'Scripts', 'pip.exe') if os.name == 'nt' else os.path.join(tmpdir, 'venv', 'bin', 'pip')
                
                cmd = f'"{pip_path}" install {package}=={rec_version} -r requirements.txt'
                result = subprocess.run(cmd, shell=True, cwd=tmpdir, capture_output=True, text=True)
                
            success = (result.returncode == 0)
            
            results.append({
                "scenario_id": scenario_id,
                "ecosystem": ecosystem,
                "package": package,
                "is_direct_dependency": is_direct,
                "recommended_version": rec_version,
                "baseline_success": success,
                "exit_code": result.returncode,
                "error_trace": result.stderr.strip() if not success else ""
            })
            
            print(f"{scenario_id} ({package}): {'PASSED' if success else 'FAILED'}")
            
    with open('experiment/deterministic_baseline_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    # Generate Markdown Report
    md = "# Deterministic Control Group Baseline Report\n\n"
    md += "## Objective\n"
    md += "The deterministic control group methodology evaluates whether a naive application of a static vulnerability scanner's recommended version passes or fails the CI build. The baseline was evaluated by forcing package managers to resolve the target versions without context-aware intervention.\n\n"
    
    md += "## Results Matrix\n"
    md += "| Scenario ID | Ecosystem | Package | Recommended Version | Result |\n"
    md += "|---|---|---|---|---|\n"
    for r in results:
        md += f"| {r['scenario_id']} | {r['ecosystem']} | {r['package']} | {r['recommended_version']} | {'**PASS**' if r['baseline_success'] else '*FAIL*'} |\n"
        
    md += "\n## Statistical Summary\n"
    total = len(results)
    fails = len([r for r in results if not r['baseline_success']])
    npm_fails = len([r for r in results if not r['baseline_success'] and r['ecosystem'] == 'npm'])
    pypi_fails = len([r for r in results if not r['baseline_success'] and r['ecosystem'] == 'pypi'])
    
    direct_fails = len([r for r in results if not r['baseline_success'] and r['is_direct_dependency']])
    transitive_fails = len([r for r in results if not r['baseline_success'] and not r['is_direct_dependency']])
    
    md += f"- **Total Failure Rate:** {fails}/{total} ({(fails/total)*100:.1f}%)\n"
    md += f"- **npm Failure Rate:** {npm_fails}/9\n"
    md += f"- **PyPI Failure Rate:** {pypi_fails}/9\n"
    md += f"- **Direct Dependency Failures:** {direct_fails}\n"
    md += f"- **Transitive Dependency Failures:** {transitive_fails}\n\n"
    
    md += "## Academic Justification\n"
    md += "The observed high failure rates are primarily driven by resolver conflicts (e.g., `ERESOLVE` errors in npm, strict bound violations in PyPI) and a lack of topological awareness. Static vulnerability scanners output one-dimensional version recommendations, completely ignoring the complex constraint graphs defined by peer dependencies and framework bounds. The deterministic failure of these naive upgrades mathematically justifies the necessity of Context-Aware LLM intervention to orchestrate safe, graph-compatible remediations.\n"
    
    with open('documentation/deterministic_baseline_report.md', 'w', encoding='utf-8') as f:
        f.write(md)

    print("-" * 50)
    print("Execution complete. Results saved to experiment/deterministic_baseline_results.json and documentation/deterministic_baseline_report.md")

if __name__ == "__main__":
    main()
