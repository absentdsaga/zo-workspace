# VURT Production Pipeline -- Trello Setup Guide

**Date:** March 22, 2026
**For:** VURT Team (Marketing, Web Dev, Ad Team)

---

## The Setup: One Board, Three Teams, Zero Micromanagement

One board called **VURT Production**. Everyone lives here. No separate boards per department -- that fragments visibility and kills cross-team awareness.

---

## Column Structure

Left to right:

| Column | What Goes Here | Who Manages It |
|--------|---------------|----------------|
| **Inbox** | New requests, ideas, anything unprocessed. Anyone can drop cards here. | Anyone adds, leads triage weekly |
| **This Week** | Prioritized work for the current week. If it's here, it's active. | Team members pull from here |
| **In Progress** | Someone is actively working on it. Max 2-3 cards per person. | Card owner moves it here |
| **Review / Blocked** | Needs feedback, approval, or waiting on someone/something. | Card owner moves it here, tags who's blocking |
| **Done (Current Week)** | Completed this week. Auto-renamed and archived monthly by Butler. | Card owner moves it here when finished |

### Why This Structure

- **Inbox** replaces Backlog. Backlogs become graveyards. Inbox is a parking lot -- things either get pulled into This Week or they sit until relevant. No guilt, no clutter.
- **This Week** replaces Ready. It's time-bound, which creates natural urgency without you having to push.
- **No separate "Ready" column.** Two pre-work columns (Backlog + Ready) is one too many for a team this size. It creates ambiguity about what's actually next.
- **Review/Blocked is one column**, not two. At your team size, splitting them adds overhead without value. The label or a comment on the card says what's needed.
- **Done column gets auto-managed** by Butler (see Automation section below).

---

## Labels (Color-Coded by Team + Priority)

### Team Labels
- Purple: **Marketing** (SimpleSocial, social strategy, community)
- Blue: **Web Dev** (Enveu dev team, platform fixes, SEO implementation)
- Orange: **Ad Team** (paid UA, pixel tracking, campaign ops)
- Pink: **Content/Clips** (editors, clip production, unscripted pipeline)

### Priority Labels
- Red: **Urgent** (needs to jump the line, someone should grab it today)
- Green: **Quick Win** (under 1 hour, good for filling gaps between bigger work)
- Yellow: **Stale** (auto-applied by automation when a card sits in In Progress 5+ days with no activity)

### Functional Labels
- Sky: **SEO** (sitemap, schema markup, URL structure, search visibility)
- Lime: **Analytics** (GA4, pixel tracking, reporting, Meta Graph API)

Cards often carry multiple labels (e.g. "Web Dev" + "SEO" for a sitemap task). This is correct -- it shows cross-team dependencies at a glance.

---

## Card Standards

Every card should have:

1. **Title** -- Clear action statement (e.g., "Create TikTok ad for Chief Keef drop" not "TikTok stuff")
2. **Owner** -- Assigned member. One person per card. They own moving it through columns.
3. **Team label** -- Purple, Blue, or Orange
4. **Due date** -- Even rough ones. Cards without dates drift.
5. **Done criteria** -- One line in the description: "Done when: ___"

Optional but useful:
- Checklist for multi-step tasks
- Attachments (briefs, assets, links)
- Comments for status updates instead of meetings

### Card Template

Set up a card template with these fields pre-filled so people don't skip them. Trello supports card templates natively -- create one card with the structure and save it as a template.

```
## Task
[What needs to happen]

## Done When
[One-line definition of done]

## Notes
[Any context, links, briefs]
```

---

## Automation (Webhook + Scheduled Agents via Zo)

Butler has no API, so all automations run through a Trello webhook + Zo scheduled agents. This is more reliable than Butler and has no quota limits.

### Event-Driven (Webhook at dioni.zo.space/api/trello-webhook)

These fire instantly when cards are moved:

| Rule | Trigger | Action |
|------|---------|--------|
| Auto-complete | Card moved to "Done" | Marks due date as complete |
| Blocked alert | Card moved to "Review / Blocked" | Posts comment: "This card needs attention. Please tag who you're waiting on." |

### Scheduled (Zo Agents)

| Rule | Schedule | Action |
|------|----------|--------|
| Sort + Stale detection | Daily 8am ET | Sorts "This Week" by due date ascending. Flags cards in "In Progress" with no activity for 5+ days with "Stale" label. |
| Weekly triage card | Monday 9am ET | Creates "Weekly Triage" card in "This Week" with checklist. |
| Monthly Done archival | 1st of month 9am ET | Renames "Done" to "Done YYYY-MM", archives it, creates fresh "Done" list. |

