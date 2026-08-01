import os
import sys
import json
import hashlib

def hash_file(path):
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def main():
    if len(sys.argv) < 3:
        print("Usage: python verify_artifacts.py <downloaded_dir> <local_dir>")
        sys.exit(1)

    downloaded_dir = sys.argv[1]
    local_dir = sys.argv[2]
    
    report = {
        "Downloaded": "YES",
        "SHA verified": "YES",
        "Manifest verified": "YES",
        "Missing files": 0,
        "Unexpected files": 0,
        "details": []
    }
    
    local_files = set(os.listdir(local_dir))
    downloaded_files = set(os.listdir(downloaded_dir))
    
    missing = local_files - downloaded_files
    unexpected = downloaded_files - local_files
    
    report["Missing files"] = len(missing)
    report["Unexpected files"] = len(unexpected)
    
    if missing or unexpected:
        report["SHA verified"] = "NO"
        
    for f in local_files.intersection(downloaded_files):
        local_path = os.path.join(local_dir, f)
        dl_path = os.path.join(downloaded_dir, f)
        
        if os.path.isfile(local_path) and os.path.isfile(dl_path):
            local_hash = hash_file(local_path)
            dl_hash = hash_file(dl_path)
            if local_hash != dl_hash:
                report["SHA verified"] = "NO"
                report["details"].append(f"Hash mismatch for {f}")
                
    if "scenario-manifest.json" not in downloaded_files:
        report["Manifest verified"] = "NO"
        report["details"].append("Missing scenario-manifest.json")
        
    with open("artifact-verification.json", "w") as out:
        json.dump(report, out, indent=2)

    print(json.dumps(report, indent=2))
    
if __name__ == "__main__":
    main()
