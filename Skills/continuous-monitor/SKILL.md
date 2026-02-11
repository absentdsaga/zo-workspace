# Continuous Monitor — Self-Improving Quality Assurance System

**Version**: 1.0.0  
**Purpose**: Autonomous monitoring, verification, and improvement system that ensures Zo always delivers to spec  
**Philosophy**: "Trust, but verify. Always check your work. Continuously improve."

---

## 🎯 Core Mission

This skill makes Zo a **self-monitoring, self-improving system** that:
1. **Verifies every deliverable** before claiming completion
2. **Monitors runtime behavior** of deployed services
3. **Identifies gaps** in current skillset
4. **Discovers and integrates** new skills proactively
5. **Learns from failures** and prevents regression

---

## 🔄 Continuous Monitoring Loop

### Phase 1: Pre-Delivery Verification (ALWAYS)
**Trigger**: Before saying "done" or "this works"

```bash
1. Code Check
   - Run linter/type checker
   - Check for syntax errors
   - Verify all imports resolve
   
2. Build Check
   - Compile/bundle succeeds
   - No build warnings
   - Output artifacts exist
   
3. Runtime Check
   - Service starts without errors
   - Browser/app loads correctly
   - No console errors
   
4. Functional Check
   - Core features work as described
   - User interactions respond
   - Data flows correctly
   
5. Performance Check
   - Meets performance targets
   - No memory leaks
   - Acceptable load times
```

### Phase 2: Post-Deployment Monitoring
**Trigger**: Every 5 minutes for active projects

```bash
1. Health Check
   - Service still running?
   - Response times acceptable?
   - Error rates < 1%
   
2. Regression Check
   - New code didn't break old features
   - Performance hasn't degraded
   - User reports no issues
   
3. Metric Tracking
   - FPS, latency, throughput
   - Resource usage (CPU, RAM)
   - User engagement metrics
```

### Phase 3: Skill Gap Analysis
**Trigger**: When encountering new problem domains

```bash
1. Current Capability Audit
   - What skills do I have?
   - What tools are available?
   - What can I do well?
   
2. Gap Identification
   - What did I struggle with?
   - What took longer than expected?
   - What did I have to improvise?
   
3. Skill Discovery
   - Search for existing skills
   - Check community best practices
   - Identify missing tools
   
4. Skill Integration
   - Build new skill if needed
   - Document for future use
   - Test and validate
```

### Phase 4: Continuous Improvement
**Trigger**: After every task completion

```bash
1. Retrospective
   - What went well?
   - What went wrong?
   - What can be improved?
   
2. Pattern Recognition
   - Recurring issues?
   - Common optimizations?
   - Best practices emerging?
   
3. Process Updates
   - Update workflows
   - Refine checklists
   - Improve automation
```

---

## 🛠️ Implementation: Monitor Scripts

### 1. Pre-Flight Checklist (`scripts/pre-flight.sh`)

```bash
#!/bin/bash
# Run before claiming any deliverable is complete

PROJECT_DIR="$1"
cd "$PROJECT_DIR" || exit 1

echo "🔍 PRE-FLIGHT VERIFICATION"
echo "=========================="
echo ""

# 1. Code Quality
echo "📝 Code Quality Checks..."
if [ -f "tsconfig.json" ]; then
    echo "  • TypeScript compilation..."
    tsc --noEmit || { echo "  ❌ TypeScript errors found"; exit 1; }
fi

if [ -f "package.json" ]; then
    echo "  • Linting..."
    npm run lint --if-present 2>/dev/null || echo "  ⚠️  No linter configured"
fi

# 2. Build Verification
echo ""
echo "🔨 Build Verification..."
if [ -f "build-client.sh" ]; then
    ./build-client.sh || { echo "  ❌ Build failed"; exit 1; }
    echo "  ✅ Build succeeded"
fi

# 3. File Existence
echo ""
echo "📦 Output Artifacts..."
if [ -d "dist" ]; then
    ls -lh dist/ | tail -n +2 | while read -r line; do
        echo "  ✅ $line"
    done
else
    echo "  ⚠️  No dist directory found"
fi

# 4. Server Health (if applicable)
echo ""
echo "🚀 Server Health..."
if pgrep -f "server" > /dev/null; then
    echo "  ✅ Server process running"
    
    # Check if server responds
    if command -v curl &> /dev/null; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 304 ]; then
            echo "  ✅ Server responding (HTTP $HTTP_CODE)"
        else
            echo "  ⚠️  Server not responding (HTTP $HTTP_CODE)"
        fi
    fi
else
    echo "  ℹ️  No server process found (may not be applicable)"
fi

echo ""
echo "✅ PRE-FLIGHT COMPLETE"
```

