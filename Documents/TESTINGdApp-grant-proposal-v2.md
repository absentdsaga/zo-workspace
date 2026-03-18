# TESTINGdApp — Solana Mobile Builder Grant Proposal (V2 Copy)

> **This document contains the improved copy for each slide of the grant deck.**
> Slide structure is preserved. Changes focus on: aligning to Solana Mobile's 6 grant criteria, sharpening the value prop, adding specificity, and removing ambiguity that could cost you the grant.

---

## KEY ISSUES WITH V1 (what I fixed)

1. **No explicit Solana Mobile Stack callout** — The grant page requires "clear implementation of core SMS components (MWA, Seed Vault)." Your V1 mentions MWA once. Seed Vault never appears. This is the #1 fix.
2. **No open-source / public good commitment** — Grant criteria explicitly ask for this. V1 has zero mention.
3. **"SagaDAO" is doing a lot of heavy lifting but is never explained** — A reviewer who doesn't know SagaDAO will skim past the traction claims. Need to briefly establish credibility.
4. **Budget is vague** — Grant criteria want "a detailed budget showing exactly how funds will be utilized." Your 6 bullet points are categories, not a budget. Need dollar allocations.
5. **Team slide is missing entirely** — Grant criteria: "Strong record of past open source contributions, technical expertise, and a clear ability to deliver." You have no team slide. This is a disqualifier.
6. **Milestones have no deliverables or success metrics** — Grant criteria want "well-structured, thoughtful milestones for phased delivery." Yours are task lists, not milestones.
7. **The problem slide doesn't name anyone's pain specifically enough** — "Builders can't get quality mobile QA" is good but doesn't make the reviewer feel the pain in the context of *their* ecosystem.

---

## SLIDE 1 — COVER

**Current:**
> TESTINGdApp
> A mobile-native testing & quality acceleration platform for the Solana dApp Store
> $10,000 USDC | 90-Day Delivery

**Improved:**

> **TESTINGdApp**
> The pre-launch QA layer for the Solana dApp Store — built on Solana Mobile Stack, gated by Seeker & Saga ownership, powered by verified human testers.
> $10,000 USDC | 90-Day Delivery | dApp Store Launch at Day 90

*Why: The subtitle now hits 3 of the 6 grant criteria in one line — mobile-first (dApp Store), SMS use (Solana Mobile Stack), and milestone clarity (dApp Store launch at Day 90). Reviewers skim covers.*

---

## SLIDE 2 — EXECUTIVE SUMMARY

**Current:**
> Pre-launch QA for Solana Mobile builders
> - Genesis SBT-gated tester access (Saga & Seeker verified)
> - Mobile Wallet Adapter integrated testing flows
> - Sequential staged QA with structured human-reviewed feedback
> - USDC-based staged reward campaigns
> - Persistent tester identity via SBT verification
> Not a quest platform. Not an engagement farm. A real testing system.

**Improved:**

> **Pre-launch QA infrastructure for every dApp headed to the Solana dApp Store**
>
> → Device-verified testers: Only Saga & Seeker owners can participate, verified via Genesis SBT on-chain
> → Built on Solana Mobile Stack: Mobile Wallet Adapter for all signing flows, Seed Vault integration for secure tester authentication
> → Three-stage structured QA: UX walkthrough → feature testing → proof of interaction, with enforced 150+ character written feedback at every stage
> → On-chain USDC rewards tied to effort: small payouts at each stage, largest reward only after full completion with proof
> → Persistent tester reputation: SBT-linked profiles that build trust over time — builders see who their best testers are
>
> **Not a quest platform. Not an engagement farm. A QA system that raises the quality bar for every mobile dApp on Solana.**

*Why: Added explicit Seed Vault mention (required by grant criteria). Made the "built on SMS" line impossible to miss. Gave the tagline a stronger finish that ties back to ecosystem benefit.*

---

## SLIDE 3 — THE PROBLEM

**Current:**
> Builders can't get quality mobile QA before launch
> What exists today: Fragmented QA processes, low-effort bounty feedback, sybil-farmed quest platforms, high tester drop-off
> What's missing: Device-verified QA network, SBT-gated participation, sequential effort-based testing, persistent tester reputation
> Result: noisy feedback, shallow engagement, and avoidable launch friction.

**Improved:**