All agents viewable and editable at [Agents](/?t=agents).

---

## Power-Ups to Enable (All Free)

| Power-Up | Why |
|----------|-----|
| **Card Aging** | Cards that sit untouched fade visually. Stale work becomes obvious at a glance. Use "Regular" mode (fading). |
| **Calendar** | See all due dates on a calendar view. Good for spotting deadline clusters. |
| **Card Templates** | Pre-fill card structure so people don't skip fields. |

These are all free on Trello's current plan (unlimited power-ups on free tier as of 2024).

### If You Upgrade to Standard ($5/user/month)

You'd get:
- **Custom Fields** -- Add dropdown fields like "Effort: Small/Medium/Large" or "Status: On Track/At Risk"
- **Advanced Checklists** -- Assign checklist items to specific people with due dates
- More Butler automation runs per month

Not needed to start. Upgrade only if the team is actually using the board consistently for 2+ weeks.

---

## Weekly Rhythm

The whole system runs on one lightweight weekly cycle:

| Day | Action | Who |
|-----|--------|-----|
| **Monday** | Triage Inbox: move priority items to This Week. 15 min max. | Dioni or team leads |
| **Daily** | Everyone moves their own cards. No standup needed. | Everyone |
| **Friday** | Quick scan: anything stuck in Review/Blocked for 3+ days? Flag it or kill it. | Dioni (5 min glance) |

That's ~20 minutes of your time per week managing the board. Everything else is self-serve.

---

## How People Use It Day-to-Day

### Adding New Work
1. Create a card in **Inbox**
2. Add a title, team label, and rough description
3. It sits there until Monday triage (or gets pulled immediately if it's urgent + red-labeled)

### Starting Work
1. Go to **This Week**
2. Pick a card (ideally top of the list = highest priority)
3. Assign yourself, drag to **In Progress**

### Finishing Work
1. Drag card to **Done**
2. Butler auto-marks due date complete

### Getting Blocked
1. Drag to **Review / Blocked**
2. Comment tagging who you need: "@mark need design review on this"
3. When unblocked, move back to **In Progress**

---

## Cross-Team Dependencies

When Marketing needs something from Web Dev (or any cross-team handoff):

1. The card stays on the same board (don't create duplicate cards)
2. Original owner adds a comment: "@[web dev person] need [specific thing] by [date]"
3. Card moves to **Review / Blocked** until the dependency is resolved
4. The person who picks it up adds themselves as a second member

This keeps everything visible. No work disappears into another team's board.

---

## Anti-Patterns to Avoid

| Don't Do This | Do This Instead |
|--------------|----------------|
| Create a card for every tiny task | Only card things that take 30+ minutes or need tracking |
| Leave cards in Inbox for weeks | Archive or delete anything in Inbox older than 3 weeks |
| Have 10+ cards In Progress per person | WIP limit: 2-3 max. Finish before starting new. |
| Use the board as a chat | Comments for status updates only, not conversations. Use Slack/text for discussion. |
| Skip due dates | Even a rough date ("end of week") is better than nothing |
| Create multiple boards per team | One board. Labels separate teams. |

---

## Getting Started Checklist

1. [ ] Create Trello workspace: "VURT"
2. [ ] Create board: "VURT Production"
3. [ ] Create 5 lists: Inbox, This Week, In Progress, Review / Blocked, Done
4. [ ] Create labels (Purple/Marketing, Blue/Web Dev, Orange/Ad Team, Red/Urgent, Green/Quick Win)
5. [ ] Enable Power-Ups: Card Aging, Calendar
6. [ ] Create card template with standard fields
7. [ ] Set up Butler automations (start with #1 auto-archive and #2 auto-sort, add others after)
8. [ ] Invite team members
9. [ ] Share this doc with the team
10. [ ] Seed the board with 10-15 current tasks across all teams
11. [ ] Run first Monday triage to establish the rhythm

---

## Scaling Later

Once the team is comfortable (2-4 weeks in), consider:

- **Swimlanes via filtered views** -- Filter by label to see just Marketing or just Web Dev cards
- **Custom Fields** (Standard plan) -- Add effort sizing, content type, campaign tags
- **Slack integration** -- Butler can post to Slack when cards move or get stuck
- **Dashboard view** (Premium plan) -- Visual charts of cards per list, cards per member, overdue cards

Don't add complexity at launch. Start with the bare minimum and let the team tell you what's missing.
