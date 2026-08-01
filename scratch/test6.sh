
cd scratch/test5
npm install 2>&1 | tee build.log || (echo "FAILED" && exit 1)
echo "SUCCEEDED"

