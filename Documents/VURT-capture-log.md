# VURT Capture Log

Tracks what VURT information was persisted and when, to prevent context loss across conversations.

---

## 2026-03-24 (Session 2) -- Content Calendar Buildout + Tracker + Plan of Attack

**Trigger:** Dioni building full social media operations handoff for Ari + intern.

**Created/Updated:**
- `Documents/VURT-Social-Media-Plan-of-Attack.md` -- full 2-week operating manual for Ari + intern. Platform rules, daily routines, brand voice, engagement rules, clip sequencing framework (5-clip arc per title), X/Twitter rules, press/announcement content types.
- `Documents/VURT-Press-Social-Copy.md` -- social copy for press coverage posts (TechCrunch, Yahoo Tech, REVOLT). Due March 25 per Trello card.
- `Documents/VURT-Content-Calendar.md` -- updated Week 1 to 5 clips (Mon-Fri), Sat stories only, Sun repost winner. Added LinkedIn section. Resolved open questions (watermarks, paid ads, X handle).
- Production Tracker (Google Sheets) -- added "Content Release Calendar" tab with:
  - Week 1 + Week 2 clip schedules with Post IDs
  - Asset Link column (Frame.io / Dropbox links per title)
  - Performance tracking columns (views, likes, comments, shares, saves, CTR)
  - Weekly Performance Dashboard with targets
  - Title Performance Leaderboard
  - Press & Brand Announcements section (press coverage, director signings, milestones, partnerships)

