import glob
import os

for path in glob.glob(".github/workflows/*remediation.yml"):
    with open(path, "r") as f:
        content = f.read()

    # Fix Syft
    content = content.replace(
        "curl -sSfL -o syft.tar.gz https://github.com/anchore/syft/releases/download/${{ env.SYFT_VERSION }}/syft_${{ env.SYFT_VERSION | replace('v', '') }}_linux_amd64.tar.gz",
        "SYFT_NO_V=${SYFT_VERSION#v}\n          curl -sSfL -o syft.tar.gz https://github.com/anchore/syft/releases/download/${SYFT_VERSION}/syft_${SYFT_NO_V}_linux_amd64.tar.gz"
    )

    # Fix Grype
    content = content.replace(
        "curl -sSfL -o grype.tar.gz https://github.com/anchore/grype/releases/download/${{ env.GRYPE_VERSION }}/grype_${{ env.GRYPE_VERSION | replace('v', '') }}_linux_amd64.tar.gz",
        "GRYPE_NO_V=${GRYPE_VERSION#v}\n          curl -sSfL -o grype.tar.gz https://github.com/anchore/grype/releases/download/${GRYPE_VERSION}/grype_${GRYPE_NO_V}_linux_amd64.tar.gz"
    )

    with open(path, "w") as f:
        f.write(content)
