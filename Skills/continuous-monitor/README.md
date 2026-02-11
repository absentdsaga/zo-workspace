# Continuous Monitor — Quick Start

## ⚡ Usage

### Before claiming any task is complete:

```bash
/home/workspace/Skills/continuous-monitor/scripts/pre-flight.sh /path/to/project
```

### What it checks:

✅ TypeScript compilation (no type errors)  
✅ Build process (succeeds without errors)  
✅ Output artifacts (dist/ exists with files)  
✅ Server health (running, responding, performance)  
✅ Syntax validation (no broken files)  
✅ Git status (uncommitted changes)

### Example Output:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 PRE-FLIGHT VERIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 Project: spatial-worlds
📍 Path: /home/workspace/Skills/spatial-worlds

📝 Code Quality Checks...
  • TypeScript compilation...
    ✅ No type errors

🔨 Build Verification...
  • Running build script...
    ✅ Build succeeded

📦 Output Artifacts...
  ✅ dist/ exists (1 files, 3.2M)
    • main-iso.js (3.2M)
  ✅ assets/ exists (1 files)

🚀 Server Health...
  ✅ Server process running
    • PID: 99
    • CPU: 0.0%
    • MEM: 0.1%
  ✅ HTTP endpoint responding
    • Status: 200
    • Response time: 0.000727s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PRE-FLIGHT COMPLETE — All checks passed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🎯 Integration

Add to your workflow:

```bash
# 1. Make changes to code
vim src/components/MyComponent.tsx

# 2. Run pre-flight before claiming done
/home/workspace/Skills/continuous-monitor/scripts/pre-flight.sh $(pwd)

# 3. If it passes, THEN test in browser
# 4. If it fails, FIX and re-run

# 5. Only claim completion after pre-flight passes
```

## 📋 What This Skill Fixes

**Before**: "This should work" → User finds it broken  
**After**: Pre-flight catches issues → Fix before delivery

**Real Example from Spatial Worlds**:
1. TypeScript had DOM errors → Pre-flight caught it
2. Fixed tsconfig.json to include DOM lib
3. TypeScript had `override` errors → Pre-flight caught it  
4. Added `override` modifiers
5. Pre-flight passed → Safe to deliver

## 🔄 Self-Improvement Loop

Every time pre-flight catches an issue:
1. Fix it
2. Document the pattern
3. Update checklist if needed
4. Prevent recurrence

## 📚 See Full Documentation

Read `SKILL.md` for complete details on:
- Runtime monitoring
- Skill gap analysis
- Continuous improvement
- Failure pattern tracking
