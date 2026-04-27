# VURT TikTok Improvement Playbook (v3)

_Generated 2026-04-22. v3 supersedes v2 after Dioni clarified that (a) some Posted clips were pulled directly from episode folders, not the Social Media Clips folder, and (b) the posted social cut may be re-edited after pulling — so Frame.io duration ≠ posted duration. The inventory walker was rebuilt to recurse every folder under each show, and Dioni refreshed Status tags. The numbers below are from that fuller pass._

## What changed since v2

| | v2 | v3 |
|---|---:|---:|
| Total videos scanned | 91 | 371 |
| Posted-tagged clips | 22 | **30** |
| Approved-tagged clips | 20 | 18 |
| Shows with at least 1 Posted | 7 | 7 |
| Shows w/ episode-folder Posted | 0 detected | **2** (CBD EP29, Parking Lot ep08) |

The 371 vs 91 swing is mostly episode masters that the v2 walker skipped. The numbers that matter for posting are the tagged ones: **+8 Posted clips found** by walking everything, and a meaningful cleanup of Approved/Needs Review/Denied across the queue.

## Ground truth: where every finished clip stands

Status tags on Frame.io as of refresh:

| Status | Count | Meaning |
|---|---:|---|
| **Posted** | 30 | Dioni posted it somewhere. Live or archived. |
| **Approved** | 18 | Cleared review. **Ready-to-post inventory.** |
| Needs Review | 8 | Not ready — don't recommend. |
| Denied | 5 | Explicitly rejected. Don't resurrect. |
| Feedback Given | 4 | Blocked on revisions. |
| _Untagged_ | 306 | Mostly episode masters; only a fraction are social-cut candidates. |

Per-show breakdown:

| Show | Total videos | Posted | Approved | Needs Review | Denied | Feedback | Untagged |
|---|---:|---:|---:|---:|---:|---:|---:|
| 35 & Ticking | 55 | 3 | 2 | 4 | 2 | 3 | 41 |
| Bride To Be | 7 | 0 | 2 | 0 | 0 | 0 | 5 |
| Come Back Dad | 43 | 3 | 5 | 0 | 0 | 0 | 35 |
| Favorite Son | 5 | 1 | 2 | 0 | 0 | 0 | 2 |
| Karma in Heels | 108 | **0** | 0 | 0 | 0 | 0 | 108 |
| Schemers | 40 | 8 | 1 | 0 | 0 | 0 | 31 |
| Something Like A Business | 64 | 4 | 0 | 0 | 0 | 0 | 60 |
| The Love Network Jam | 33 | 8 | 1 | 4 | 0 | 0 | 20 |
| The Parking Lot Series | 16 | 3 | 0 | 0 | 2 | 1 | 10 |
| **Total** | **371** | **30** | **18** | **8** | **5** | **4** | **306** |

### Two new findings worth flagging

1. **CBD EP29 = the source of the #1 organic save-rate winner.** `VURT_COMEBACKDAD_EP29.mp4` (in the CBD show root, not in `Social Media Clips/`) is now tagged Posted. This is the master that the "EP29 Tatyana Ali waiting for Spence" TikTok cut (1,135v / 7.7% L / **2.47% S**) was pulled from. The posted social cut was trimmed from this episode master. Confirms the v2 hypothesis and proves the v2 walker was missing that source path.

2. **Parking Lot has a third Posted clip from episode masters.** `episode 8 - Wrong Place.mp4` (in `Season 1/Vertical Episodes/`) is Posted. Combined with Ep06 + Ep07 social edits = 3 Posted (v2 had 2). Note: `PARKING_LOT-Ep05-_Social Edit-004-v2.mp4` was Posted in v2 but is now untagged — flag for confirmation that this was intentional.

### Critical correction: Karma in Heels

KIH has 108 videos in Frame.io and **zero Status tags**. The v2 playbook claimed 3 Posted / 4 Approved for KIH — that was inferential from filenames. Real ground truth: KIH is fully untagged. The TikTok metrics still show 4 KIH posts went live (one boosted to 189.6K, three organic ~190–315 views), but until Dioni applies tags here, the per-clip mapping is a guess. **Tag KIH first** before optimizing.

## What the organic data says is working (unchanged from v2)

Stripping the 2 boosted posts (SLAB 380K, KIH 189.6K), the real organic leaderboard. 4 posts cleared the 1% save-rate threshold:

| Rank | Show | Clip | Views | Like % | **Save %** |
|---:|---|---|---:|---:|---:|
| 1 | CBD | EP29 Tatyana Ali "waiting for Spence" | 1,135 | 7.7% | **2.47%** |
| 2 | SLAB | "told the judge he was a client" | 569 | 9.5% | **1.41%** |
| 3 | FS | "father announces your future at dinner" | 283 | 6.7% | **1.06%** |
| 4 | SLAB | "Uncle 3D little league pep talk" | 691 | 9.7% | **1.01%** |
| 5 | SLAB | "Mike Epps battling through the door" | 691 | 8.4% | 0.87% |
| 6 | CBD | OTR "I got straight A's" (Comeback-1) | 909 | 11.6% | 0.55% |
| 7 | FS | "more than your party planner" (Edit_004-v2) | 982 | 3.1% | 0.41% |

**Save rate is the signal.** Same as v2.

### Pattern 1 — CBD and SLAB still own the organic leaderboard
CBD #1 + #6, SLAB #2 + #4 + #5. Female-lead and specific-receipts dialogue indexes high.

