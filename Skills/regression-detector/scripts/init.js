#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const cwd = process.cwd();
const regressionDir = path.join(cwd, '.regression');

console.log('🔍 Initializing Regression Detector...\n');

// Create .regression directory
if (!fs.existsSync(regressionDir)) {
  fs.mkdirSync(regressionDir, { recursive: true });
  console.log('✅ Created .regression/ directory');
}

// Create default config
const defaultConfig = {
  checks: {
    fileIntegrity: true,
    visualRegression: true,
    functionalTests: false,
    apiContract: false,
    performance: false
  },
  testCommand: null,
  devServerCommand: null,
  devServerUrl: null,
  criticalPaths: ['/'],
  ignorePatterns: [
    '*.log',
    '.cache/*',
    'node_modules/*',
    '.git/*',
    'dist/*',
    'build/*',
    '.regression/*'
  ],
  visualDiffThreshold: 0.05,
  performanceMargin: 0.2
};

const configPath = path.join(regressionDir, 'config.json');
if (!fs.existsSync(configPath)) {
  fs.writeFileSync(configPath, JSON.stringify(defaultConfig, null, 2));
  console.log('✅ Created .regression/config.json');
} else {
  console.log('ℹ️  Config already exists: .regression/config.json');
}

// Create README
const readme = `# Regression Detection

This directory contains baseline snapshots and configuration for regression detection.

## Files

- \`config.json\`: Configuration for regression checks
- \`baseline-*.json\`: Baseline snapshots
- \`screenshots/\`: Baseline UI screenshots
- \`diffs/\`: Visual diffs when regressions detected

## Usage

**Capture baseline:**
\`\`\`bash
node ~/Skills/regression-detector/scripts/capture-baseline.js
\`\`\`

**Check for regressions:**
\`\`\`bash
node ~/Skills/regression-detector/scripts/check-regression.js
\`\`\`

**Update baseline:**
\`\`\`bash
node ~/Skills/regression-detector/scripts/update-baseline.js
\`\`\`

## Integration

Add to your git hooks:
\`\`\`bash
# .git/hooks/pre-commit
node ~/Skills/regression-detector/scripts/check-regression.js
\`\`\`
`;

const readmePath = path.join(regressionDir, 'README.md');
fs.writeFileSync(readmePath, readme);
console.log('✅ Created .regression/README.md');

// Create .gitignore to keep baselines in git
const gitignorePath = path.join(regressionDir, '.gitignore');
const gitignoreContent = `# Keep baselines in git
!baseline-*.json
!screenshots/
!config.json
!README.md

# Ignore runtime artifacts
diffs/
*.tmp
`;
fs.writeFileSync(gitignorePath, gitignoreContent);
console.log('✅ Created .regression/.gitignore');

console.log('\n📋 Next steps:');
console.log('1. Update .regression/config.json with your project settings');
console.log('2. Get your app to a working state');
console.log('3. Run: node ~/Skills/regression-detector/scripts/capture-baseline.js');
console.log('4. After each change, run: node ~/Skills/regression-detector/scripts/check-regression.js');
