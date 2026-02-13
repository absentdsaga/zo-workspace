#!/bin/bash
# Initialize complete anti-degradation stack for a project

set -e

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

echo "🛡️  ANTI-DEGRADATION MASTER"
echo "============================"
echo ""
echo "Initializing complete stack for: $PROJECT_DIR"
echo ""

# 1. Initialize git if needed
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - baseline before anti-degradation setup"
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi
echo ""

# 2. Initialize Context Guardian
if [ ! -d .context ]; then
    echo "🧠 Initializing Context Guardian..."
    bash ~/Skills/context-guardian/scripts/init-project.sh
    echo "✅ Context Guardian ready"
else
    echo "✅ Context Guardian already initialized"
fi
echo ""

# 3. Initialize Regression Detector  
if [ ! -d .regression ]; then
    echo "🔍 Initializing Regression Detector..."
    node ~/Skills/regression-detector/scripts/init.js
    echo "✅ Regression Detector ready"
else
    echo "✅ Regression Detector already initialized"
fi
echo ""

# 4. Create iteration log
if [ ! -f .context/iteration-log.txt ]; then
    echo "# Iteration Log" > .context/iteration-log.txt
    echo "$(date -u +"%Y-%m-%d %H:%M:%S UTC"): Anti-degradation stack initialized" >> .context/iteration-log.txt
    echo "✅ Iteration log created"
fi
echo ""

# 5. Create quick reference
cat > .context/QUICK-REFERENCE.md << 'EOF'
# Anti-Degradation Quick Reference

## Before Making Changes

```bash
# Read current state
cat .context/state-snapshot.md
cat .context/decisions.md

# Run pre-flight check
bash ~/Skills/context-guardian/scripts/pre-flight.sh
```

## Making Changes

**ONE change at a time!**

```bash
# 1. Checkpoint current state
git add -A && git commit -m "checkpoint: before [change description]"

# 2. Make ONE change

# 3. Test immediately
npm run dev  # or your test command

# 4. Commit if works, revert if breaks
git add -A && git commit -m "feat: [what changed]"
# OR
git checkout .  # revert
```

## After Changes

```bash
# Check for regressions
node ~/Skills/regression-detector/scripts/check-regression.js

# Update state
bash ~/Skills/context-guardian/scripts/update-state.sh "Session complete"
```

## When Things Break

```bash
# Emergency recovery
bash ~/Skills/context-guardian/scripts/recovery.sh

# See what changed
git log --oneline -10
git diff HEAD~3 HEAD

# Rollback to last good commit
git log --oneline  # find good commit hash
git checkout [hash]
```

## Capturing Baselines

```bash
# After each working build
node ~/Skills/regression-detector/scripts/capture-baseline.js
```

## Files to Read

- `.context/state-snapshot.md` - Current working state
- `.context/decisions.md` - Why we made choices
- `.context/verification-checklist.md` - How to verify
- `.regression/config.json` - Regression detection config
EOF
echo "✅ Quick reference created: .context/QUICK-REFERENCE.md"
echo ""

# 6. Commit the setup
git add .context .regression
git commit -m "feat: initialize anti-degradation stack

- Context Guardian for state management
- Regression Detector for verification
- Iteration protocol enforcement
" || echo "ℹ️  No changes to commit"

echo ""
echo "🎯 SETUP COMPLETE!"
echo ""
echo "📚 What was created:"
echo "   .context/           - State management files"
echo "   .regression/        - Baseline snapshots"
echo "   .context/QUICK-REFERENCE.md - How to use"
echo ""
echo "🚀 Next steps:"
echo "   1. Build your first working version"
echo "   2. Capture baseline: node ~/Skills/regression-detector/scripts/capture-baseline.js"
echo "   3. Work normally - system will auto-activate as needed"
echo ""
echo "💡 Quick reference:"
echo "   cat .context/QUICK-REFERENCE.md"