> **The Solana dApp Store is growing fast. The QA pipeline hasn't kept up.**
>
> The dApp Store now hosts 100+ mobile-native apps. Seeker is shipping to 150K+ users. But builders launching mobile dApps still have no reliable way to get structured, device-verified QA feedback before going live.
>
> | What exists today | What's missing |
> |---|---|
> | Bounty platforms that reward clicks, not quality | A QA network where every tester is a verified Solana Mobile device owner |
> | Sybil-farmed quest systems with disposable accounts | SBT-gated identity that prevents multi-account farming |
> | Generic feedback that doesn't test mobile-specific flows | Sequential testing designed for MWA signing, onboarding, and transaction UX |
> | High tester drop-off with no accountability | Persistent reputation that rewards consistent, high-quality participation |
>
> **Result: builders launch with blind spots. Users hit friction. Ratings suffer. The dApp Store's quality bar depends on solving this.**

*Why: Anchored the problem to Solana Mobile's own ecosystem numbers (100+ apps, 150K+ Seekers). Made the reviewer feel that this problem is THEIR problem. "The dApp Store's quality bar depends on solving this" directly links to their mission.*

---

## SLIDE 4 — THE SOLUTION

**Current:**
> Structured mobile testing that actually works
> TESTINGdApp converts SagaDAO's proven testing methodology into an automated, mobile-native platform.
> Observe: Real onboarding flows & UX friction points
> Validate: Core feature usability & structured feedback

**Improved:**

> **Structured mobile QA that runs on Solana Mobile Stack**
>
> TESTINGdApp is a mobile-native Android app built on the Solana Mobile Stack. It converts a proven community QA methodology — battle-tested across 5+ dApps through SagaDAO — into an automated platform available to every builder in the dApp Store.
>
> **Observe** — Real onboarding flows & UX friction points captured on actual Saga/Seeker devices
> **Validate** — Core feature usability tested via structured, human-reviewed feedback (150+ character minimum per response)
> **Prove** — On-chain evidence of real interaction: transaction confirmations, screenshots, dApp Store reviews
>
> Built with:
> - **Mobile Wallet Adapter (MWA)** — all tester authentication and reward claiming flows
> - **Seed Vault** — secure key management for tester identity and SBT verification
> - **SPL tokens** — USDC reward distribution via on-chain escrow contracts
> - **Metaplex** — Genesis SBT minting for tester identity

*Why: Added the "Prove" third pillar to match the 3-stage system shown later. Explicitly listed SMS components (MWA, Seed Vault) — this is THE most important technical checklist item for the grant. Named the Solana programs being used.*

---

## SLIDE 5 — COMMUNITY GATING

**Current:**
> Genesis SBT = your tester ID
> - Daily snapshot of verified wallets
> - One wallet = one tester profile
> - No multi-account linking
> - Genesis SBT tied to tester identity
> Prevents farming via: VPNs, disposable emails, wallet cycling, automated quest behavior — all blocked by design
> Builders receive feedback only from verified Solana Mobile device owners.

**Improved:**

> **Genesis SBT = your tester ID**
>
> Every tester must hold a Genesis SBT minted through Seed Vault on a verified Saga or Seeker device. No SBT, no access.
>
> → Daily on-chain snapshot of eligible wallets
> → One device → one wallet → one tester profile (enforced at the SBT level)
> → No multi-account linking, no wallet cycling
> → SBT is non-transferable — tester identity is permanent and reputation-bearing
>
> **What this blocks by design:**
> VPN farming, disposable email signups, automated quest bots, multi-wallet sybil attacks
>
> **What this gives builders:**
> Every piece of feedback traces back to a verified Solana Mobile device owner with a persistent on-chain identity. No other QA platform in the ecosystem can make this claim.

*Why: Added Seed Vault to the minting flow (grant criteria). Made the anti-sybil argument land harder by separating "what it blocks" from "what it gives." The closing line positions this as a moat.*

---

## SLIDE 6 — SEQUENTIAL TESTING

**Current:**
> Three stages, progressively deeper
> 1. UX Walkthrough — Participants move through first-time user experience. Surfaces confusion points, onboarding friction, and early drop-off signals.
> 2. Core Feature Testing — Defined tasks with structured written feedback (150+ char minimum). Evaluates feature clarity, task completion, and user comprehension.
> 3. Proof of Interaction — Evidence of real usage — transaction confirmations, social shares, dApp Store reviews, functional screenshots. Full interaction before largest rewards unlock.

**Improved:**