**CBD action:** 5 Approved clips sitting unused. Now that EP29 source is confirmed (= #1 winner), cut a Part 2 directly from the EP29 master targeting the same emotional beat with a different line.

**SLAB action:** With SLB-7 newly tagged Posted, the From OTR sub-folder is the proven source path. 60 untagged videos are mostly episode masters. Source fresh Part 2 cuts from the masters; the OTR cuts are essentially exhausted.

### Pattern 2 — Favorite Son
Edit_005 was bumped from Scheduled → Posted (so it's live now). The 2 Approved (Edit_002 dad-confrontation, Edit_003 Sadie-foundation) are still the queue. Note: Edit_001-v2 and Edit_004-v2 (the two clips with TikTok metrics, including the #3 winner "party planner") are now untagged on Frame.io — likely re-cut and superseded. Confirm with Dioni before recommending re-posts from those source files.

### Pattern 3 — Schemers is genuinely Posted-heavy
Schemers Posted count went 5 → 8 (Social_001, _004, _005 retagged). 1 Approved left (Social_006). The trailer Edit_004 dropped from Approved to Untagged — flag for clarification. Schemers' channel strategy (archived from public feed) is still the open question, not the production.

### Pattern 4 — 35 & Ticking review-queue resolved
Edit_004 + Social Clip 1 retagged Posted (so Posted: 1 → 3). Several Needs Review clips were pushed to Feedback Given / Denied. 2 Approved remain (Edit_001, Social Clip 6). Review queue is shorter (4 left). **Move forward by posting the 2 Approved and revisiting Feedback Given clips.**

### Pattern 5 — LNJ review queue cleaned up
Eezo + IG CliP (NEW) retagged Posted (6 → 8). 1 Approved (IG Clip 5), 4 Needs Review (mostly subtitle variants). 20 untagged still need triage.

### Pattern 6 — Parking Lot
3 Posted now. 0 Approved. 2 Denied + 1 Feedback Given = pause posting until new social edits clear review.

### Pattern 7 — Bride To Be unchanged
0 Posted, 2 Approved. Post the 2 Approved to get a baseline.

## What structurally makes an organic win (unchanged)

Same patterns from v2 — opening punch, female lead confronting family figure, specificity, single-face framing, don't close the wound. Director/talking-head and carousel formats kill engagement.

## Action plan v3 — ranked by expected ROI

### Tier 1 (this week) — work the Approved queue
1. **CBD — post the 5 Approved + cut a fresh part-2 from EP29 master.** EP29 is now confirmed as the #1-winner source. Cut a different emotional beat from the same scene.
2. **Schemers — post the 1 Approved (Social_006).** Then resolve the channel-archive decision separately.
3. **35 & Ticking — post the 2 Approved (Edit_001 marriage convo, Social Clip 6 club confrontation).**
4. **FS — post the 2 Approved (Edit_002 dad scene, Edit_003 Sadie/Foundation).** Confirm Edit_001-v2 and Edit_004-v2 status with Dioni separately.
5. **LNJ — post the 1 Approved (IG Clip 5).**
6. **BTB — post the 2 Approved Social Clips.** First baseline data for the show.

### Tier 2 (next 2 weeks)
7. **SLAB — cut fresh Part 2s from the 60 untagged episode masters.** The OTR-source social cuts are exhausted.
8. **CBD — second EP-master sweep.** EP29 Posted-tag confirms the workflow; do the same for other CBD episodes that have strong scenes.
9. **35 & T — resolve 4 Needs Review subtitle variants.**

### Tier 3 (rethink cadence / unblock)
10. **Karma in Heels — apply Status tags before any further KIH recommendations.** This is the biggest data gap.
11. **Parking Lot — pause posting until the 1 Feedback Given clears or a new Approved appears.** Confirm Ep05 untag intent.
12. **LNJ — triage the 20 untagged clips** (subtitle variants vs unused vs already-posted).

## Caption template (unchanged from v2)

```
"<QUOTED DIALOGUE LINE FROM THE CLIP>"
<One-line emotional reframe — NOT a summary>
<Show title>. Streaming free on VURT.
@[top cast handle]  #VURT #<ShowHash> #<AudienceHash> #DramaTok
```

## How to improve — short version (v3)

1. **Tag KIH.** Without Status tags on KIH, you have a 108-video blind spot. Highest-leverage tagging task.
2. **Cut Part 2s from confirmed winner sources.** EP29 (CBD), OTR scenes (SLAB), the dad-receipts beat (CBD ComeBack-2) — the source paths are now identified, just need new edits.
3. **Work the 18 Approved queue** before hunting for new material.
4. **Confirm two open tag flips with Dioni:** PL Ep05 (was Posted, now untagged) and FS Edit_001-v2 / Edit_004-v2 (were Posted with metrics, now untagged).
5. **Quote, don't summarize.** Same as v2.

## Files + where to look

- Inventory full (all 371 videos with tags): `Skills/vurt-captions/footage/inventory_full.json`
- Posted-only compact view: `Skills/vurt-captions/footage/inventory_posted.json`
- Per-show clip maps: `Skills/vurt-captions/footage/<show-slug>/CLIP_MAP.md`
- Walker that built the v3 inventory: `Skills/vurt-captions/scripts/inventory_all_posted.py` (run via Zo bash so VURT_FRAMEIO_* secrets are available)
- Daily save rate leaderboard: automated into `daily-report.py` → VURT Daily email

## Open follow-ups

- Confirm `PARKING_LOT-Ep05-_Social Edit-004-v2.mp4` untag was intentional.
- Confirm `VURT_FavoriteSon_Social_Edit_001-v2.mp4` and `Edit_004-v2.mp4` untag (these had real TikTok metrics including the #3 organic winner).
- Apply Status tags to Karma in Heels (108-video gap).
- Triage Schemers' 31 untagged + LNJ's 20 untagged + 35&T's 41 untagged for any forgotten Posted cuts.
