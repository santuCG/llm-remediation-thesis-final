import glob
import os

for path in glob.glob(".github/workflows/*remediation.yml"):
    with open(path, "r") as f:
        content = f.read()
    
    filename = path.split("/")[-1]
    if "\\" in filename: # Windows
        filename = path.split("\\")[-1]
        
    content = content.replace(
        "cp .github/workflows/templates/${{ github.job }}.yml provenance/workflow.yml || true",
        f"cp .github/workflows/{filename} provenance/workflow.yml || true"
    )

    with open(path, "w") as f:
        f.write(content)