### 2. Runtime Monitor (`scripts/runtime-monitor.sh`)

```bash
#!/bin/bash
# Continuous monitoring of running services

PROJECT_NAME="$1"
CHECK_INTERVAL="${2:-300}" # 5 minutes default

while true; do
    echo "🔍 [$(date)] Monitoring $PROJECT_NAME..."
    
    # Check process health
    if pgrep -f "$PROJECT_NAME" > /dev/null; then
        PID=$(pgrep -f "$PROJECT_NAME" | head -1)
        CPU=$(ps -p "$PID" -o %cpu= 2>/dev/null || echo "N/A")
        MEM=$(ps -p "$PID" -o %mem= 2>/dev/null || echo "N/A")
        
        echo "  ✅ Process alive (PID: $PID, CPU: ${CPU}%, MEM: ${MEM}%)"
    else
        echo "  ❌ Process not running! Restarting..."
        # Add restart logic here
    fi
    
    # Check HTTP endpoint
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:3000)
        echo "  ✅ HTTP endpoint healthy (${RESPONSE_TIME}s)"
    else
        echo "  ❌ HTTP endpoint unreachable"
    fi
    
    sleep "$CHECK_INTERVAL"
done
```

### 3. Skill Gap Analyzer (`scripts/skill-gap-analyzer.py`)

```python
#!/usr/bin/env python3
"""
Analyzes project requirements and identifies missing skills
"""

import os
import json
from pathlib import Path

def analyze_project(project_dir):
    """Scan project and identify what skills might be needed"""
    
    skills_needed = set()
    skills_found = set()
    
    # Scan for tech stack indicators
    if (Path(project_dir) / "package.json").exists():
        with open(Path(project_dir) / "package.json") as f:
            pkg = json.load(f)
            
            # Check dependencies
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            
            if "phaser" in deps:
                skills_needed.add("game-development")
            if "react" in deps:
                skills_needed.add("react-development")
            if "typescript" in deps:
                skills_needed.add("typescript-expert")
    
    # Check for Tiled maps
    if list(Path(project_dir).rglob("*.tmj")) or list(Path(project_dir).rglob("*.json")):
        skills_needed.add("tiled-map-integration")
    
    # Check for asset generation needs
    if (Path(project_dir) / "assets").exists() and len(list(Path(project_dir / "assets").glob("*.png"))) < 5:
        skills_needed.add("sprite-generation")
    
    # Check existing skills
    skills_dir = Path("/home/workspace/Skills")
    if skills_dir.exists():
        for skill in skills_dir.iterdir():
            if skill.is_dir() and (skill / "SKILL.md").exists():
                skills_found.add(skill.name)
    
    # Calculate gaps
    gaps = skills_needed - skills_found
    
    return {
        "needed": list(skills_needed),
        "found": list(skills_found),
        "gaps": list(gaps)
    }

if __name__ == "__main__":
    import sys
    project = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    
    result = analyze_project(project)
    
    print(f"🎯 Skills Needed: {', '.join(result['needed']) or 'None detected'}")
    print(f"✅ Skills Found: {', '.join(result['found'][:5])}..." if len(result['found']) > 5 else f"✅ Skills Found: {', '.join(result['found'])}")
    print(f"⚠️  Skill Gaps: {', '.join(result['gaps']) or 'None!'}")
    
    if result['gaps']:
        print("\n💡 Recommendation: Create these skills or find alternatives")
```

