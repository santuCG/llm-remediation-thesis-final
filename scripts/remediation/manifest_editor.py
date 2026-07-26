import json
import os
import shutil

def apply_remediation(ecosystem, app_dir, recommendation):
    print(f"[MANIFEST] Applying recommendation for {ecosystem}...")
    
    original_dir = os.getcwd()
    os.chdir(app_dir)
    
    try:
        if ecosystem == 'npm':
            # Save before state
            shutil.copy2('package.json', os.path.join(original_dir, 'package-before.json'))
            
            with open('package.json', 'r') as f:
                pkg = json.load(f)
                
            patch = recommendation.get('manifest_patch', {})
            if not isinstance(patch, dict) or 'operation' not in patch:
                raise ValueError("manifest_patch must be a structured dictionary.")
                
            op = patch.get('operation')
            target_pkg = patch.get('package')
            constraint = patch.get('constraint')
            
            if op == 'add_override' or op == 'transitive_override':
                pkg['overrides'] = pkg.get('overrides', {})
                pkg['overrides'][target_pkg] = constraint
            elif op in ['replace', 'bump', 'direct_upgrade']:
                # Update in dependencies or devDependencies if it exists
                if 'dependencies' in pkg and target_pkg in pkg['dependencies']:
                    pkg['dependencies'][target_pkg] = constraint
                elif 'devDependencies' in pkg and target_pkg in pkg['devDependencies']:
                    pkg['devDependencies'][target_pkg] = constraint
                else:
                    pkg['dependencies'] = pkg.get('dependencies', {})
                    pkg['dependencies'][target_pkg] = constraint
            else:
                print(f"[WARNING] Unknown operation {op}, attempting fallback override.")
                pkg['overrides'] = pkg.get('overrides', {})
                pkg['overrides'][target_pkg] = constraint
                
            with open('package.json', 'w') as f:
                json.dump(pkg, f, indent=2)
                
            # Save after state
            shutil.copy2('package.json', os.path.join(original_dir, 'package-after.json'))
            
        elif ecosystem == 'python':
            # Save before state
            if os.path.exists('requirements.txt'):
                shutil.copy2('requirements.txt', os.path.join(original_dir, 'package-before.json')) # using generic name
                
            patch = recommendation.get('manifest_patch', {})
            target_pkg = patch.get('package')
            constraint = patch.get('constraint', '')
            
            if constraint and constraint[0].isdigit():
                constraint_str = f"=={constraint}"
            else:
                constraint_str = constraint
                
            with open('requirements.txt', 'a') as f:
                f.write(f"\n{target_pkg}{constraint_str}\n")
                
            # Save after state
            shutil.copy2('requirements.txt', os.path.join(original_dir, 'package-after.json'))
            
        print("[MANIFEST] Successfully applied remediation to manifest.")
    finally:
        os.chdir(original_dir)
