# Reproducibility Verification Evidence

This directory contains fresh CI runs of all 18 scenarios' baseline (Syft/Grype) pipeline, dispatched via GitHub Actions after two reproducibility fixes:

1. Pinning the Juice Shop frontend's npm dependencies (previously unpinned).
2. Excluding `**/bin` from Syft's scan scope (previously scanning the scanner's own binary).

**This is a separate verification pass — it does not replace or modify `results/execution_evidence/`.** Every file in this directory was generated after both fixes were applied, and is provided as direct evidence that the pipeline produces deterministic, internally-consistent results across all 18 scenarios.
