import sys
import json

def main():
    if len(sys.argv) < 3:
        print("Usage: python apply_graph_patch.py <package.json> <llm-response.json>")
        sys.exit(1)

    package_json_path = sys.argv[1]
    response_json_path = sys.argv[2]

    with open(response_json_path, 'r') as f:
        llm_response = json.load(f)

    patch = llm_response.get("manifest_patch", {})
    operation = patch.get("operation")
    package = patch.get("package")
    constraint = patch.get("constraint")

    if not operation or not package or not constraint:
        print("[ERROR] Invalid manifest_patch in llm response.")
        sys.exit(1)

    with open(package_json_path, 'r') as f:
        manifest = json.load(f)

    if operation == "add_override":
        if "overrides" not in manifest:
            manifest["overrides"] = {}
        manifest["overrides"][package] = constraint
    elif operation == "replace_dependency":
        if "dependencies" in manifest and package in manifest["dependencies"]:
            manifest["dependencies"][package] = constraint
        elif "devDependencies" in manifest and package in manifest["devDependencies"]:
            manifest["devDependencies"][package] = constraint
        else:
            if "dependencies" not in manifest:
                manifest["dependencies"] = {}
            manifest["dependencies"][package] = constraint
    elif operation == "add_resolution":
        if "resolutions" not in manifest:
            manifest["resolutions"] = {}
        manifest["resolutions"][package] = constraint
    elif operation == "bump_dependency":
        if "dependencies" in manifest and package in manifest["dependencies"]:
            manifest["dependencies"][package] = constraint
        elif "devDependencies" in manifest and package in manifest["devDependencies"]:
            manifest["devDependencies"][package] = constraint
        else:
            print(f"[WARN] Dependency {package} not found for bumping, adding to dependencies.")
            if "dependencies" not in manifest:
                manifest["dependencies"] = {}
            manifest["dependencies"][package] = constraint
    else:
        print(f"[ERROR] Unknown operation: {operation}")
        sys.exit(1)

    with open(package_json_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"[SUCCESS] Applied {operation} for {package} to {constraint}")

if __name__ == "__main__":
    main()
