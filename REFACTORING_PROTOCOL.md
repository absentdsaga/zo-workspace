# Mandatory Refactoring Protocol - Never Break Working Code Again

## The Problem

During the Solana bot refactor, I broke 5 critical features by:
1. Being overconfident
2. "Simplifying" working code without verification
3. Trusting memory over source code
4. Not doing line-by-line comparison
5. Claiming "done" without proof

**Result**: User had to catch all my mistakes and force me to fix them.

---

## The Solution: Mandatory Protocol

### STEP 1: Pre-Refactor Checklist

Before touching ANY working code:

```bash
# 1. Create safety branch
git checkout -b refactor-backup-$(date +%Y%m%d-%H%M%S)
git add -A && git commit -m "Pre-refactor snapshot"

# 2. Document current behavior
./document-current-behavior.sh [component-name]

# 3. Create baseline tests
./capture-baseline.sh [component-name]
```

**Required files created:**
- `[component]-CURRENT-BEHAVIOR.md` - What it does now
- `[component]-baseline-tests.json` - Expected outputs
- Git commit with working state

---

### STEP 2: During Refactor - Line-by-Line Protocol

**NEVER freestyle refactor. Follow this exactly:**

```bash
# 1. Extract original method to temporary file
./extract-method.sh [file] [method-name] > /tmp/original-method.txt

# 2. Copy to new file for editing
cp /tmp/original-method.txt /tmp/refactored-method.txt

# 3. Make ONLY necessary changes
#    - this.CONSTANT → config.constant
#    - Add circuit breakers around external calls
#    - Add config manager calls
#    - DO NOT "simplify" logic
#    - DO NOT remove "verbose" logging
#    - DO NOT remove "redundant" fallbacks

# 4. Diff before applying
diff -u /tmp/original-method.txt /tmp/refactored-method.txt

# 5. Review every line removed
#    Ask: "Is this ACTUALLY unnecessary or am I being lazy?"
```

---

### STEP 3: Verification Checklist

Before claiming "done":

- [ ] **Build test**: `bun build [file] --target=bun`
- [ ] **Diff review**: Every removed line justified
- [ ] **Feature inventory**: All original features present
- [ ] **Side-by-side test**: Run original + refactored for 10 minutes
- [ ] **Log comparison**: Outputs match
- [ ] **User approval**: Show diff and get explicit OK

---

### STEP 4: Deployment Protocol

```bash
# 1. Stop original
pkill -f [original-bot]

# 2. Backup state
cp /tmp/[state-files] /tmp/backup-$(date +%Y%m%d-%H%M%S)/

# 3. Start refactored with monitoring
nohup bun [refactored-bot] > /dev/shm/[bot]-refactored.log 2>&1 &

# 4. Monitor for 1 hour minimum
tail -f /dev/shm/[bot]-refactored.log

# 5. Compare metrics
./compare-performance.sh original-logs refactored-logs
```

---

## Mandatory Diff Review Questions

For EVERY line removed, answer:

1. **What does this line do?**
2. **Why was it added originally?**
3. **What breaks if I remove it?**
4. **Is there a test covering this?**
5. **Am I removing it because:**
   - [ ] Actually unnecessary (prove it)
   - [ ] Looks redundant (DANGER - probably wrong)
   - [ ] Making code "cleaner" (DANGER - preserve working code)
   - [ ] Don't understand it (DANGER - keep it)

**Default rule**: If unsure, KEEP IT.

---

## Red Flags That Mean STOP

If you catch yourself thinking:

- ❌ "This looks redundant" → STOP - prove it's unnecessary first
- ❌ "I can simplify this" → STOP - working code > clean code
- ❌ "This is too verbose" → STOP - logging saves debugging time
- ❌ "I remember how this works" → STOP - read the source
- ❌ "This should be obvious" → STOP - check if it's tested
- ❌ "I'll fix it later" → STOP - fix it now or keep original

---

## Tools To Create

### 1. extract-method.sh
```bash
#!/bin/bash
# Extract a method from a TypeScript file
FILE=$1
METHOD=$2
awk "/private.*$METHOD.*\{/,/^  \}/" "$FILE"
```

### 2. verify-features.sh
```bash
#!/bin/bash
# Verify all features from original are in refactored
ORIGINAL=$1
REFACTORED=$2

# Extract all method names, variable names, feature flags
grep -o "private.*(" "$ORIGINAL" | sort > /tmp/original-features.txt
grep -o "private.*(" "$REFACTORED" | sort > /tmp/refactored-features.txt

diff /tmp/original-features.txt /tmp/refactored-features.txt
```

### 3. compare-logs.sh
```bash
#!/bin/bash
# Compare log patterns between original and refactored
ORIGINAL_LOG=$1
REFACTORED_LOG=$2

echo "=== Original log patterns ==="
grep -oP '(?<=📊).*' "$ORIGINAL_LOG" | head -20

echo "=== Refactored log patterns ==="
grep -oP '(?<=📊).*' "$REFACTORED_LOG" | head -20
```

---

## Apply To All Builds

### Polymarket Bot (Next)
- [ ] Create pre-refactor snapshot
- [ ] Document current behavior
- [ ] Extract methods to temp files
- [ ] Line-by-line refactor with diff review
- [ ] Verify all features present
- [ ] Side-by-side test for 1 hour
- [ ] Get user approval before deploying

### Spatial Worlds (If Needed)
- [ ] Same protocol
- [ ] Focus on game loop, rendering, multiplayer sync
- [ ] Verify frame rates match

### Any Future Refactor
- [ ] Follow this protocol EXACTLY
- [ ] No shortcuts
- [ ] No "I know what I'm doing"
- [ ] Trust the process, not your memory

---

## Lessons Embedded In Protocol

1. **Humility**: Assume you don't know better than working code
2. **Verification**: Proof required before claiming done
3. **Preservation**: Keep working logic verbatim
4. **Documentation**: Future you needs to understand why
5. **Testing**: Side-by-side comparison required

---

## Enforcement

**This protocol is MANDATORY for:**
- Any refactoring
- Any "cleanup"
- Any "simplification"
- Any "improvement" to working code

**Violation consequences:**
- User has to catch your bugs
- User loses trust
- Code breaks in production
- You look incompetent

**Success metrics:**
- Zero regressions
- All features preserved
- User approves before deployment
- Side-by-side test passes

---

## Final Rule

> **If it ain't broke, don't fix it.**
>
> And if you MUST fix it:
> - Document why
> - Preserve ALL behavior
> - Verify EVERYTHING
> - Get approval BEFORE deploying

Never again will I break working code through arrogance.