**Key decisions:**
- Week 1: 5 clips from approved titles only (Killer Stepdad, Baby Mama, 35 & Ticking, Drops Of Mercy, Church Boy)
- Killer Stepdad leads Day 1 (scroll-stopper), 35 & Ticking Day 2 (star power)
- 5-clip arc per title: Hook > Escalation > Twist > Confrontation > Edge of Resolution. Never resolve conflict in clips.
- Mark requested A/B test of "What Is VURT" sizzle videos (Nigeria version vs woman's voice). Test on TikTok, winner deploys everywhere.
- Ted wants director signing announcements as ongoing social content.

**New references:**
- Celebrity actors spreadsheet: https://docs.google.com/spreadsheets/d/1BHb0_l6MQbL69Eff9ET8vby5tiOaip-n/ -- 73 celebrity actors across catalog. 35 & Ticking has 12+ names including Kevin Hart, Meagan Good, Mike Epps.
- "What Is VURT" sizzle videos: Nigeria/international version + woman's voice version. Asset location TBD (Dioni to find folder).

---

## 2026-03-24 (Session 1) -- Content Calendar Answers + Team Updates

**Trigger:** Dioni answered open questions on content calendar.

**Captured:**
- TikTok handle: Using @vurt_official (interim). @myvurt in cooldown period after being released from another account, waiting to reclaim. Account is LIVE with 8 videos, 6 followers, 260 likes. Top performer: 35 & Ticking (1,305 views).
- Social posting executed by internal intern (not SimpleSocial team).
- Miami Confidential, Miami Kingpins, Fatal Lust: Still waiting on editors to address notes. Not yet approved.
- Platform access: Dioni has IG + YouTube. Ari also has logins. TikTok @vurt_official is LIVE.
- Dioni will pick top clips to lead Week 1.
- New team members added to VURT-master.md: Ari (platform logins), internal intern (content posting).
- Watermarks: No watermarks on clips yet, just logo card at end. Text overlays need to be added before posting.
- Paid ads: Team has budget. Coordinate to boost top organic performers after 72hr window.
- X/Twitter: @myvurt secured. Need to start posting.

**Persisted to:** VURT-master.md (team section), VURT-Content-Calendar.md (resolved questions, TikTok handle update)

---

## 2026-03-22 — Analytics Report Feedback from Investors

**Trigger:** Tarik Brooks and Alex Akimov responded to the daily analytics report with questions and action items.

**Captured:**
- Tarik Brooks (tarikamin@gmail.com) emailed team at 7:33 PM on 2026-03-21 with questions:
  - "Who generates the insights? Who is determining which ones to prioritize?"
  - "99% of traffic is US — should we allocate bigger % to international cities?"
  - "Have we made it so links in content clips go directly to the series?"
  - "How is Engagement Rate defined?"
  - "What do we need to do to fix the 'Not Set' results?"
  - "Can we make content auto-start when someone lands on a series/episode?"
- Alex Akimov (alex@simplesocial.info) replied to team:
  - "Ok this is really good"
  - "Switch everything to app and focus on downloads"
  - "Web is not performing as good as the app"
  - "Can you please get the pixel set up and start driving to downloads"
- Alex Akimov contact: O: (626) 823-3740, M: (626) 497-2459 (from email signature)
- 2026-03-21 duplicate send incident: agent sent 15 copies of report. Fixed with sent-flag guard + agent rewrite.

**Actions taken:**
- Hardened insights engine: removed unverified CPM benchmarks, added sample size warnings, softened speculative language
- Added methodology section to report footer (GA4 definitions, data sources, benchmark citations)
- Fixed duplicate send with sent-flag mechanism (Skills/vurt-analytics/scripts/send-report.py)
- Report now goes to Dioni first for review before team distribution (temporary)

**Persisted to:**
- Memory: `project_vurt_report_distribution.md` — updated with Alex contact info + Tarik reads insights closely note
- `Documents/VURT-capture-log.md` — this entry
- Insights engine: `Skills/vurt-analytics/scripts/insights_engine.py` — benchmarks, sample sizes, methodology

---

## 2026-03-20 (Session 2) — Revised Social Media Strategy

**Trigger:** Dioni requested revised social media strategy and asset tracker overhaul.

**Captured:**
- TikTok @myvurt handle released for team transfer, now in cooldown (up to 30 days)
- Clip pipeline status: 4 titles with 5/5 clips complete, 60+ titles QC approved but unassigned
- SimpleSocial team (Christian, Alex) handles social posting — christian@simplesocial.info, alex@simplesocial.info
- X/Twitter organic buzz from @mediagazer, @entrepreneur_cm, @TyCarver, @dailytechonx — zero VURT engagement
- Active editors: OTR, Daniel, Brad, Wayne Alford (waynetheeditor@gmail.com)

**Persisted to:**
- `Documents/VURT-Revised-Social-Media-Strategy-2026-03-20.md` — full strategy doc
- `Documents/VURT-master.md` — workstreams, decision log, existing docs table updated

---

## 2026-03-20 (Session 1)

**Trigger:** Dioni flagged that team distribution list (6 emails) was discussed in prior conversation but never saved.

**Captured:**
- Team distribution list for daily analytics report (6 TO + 1 CC)
  - mark@myvurt.com, ted@thesourcegroups.com, hilmon@thesourcegroups.com, tarikamin@gmail.com, eric@swirlfilms.com, ariella@thesourcegroups.com
  - CC: dioni@myvurt.com
- Daily report agent must use Gmail HTML sending (not send_email_to_user)
- Agent ID: a8df5858-1fd9-4b87-9481-d04aa4a75de2

**Persisted to:**
- `Documents/VURT-master.md` — distribution list added to analytics section
- Memory: `project_vurt_report_distribution.md` — full distribution list + delivery method
- Memory: `MEMORY.md` — index entry added

**Root cause of failure:** Contacts were discussed in a prior Zo conversation but only stored in the agent instruction — not persisted to master doc or memory. When the agent was recreated/updated, the contacts were lost.

**Prevention:** Created `vurt-capture` skill + conditional rule to auto-capture VURT facts at end of every VURT conversation.

---
### 2026-03-28 — Social Ops Context Update

**Captured:**
- TikTok (@vurt_official) is ACTIVE — Dioni confirmed posting there alongside IG/FB/YT
- 72-hour rule clarified: runs in parallel with posting, not a freeze. New clip every 2-3 days.
- Platform exports simplified: one clean vertical export works for all platforms, only extra is SRT for YouTube
- Weekly cadence for titles even with 10 clips — volume of director features means 1 title/week
- Clip 2 for Karma in Heels: "I want to play... especially with this motherfucker." Two girls + one guy, camera spins, wide room, dark/menacing.
- Clip 1 (the craziest of 5) was posted to all 4 platforms same day (stagger going forward)
- Subtitles were missing from Clip 1 post — noted for future
- "Be thoughtful and disciplined" quote = Ted Lucas (corrected from Mark)

**Persisted to:**
- Documents/VURT-Original-Launch-Playbook.md (posting schedule, weekend push, clip arc, exports)
- Documents/VURT-Social-Media-Plan-of-Attack.md (TikTok active, exports simplified)
- Documents/VURT-master.md (Ted attribution fix)
- Skills/vurt-social-tracker/state.md (NEW — living state file)
- Skills/vurt-social-tracker/SKILL.md (NEW — context tracker skill)
- Memory: project_vurt_social_ops.md (TikTok active, cadence rules, Clip 2 info)
- Memory: MEMORY.md (social tracker skill reference, TikTok active)