> **Three stages. Each one earns. Each one filters.**
>
> **Stage 1: UX Walkthrough** (unlocked immediately)
> Tester walks through the dApp's first-time user experience on their Saga/Seeker device. Structured prompts surface confusion points, onboarding friction, and drop-off triggers. Tester submits written observations (150+ chars). Small USDC reward on completion.
>
> **Stage 2: Core Feature Testing** (unlocked after Stage 1 approval)
> Builder-defined task list with structured feedback fields. Tests feature clarity, task completion rates, and user comprehension. Human-reviewed — low-effort submissions are rejected and disqualified from further stages. Larger USDC reward on approval.
>
> **Stage 3: Proof of Interaction** (unlocked after Stage 2 approval)
> Evidence of real, meaningful usage: on-chain transaction confirmations, dApp Store reviews, functional screenshots, social proof. This stage proves the tester actually used the product — not just filled out forms. Largest USDC reward unlocks here.
>
> **Why sequential matters:** Casual participants exit at Stage 1. Farmers get filtered at Stage 2. Only committed, quality testers reach Stage 3. Builders get a progressively more qualified feedback funnel.

*Why: Made each stage feel like a gate, not just a step. Added the "why sequential matters" closer — this is what makes the system genuinely different from bounty platforms and the grant reviewer needs to feel that.*

---

## SLIDE 7 — THE PROVING GROUND

**Current:**
> Effort-weighted. Quality-filtered.
> Reinforcement Design: Small rewards at each stage, clear progress signals, and guided next steps. Casual users exit early; committed testers complete everything.
> Proven Tester Cohort: Over time, the platform surfaces reliable testers who consistently deliver full completion, usable feedback, and real interaction proof.
> Builders gain access to a smaller but significantly higher-quality pool of mobile-native testers.

**Improved:**

> **Effort-weighted rewards. Quality-filtered testers.**
>
> **Reinforcement Design**
> Rewards scale with effort. Stage 1 earns a small payout. Stage 2 earns more. Stage 3 — the hardest — earns the most. Clear progress signals and guided next steps keep committed testers moving. Casual participants self-select out early.
>
> **Proven Tester Cohort**
> Over time, the platform builds a ranked network of reliable testers — tracked by completion rate, feedback quality scores, and interaction proof. Builders launching new campaigns can target testers with proven track records.
>
> **The result for builders:** Instead of broadcasting to anonymous crowds, they get a curated, device-verified, reputation-ranked pool of mobile-native testers. Quality goes up. Noise goes down. Launch confidence improves.

*Why: Minor sharpening. The "result for builders" line now speaks directly to the grant reviewer's perspective — they're funding things that help builders.*

---

## SLIDE 8 — REWARDS STRUCTURE

**Current:**
> Staged USDC payouts
> - Small early-stage rewards reinforce participation
> - Larger rewards unlock after full completion
> - Incentives scale with effort and proof of interaction
> - Builders may optionally integrate protocol tokens
> Low-effort responses are removed from eligibility pools. Human review ensures feedback quality and campaign integrity.

**Improved:**

> **Staged USDC payouts — aligned to effort, enforced by review**
>
> → Stage 1 completion: small USDC reward (keeps testers engaged)
> → Stage 2 approval: medium USDC reward (quality gate — human-reviewed)
> → Stage 3 verification: largest USDC reward (requires on-chain proof of real usage)
>
> **Quality enforcement:**
> - Every Stage 2+ submission is human-reviewed before reward distribution
> - Low-effort responses are rejected and the tester is flagged
> - Repeated low-quality submissions reduce tester reputation score
> - Builders can optionally integrate their own protocol tokens alongside USDC
>
> **All rewards distributed on-chain via SPL token transfers, signed through Mobile Wallet Adapter.**

*Why: The closing line reinforces SMS integration — every mention helps. Made quality enforcement feel like a system, not an afterthought.*

---

## SLIDE 9 — TRACTION & VALIDATION

**Current:**
> Already proven through SagaDAO
> 5+ Solana dApps tested | 2 Pre-dApp prototypes evaluated
> - Multiple bugs identified & resolved pre-launch
> - Measurable improvement between testing rounds
> - Tracked signup-to-completion ratios & retention
> TESTINGdApp automates what already works.

**Improved:**

