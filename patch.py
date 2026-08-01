import re

with open('.github/workflows/baseline-npm-remediation.yml', 'r') as f:
    npm = f.read()

npm_inject = '''      - name: Validate Baseline Functionality
        run: |
          cd ${{ env.APP_DIR }}
          echo "Validating application functionality..." 2>&1 | tee -a ../../baseline-build.log
          if jq -e '.scripts["build:frontend"]' package.json > /dev/null 2>&1; then npm run build:frontend 2>&1 | tee -a ../../baseline-build.log; fi
          if jq -e '.scripts["build:server"]' package.json > /dev/null 2>&1; then npm run build:server 2>&1 | tee -a ../../baseline-build.log; fi
          if jq -e '.scripts["build"]' package.json > /dev/null 2>&1; then npm run build 2>&1 | tee -a ../../baseline-build.log; fi
          if jq -e '.scripts["test"]' package.json > /dev/null 2>&1; then
            npm test 2>&1 | tee ../../baseline-test.log || true
          fi

'''

npm = re.sub(r'(?m)^\s+- name: Build Provenance Bundle', npm_inject + '      - name: Build Provenance Bundle', npm)
npm = re.sub(r'(?m)^\s+dependency_install.log', '            dependency_install.log\n            baseline-build.log\n            baseline-test.log', npm)

with open('.github/workflows/baseline-npm-remediation.yml', 'w') as f:
    f.write(npm)


with open('.github/workflows/baseline-python-remediation.yml', 'r') as f:
    py = f.read()

py_inject = '''      - name: Validate Baseline Functionality
        run: |
          cd ${{ env.APP_DIR }}
          echo "Validating application functionality..." 2>&1 | tee -a ../../baseline-build.log
          if [ -d "tests/core" ]; then
            pip install pytest==7.4.4 pytest-asyncio sentry-sdk || true
            python3 -m pytest tests/core 2>&1 | tee ../../baseline-test.log || true
          fi

'''

py = re.sub(r'(?m)^\s+- name: Build Provenance Bundle', py_inject + '      - name: Build Provenance Bundle', py)
py = re.sub(r'(?m)^\s+dependency_install.log', '            dependency_install.log\n            baseline-build.log\n            baseline-test.log', py)

with open('.github/workflows/baseline-python-remediation.yml', 'w') as f:
    f.write(py)
