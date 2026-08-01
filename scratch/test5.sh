
cd scratch
mkdir test5
cd test5
cp ../../applications/juice-shop/package.json .
cp ../../applications/juice-shop/package-lock.json .
npm ci --ignore-scripts
node -e "let p=require('./package.json'); p.overrides={'body-parser': '^1.20.3'}; require('fs').writeFileSync('package.json', JSON.stringify(p, null, 2))"
npm install --ignore-scripts