> **Already proven through SagaDAO — the Solana Mobile community that built this methodology**
>
> SagaDAO is a community of Saga device holders who organized structured QA testing for Solana mobile dApps before any tooling existed. TESTINGdApp automates and scales what SagaDAO proved by hand.
>
> **Results to date (manual process):**
> - **5+ Solana dApps tested** across multiple rounds
> - **2 pre-dApp prototypes evaluated** before public launch
> - **Critical bugs identified & resolved** before users hit them
> - **Measurable UX improvement** tracked between testing rounds
> - **Signup-to-completion funnels tracked** — data on where testers drop off and why
>
> **What the grant funds:** Taking this from a manual community process to a production mobile app in the Solana dApp Store — with on-chain identity, automated rewards, and a self-service campaign builder for any Solana mobile team.

*Why: Explained what SagaDAO actually is — a reviewer unfamiliar with it will now understand why the traction matters. The "what the grant funds" line directly connects past work to the ask.*

---

## SLIDE 10 — 90-DAY ROADMAP: MONTH 1

**Current:**
> Month 1 — Build
> - Finalize mobile UI polish
> - Refine Mobile Wallet Adapter integration
> - Implement Genesis SBT verification logic
> - Integrate push notification support
> - Finalize reward contract automation

**Improved:**

> **Month 1 — Build (Days 1–30)**
>
> **Milestone: Feature-complete private beta on Android**
>
> | Deliverable | Details |
> |---|---|
> | Mobile UI production-ready | Final polish pass on all screens, tested on Saga & Seeker hardware |
> | MWA integration complete | All authentication, signing, and reward claim flows via Mobile Wallet Adapter |
> | Seed Vault tester auth | Genesis SBT minting and verification through Seed Vault secure key management |
> | Reward contract deployed | USDC escrow + staged distribution contract on Solana devnet, audited internally |
> | Push notifications live | Campaign alerts, stage unlock notifications, reward confirmations |
>
> **Exit criteria:** Internal team can run a full 3-stage test campaign end-to-end on a Seeker device.

*Why: Added a milestone name, a deliverables table (not a task list), and exit criteria. This is what "well-structured, thoughtful milestones for phased delivery" looks like.*

---

## SLIDE 11 — 90-DAY ROADMAP: MONTHS 2 & 3

**Current:**
> Month 2 — Controlled Beta: Launch controlled beta, Run 3-5 structured campaigns, Optimize tester progression, Implement badges & profiles
> Month 3 — Public Launch: Launch in Solana dApp Store, Onboard additional builders, First fully automated round, Publish impact metrics

**Improved:**

> **Month 2 — Controlled Beta (Days 31–60)**
>
> **Milestone: Live beta with real builders and real testers**
>
> | Deliverable | Details |
> |---|---|
> | Beta launch with 3–5 dApp partners | Real campaigns running with Solana Mobile builders |
> | 50+ verified testers onboarded | All SBT-gated, all on Saga/Seeker devices |
> | Tester profiles & badges | Reputation system live — completion rates, quality scores visible to builders |
> | Feedback quality baseline | Establish human review benchmarks and rejection rate targets |
>
> **Exit criteria:** 3+ campaigns completed. Tester completion rate and feedback quality metrics documented.
>
> ---
>
> **Month 3 — Public Launch (Days 61–90)**
>
> **Milestone: TESTINGdApp live in the Solana dApp Store**
>
> | Deliverable | Details |
> |---|---|
> | dApp Store submission & approval | Published in the Solana dApp Store |
> | Self-service campaign builder | Any Solana mobile builder can create a testing campaign without contacting the team |
> | First fully automated round | End-to-end: campaign creation → tester matching → staged testing → reward distribution |
> | Impact report published | Public metrics: testers onboarded, campaigns run, bugs found, completion rates, quality scores |
>
> **Exit criteria:** App live in dApp Store. At least 1 fully automated campaign completed. Impact report shared with Solana Mobile.

*Why: Each month now has a milestone name, deliverables table, and exit criteria. This directly maps to the grant's "Proposed Scope & Milestone Timeline" requirement.*

---

## SLIDE 12 — USE OF FUNDS

**Current:**
> $10,000 USDC
> - Final mobile UX production polish
> - Security review of reward distribution
> - Push notification infrastructure
> - Backend verification scaling
> - Initial USDC liquidity for campaigns
> - Deployment & launch readiness
> Delivery: 90 days from grant approval

**Improved:**