### 4. Automated QA Report (`scripts/generate-qa-report.sh`)

```bash
#!/bin/bash
# Generate comprehensive QA report

PROJECT_DIR="$1"
OUTPUT_FILE="${2:-QA-REPORT-$(date +%Y%m%d-%H%M%S).md}"

cd "$PROJECT_DIR" || exit 1

cat > "$OUTPUT_FILE" << 'EOF'
# QA Report — Automated Verification

**Generated**: $(date)
**Project**: $(basename "$PROJECT_DIR")
**Status**: 🔍 Analyzing...

---

## 🧪 Test Results

### Code Quality
EOF

# TypeScript Check
if [ -f "tsconfig.json" ]; then
    echo "**TypeScript Compilation**" >> "$OUTPUT_FILE"
    if tsc --noEmit 2>&1 | tee -a "$OUTPUT_FILE"; then
        echo "✅ No type errors" >> "$OUTPUT_FILE"
    else
        echo "❌ Type errors found" >> "$OUTPUT_FILE"
    fi
fi

# Build Check
echo "" >> "$OUTPUT_FILE"
echo "### Build Verification" >> "$OUTPUT_FILE"
if [ -f "build-client.sh" ]; then
    if ./build-client.sh >> "$OUTPUT_FILE" 2>&1; then
        echo "✅ Build succeeded" >> "$OUTPUT_FILE"
    else
        echo "❌ Build failed" >> "$OUTPUT_FILE"
    fi
fi

# Performance Metrics
echo "" >> "$OUTPUT_FILE"
echo "### Performance Metrics" >> "$OUTPUT_FILE"
if pgrep -f "server" > /dev/null; then
    PID=$(pgrep -f "server" | head -1)
    echo "- CPU Usage: $(ps -p "$PID" -o %cpu=)%" >> "$OUTPUT_FILE"
    echo "- Memory Usage: $(ps -p "$PID" -o %mem=)%" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "*Generated by continuous-monitor skill*" >> "$OUTPUT_FILE"

echo "✅ QA Report saved to: $OUTPUT_FILE"
```

---

## 📋 Verification Checklist Templates

### For Web Applications
```markdown
- [ ] Code compiles without errors
- [ ] Build succeeds
- [ ] Server starts
- [ ] Page loads in browser
- [ ] No console errors
- [ ] No console warnings
- [ ] Navigation works
- [ ] Forms submit correctly
- [ ] API endpoints respond
- [ ] Performance targets met (FPS, load time)
- [ ] Mobile responsive (if applicable)
- [ ] Accessibility checked (if applicable)
```

### For Game Development
```markdown
- [ ] Game engine initializes
- [ ] Assets load correctly
- [ ] Sprites render
- [ ] Movement/controls work
- [ ] Physics behaves correctly
- [ ] Collisions detect
- [ ] FPS meets target (30/60)
- [ ] No memory leaks
- [ ] Audio plays (if applicable)
- [ ] Multi-player syncs (if applicable)
```

### For APIs/Services
```markdown
- [ ] Service starts without errors
- [ ] Health endpoint responds
- [ ] All routes respond correctly
- [ ] Authentication works
- [ ] Database connections stable
- [ ] Error handling works
- [ ] Logging configured
- [ ] Response times acceptable
- [ ] Load testing passed
- [ ] Security scan clean
```

---

## 🚨 Failure Response Protocol

### When Something Doesn't Work

**NEVER** say "this should work" or "try it now" — **VERIFY FIRST**

```bash
1. Acknowledge the issue
   "I found an issue with [X]. Let me fix it."
   
2. Diagnose root cause
   - Check logs
   - Test in isolation
   - Reproduce the error
   
3. Fix systematically
   - Make targeted change
   - Test the fix
   - Verify no regression
   
4. Document the fix
   - What was broken
   - What caused it
   - How it was fixed
   - How to prevent it
```

---

## 🎓 Learning from Failures

### Failure Pattern Recognition

Track these in `/home/workspace/.monitor/failure-log.json`:

