import json
import sys
import os
import re
import subprocess


def _version_tuple(version):
    """Parse a dotted version string into a comparable tuple of ints, falling
    back to string comparison for any non-numeric component (e.g. pre-release
    suffixes like '1.4.5-lts.1'). Best-effort, not a full semver/PEP440
    parser -- sufficient for comparing two release versions of the same
    package."""
    parts = re.split(r'[.\-+]', version)
    out = []
    for p in parts:
        out.append(int(p) if p.isdigit() else p)
    return tuple(out)


def _version_at_least(installed, expected):
    """True if installed >= expected as a version comparison, not a string
    comparison -- an installed version can legitimately be a newer, still-safe
    patch/minor release than the LLM's specific recommendation (e.g. a caret
    range resolving to 1.20.6 when 1.20.3 was recommended), and that is a
    correct outcome, not an unverified one."""
    if installed == expected:
        return True
    try:
        it, et = _version_tuple(installed), _version_tuple(expected)
        # Compare element-wise; mismatched types (int vs str) at the same
        # position can't be meaningfully ordered -- treat as not-comparable
        # and fall through to the exact-match result already computed above.
        for a, b in zip(it, et):
            if type(a) is not type(b):
                return False
            if a != b:
                return a > b
        return len(it) >= len(et)
    except (ValueError, TypeError):
        return False


def _npm_tree_contains_version(node, package_name, expected_version, _depth=0):
    """Recursively search an `npm ls --json` tree for package_name resolved to
    expected_version or newer, at any depth (the vulnerable instance may be
    transitive)."""
    if _depth > 20 or not isinstance(node, dict):
        return False
    deps = node.get('dependencies', {})
    for name, info in deps.items():
        if name == package_name and info.get('version') and _version_at_least(info['version'], expected_version):
            return True
        if _npm_tree_contains_version(info, package_name, expected_version, _depth + 1):
            return True
    return False


def verify_dependency_installed(ecosystem, package_name, expected_version):
    """Independent check that the actual installed/resolved dependency graph
    contains package_name at expected_version, using the package manager's
    own resolution (npm ls / pip show). This does not look at the rescan
    result at all -- it is a separate signal from rescan_success, not a
    duplicate of it."""
    if not package_name or not expected_version:
        return False
    try:
        if ecosystem == 'npm':
            result = subprocess.run(
                ['npm', 'ls', package_name, '--json', '--all'],
                capture_output=True, text=True, timeout=60
            )
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError:
                return False
            return _npm_tree_contains_version(data, package_name, expected_version)
        elif ecosystem == 'python':
            result = subprocess.run(
                ['pip', 'show', package_name],
                capture_output=True, text=True, timeout=30
            )
            for line in result.stdout.splitlines():
                if line.startswith('Version:'):
                    return _version_at_least(line.split(':', 1)[1].strip(), expected_version)
            return False
    except Exception as e:
        print(f"[VALIDATOR] Dependency verification check failed: {e}")
        return False
    return False


def validate_remediation(grype_json_path, target_cve_id, metrics_path=None,
                          ecosystem=None, package_name=None, expected_version=None):
    try:
        with open(grype_json_path, 'r') as f:
            data = json.load(f)

        matches = data.get('matches', [])
        found = False
        for match in matches:
            vuln_id = match.get('vulnerability', {}).get('id', '')
            related = [r.get('id', '') for r in match.get('relatedVulnerabilities', [])]

            if vuln_id == target_cve_id or target_cve_id in related:
                print(f"[VALIDATOR] FAILED: {target_cve_id} is still present.")
                found = True
                break

        if not found:
            print(f"[VALIDATOR] SUCCESS: {target_cve_id} has been eradicated.")
            if metrics_path and os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    metrics = json.load(f)
                metrics["rescan_success"] = True
                # dependency_verified is an independent check of the actual
                # installed dependency graph (npm ls / pip show) against the
                # expected package/version -- not inferred from rescan_success.
                dep_verified = verify_dependency_installed(ecosystem, package_name, expected_version)
                metrics["dependency_verified"] = dep_verified
                print(f"[VALIDATOR] Dependency verification (independent of rescan): {dep_verified}")
                # NOTE: build_success is NOT set here. It must have been set by the
                # workflow's build step before reaching this validator. Setting it
                # implicitly here would mask genuine build failures.
                # build_success is set to True by the workflow's "Apply Fix" step
                # exiting with code 0. If that step failed, the pipeline would have
                # halted before reaching this validator.
                metrics["validation_stage_reached"] = "validator"
                with open(metrics_path, 'w') as f:
                    json.dump(metrics, f, indent=2)
            return True
        else:
            if metrics_path and os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    metrics = json.load(f)
                metrics["rescan_success"] = False
                metrics["failure_stage"] = "validator"
                metrics["validation_stage_reached"] = "validator"
                with open(metrics_path, 'w') as f:
                    json.dump(metrics, f, indent=2)
            return False
    except Exception as e:
        print(f"[ERROR] Validator failed to read JSON: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python validator.py <grype_json> <cve_id> [metrics_json] [ecosystem] [package_name] [expected_version]")
        sys.exit(1)

    metrics_file = sys.argv[3] if len(sys.argv) > 3 else None
    ecosystem_arg = sys.argv[4] if len(sys.argv) > 4 else None
    package_name_arg = sys.argv[5] if len(sys.argv) > 5 else None
    expected_version_arg = sys.argv[6] if len(sys.argv) > 6 else None

    success = validate_remediation(sys.argv[1], sys.argv[2], metrics_file,
                                    ecosystem_arg, package_name_arg, expected_version_arg)
    if not success:
        sys.exit(1)
