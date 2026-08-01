import os

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        
    content = content.replace(
        "- name: Validate Remediation & Rescan\n        id: build_test\n        run:",
        "- name: Validate Remediation & Rescan\n        id: build_test\n        if: always()\n        run:"
    )
    
    content = content.replace(
        "- name: Golden Validation\n        run:",
        "- name: Golden Validation\n        if: always()\n        run:"
    )
    
    with open(filepath, 'w') as f:
        f.write(content)

patch_file('.github/workflows/npm-remediation.yml')
patch_file('.github/workflows/python-remediation.yml')