```json
{
  "failures": [
    {
      "date": "2026-02-09",
      "project": "spatial-worlds",
      "issue": "Loading screen stuck",
      "root_cause": "Server not serving /assets/",
      "fix": "Added assets route to server.ts",
      "prevention": "Always verify all static file routes"
    },
    {
      "date": "2026-02-09",
      "project": "spatial-worlds",
      "issue": "Loading screen stuck (again)",
      "root_cause": "Browser can't execute TypeScript",
      "fix": "Added build step to compile TS→JS",
      "prevention": "Always build before deploying client code"
    }
  ]
}
```

### Improvement Suggestions

When patterns emerge:
1. **Create a checklist** to prevent recurrence
2. **Add automation** (pre-flight script)
3. **Update skill documentation**
4. **Build a new skill** if gap is significant

---

## 🔧 Usage Examples

### Example 1: Before Claiming Completion

```bash
# In your workflow, ALWAYS run this before saying "done"
cd /home/workspace/Skills/spatial-worlds
/home/workspace/Skills/continuous-monitor/scripts/pre-flight.sh $(pwd)

# If pre-flight passes, THEN verify in browser
# If pre-flight fails, FIX then re-run
```

### Example 2: Monitoring Active Service

```bash
# Start background monitor
/home/workspace/Skills/continuous-monitor/scripts/runtime-monitor.sh "spatial-worlds" 300 &

# Monitor will check every 5 minutes and alert on issues
```

### Example 3: Skill Gap Analysis

```bash
# Analyze current project
python3 /home/workspace/Skills/continuous-monitor/scripts/skill-gap-analyzer.py /home/workspace/Skills/spatial-worlds

# Output:
# 🎯 Skills Needed: game-development, sprite-generation, tiled-map-integration
# ✅ Skills Found: isometric-sprite-gen, isometric-world-builder, spatial-audio-zones...
# ⚠️  Skill Gaps: tiled-map-integration
# 💡 Recommendation: Create these skills or find alternatives
```

---

## 🎯 Integration with Workflow

### Every Task Completion

```markdown
1. Write code
2. **RUN PRE-FLIGHT** ← MANDATORY
3. Test in browser/runtime
4. Generate QA report
5. Update documentation
6. **ONLY THEN** tell user it's done
```

### Weekly Review

```markdown
1. Review failure log
2. Identify patterns
3. Create preventive measures
4. Update skills as needed
5. Archive resolved issues
```

### Monthly Audit

```markdown
1. Skill gap analysis across all projects
2. Performance trend analysis
3. Identify underutilized skills
4. Discover new tool opportunities
5. Update skill ecosystem map
```

---

## 📊 Success Metrics

Track these in `/home/workspace/.monitor/metrics.json`:

```json
{
  "total_tasks": 127,
  "first_time_success": 89,
  "required_fixes": 38,
  "avg_fix_cycles": 1.4,
  "improvement_trend": "+12% (month over month)",
  "skills_created": 12,
  "skills_improved": 8
}
```

**Goal**: Increase first-time success rate to >95%

---

## 🤖 Self-Improvement Loop

```
┌─────────────────────────────────────────────────┐
│  1. Task Assignment                             │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  2. Gap Analysis: Do I have skills for this?    │
└──────────────┬──────────────────────────────────┘
               │
               ├─ NO → Create/Find Skill → Back to 2
               │
               ▼ YES
┌─────────────────────────────────────────────────┐
│  3. Execute Task                                │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  4. PRE-FLIGHT CHECK (mandatory)                │
└──────────────┬──────────────────────────────────┘
               │
               ├─ FAIL → Fix → Back to 4
               │
               ▼ PASS
┌─────────────────────────────────────────────────┐
│  5. Runtime Verification (browser/app test)     │
└──────────────┬──────────────────────────────────┘
               │
               ├─ FAIL → Diagnose → Fix → Back to 4
               │
               ▼ PASS
┌─────────────────────────────────────────────────┐
│  6. Generate QA Report                          │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  7. Deliver to User                             │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  8. Post-Delivery Monitoring                    │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  9. Retrospective & Learn                       │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  10. Update Skills/Processes                    │
└─────────────────────────────────────────────────┘
```

