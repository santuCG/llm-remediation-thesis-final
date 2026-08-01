# PHASE 6 — EVIDENCE DIRECTORY COMPLETENESS / CORRUPTION SWEEP

Swept all 18 `results/execution_evidence/*/` directories: file counts, JSON validity, zero-byte checks.

## File counts
17 of 18 scenarios have exactly 13 files (the standard schema). **AF-01 has 14** — an extra `pipeline_logs/` directory (raw CI log dump: `0_orchestrate-remediation.txt` + a subfolder), not present in any other scenario and not part of the documented evidence schema. Its file timestamp (`Jan 1 1980` on the inner .txt) is a known artifact of certain log-extraction tools, consistent with this being leftover debugging output rather than intentional experiment evidence. **Not modified** — flagged for your decision since it's inside the immutable evidence directory.

## JSON validity
All `.json` files parse correctly except AF-track `package-before.json`/`package-after.json` (18 files, all 9 AF scenarios), which fail JSON parsing — **this is expected, not corruption**: for the Python/pip track these files actually contain plain-text `pip freeze`-style `name==version` lines, not JSON, despite the `.json` extension. Confirmed by direct inspection of content. Worth a documentation note (misleading extension) but not a defect in the data itself.

## Zero-byte / missing content
None found.

## Known, already-documented gap re-confirmed unchanged
`JS-09/experiment_manifest.json` still has no `=== EMPIRICAL EVIDENCE ===` block (0 matches for the marker string), consistent with the original forensic-pass finding — unchanged because no JS-09 rerun has occurred. This remains a "requires rerun" item per your earlier direction to produce fresh JS-09 evidence in a separate branch; out of scope for this read-only completeness sweep.

## Verdict
No corruption found. One anomalous extra file (AF-01/pipeline_logs) and one pre-existing, already-tracked gap (JS-09). Both are pointers for your decision, not touched.
