
set -e -o pipefail
function mock_npm() {
    echo "npm error code EOVERRIDE"
    return 1
}
mock_npm 2>&1 | tee test_pipe.log || (echo "NPM Install Failed" && exit 1)
echo "This should not be reached"