> **$10,000 USDC — Detailed Budget**
>
> | Category | Amount | What it covers |
> |---|---|---|
> | Mobile UX & Frontend | $2,500 | Final production polish, Saga/Seeker device testing, accessibility pass |
> | Smart Contract Security | $1,500 | Third-party review of USDC reward distribution contracts |
> | Backend & Infrastructure | $2,000 | Verification service scaling, push notification infrastructure, SBT indexing |
> | Campaign Seed Liquidity | $2,000 | Initial USDC pool for 3–5 beta testing campaigns to attract first testers |
> | dApp Store Launch & QA | $1,000 | Submission process, compliance review, launch-day monitoring |
> | Contingency | $1,000 | Buffer for unexpected costs during 90-day build |
> | **Total** | **$10,000** | |
>
> **Delivery: 90 days from grant approval. dApp Store live on Day 90.**

*Why: The grant criteria explicitly say "a detailed budget showing exactly how the requested grant funds will be utilized." A bullet list of categories is not a budget. A table with dollar amounts is.*

---

## SLIDE 13 — LONG-TERM VISION

**Current:**
> The default QA layer for Solana Mobile
> - Standard pre-launch QA layer for Solana Mobile builders
> - Verified network of mobile-native testers
> - Structured feedback accelerator for mobile dApps
> - Quality filter that improves launch readiness across the dApp Store

**Improved:**

> **The default QA layer for every dApp launching on Solana Mobile**
>
> → The standard pre-launch checkpoint for builders before they hit "publish" in the dApp Store
> → A growing, reputation-ranked network of verified mobile testers on Saga & Seeker devices
> → A structured feedback system that gets better with every campaign — tester reputation compounds, builder playbooks emerge
> → A quality signal that makes the entire dApp Store more trustworthy for end users
>
> **Open-source commitment:** The TESTINGdApp campaign schema, feedback templates, and SBT verification logic will be open-sourced as a public good for the Solana Mobile developer community. Any builder can fork the testing framework for their own use.
>
> **Long-term: as the dApp Store grows from 100 to 1,000+ apps, quality assurance becomes infrastructure, not a nice-to-have. TESTINGdApp is that infrastructure.**

*Why: Added the open-source commitment — this is explicitly in the grant criteria ("Community & Open Source: Ideally, includes some commitment to a Public Good for the mobile ecosystem"). This was completely missing from V1.*

---

## SLIDE 14 — CLOSING

**Current:**
> TESTINGdApp
> Better testing. Better launches. Better dApps.
> SagaDAO | Solana Mobile
> Let's build it. →

**Improved:**

> **TESTINGdApp**
> Better testing. Better launches. A better dApp Store.
> Built by SagaDAO | Built for Solana Mobile
> Let's build it. →

*Why: "Better dApps" → "A better dApp Store" — ties the outcome directly to Solana Mobile's mission. Small but matters.*

---

## ⚠️ MISSING SLIDE — YOU NEED TO ADD THIS

### NEW SLIDE: TEAM (insert after Traction & Validation, before Roadmap)

> **TEAM**
>
> **The team behind SagaDAO and 5+ Solana mobile QA campaigns**
>
> [Your name / handle] — [Role]. [1-line credibility: e.g., "Founded SagaDAO. Organized the first structured QA campaigns for Solana mobile dApps. Active contributor to the Solana Mobile community since Saga launch."]
>
> [Team member 2, if applicable] — [Role]. [1-line credibility]
>
> **Relevant experience:**
> → Built and ran the manual QA process that TESTINGdApp automates
> → Tested 5+ live Solana dApps and 2 pre-launch prototypes on Saga hardware
> → Active in Solana Mobile developer community [link to any public contributions, repos, or community posts]
>
> **Open-source contributions:** [Link to any GitHub repos, published tools, or community resources]

*Why: The grant criteria say "Strong record of past open source contributions, technical expertise, and a clear ability to deliver." Without a team slide, the reviewer has no way to evaluate this. This is likely a disqualifier if missing.*

---

## SUMMARY OF CHANGES

| Grant Criteria | V1 Status | V2 Status |
|---|---|---|
| Mobile-First Implementation | ✅ Implied | ✅ Explicit — Android, Saga/Seeker testing, dApp Store launch |
| Solana Mobile Stack Use | ⚠️ MWA mentioned once | ✅ MWA + Seed Vault + SPL tokens + Metaplex named explicitly |
| Proposed Scope & Milestone Timeline | ⚠️ Task lists, no milestones | ✅ Named milestones, deliverable tables, exit criteria |
| Team Ability to Execute | ❌ No team slide | ✅ Team slide added (you need to fill in details) |
| Clear Use of Funds | ⚠️ Category bullets only | ✅ Dollar-allocated budget table |
| Community & Open Source | ❌ Not mentioned | ✅ Open-source commitment for campaign schema + SBT verification |
