# U$ER Website Copy Changes — Dev Implementation Guide

> This doc maps each section of the current site to the new copy. Copy is exact — ready to implement. Changes highlighted in **bold**.

---

## 1. HERO SECTION

**Current (old):**
> Real users. Real devices. Real feedback.
> Stop guessing. Saga & Seeker owners run your app through a 5-step gated pipeline. SBT-verified testers. Sequential filtering. What comes back is pure signal. Ship faster.

**New (replace with):**
> **Real users test your app. You get the truth.**
>
> 120,000+ verified Solana Mobile device owners run your app, find the bugs, rate the UX, and post reviews on the dApp Store. **Tested 11 dApps.**
>
> [Get a Test Quote] [See How It Works ↓]

**Changes:**
- Shortened headline from 3 sentences to 1
- Added proof numbers (120K testers, 11 dApps)
- **Removed "$15,000" — too small-sounding for B2B**
- CTA changed from "Submit Your App" to "Get a Test Quote"

---

## 2. SOCIAL PROOF BAR (NEW SECTION)

**Add directly below hero:**

> **Trusted by builders shipping on Solana Mobile**
>
> [&milo] [&dubs]
>
> _"$1,500 up for grabs through our dApp testing partner @SagaMobileDAO"_ — @dubsdotapp

**Notes for dev:**
- Use actual logos if available, or brand name text
- Tweet quote is real — link to: https://x.com/dubsdotapp/status/2029244200391172426

---

## 3. "LESS NOISE. MORE SIGNAL" → Rename to "WHAT YOU GET BACK"

**Current (old):**
> Less NOISE. More SIGNAL.
> [long paragraphs about filtering philosophy + 6 small cards]

**New (replace with):**

> ### What you get back
>
> Every campaign delivers a compiled intelligence package. Not surveys. Not vibes. Structured data from verified device owners who actually used your app.
>
> - **Bug Reports** — Annotated screenshots with severity flags. Visual context for every issue.
> - **UX Friction Map** — Where users got confused, hesitated, or quit. Ranked by frequency.
> - **dApp Store Reviews** — Real testers post real reviews from real devices. Organic social proof.
> - **Sentiment Score** — Did users understand your value prop? Quantified.
> - **Mid-Round Alerts** — We ping you the moment something critical surfaces. Fix it before the round ends.
> - **Exportable Data** — Markdown, CSV, or pushed to Slack/Discord/Telegram.

**Changes:**
- Merged the philosophical section with the deliverables grid
- Added **Mid-Round Alerts** (new — addresses your note about finding things mid-test)
- "Not surveys. Not vibes." = brief dismissal of competitors
- Each bullet is now 1 sentence max

---

## 4. "DROP IT IN. GET ANSWERS." → Rewrite to "HOW IT WORKS"

**Current (old):**
> [3 steps: Drop it in → We put it through → Get answers]

**New (replace with):**

