# Anti-Fraud Checklist for VURT Clipper Program

Sourced from Whop's production playbook + Vyro's documented controls + Adin Ross / N3on operational reports. Every guardrail below is one that a real program with $1M+ payouts has shipped.

## Mandatory at launch

- [ ] **Whop platform layer** — inherit their 24-hour payout buffer + post-approval bot sweep + KYC + lifetime ban for confirmed botters
- [ ] **5,000-view minimum** before any CPM accrues
- [ ] **30%+ average watch-through** required for CPM to count
- [ ] **50%+ US audience** verified via screen-recorded analytics (Tier 1) — required for Tier 1 clippers
- [ ] **myvurt.com / @myvurt on-screen for ≥2 seconds** in every clip
- [ ] **Captions burned in** — forces real editing labor, not auto-repost
- [ ] **No bare reposts** of VURT's own social clips — must add edit value
- [ ] **3-day account warmup** before posting on a fresh account (TikTok shadowban prevention)
- [ ] **Submit-within-1-hour-of-posting rule** — prevents late-attribution gaming
- [ ] **14-day post-publish view-counting window** — let bot views get scrubbed by platforms
- [ ] **Per-clipper monthly cap** until trust history accrues
- [ ] **No-spoiler list per show** — never clip finale beats; tracked per active title

## Tier-specific gates

| Gate | Tier 1 (Verified) | Tier 2 (Open Pool) | Tier 3 (Ambassador) |
|---|---|---|---|
| Audience screen-record | Required | Required | Required |
| Sample clip approval | Required | Optional | N/A (already proven) |
| Per-clip approval before view-tracking | Yes | Yes | Auto-approved (subject to retroactive review) |
| Monthly cap on first 30 days | Mid | Lower | Higher |
| Geo-screen | 50%+ US | 50%+ US | 60%+ US |

## What "verified views" means for the pay metric

- Pulled from TikTok/IG/YT API at **t+14 days post-publish**
- Multiplied by clipper's average watch-through % (only clips with ≥30% watch-through count toward CPM)
- Bot-detection from the host platform applied at the API source — Whop additionally runs its own sweep

## What kills clippers from the program (lifetime ban)

1. Confirmed bot views (Whop's detection or VURT's audit)
2. Buying engagement (likes, comments, shares)
3. Misrepresenting audience analytics (faked screen-record)
4. Clipping spoilers from no-spoiler list
5. Adding clipper's own brand sponsorships to a VURT clip during the program
6. Deepfake / face-swap / AI voice clone of VURT talent
7. Stacking sportsbook / gambling / tobacco / cannabis content on a VURT clip

## Periodic audit cadence

- **Daily:** New submissions reviewed within 24 hours
- **Weekly:** Top 20 clipper-by-views audited for view-quality (drop-off patterns, geo distribution, comment authenticity)
- **Bi-weekly:** Random sampling — 10% of paid-out clips re-examined for compliance
- **Monthly:** Full program review — average CPM-cost-per-clipper-recruited, top-performer retention, bot-detection false positives/negatives

## Red flags to monitor

| Signal | Likely cause | Action |
|---|---|---|
| Clip pulls 50K views in 1 hour, then flat | View bot | Hold payout, manual audit |
| Clip has 100K views, 3 likes, 0 comments | Bought views | Decline payout, flag account |
| Clipper's other recent posts avg 2K views, this one 200K | View boost service | Investigate, slow-pay (release after 30 days) |
| Audience analytics screenshot shows 60% Indonesia, but caption is English | Faked geo | Decline + ban |
| Same clip reposted across 5+ accounts within 1 hour | Sock puppet network | Ban entire account cluster |
