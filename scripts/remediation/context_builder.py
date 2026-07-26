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
            # pip show
            try:
                show_out = subprocess.check_output(['pip', 'show', package_name], text=True, stderr=subprocess.STDOUT)
                context['pip_show'] = show_out
            except Exception as e:
                context['pip_show'] = str(e)
                
            # pip freeze
            try:
                freeze_out = subprocess.check_output(['pip', 'freeze'], text=True, stderr=subprocess.STDOUT)
                context['pip_freeze'] = freeze_out
            except Exception as e:
                context['pip_freeze'] = str(e)
                
            # Read requirements.txt
            if os.path.exists('requirements.txt'):
                with open('requirements.txt', 'r') as f:
                    context['requirements_txt'] = f.read()
                    
    finally:
        os.chdir(original_dir)
        
    return context
