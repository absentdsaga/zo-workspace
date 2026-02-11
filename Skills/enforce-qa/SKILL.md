# Enforce-QA Meta-Skill

**Purpose:** Forces AI to ALWAYS verify work before claiming completion. No exceptions.

## The Core Problem

**User's Observation:**
> "theres so many skills on zo we built together acrsoos different chats that i don't even know which one youre running, ideally its be one major skill that verifies, qa, and motniros your work for yourself to review and imrove to my guidance. how do i know you even run it afte every task i give you?"

**Current Failure:**
- AI builds features
- AI claims "it works!"
- AI doesn't actually verify
- User finds it broken
- Trust erodes

## The Solution

A **mandatory checkpoint system** that:
1. Runs automatically after task completion
2. Blocks claiming "done" until QA passes
3. Logs verification attempts
4. Integrates all existing QA skills into one workflow

## How It Works

### 1. AI Completes Task
```
✅ Code written
✅ Build successful
```

### 2. MANDATORY Checkpoint (Cannot Skip)
```bash
# AI MUST run this before claiming completion:
/home/workspace/Skills/enforce-qa/checkpoint.sh
```

### 3. Checkpoint Runs Full Verification
```
→ Technical QA (compilation, build, server)
→ Visual verification (screenshot comparison)
→ Spec compliance (matches requirements)
→ Audit log (record verification occurred)
```

### 4. Only After Passing
```
✅ All checks passed
✅ Logged to audit trail
NOW AI can tell user "Task complete"
```

## Enforcement Mechanism

**System Prompt Integration Required:**

```
CRITICAL RULE:
After completing any user task, you MUST:
1. Run: /home/workspace/Skills/enforce-qa/checkpoint.sh
2. Wait for results
3. Fix any failures
4. Only claim "done" after checkpoint passes

If you skip this, you are violating core protocol.
```

## Audit Trail

Every checkpoint run logs to:
```
/home/workspace/Skills/enforce-qa/audit.log
```

Format:
```
[2026-02-09 23:45:12] TASK: Fix isometric grid rendering
[2026-02-09 23:45:13] TECHNICAL_QA: ✅ PASS
[2026-02-09 23:45:14] VISUAL_VERIFY: ❌ FAIL (grid not visible)
[2026-02-09 23:45:15] STATUS: In progress (fixing)
[2026-02-09 23:46:30] VISUAL_VERIFY: ✅ PASS (grid visible)
[2026-02-09 23:46:31] SPEC_CHECK: ✅ PASS
[2026-02-09 23:46:32] CLAIMED_COMPLETE: YES
```

User can check: "Did AI actually run QA?"
```bash
tail -20 /home/workspace/Skills/enforce-qa/audit.log
```

## Integration with Existing Skills

This meta-skill orchestrates:
- `/home/workspace/Skills/continuous-monitor/` (technical QA)
- `/home/workspace/Skills/visual-verify/` (visual checks)
- `/home/workspace/Skills/auto-qa/` (root cause analysis)

## Files

- `SKILL.md` - This documentation
- `checkpoint.sh` - Mandatory verification gate
- `audit.log` - Verification history
- `config.yaml` - Which checks to run for which tasks

## Success Criteria

This skill is working when:
1. AI never claims completion without running checkpoint
2. User can verify AI ran QA via audit log
3. Issues are caught before user sees them
4. Trust is rebuilt through consistent verification

## The Key Insight

**You can't trust AI to self-enforce.** You need:
- System-level integration (in prompt/instructions)
- Audit trail (so you can verify)
- Failure loudness (checkpoint failure must be visible)

This skill provides the framework. The system prompt must enforce it.
