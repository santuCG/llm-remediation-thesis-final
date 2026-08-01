
cd scratch
mkdir test4
cd test4
cp ../../applications/juice-shop/package.json .
node -e "let p=require('./package.json'); p.overrides={'body-parser': '^1.20.3'}; require('fs').writeFileSync('package.json', JSON.stringify(p, null, 2))"
npm install --ignore-scripts

