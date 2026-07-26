import argparse
import json
import os
import sys

def update_python(package_name, version):
    manifest_file = 'requirements.txt'
    if not os.path.exists(manifest_file):
        print(f"[BASELINE] No {manifest_file} found.")
        return
        
    with open(manifest_file, 'r') as f:
        lines = f.readlines()
        
    pkg = package_name.lower()
    updated = False
    original_version = "unknown"
    
    new_lines = []
    for line in lines:
        if line.lower().startswith(pkg + '==') or line.lower().startswith(pkg + '>='):
            parts = line.strip().split('==')
            if len(parts) == 1:
                parts = line.strip().split('>=')
            if len(parts) > 1:
                original_version = parts[1]
                
            new_lines.append(f"{pkg}=={version}\n")
            updated = True
        else:
            new_lines.append(line)
            
    # As per baseline policy, if not found, we don't do complex insertion, we just append it
    # to mimic a naive override/replacement. Wait, no reasoning allowed, so if it's transitive, appending works.
    if not updated:
        new_lines.append(f"{pkg}=={version}\n")
        
    with open(manifest_file, 'w') as f:
        f.writelines(new_lines)
        
    record_evidence(package_name, original_version, version, manifest_file, "direct_replacement")
    print(f"[BASELINE] Applied Python update for {package_name} to {version}")

def update_npm(package_name, version):
    manifest_file = 'package.json'
    if not os.path.exists(manifest_file):
        print(f"[BASELINE] No {manifest_file} found.")
        return
        
    with open(manifest_file, 'r') as f:
        data = json.load(f)
        
    is_direct = False
    original_version = None
    
    for dep_type in ['dependencies', 'devDependencies', 'optionalDependencies']:
        if dep_type in data and package_name in data[dep_type]:
            original_version = data[dep_type][package_name]
            data[dep_type][package_name] = version
            is_direct = True
            
    if is_direct:
        application_method = "direct_replacement"
    else:
        if 'overrides' not in data:
            data['overrides'] = {}
        data['overrides'][package_name] = version
        application_method = "override_added"
        
    with open(manifest_file, 'w') as f:
        json.dump(data, f, indent=2)
        
    record_evidence(package_name, original_version, version, manifest_file, application_method)
    print(f"[BASELINE] Applied NPM update for {package_name} to {version} (Method: {application_method})")

def record_evidence(package, original_version, new_version, manifest_file, application_method):
    evidence = {
        "package": package,
        "original_version": original_version,
        "new_version": new_version,
        "manifest_file": manifest_file,
        "application_method": application_method
    }
    with open("../../baseline-patch.json", "w") as f:
        json.dump(evidence, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Deterministic baseline manifest updater")
    parser.add_argument('--ecosystem', required=True, choices=['npm', 'python'])
    parser.add_argument('--package', required=True)
    parser.add_argument('--version', required=True)
    
    args = parser.parse_args()
    
    if args.ecosystem == 'python':
        update_python(args.package, args.version)
    elif args.ecosystem == 'npm':
        update_npm(args.package, args.version)

if __name__ == '__main__':
    main()
