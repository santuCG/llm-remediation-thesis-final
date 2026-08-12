#!/bin/bash
# Shared build validation for every npm execution path in this repository:
# generic-remediation.yml's first attempt and retry, and grype-baseline.yml's
# single build step. One implementation instead of duplicated, drift-prone
# copies of the same "did the actual npm build succeed" check.
#
# Runs the application's own build:frontend / build:server / build scripts
# (whichever are defined in package.json).
#
# Usage: check_npm_build.sh <app_dir> <metrics_json_path> <build_log_path> [--fatal]
#
# Default (non-fatal) mode -- used by generic-remediation.yml:
#   Sets metrics.json's build_success = false if any build script fails, and
#   always exits 0 so the calling step continues (that pipeline runs tests
#   and rescan even after a failed build, to gather complete evidence). It
#   never sets build_success = true itself -- that remains the responsibility
#   of the preceding install step, unchanged.
#
# --fatal mode -- used by grype-baseline.yml:
#   Does NOT write metrics.json itself. Exits 1 if any build script fails, so
#   the calling step aborts immediately under GitHub Actions' default `set -e`
#   -- preserving that workflow's pre-existing behavior of never running
#   tests after a failed build, and of relying on its own separate
#   "Update Metrics on Build Failure" step (unchanged) to record
#   build_success/test_success/validation_success/failure_stage together.
set -u

APP_DIR="$1"
METRICS_PATH="$2"
BUILD_LOG_PATH="$3"
MODE="${4:-}"

cd "$APP_DIR" || exit 1

BUILD_FAILED=0
for script_name in build:frontend build:server build; do
  if jq -e ".scripts[\"$script_name\"]" package.json > /dev/null 2>&1; then
    npm run "$script_name" 2>&1 | tee -a "$BUILD_LOG_PATH"
    if [ "${PIPESTATUS[0]}" -ne 0 ]; then
      echo "[BUILD CHECK] npm run $script_name failed."
      BUILD_FAILED=1
    fi
  fi
done

if [ "$BUILD_FAILED" -eq 1 ]; then
  if [ "$MODE" == "--fatal" ]; then
    echo "[BUILD CHECK] Build failed (fatal mode) -- exiting non-zero for the caller's own failure handling."
    exit 1
  fi
  jq '.build_success = false' "$METRICS_PATH" > "${METRICS_PATH}.tmp" && mv "${METRICS_PATH}.tmp" "$METRICS_PATH"
  echo "[BUILD CHECK] build_success set to false (compile step failed)."
else
  echo "[BUILD CHECK] All defined build scripts succeeded; build_success left unchanged."
fi
