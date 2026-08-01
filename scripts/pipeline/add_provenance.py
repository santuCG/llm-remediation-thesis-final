import yaml
import os

for path in [".github/workflows/templates/npm-remediation.yml", ".github/workflows/templates/python-remediation.yml"]:
    with open(path, "r") as f:
        content = f.read()
    
    provenance_script = """
      - name: Build Provenance Bundle
        if: always()
        run: |
          mkdir provenance
          cp ${{ inputs.profile }} provenance/profile.yaml || true
          cp .github/workflows/templates/${{ github.job }}.yml provenance/workflow.yml || true
          cp evidence/scenario-manifest.json provenance/manifest.json || true
          cp evidence/pipeline-summary.json provenance/pipeline-summary.json || true
          env > provenance/environment.txt
          echo '{"node": "${{ env.NODE_VERSION }}", "python": "${{ env.PYTHON_VERSION }}", "syft": "${{ env.SYFT_VERSION }}", "grype": "${{ env.GRYPE_VERSION }}"}' > provenance/tool_versions.json
"""
    if "Build Provenance Bundle" not in content:
        content = content.replace("      - name: Upload Remediation Evidence", provenance_script + "\n      - name: Upload Remediation Evidence")
        content = content.replace("path: evidence/", "path: |\n            evidence/\n            provenance/")

    with open(path, "w") as f:
        f.write(content)
