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
                
            patch = recommendation.get('manifest_patch', '{}')
            try:
                patch_json = json.loads(patch)
                # Naive merge for overrides/resolutions
                for key, val in patch_json.items():
                    if isinstance(val, dict):
                        pkg[key] = pkg.get(key, {})
                        pkg[key].update(val)
                    else:
                        pkg[key] = val
            except json.JSONDecodeError:
                print("[ERROR] manifest_patch is not valid JSON. Rejecting LLM response.")
                raise ValueError("manifest_patch must be valid JSON.")
                
            with open('package.json', 'w') as f:
                json.dump(pkg, f, indent=2)
                
            # Save after state
            shutil.copy2('package.json', os.path.join(original_dir, 'package-after.json'))
            
        elif ecosystem == 'python':
            # Save before state
            if os.path.exists('requirements.txt'):
                shutil.copy2('requirements.txt', os.path.join(original_dir, 'package-before.json')) # using generic name
                
            patch = recommendation.get('manifest_patch', '')
            with open('requirements.txt', 'a') as f:
                f.write(f"\n{patch}\n")
                
            # Save after state
            shutil.copy2('requirements.txt', os.path.join(original_dir, 'package-after.json'))
            
        print("[MANIFEST] Successfully applied remediation to manifest.")
    finally:
        os.chdir(original_dir)
