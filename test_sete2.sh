
set -e
ECOSYSTEM="npm"
if [ "$ECOSYSTEM" == "python" ]; then
  cp ../evidence/airflow_pip_freeze.txt requirements.txt
elif [ "$ECOSYSTEM" == "npm" ]; then
  cp ../evidence/package-before.json package.json
fi
cd ../..
echo "Survived!"

