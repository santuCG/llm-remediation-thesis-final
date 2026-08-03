#!/bin/bash
# Shared build_success check for npm scenarios, used identically by both the
# first attempt ("Validate Remediation & Rescan") and the retry path
# ("Retry Remediation Strategy") so build_success has one consistent
# definition regardless of which attempt produced it.
#
# Runs the application's own build:frontend / build:server / build scripts
# (whichever are defined in package.json) and sets metrics.json's
# build_success = false if any of them actually fails. It never sets
# build_success = true itself -- that remains the responsibility of the
# preceding install step, unchanged.
#
# Usage: check_npm_build.sh <app_dir> <metrics_json_path> <build_log_path>
set -u

APP_DIR="$1"
METRICS_PATH="$2"
BUILD_LOG_PATH="$3"

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
  jq '.build_success = false' "$METRICS_PATH" > "${METRICS_PATH}.tmp" && mv "${METRICS_PATH}.tmp" "$METRICS_PATH"
  echo "[BUILD CHECK] build_success set to false (compile step failed)."
else
  echo "[BUILD CHECK] All defined build scripts succeeded; build_success left unchanged."
fi