---

## 💡 Key Principles

1. **Trust, but verify** — Always test before claiming success
2. **Fail fast, fix faster** — Catch issues early with automation
3. **Learn from mistakes** — Track failures and prevent recurrence
4. **Continuous improvement** — Every task makes the system better
5. **Skill evolution** — Create new skills when gaps are found
6. **User first** — Never deliver broken or untested work

---

## 🔗 Related Skills

- `self-qa` — Manual QA reporting
- `workflow-orchestrator` — Task coordination
- `live-logger` — Real-time logging
- `build-preview` — Visual verification

---

## 🚀 Future Enhancements

1. **Automated browser testing** with Playwright/Puppeteer
2. **Performance regression detection** with benchmarking
3. **AI-powered code review** suggestions
4. **Automatic skill generation** from task patterns
5. **Integration with CI/CD** pipelines
6. **Metric dashboards** for trend visualization

---

*This skill ensures Zo never delivers subpar work and continuously improves its capabilities.*

---

## 🎯 SPEC VALIDATION (NEW)

### Purpose
Validates deliverables against user requirements, not just technical correctness.

### How It Works

**1. Create USER-GUIDANCE.md in project root**
```markdown
# User Requirements

- [ ] Requirement 1 (unchecked = pending)
- [x] Requirement 2 (checked = complete)
- Must have X feature
- Should include Y functionality
```

**2. Run spec validator**
```bash
/home/workspace/Skills/continuous-monitor/scripts/spec-validator.sh /path/to/project
```

**3. It checks:**
- ✅ Checkbox requirements (completed vs pending)
- ✅ MUST/REQUIRED/CRITICAL keywords
- ✅ Project-specific patterns (isometric, FFT, Chrono Trigger, etc.)
- ✅ Previous QA report issues
- ✅ Implementation quality markers

**4. Output example:**
```
📋 SPEC VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **Square tiles on map** like FFT
⚠️  **Chrono Trigger-style sprites** (needs improvement)
✅ **8-direction movement**
⚠️  **60 FPS target** (verify in browser)

🎮 Isometric Game Requirements:
  ✅ Isometric rendering implementation found
  ✅ Multi-level platforms implemented
  ✅ Depth sorting system found

⚠️  SPEC VALIDATION: WARNINGS ONLY
✅ No critical failures
⚠️  4 warning(s) found
```

### Full Validation Workflow

Run the complete 3-phase check:

```bash
/home/workspace/Skills/continuous-monitor/scripts/full-validation.sh /path/to/project
```

**Phase 1: Technical** (pre-flight.sh)
- TypeScript compilation
- Build process
- Server health
- File artifacts

**Phase 2: Spec Compliance** (spec-validator.sh)
- User requirements
- Feature completeness
- Quality standards
- Previous feedback

**Phase 3: Browser Testing** (manual)
- Visual verification
- Functional testing
- Performance measurement
- Console error check

### Integration Example

```bash
# Your workflow should be:

# 1. Make changes
vim src/MyComponent.tsx

# 2. Run full validation
/home/workspace/Skills/continuous-monitor/scripts/full-validation.sh $(pwd)

# 3. If Phase 1 or 2 fail, FIX IMMEDIATELY
# 4. When both pass, proceed to Phase 3 (browser test)
# 5. Only claim completion after all 3 phases pass
```

### Captures User Intent

The spec validator **learns from user feedback**:
- Extracts requirements from conversation history
- Checks against exact user quotes
- Validates previous feedback was addressed
- Ensures no regression on fixed issues

**Example**: User said *"square tiles like FFT"*
- Validator checks for: elevated platforms ✅
- Validator checks for: isometric rendering ✅
- Validator checks for: visible platform sides ✅

### Self-Improving

As user provides more guidance:
1. Update USER-GUIDANCE.md with new requirements
2. Spec validator automatically checks them
3. Creates audit trail of what's been addressed
4. Prevents forgetting user requests

