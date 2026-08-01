import yaml

for s in ["JS-01", "JS-08", "JS-09"]:
    path = f"profiles/{s}.yaml"
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    
    data["tool_versions"]["syft"] = "v1.44.0"
    data["tool_versions"]["grype"] = "v0.112.0"
    
    with open(path, "w") as f:
        yaml.dump(data, f, sort_keys=False)
