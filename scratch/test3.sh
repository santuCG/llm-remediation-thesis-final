
cd scratch
mkdir test-eoverride3
cd test-eoverride3
npm init -y
npm install body-parser@1.20.2
node -e "let p=require('./package.json'); p.overrides={'body-parser': '^1.20.3'}; require('fs').writeFileSync('package.json', JSON.stringify(p, null, 2))"
npm install

