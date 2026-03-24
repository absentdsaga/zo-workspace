---
name: vurt-capture
description: Captures and persists all VURT-related decisions, contacts, configurations, and commitments from conversations. Prevents information loss between sessions. Run this at the END of every VURT conversation or when important VURT details surface mid-conversation.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

# VURT Capture — Never Forget What Matters

## When to activate (MANDATORY)
This skill MUST run whenever a conversation involves VURT and any of the following surfaces:
- **Contacts/emails** — team members, investors, partners, vendors, distribution lists
- **Decisions** — strategic choices, feature priorities, timeline commitments
- **Configurations** — agent settings, report formats, delivery methods, API keys
- **Commitments** — things promised to team/investors, deadlines, deliverables
- **Relationships** — who does what, who reports to whom, partner dynamics
- **Numbers** — budgets, metrics targets, deal terms, revenue figures
- **Infrastructure** — dev team contacts, platform configs, tracking setup

## How it works

### Step 1: Extract
Scan the conversation for any VURT-related facts that:
1. Are NOT already in `Documents/VURT-master.md`
2. Are NOT already in memory files under `/root/.claude/projects/-home-workspace/memory/`
3. Would be painful to lose (contacts, configs, decisions, commitments)

### Step 2: Persist to VURT Master Doc
Update `Documents/VURT-master.md` with new information in the appropriate section. This is the single source of truth for VURT. If a section doesn't exist, create one.

Key sections to update:
- **Team & Contacts** — names, emails, roles, phone numbers
- **Analytics & Tracking** — GA4 config, report settings, distribution lists
- **Strategy & Decisions** — key strategic calls and their rationale
- **Timeline & Commitments** — what was promised, to whom, by when
- **Technical Infrastructure** — platform details, API configs, dev contacts
- **Meeting Notes** — key takeaways from calls/meetings

### Step 3: Persist to Memory
Create or update memory files for information that should influence future conversation behavior:
- Distribution lists → `project_vurt_report_distribution.md`
- Role/relationship changes → `project_vurt_role.md`
- New team contacts → dedicated memory file
- Strategic decisions → dedicated memory file

### Step 4: Log
Append a capture entry to `Documents/VURT-capture-log.md` with:
- Date
- What was captured
- Where it was persisted

## The capture script
Run: `python3 Skills/vurt-capture/scripts/capture-check.py`
This scans recent conversation logs and flags potential uncaptured VURT information.

## Rules
- NEVER assume something is already saved. Check first.
- When in doubt, SAVE IT. Storage is cheap, lost context is expensive.
- Always update the master doc AND memory — they serve different purposes (master doc = reference, memory = behavior guidance).
- Contacts are HIGH PRIORITY — emails, phone numbers, roles. These get lost the most.
- Configurations are HIGH PRIORITY — agent settings, distribution lists, delivery methods. These cause visible failures when forgotten.