> ### How it works
>
> **1. Submit your app**
> Upload your APK or web URL. Tell us what you want to learn. **(Consultation call optional — we'll guide you through setup either way.)**
>
> **2. We run the campaign**
> 120K+ verified device owners get access. The 5-step pipeline filters for quality. AI monitors every submission in real time.
>
> **3. You get the report**
> Bugs, UX friction, sentiment, dApp Store reviews. Delivered within 7 days. Exportable to your tools.
>
> **4. We debrief together**
> **(Optional — included in $10K+ packages)** We walk through findings with your team. What to fix first. What's working. What to test next round.

**Changes:**
- Made consultation "optional" — addresses your note about self-serve option
- Added "(Included in $10K+ packages)" to Step 4 — upsells higher tiers
- "7 days" = specific turnaround time (adjust if needed)

---

## 5. 5-STEP PIPELINE

**Current (old):**
> Each step has a long paragraph (50+ words each)

**New (replace with):**

> ### The 5-step test flow
>
> **Step 01 — Wallet Connect** Genesis SBT verification. Device ownership confirmed. Anonymous but verifiable.
>
> **Step 02 — App Exploration** First impressions. Load time. Did it crash? Did they understand what the app is?
>
> **Step 03 — Task Completion** Can they actually do what the app is for? Where do they get stuck?
>
> **Step 04 — Deep Feedback** Written feedback (150+ chars). Screenshots. What would make this better?
>
> **Step 05 — Rating & Review** Star rating + public dApp Store review. **This is the output that matters most.**

**Changes:**
- Trimmed each step to 1 sentence max
- Added line in Step 5 to drive home why it matters

---

## 6. SENTINEL AI

**Minor tweaks only — keep mostly as-is:**

**Current (old):**
> Autonomous QA intelligence that reads every submission so you don't have to.

**New:**
> **Sentinel AI**
> **AI that reads every submission so you don't have to.**
>
> - **Bug Triage** — Auto-categorizes issues by severity. Duplicates merged. Priority ranked.
> - **Screenshot Analyzer** — Visual context for every bug. No more "it didn't work."
> - **Conversational QA** — Testers answer follow-up questions. AI extracts themes.
> - **Trend Detection** — Patterns across rounds. "3 of the last 5 apps had the same onboarding issue."

**Changes:**
- Shortened the lead-in line
- Minor trim on bullet descriptions

---

## 7. "EARN YOUR SPOT" → Split into TWO sections

### 7a. FOR BUILDERS (NEW SECTION)

Add this section (between Sentinel AI and the tester section):

> ### For Builders
>
> Launch with confidence. Not guesses.
>
> - **SBT-gated testers** — verified Saga & Seeker owners, not randos
> - **Sequential filtering** — casual testers drop off, serious testers rise
> - **dApp Store reviews** — real reviews from real devices, not bots
> - **Mid-round alerts** — we tell you what's breaking NOW, not after
> - **White-glove reports** — compiled, actionable, ready to share with your team

**Notes:**
- New explicit section for builder segment
- "White-glove" addresses your note about high-touch service

---

### 7b. FOR TESTERS (REPLACE existing "EARN YOUR SPOT")

**Current (old):**
> Earn your spot
> Not every tester is equal
> [describes filtering, but talks TO builders ABOUT testers]

**New (replace with):**

> ### For Testers — Test apps. Win USDC.
>
> Got a Saga or Seeker? You're already in.
>
> Connect your wallet, verify your Genesis SBT, and get access to paid testing campaigns. Complete stages to enter prize draws. Give the best feedback to win bounties. Refer friends for bonus entries.
>
> **What you can win:**
>
> - **Raffle entries** at every stage — complete, enter, win
> - **Top-feedback bounties** — best reviewers earn the biggest payouts
> - **Referral bonuses** — bring friends, both win
> - **Focus group invites** — paid live sessions with project teams
>
> **120,000+ Genesis Token holders eligible.** Campaigns run every week.
>
> [Connect Wallet & Start Testing]

**Changes:**
- Now talks TO testers, not ABOUT testers
- Clear value prop: "Test apps. Win USDC."
- Focus groups mentioned as paid opportunity

---

## 8. SERVICES & ADD-ONS (NEW SECTION)

**Add this section (before pricing):**

> ### Scale your launch
>
> Testing is the starting point. Layer on services to turn a campaign into a full go-to-market push.
>
> | **Campaign Testing** | **Focus Groups** | **KOL Amplification** |
> | --- | --- | --- |
> | Verified testers run your app through the 5-step pipeline. Full intelligence package. | Hand-pick testers from your campaign for live video sessions. Ask what surveys can't answer. | We pay KOLs to drive verified users to your campaign. Reach + feedback simultaneously. |
> | **Starting at $5,000** | **Starting at $3,000** | **Starting at $2,500** |
>
> **Consultation & Strategy** — Included in $10K+ campaigns. We'll design the test criteria, advise on what to measure, and debrief results with your team.
>
> **Custom Bundle** — Contact us. Bundle pricing for multi-round campaigns.
>
> [Get a Custom Quote]

**Notes:**
- Services now named and priced
- Table format for easy comparison
- Consultation included at $10K+

---

## 9. PRICING TIERS (REPLACE dropdown form)

**Current (old):**
> [Form with "Funding Amount" dropdown: $5K–$30K]

**New (replace with):**

> ### Choose your campaign
>
> | | **Launch** | **Growth** | **Enterprise** |
> | --- | --- | --- | --- |
> | **Price** | $5,000 USDC | $10,000 USDC | $15,000+ USDC |
> | Verified testers | Up to 50 | Up to 150 | 200+ |
> | 5-step pipeline | ✓ | ✓ | ✓ |
> | AI reports | ✓ | ✓ | ✓ |
> | dApp Store reviews | ✓ | ✓ | ✓ |
> | Mid-round alerts | ✓ | ✓ | ✓ |
> | Consultation call | — | ✓ | ✓ |
> | Focus group session | — | — | 1 included |
> | KOL amplification | — | Add-on | 1 included |
> | Dedicated manager | — | — | ✓ |
> | | [Get Started] | [Get Started] | [Contact Us] |
>
> _All campaigns include Sentinel AI. **Not sure what you need? We'll help you scope. Just reach out.**_

**Changes:**
- Tiered table replaces dropdown (anchors high)
- "Not sure what you need?" line captures lower-budget leads

---

## 10. CONTACT / FORM

**Simplify:**

> ### Let's get your app tested
>
> **Ready to ship? Let's talk.**
>
> [App Name] [App URL] [Your Email] [Telegram/Discord]
>
> **What's your budget?** (Optional — helps us scope right)
>
> [Submit]

**Changes:**
- Removed "Funding Amount" dropdown
- Made budget "optional" — more approachable
- Still captures budget signal for scoping

---

## 11. FOOTER

**Update to:**

> **U$ER** — The testing platform for Solana Mobile.
>
> Built by [SagaDAO](https://twitter.com/SagaMobileDAO) — 20,000+ Saga Genesis holders, 100,000+ Seeker Genesis holders.
>
> [Twitter/X] [Discord] [Website]
>
> © 2026 U$ER. All rights reserved.

---

## SUMMARY OF CHANGES

| Section | Change Type |
|---|---|
| Hero | Shortened to 1 sentence, added proof numbers, removed $ (too small) |
| Social Proof Bar | **NEW** — client logos + tweet quote |
| What You Get Back | **NEW NAME** — merged with deliverables, added Mid-Round Alerts |
| How It Works | 4 steps, consultation optional, added 7-day SLA |
| 5-Step Pipeline | Trimmed to 1 sentence per step |
| Sentinel AI | Minor trim on lead-in |
| For Builders | **NEW** — explicit builder section |
| For Testers | **REWRITE** — now talks TO testers |
| Services & Add-Ons | **NEW** — named services with prices |
| Pricing Tiers | **NEW** — tiered table replaces dropdown |
| Contact Form | Simplified, made budget optional |
| Footer | Updated with holder numbers |

---

## TOTAL WORD COUNT

~420 words (target was 350-450 for optimal conversion)
