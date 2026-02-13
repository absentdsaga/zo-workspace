#!/bin/bash
# Initialize context guardian for a project

set -e

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

echo "🛡️  Initializing Context Guardian for: $PROJECT_DIR"

# Create .context/ directory for state management
mkdir -p .context

# Initialize state snapshot
cat > .context/state-snapshot.md << 'EOF'
# Project State Snapshot
*Last Updated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")*

## Current Working State
- Status: Initial setup
- Verified: Not yet tested

## Architecture
- Core stack: [To be determined]
- Key files: [To be listed]
- Critical dependencies: [To be documented]

## What Works and WHY
[To be documented after initial build]

## Do NOT Change
[To be documented as patterns emerge]

## Known Issues
- None yet

## Build History
1. $(date -u +"%Y-%m-%d %H:%M:%S UTC"): Project initialized
EOF

# Initialize decisions log
cat > .context/decisions.md << 'EOF'
# Architectural Decisions

## Decision Log
*Chronological record of key choices*

---

### Initial Setup
**Date:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Context:** Project initialization
**Decision:** Using Context Guardian for state management
**Rationale:** Prevent degradation across iterations

---
EOF

# Initialize verification checklist
cat > .context/verification-checklist.md << 'EOF'
# Verification Checklist

## Core Functionality Tests
- [ ] [To be added after initial build]

## Visual Tests (if applicable)
- [ ] [To be added if UI exists]

## Regression Tests
- [ ] [To be added as bugs are fixed]

## Performance Baselines
- [ ] [To be added if performance-critical]

## Last Verified
- Date: [Not yet verified]
- By: [Not yet verified]
- Result: [Pending]
EOF

# Create gitignore if needed
if [ -f .gitignore ]; then
    if ! grep -q ".context/" .gitignore; then
        echo "" >> .gitignore
        echo "# Context Guardian state files (keep these in git!)" >> .gitignore
        echo "# .context/" >> .gitignore
    fi
fi

# Create quick reference
cat > .context/README.md << 'EOF'
# Context Guardian State Files

This directory contains the "ground truth" state of the project.

**Always read these files before making changes.**

## Files

- `state-snapshot.md`: Current working state and architecture
- `decisions.md`: Why we made key choices
- `verification-checklist.md`: How to verify functionality

## Workflow

**Before changing anything:**
```bash
cat .context/state-snapshot.md
cat .context/decisions.md
```

**After making changes:**
1. Run verification checklist
2. Update state-snapshot.md
3. Document new decisions in decisions.md

## Emergency Recovery

If things break:
```bash
# Check last known good state
git log -p .context/state-snapshot.md

# See what changed
git diff HEAD~1 HEAD
```
EOF

echo "✅ Context Guardian initialized!"
echo ""
echo "📁 Created state files in .context/"
echo "   - state-snapshot.md"
echo "   - decisions.md"
echo "   - verification-checklist.md"
echo ""
echo "🎯 Next steps:"
echo "   1. Build your initial version"
echo "   2. Run: ./update-state.sh 'Initial build complete'"
echo "   3. Run: ./verify.sh to create baseline tests"
