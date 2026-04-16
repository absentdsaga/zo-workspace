# U$ER -- Master Grant & Hackathon Application
## The Open Mobile QA Layer for Solana

> **Last updated:** April 12, 2026
> **Use this document as:** A modular source for any grant application, hackathon submission, or pitch. Copy the sections you need, adapt the framing to match the program's criteria.

---

## TABLE OF CONTENTS

1. [One-Liner & Elevator Pitch](#1-one-liner--elevator-pitch)
2. [The Problem](#2-the-problem)
3. [The Solution](#3-the-solution)
4. [How It Works](#4-how-it-works)
5. [Traction & Validation](#5-traction--validation)
6. [Competitive Landscape](#6-competitive-landscape)
7. [Team](#7-team)
8. [Technical Architecture](#8-technical-architecture)
9. [Roadmap & Milestones](#9-roadmap--milestones)
10. [Budget](#10-budget)
11. [Ecosystem Impact & Public Good](#11-ecosystem-impact--public-good)
12. [Appendix A: Solana Frontier Hackathon Submission](#appendix-a-solana-frontier-hackathon)
13. [Appendix B: Solana Mobile Builder Grant (RFP Track)](#appendix-b-solana-mobile-builder-grant)
14. [Appendix C: General Web3 Grant Template](#appendix-c-general-web3-grant)

---

## 1. ONE-LINER & ELEVATOR PITCH

**One-liner:**
U$ER is the device-verified, community-powered QA layer for the Solana dApp Store -- the open-ecosystem equivalent of TestFlight and Firebase Test Lab.

**Elevator pitch (30 seconds):**
The Solana dApp Store has 435+ apps and zero structured QA infrastructure. Builders ship and pray. U$ER fixes that. We connect dApp teams with SBT-verified Saga and Seeker device owners who test their apps through three-stage paid campaigns. We've already tested 11 dApps, earned $3,000 from live clients, and the app is ~80% built. No one else does this. We're asking for funding to cross the finish line and launch in the dApp Store within 90 days.

**Elevator pitch (60 seconds):**
Every mature app platform has QA infrastructure. Apple has TestFlight. Google has Firebase Test Lab. The Solana dApp Store -- 435+ apps, 150K+ Seeker users across 50+ countries -- has nothing. Builders either skip mobile QA entirely or rely on quest platforms that measure clicks, not quality.

U$ER is the missing layer. We gate every tester by their Genesis SBT -- a non-transferable token minted on verified Saga or Seeker hardware. 120,000+ devices are eligible on day one. Testers move through three sequential stages: UX walkthrough, core feature testing, and proof of interaction. Each stage filters low-effort participants. Builders get structured bug reports, UX friction maps, and on-chain proof of real usage. Testers compete for USDC bounties.

This isn't a concept. SagaDAO's Innovation Lab has been running this process manually since early 2026. We've tested 11 dApps, caught critical bugs pre-launch, and earned $3,000 from paying clients like Dubs and &milo -- with ~80% flowing directly to testers. The app is built and in testing. We need funding to finalize Solana Mobile Stack integration, run beta campaigns, and launch in the dApp Store.

Zero direct competitors. Revenue before grant. Monopoly position in structured, device-verified QA for the open mobile ecosystem.

---

## 2. THE PROBLEM

### The Gap

The Solana dApp Store grew from 160 to 435+ apps in under 6 months. Seeker shipped to 150,000+ users across 50+ countries. The ecosystem is scaling fast -- but there is zero structured QA infrastructure for mobile dApps.

### What Builders Do Today (and Why It Fails)

| Current Approach | Why It Fails |
|---|---|
| **Skip QA entirely** -- ship and pray | Users hit Seeker-specific bugs never caught in dev. Bad reviews tank app ratings on day one. |
| **Quest platforms** (Layer3, Galxe, Zealy) | Measures clicks, not quality. Output is vanity metrics, not bug reports. No device verification. |
| **Superteam Earn bounties** | Unstructured, one-off tasks. No device verification. No sequential test flows. No accountability. |
| **Discord recruiting** | Inconsistent feedback, high drop-off, sybil-vulnerable, no quality enforcement. |
| **Traditional QA** (UserTesting, Applause) | $30K-$100K/year. No crypto knowledge. Self-reported device info. Pricing excludes 99% of Solana teams. |

### The Comparison That Matters

Apple has TestFlight. Google has Firebase Test Lab. The Solana dApp Store has nothing equivalent.

That's the gap. U$ER fills it -- but decentralized, incentivized, and built for the open mobile ecosystem.

---

## 3. THE SOLUTION

### U$ER: The Open Mobile QA Layer

U$ER is a mobile-native Android app that connects dApp builders with verified Saga & Seeker testers through paid, structured testing campaigns.

**For Builders:**
- Create a testing campaign: define tasks, fund the USDC prize pool, specify what to test
- Receive structured bug reports, UX feedback, screenshots, and on-chain proof of interaction
- AI-powered triage via Sentinel AI reads and categorizes every submission

**For Testers:**
- Verified Saga/Seeker device owners compete for USDC bounties, raffle prizes, and top-feedback awards
- Three sequential stages filter casual participants -- the best testers earn the most
- Build a persistent reputation score across campaigns

**Key Properties:**
- **Device-verified only.** Gated by Genesis SBT minted on verified Saga/Seeker hardware. One wallet per profile. Non-transferable. No sybils.
- **Built on Solana Mobile Stack.** Mobile Wallet Adapter (MWA) for signing. Seed Vault for auth. SPL tokens (USDC) for rewards. Metaplex for SBT identity.
- **Revenue-generating today.** dApp teams pay for campaigns. $3,000+ earned from live clients with ~80% flowing to tester prize pools.
- **Proven methodology.** 11 dApps tested via SagaDAO Innovation Lab. Critical bugs caught pre-launch across every round.

---

## 4. HOW IT WORKS

### Community Gating

Every tester holds a Genesis SBT minted through Seed Vault on a verified Saga or Seeker device. No SBT, no access.

- One device = one wallet = one tester profile (enforced at SBT level)
- Non-transferable -- tester identity is permanent and reputation-bearing
- Daily on-chain snapshot of eligible wallets
- **120,000+ Genesis Tokens minted** across Saga (~20,000) and Seeker (100,908 verified via SKR airdrop) -- this is the eligible tester pool on day one

**What this blocks:** VPN farming, disposable email signups, automated quest bots, multi-wallet sybil attacks, wallet cycling

**What no other platform can claim:** Every piece of feedback traces to a cryptographically verified Solana Mobile device owner with a persistent on-chain identity.

### Three-Stage Testing Structure

**Stage 1: UX Walkthrough** (unlocked immediately)
- Observe onboarding flow end-to-end on real Saga/Seeker hardware
- Surface friction points, confusion, and drop-off moments
- Written feedback required (150+ characters)
- Completing this stage enters the tester into raffle prizes and unlocks Stage 2
- *Purpose: Surface-level detection + filter unengaged testers*

**Stage 2: Core Feature Testing** (unlocks after Stage 1 approved)
- Complete builder-defined task list
- Submit 150+ character feedback per task
- Assess comprehension and UX logic
- Every submission human-reviewed. Low-effort = rejected + flagged
- *Purpose: Deep UX + feature validation + filter low-intent users*

**Stage 3: Proof of Interaction** (unlocks after Stage 2 approved)
- Submit transaction confirmations + screenshots
- Confirm full genuine engagement with the dApp
- Eligible for largest reward tier (top-feedback bounties)
- *Purpose: Evidence-based completion + builds Proven Tester Cohort*

**Why sequential > parallel:**
Casual participants exit at Stage 1. Farmers get filtered at Stage 2. Only committed, quality testers reach Stage 3. Builders get a progressively more qualified feedback funnel -- not a blast of low-effort responses.

### Sentinel AI Triage

Every tester submission is processed by Sentinel AI, which:
- Reads and categorizes feedback by type (bug, UX friction, feature request, positive signal)
- Flags low-effort or copy-paste responses for human review
- Generates structured summaries for builders
- Reduces builder review time from hours to minutes per campaign

### Reward Structure

- **Raffle waves** at each stage -- complete the stage, enter the draw
- **Top-feedback bounties** -- DAO working groups + builder team select the best testers for largest payouts
- **Referral bonuses** -- bring more qualified testers, earn more
- **Completion milestones** -- community-wide goals unlock additional prize pools
- All rewards distributed on-chain via SPL token transfers, signed through MWA
- Builders can add their own tokens alongside USDC to the prize pool

---

## 5. TRACTION & VALIDATION

### This Is Not a Concept

U$ER automates and productizes SagaDAO's Innovation Lab -- a community QA operation that has been running structured testing campaigns manually since early 2026.

| Metric | Value |
|---|---|
| Revenue from live clients | **$3,000+** |
| dApps tested | **11** |
| Revenue to tester prize pools | **~80%** |
| Live dApps shipped post-testing | **5+** |
| App build status | **~80% complete** |
| Direct competitors | **0** |

### Live Clients

- **Dubs** -- paid $1,500 campaign. Public confirmation: "@SagaMobileDAO" tweet on March 4, 2026 announcing "$1,500 up for grabs through our dApp testing partner."
- **&milo** -- paid campaign through Innovation Lab
- Additional dApps tested via SagaDAO Innovation Lab rounds

### SagaDAO's Track Record (the team behind U$ER)

- 20,000+ X followers, 10,000+ Discord members
- Mainnet Solana validator with Solana Foundation stake delegation (vote account: ELLB9...HcG)
- 14+ ecosystem partnerships: Solana Foundation, Ledger, Phase Labs, Sec3, and more
- SagaDAO House events: Breakpoint Abu Dhabi (Dec 2025), NYC, Miami, Art Basel
- Gate.io Learn published overview of SagaDAO
- Paul Barron Network, Jup & Juice media coverage
- On-chain Realms governance with published Codex charter
- Unlock claims platform -- Sec3 X-Ray audited smart contract, thousands of users

### Sustainability Model

The platform generates revenue from builder-paid campaigns. $3,000 earned before requesting any grant funding. This grant accelerates productization of a proven, working system -- not speculation.

**Public good commitment:** 2 free testing campaigns per quarter for early-stage Solana Mobile builders and hackathon winners. Published ecosystem QA benchmarks benefit all builders, even those who don't use U$ER directly.

---

## 6. COMPETITIVE LANDSCAPE

### Nothing Else Like This Exists in the Solana Ecosystem

| Platform | What They Do | Why They're Not QA |
|---|---|---|
| **Layer3 / Galxe / Zealy** | Quest platforms for user acquisition | Reward speed, not quality. No bug reports. No device verification. |
| **Immunefi** | Smart contract bug bounties | Finds code exploits, not UX bugs. Elite security researchers, not device owners. |
| **UserTesting / Applause** | Enterprise QA ($30K-$100K/yr) | No crypto knowledge. Self-reported devices. Pricing excludes 99% of Solana teams. |
| **Superteam Earn** | Freelance bounty board | One-off tasks. No structured campaigns. No device gating. |
| **Discord testing** | "Hey can someone test my app?" | Unstructured, inconsistent, sybil-vulnerable, zero accountability. |

### U$ER's Monopoly Position

The only platform that combines:
1. Verified device ownership (Genesis SBT)
2. Structured sequential testing (3-stage filtering)
3. Crypto-native pricing (USDC campaigns, accessible to any team)
4. On-chain tester identity (persistent, reputation-bearing)
5. Human-reviewed quality enforcement (low-effort = rejected)
6. AI-powered triage (Sentinel AI)

**First mover in structured, device-verified QA for the open mobile ecosystem.**

---

## 7. TEAM

**The team that built SagaDAO and ran 11 live QA campaigns for Solana Mobile dApps.**

| Name | Role | Handle |
|---|---|---|
| **Cloud King** | Community + Growth, Co-founder | @cloudkingtv |
| **Absent D (Dioni)** | Business + Innovation, Partnerships + Strategy | @dioni_sol |
| **Daemon** | Operations + Support, DAO Ops | @kaizenguru_sol |
| **Ay0h** | Research + Development, R&D Lead | @ay0h_sol |
| **Quark** | Lead Developer, Full-stack Engineering | @MoonManQuark |

**What we've shipped:**
- Mainnet Solana validator (vote account: ELLB9...HcG) with Solana Foundation delegation
- Unlock claims platform -- Sec3 X-Ray audited smart contract, thousands of users
- Innovation Lab -- live testing campaigns for Solana mobile dApps (the manual version of U$ER)
- On-chain Realms governance with published Codex charter
- SagaDAO House events across multiple continents

Plus dozens of active contributors across working groups, events, moderation, and development.

---

## 8. TECHNICAL ARCHITECTURE

### Built on Solana Mobile Stack

| Component | Technology |
|---|---|
| Tester authentication | Mobile Wallet Adapter (MWA) via Seed Vault |
| Tester identity | Genesis SBT (Metaplex, non-transferable) |
| Reward distribution | SPL token transfers (USDC) via MWA signing |
| Device verification | Genesis SBT + daily wallet snapshot indexing |
| Submission triage | Sentinel AI (NLP classification + quality scoring) |
| Backend | Node.js API + PostgreSQL + on-chain verification |
| Frontend | React Native (Android-first, dApp Store target) |
| Campaign management | Builder dashboard (web) + tester app (mobile) |

### Key Integrations

- **Solana Mobile dApp Store** -- primary distribution channel (Day 90 launch target)
- **SKR / Guardians ecosystem** -- U$ER data complements Guardian curation. Guardians answer "should this app be trusted?" U$ER answers "does this app actually work?"
- **Metaplex** -- SBT minting and verification
- **Jupiter / DEX aggregation** -- optional token swaps for multi-token prize pools

---

## 9. ROADMAP & MILESTONES

### 90-Day Plan: Grant to dApp Store Launch

**Month 1 -- Build & Integrate (Days 1-30)**
*Milestone: Production-ready app, fully tested on Saga & Seeker hardware*

| Deliverable | Detail |
|---|---|
| MWA integration finalized | All auth, signing, and reward flows via Mobile Wallet Adapter |
| Seed Vault tester auth | Genesis SBT verification through Seed Vault -- tested on both Saga & Seeker |
| Sentinel AI deployment | Submission triage pipeline live, categorizing feedback automatically |
| Push notification infrastructure | Campaign alerts, stage unlocks, prize notifications |
| Reward contract on devnet | USDC escrow + staged prize distribution, internally tested |

*Exit criteria: Team can run a full 3-stage campaign end-to-end on a Seeker device with real USDC prize distribution.*

**Month 2 -- Beta & Optimize (Days 31-60)**
*Milestone: Live beta with real builders and real testers*

| Deliverable | Detail |
|---|---|
| Beta with 3-5 dApp partners | Real campaigns with Solana Mobile builders |
| 50+ verified testers | All SBT-gated, all on Saga/Seeker |
| Tester profiles + reputation | Completion rates and quality scores visible to builders |
| Quality benchmarks | Human review rejection rates and feedback quality baseline |
| Sentinel AI tuning | Model accuracy validated against human review decisions |

*Exit criteria: 3+ campaigns completed. Completion rates and quality metrics documented.*

**Month 3 -- Launch (Days 61-90)**
*Milestone: U$ER live in the Solana dApp Store*

| Deliverable | Detail |
|---|---|
| dApp Store listing | Submitted and approved |
| Self-service campaign builder | Any builder can create a testing campaign |
| First fully automated round | Campaign to tester match to testing to USDC payout, no manual intervention |
| Impact report | Published metrics: testers, campaigns, bugs found, quality scores |
| Free tier live | 2 free campaigns/quarter for hackathon winners and early-stage builders |

*Exit criteria: Live in dApp Store. 1+ fully automated campaign completed. Impact report shared with Solana Mobile.*

---

## 10. BUDGET

### $15,000 USDC -- Use of Funds

| Category | Amount | What It Covers |
|---|---|---|
| Mobile UX production polish | $3,000 | Final UI build, Saga/Seeker device testing, production quality |
| Security review (reward logic) | $2,000 | Reward distribution contract review, escrow audit |
| Push notification infrastructure | $2,000 | Real-time campaign alerts, stage unlocks, prize notifications |
| Backend scaling & verification | $3,000 | SBT indexing, verification service, Sentinel AI hosting |
| Initial USDC campaign liquidity | $3,000 | Seed pool for 3-5 beta testing campaigns to bootstrap tester network |
| Deployment & launch costs | $2,000 | dApp Store submission, launch monitoring, store optimization |
| **Total** | **$15,000** | |

**Why this is low risk:** The app is ~80% built. We've already earned $3,000 from live clients. These funds accelerate productization of a proven system -- execution risk is minimal. Impact is immediate.

**What happens at Day 91:** The platform sustains itself through campaign fees. Revenue model proven before grant. This is not a project that dies when funding ends.

---

## 11. ECOSYSTEM IMPACT & PUBLIC GOOD

### What U$ER Does for the Solana Mobile Ecosystem

**For builders:** A structured, affordable way to QA mobile dApps before dApp Store launch. Catches bugs that damage ratings and user trust. The cheapest QA infrastructure in mobile.

**For the dApp Store:** As the store scales from 435 to 1,000+ apps, quality infrastructure becomes essential. U$ER provides the quality data layer that keeps the "permissionless but trustworthy" promise real.

**For Guardians:** Testing data complements Guardian curation. Guardians answer "should this app be trusted?" U$ER answers "does this app actually work?" Together, they give the dApp Store a complete quality assurance layer no other mobile ecosystem has in decentralized form.

**For Seeker owners:** A way to earn USDC by testing apps that will run on their own device. More testers = better apps = better Seeker experience for everyone. Real utility for device ownership beyond speculation.

**For the ecosystem narrative:** Every mature app platform has QA infrastructure. With U$ER, the Solana dApp Store gets its own -- community-driven, crypto-native, and permissionless. No gatekeepers. No Apple. No Google.

**Public good commitments:**
- 2 free testing campaigns per quarter for early-stage builders and hackathon winners
- Published ecosystem QA benchmarks and metrics (open data)
- Integration with Guardians for data-driven curation
- Free for Solana Mobile Hackathon winners

---

## APPENDIX A: SOLANA FRONTIER HACKATHON

**Competition:** Solana Frontier Hackathon (Colosseum)
**Dates:** April 6 -- May 11, 2026
**Category:** Infrastructure
**Prize:** Up to $25,000 + Colosseum Accelerator pipeline + $2.5M venture fund access

### Submission Framing

**Project Name:** U$ER -- dApp QA Layer for Solana Mobile

**Tagline:** The pre-launch QA infrastructure the Solana dApp Store has been missing. Device-verified. Community-powered. Already generating revenue.

**Category:** Infrastructure

**Why Infrastructure (not Consumer):**
U$ER is foundational plumbing for the dApp Store ecosystem. It's not a consumer app -- it's the quality layer that makes every other consumer app better. Like TestFlight for iOS or Firebase Test Lab for Android, U$ER is infrastructure that the ecosystem cannot scale without.

### Hackathon Evaluation Criteria Mapping

**Stickiness / PMF (25%):**
- $3,000 revenue from live clients before any grant or prize money
- 11 dApps tested, 5+ shipped post-testing
- Paying customers (Dubs, &milo) returning for additional campaigns
- 120,000+ eligible testers via Genesis SBT on day one
- Zero direct competitors in the Solana ecosystem

**UX (25%):**
- Three-stage sequential flow designed for mobile-first experience on Saga/Seeker
- Sentinel AI reduces builder review burden from hours to minutes
- Push notifications for every campaign state change
- Tester reputation system makes repeat campaigns progressively easier to staff
- MWA-native signing flows -- no wallet switching, no browser redirects

**Innovation (25%):**
- First platform to combine verified device ownership (SBT) with structured sequential QA
- Sentinel AI auto-triage of community feedback is novel in crypto QA
- "Proof of Interaction" (Stage 3) creates on-chain evidence of real app usage -- a new primitive
- Complementary to Guardians -- "does it work?" + "should you trust it?" = complete quality signal
- Crypto-native pricing makes QA accessible to teams at any funding level

**Presentation (25%):**
- Proven track record: 11 dApps, $3K revenue, 5+ shipped apps
- Clear 90-day roadmap with named milestones and exit criteria
- Competitive landscape makes monopoly position undeniable
- Team has shipped: mainnet validator, audited smart contracts, live events globally
- The comparison: "Apple has TestFlight. Google has Firebase. We're building the Solana equivalent -- but open."

### Demo Requirements

If a live demo is required:
1. Show the tester app on a Seeker device -- MWA login via Genesis SBT
2. Walk through a sample 3-stage campaign (Stage 1 UX walkthrough)
3. Show Sentinel AI processing a batch of test submissions
4. Show builder dashboard with aggregated feedback and quality scores
5. Show on-chain reward distribution via MWA

### Hackathon-Specific Talking Points

- "We didn't build this for the hackathon. We've been running this for months. The hackathon is our launchpad."
- "Every hackathon winner ships an app that needs testing. U$ER gives them that for free."
- "$3,000 in revenue before a single judge saw this. PMF isn't theoretical."
- "435+ dApps, zero QA. This isn't a nice-to-have. It's missing infrastructure."
- "The Colosseum Accelerator is how we go from dApp Store launch to the standard QA layer for the entire ecosystem."

---

## APPENDIX B: SOLANA MOBILE BUILDER GRANT

**Program:** Solana Mobile Builder Grants (RFP Track)
**URL:** solanamobile.com/grants
**Amount:** $15,000 USDC

### Grant Criteria Mapping (6 criteria from solanamobile.com/grants)

**1. Mobile-First**
U$ER is a native Android app built exclusively for Solana Mobile hardware. The entire product runs on Saga and Seeker devices. The 90-day roadmap ends with dApp Store submission and launch. Every testing campaign is executed on real mobile hardware -- not emulators, not desktop.

**2. Solana Mobile Stack Integration**
- Mobile Wallet Adapter (MWA): All tester authentication, campaign signing, and USDC reward claiming
- Seed Vault: Genesis SBT verification for tester identity
- SPL tokens: On-chain USDC reward distribution
- Metaplex: Genesis SBT minting for non-transferable tester identity
- dApp Store: Primary distribution channel

**3. Milestones & Deliverables**
Three months, three milestones, each with named deliverables and explicit exit criteria:
- Month 1: Production-ready app with full SMS integration
- Month 2: Live beta with 3-5 builder partners and 50+ verified testers
- Month 3: dApp Store launch + first fully automated campaign + published impact report

**4. Team Ability to Execute**
Five named team members who have collectively shipped: a mainnet Solana validator with Foundation delegation, a Sec3-audited smart contract used by thousands, 11 live QA campaigns, SagaDAO House events on three continents, and on-chain governance via Realms.

**5. Budget Justification**
$15,000 allocated across 6 categories with dollar amounts. The app is ~80% built. Revenue of $3,000 proves sustainability beyond the grant period. This is acceleration funding, not survival funding.

**6. Community & Public Good**
- 2 free testing campaigns per quarter for early-stage builders and hackathon winners
- Published ecosystem QA benchmarks (open data)
- Complementary to Guardians: U$ER provides the "does it work?" data layer
- Verified tester network benefits every app in the dApp Store, not just U$ER clients

### Application Copy (ready to paste)

**Project Name:** U$ER

**One-line description:** Device-verified, community-powered QA infrastructure for the Solana dApp Store -- the open-ecosystem equivalent of TestFlight.

**Grant amount requested:** $15,000 USDC

**Timeline:** 90 days from grant receipt to dApp Store launch

**What does your project do?**

U$ER is the pre-launch QA layer for the Solana dApp Store. We connect dApp builders with Genesis SBT-verified Saga and Seeker device owners who test their apps through structured, three-stage campaigns with USDC bounties.

The dApp Store has 435+ apps and zero structured QA infrastructure. Builders either skip mobile testing entirely or use quest platforms that measure clicks, not quality. U$ER fixes this with device-verified testers, sequential filtering that removes low-effort participants, AI-powered submission triage, and on-chain reward distribution.

We've already tested 11 dApps through SagaDAO's Innovation Lab, earned $3,000 from paying clients (Dubs, &milo), and the app is ~80% built. This grant funds the final Solana Mobile Stack integration, beta campaigns with real builders, and dApp Store launch.

No other platform in the Solana ecosystem offers structured, device-verified QA for mobile dApps. U$ER fills a critical infrastructure gap with zero direct competition.

**How does your project use Solana Mobile Stack?**

- Mobile Wallet Adapter (MWA): All tester authentication and reward claiming flows
- Seed Vault: Genesis SBT verification ensures every tester owns a verified Saga or Seeker
- SPL tokens (USDC): On-chain reward distribution through MWA-signed transactions
- Metaplex: Genesis SBT as non-transferable tester identity
- dApp Store: Primary distribution -- U$ER launches in the dApp Store at Day 90

**What traction do you have?**

- $3,000 revenue from live clients (Dubs, &milo) -- before requesting any grant funding
- 11 Solana dApps tested through SagaDAO Innovation Lab campaigns
- ~80% of revenue flows directly to tester prize pools
- 5+ dApps shipped post-testing
- Critical bugs caught pre-launch across every testing round
- 120,000+ Genesis Token holders eligible as testers on day one (Saga ~20K + Seeker 100,908)
- App is ~80% built and in internal testing

**Team:**

Cloud King (@cloudkingtv) -- Community + Growth, Co-founder
Absent D / Dioni (@dioni_sol) -- Business + Innovation, Partnerships + Strategy
Daemon (@kaizenguru_sol) -- Operations + Support, DAO Ops
Ay0h (@ay0h_sol) -- Research + Development, R&D Lead
Quark (@MoonManQuark) -- Lead Developer, Full-stack Engineering

Shipped: Mainnet Solana validator (Foundation-delegated), Sec3-audited unlock claims platform, Innovation Lab (11 live campaigns), on-chain Realms governance, SagaDAO House events (Breakpoint Abu Dhabi, NYC, Miami, Art Basel). 20K+ X followers, 10K+ Discord members, 14+ ecosystem partnerships.

**Budget breakdown:**

Mobile UX polish: $3,000 | Security review: $2,000 | Push notifications: $2,000 | Backend scaling & verification: $3,000 | Campaign seed liquidity: $3,000 | Deployment & launch: $2,000 | Total: $15,000

**What is your project's ecosystem impact?**

U$ER makes the dApp Store better for everyone. For builders: affordable pre-launch QA that catches bugs before they damage ratings. For Guardians: complementary data -- Guardians say "trust this app," U$ER says "this app actually works." For Seeker owners: USDC earnings for testing apps that run on their own device. For the ecosystem narrative: the Solana dApp Store gets its own QA layer -- community-driven and permissionless, like the store itself.

We commit to 2 free campaigns per quarter for early-stage builders and hackathon winners, plus published QA benchmarks as open ecosystem data.

---

## APPENDIX C: GENERAL WEB3 GRANT TEMPLATE

*Use this as a starting template for any Web3 grant program (Solana Foundation, ecosystem grants, etc.). Adapt the framing to match specific criteria.*

### Short-Form Application (500 words)

**Project:** U$ER -- Open Mobile QA Layer

**Problem:** The Solana dApp Store has 435+ apps and 150K+ active device users but zero structured quality assurance infrastructure. Builders ship mobile dApps without systematic testing on real hardware, leading to bugs that damage user trust and app ratings. Existing alternatives -- quest platforms, bounty boards, informal Discord testing -- measure engagement, not quality, and lack device verification.

**Solution:** U$ER is a device-verified, community-powered QA platform for Solana Mobile dApps. Every tester is gated by a Genesis SBT (SoulBound Token) minted on verified Saga or Seeker hardware -- ensuring only real device owners participate. Builders create paid testing campaigns where testers progress through three sequential stages (UX walkthrough, core feature testing, proof of interaction), with each stage filtering low-effort participants. Submissions are triaged by Sentinel AI and human-reviewed before prize eligibility. Rewards are distributed on-chain in USDC via Mobile Wallet Adapter.

**Traction:** 11 dApps tested. $3,000 revenue from paying clients (Dubs, &milo). ~80% of revenue flows to tester prize pools. 5+ dApps shipped post-testing. Critical bugs caught pre-launch. 120,000+ eligible testers via Genesis SBT. App ~80% built.

**Team:** SagaDAO -- the world's first mobile DAO built around Solana Mobile devices. 20K+ X followers, 10K+ Discord. Mainnet validator with Foundation delegation. Sec3-audited smart contracts. SagaDAO House events globally. 14+ ecosystem partnerships.

**Ask:** $15,000 USDC for 90-day buildout: finalize Solana Mobile Stack integration, run beta campaigns, launch in dApp Store. Revenue model proven -- platform sustains itself post-grant through campaign fees.

**Impact:** U$ER fills a critical infrastructure gap with zero competitors. Complements Guardians (curation + "does it work?" = complete quality signal). Free campaigns for hackathon winners and early-stage builders. Published QA benchmarks benefit the entire ecosystem.

### Long-Form Sections (mix and match as needed)

*All sections above (Problem, Solution, How It Works, Traction, Team, Architecture, Roadmap, Budget, Ecosystem Impact) can be combined in any order to match specific grant application forms.*

### Common Grant Questions -- Pre-Written Answers

**Q: Is this open source?**
The platform itself is the public good -- it makes the dApp Store better for every builder and every user. We publish ecosystem QA benchmarks as open data and offer free campaigns for early-stage builders. Commercial companies receive ecosystem grants across crypto (Alchemy, Nansen, Tenderly, Chainlink) -- the standard is impact, not license.

**Q: What happens when the grant runs out?**
We've already earned $3,000 from paying clients before requesting any funding. The revenue model is proven: builders pay for testing campaigns, ~80% goes to testers, ~20% sustains the platform. The grant accelerates our timeline -- it doesn't fund our survival.

**Q: Why can't builders just use [quest platform / Discord / etc.]?**
Quest platforms reward speed and completion counts -- output is vanity metrics, not bug reports. Discord testing is unstructured, inconsistent, and sybil-vulnerable. Neither verifies device ownership. U$ER is the only platform that combines verified hardware, structured sequential testing, quality enforcement, and crypto-native pricing. The comparison table in Section 6 makes this concrete.

**Q: How do you prevent gaming / fake feedback?**
Three layers: (1) Genesis SBT gating ensures one verified device per tester, blocking sybils at the hardware level. (2) Sequential stages filter low-effort participants -- casual users exit at Stage 1, farmers caught at Stage 2. (3) Every Stage 2+ submission is human-reviewed; low-effort = rejected + reputation penalty. Sentinel AI pre-screens all submissions for copy-paste and low-signal content.

**Q: What's your competitive advantage / moat?**
120,000+ Genesis SBT holders are our tester pool -- no one else has access to this verified hardware base. Sequential testing methodology with quality enforcement is proprietary. Existing reputation data from 11 campaigns is non-replicable. First-mover in a category with zero competitors. Network effects: more testers = better data = more builders = more campaigns = more testers.

**Q: How does this relate to SagaDAO?**
SagaDAO is the community DAO behind U$ER. SagaDAO's Innovation Lab has been running QA campaigns manually since early 2026 -- U$ER productizes this into a scalable, automated platform. The team, community, tester network, and builder relationships all flow from SagaDAO's established ecosystem position.

---

## PRE-SUBMISSION CHECKLIST

Before submitting any application:

- [ ] Include the Dubs public tweet as proof of paying client: https://x.com/dubsdotapp/status/2029244200391172426
- [ ] Screenshot on-chain Genesis Token data (120K+ minted tokens) with block explorer links
- [ ] Confirm team member handles are current
- [ ] Update revenue number if new campaigns have been completed (currently $3,000+)
- [ ] Update dApp count if new tests have been run (currently 11)
- [ ] If hackathon: prepare live demo on Seeker device
- [ ] If RFP grant: map every criterion explicitly (see Appendix B)
- [ ] Optional but powerful: publish one Innovation Lab testing report as a 1-page case study

---

*Built by SagaDAO. @SagaMobileDAO / @cloudkingtv*
