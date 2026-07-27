import subprocess
import os
import json

def get_context(ecosystem, package_name, app_dir):
    context = {}
    print(f"[CONTEXT] Building context for {package_name} in {ecosystem}...")
    
    # Switch to app dir to run commands
    original_dir = os.getcwd()
    os.chdir(app_dir)
    
    try:
        if ecosystem == 'npm':
            # npm ls --json
            try:
                ls_out = subprocess.check_output(['npm', 'ls', package_name, '--json'], text=True, stderr=subprocess.STDOUT)
                context['npm_ls'] = json.loads(ls_out)
            except subprocess.CalledProcessError as e:
                try:
                    context['npm_ls'] = json.loads(e.output)
                except:
                    context['npm_ls'] = e.output
                    
            # npm explain
            try:
                explain_out = subprocess.check_output(['npm', 'explain', package_name, '--json'], text=True, stderr=subprocess.STDOUT)
                context['npm_explain'] = json.loads(explain_out)
            except Exception as e:
                context['npm_explain'] = str(e)
                
            # Read package.json
            if os.path.exists('package.json'):
                with open('package.json', 'r') as f:
                    pkg_json = json.load(f)
                    pkg_json.pop('scripts', None)
                    context['package_json'] = pkg_json
                    
        elif ecosystem == 'python':
            pip_show_content = ""
            # pip show
            try:
                show_out = subprocess.check_output(['pip', 'show', package_name], text=True, stderr=subprocess.STDOUT)
                context['pip_show'] = show_out
                pip_show_content = show_out
            except Exception as e:
                context['pip_show'] = str(e)
                
            # Parse relevant packages (direct dependencies and direct consumers)
            relevant_pkgs = {package_name.lower()}
            for line in pip_show_content.splitlines():
                if line.lower().startswith("requires:"):
                    parts = line.split(":", 1)[1].split(",")
                    for p in parts:
                        if p.strip():
                            relevant_pkgs.add(p.strip().lower())
                elif line.lower().startswith("required-by:"):
                    parts = line.split(":", 1)[1].split(",")
                    for p in parts:
                        if p.strip():
                            relevant_pkgs.add(p.strip().lower())
            
            # pip freeze (filtered snippet only)
            try:
                freeze_out = subprocess.check_output(['pip', 'freeze'], text=True, stderr=subprocess.STDOUT)
                filtered_freeze = []
                for f_line in freeze_out.splitlines():
                    f_pkg = f_line.split("==")[0].strip().lower()
                    if f_pkg in relevant_pkgs:
                        filtered_freeze.append(f_line)
                context['pip_freeze'] = "\n".join(filtered_freeze)
            except Exception as e:
                context['pip_freeze'] = str(e)
                
            # Read requirements.txt (filtered snippet only)
            if os.path.exists('requirements.txt'):
                with open('requirements.txt', 'r') as f:
                    req_content = f.read()
                    filtered_req = []
                    for r_line in req_content.splitlines():
                        clean_r_line = r_line.strip()
                        if not clean_r_line or clean_r_line.startswith("#"):
                            continue
                        r_pkg = clean_r_line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip().lower()
                        if r_pkg in relevant_pkgs or any(p in clean_r_line.lower() for p in relevant_pkgs):
                            filtered_req.append(r_line)
                    context['requirements_txt'] = "\n".join(filtered_req)
                    
    finally:
        os.chdir(original_dir)
        
    return context
