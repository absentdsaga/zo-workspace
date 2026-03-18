# TESTINGdApp — Solana Mobile Builder Grant Proposal V3
## Research-Backed Rewrite

> **How this was built:** 5 parallel deep research tracks — past grant winners, competitive landscape, grant writing best practices, Solana Mobile strategic priorities, and SagaDAO traction evidence. Every recommendation below is grounded in specific findings.

---

## STRATEGIC FRAMING — READ THIS FIRST

### What the research revealed about how to win this grant:

**1. This is NOT a hackathon prize. It's an RFP-track builder grant.**
Solana Mobile runs two grant tracks. The Colosseum Hackathon Grants are capped at $10K per team (10 teams, evaluated on Stickiness/PMF, UX, Innovation, Presentation — 25% each). The RFP-track Builder Grants have no published cap — grant amounts are set per-RFP. Your proposal is an RFP-track application, evaluated against 6 specific criteria on solanamobile.com/grants. Your proposal needs to explicitly check all 6 boxes. The hackathon winners were gaming and commerce apps. You're not competing with them — you're in the tooling/infrastructure lane.

**2. The "already 80% done" play is the strongest micro-grant tactic.**
Grant writing research was unanimous: at this grant size, reviewers worry about execution risk above all else. The killer move is showing you've already done most of the work and the grant accelerates what's already working. You have revenue ($1,500), active testers, and a proven methodology. Lead with that. This isn't "fund our idea" — it's "fund the productization of something that already works and already makes money."

**3. Revenue is your biggest weapon, not a liability.**
The grant writing research found that the best framing is: "The grant funds the public-good layer around a sustainable product." Your commercial revenue ($1,500 from Dubs and Milo) proves product-market fit AND guarantees sustainability beyond the grant period. Reviewers prefer funding things that won't die when the grant runs out.

**4. There are ZERO direct competitors.**
The competitive landscape research confirmed: no one else is building structured, device-verified QA for Solana mobile dApps. Not quest platforms (marketing tools), not Immunefi (code-level security), not UserTesting (enterprise pricing, no crypto knowledge). You're alone in the quadrant. The proposal should make this monopoly position extremely clear.

**5. Mirror Solana Mobile's exact language.**
Their vocabulary: "open mobile ecosystem," "builders" (not developers), "community-driven," "permissionless," "ownership." They frame everything as the anti-Apple/anti-Google. Your QA infrastructure should be framed as "the open-ecosystem equivalent of TestFlight + Firebase Test Lab."

**6. The "public good" angle without open-sourcing your product.**
You don't need to open-source TESTINGdApp. The research found the proven framing: "The platform itself is the public good — it makes the dApp Store better for every builder and every user." Pair with: free campaigns for hackathon winners / early-stage builders, and published ecosystem QA benchmark data. Commercial companies get ecosystem grants all the time (Alchemy, Nansen, Tenderly, Chainlink).

**7. The Guardians angle is your secret weapon.**
Solana Mobile's Guardians program is community-driven dApp curation. TESTINGdApp gives Guardians *data* — "Guardians answer 'should this app be trusted?' TESTINGdApp answers 'does this app actually work?'" This makes you complementary to their existing infrastructure, not a standalone tool.

---

## THE ACTUAL DECK COPY — V3

### SLIDE 1 — COVER

> **TESTINGdApp**
>
> Pre-launch QA infrastructure for the Solana dApp Store — device-verified, community-powered, already generating revenue.
>
> **$15,000 USDC** | **90-Day Delivery** | **dApp Store Launch at Day 90**

*What changed: "already generating revenue" signals this is a funded, working product — not a concept. $15K positions this as an RFP-track infrastructure grant, not a hackathon side-project. Still firmly micro-grant territory — low scrutiny, high approval probability.*

---

### SLIDE 2 — EXECUTIVE SUMMARY

> **The dApp Store is scaling. Quality infrastructure needs to scale with it.**
>
> TESTINGdApp is the pre-launch QA layer for Solana Mobile builders. We connect dApp teams with verified Saga & Seeker owners who test their apps through structured, three-stage campaigns — with USDC bounties and prizes for quality participation.
>
> → **Device-verified testers only.** Every tester holds a Genesis SBT minted on a verified Saga or Seeker device.
> → **Built on Solana Mobile Stack.** Mobile Wallet Adapter for all signing flows. Seed Vault for tester authentication.
> → **Revenue-generating today.** dApp teams pay for testing campaigns. Testers compete for USDC bounties, raffle prizes, and top-feedback awards. We've charged $1,500+ from live clients — with ~80% going directly to the prize pool.
> → **Proven methodology.** 11 dApps tested, multiple critical bugs caught pre-launch, measurable improvement between rounds — all run manually through SagaDAO's Innovation Lab.
> → **The app is already built and in testing.** This grant funds the final SMS integration, beta campaigns with real builders, and dApp Store launch.
>
> **No other platform in the Solana ecosystem does this.**

*What changed: Opens with the ecosystem problem (dApp Store scaling), not the product. Leads with "revenue-generating today" — the strongest signal for a micro-grant. Closes with the monopoly position. Explicitly names MWA + Seed Vault (grant criteria #2). The last line is the competitive landscape finding — zero direct competitors.*

---

### SLIDE 3 — THE PROBLEM

> **435+ dApps in the Solana dApp Store. Zero structured QA infrastructure.**
>
> The dApp Store grew from 160 to 435+ apps in under 6 months. Seeker has shipped to 150K+ users across 50+ countries. Builders are launching fast — but there's no systematic way to test mobile dApps on real Solana Mobile hardware before they go live.
>
> | What builders do today | What goes wrong |
> |---|---|
> | Skip mobile QA entirely — ship and pray | Users hit bugs on Seeker that weren't caught in development |
> | Use quest platforms (Layer3, Galxe, Zealy) for "testing" | Quests measure clicks, not quality. Output is vanity metrics, not bug reports |
> | Post testing bounties on Superteam Earn | Unstructured, one-off, no device verification, no sequential test flows |
> | Recruit testers informally via Discord | Inconsistent feedback, no accountability, high drop-off, sybil-vulnerable |
>
> Apple has TestFlight. Google has Firebase Test Lab. The Solana dApp Store has nothing equivalent.
>
> **That's the gap. TESTINGdApp fills it.**

*What changed: Opens with real ecosystem numbers (435+ dApps, 150K+ Seekers — from research). Names the actual alternatives builders use and why each fails. The Apple/Google comparison came directly from the strategic priorities research — Solana Mobile positions as the "open alternative" to Apple/Google, and they're missing this entire infrastructure layer. The punchline makes the gap undeniable.*

---

### SLIDE 4 — THE SOLUTION

> **Structured mobile QA that runs on Solana Mobile Stack**
>
> TESTINGdApp is a mobile-native Android app that connects dApp builders with verified Saga & Seeker testers through paid, structured testing campaigns.
>
> **How it works:**
>
> **Builders** create a testing campaign → define tasks, fund the prize pool, specify what to test
> **Testers** (verified Saga/Seeker owners) complete 3 sequential stages → win USDC bounties, raffles, and top-feedback prizes
> **Output** → structured bug reports, UX feedback, screenshots, on-chain proof of interaction
>
> Built with:
> - **Mobile Wallet Adapter (MWA)** — all tester authentication and reward claiming
> - **Seed Vault** — secure tester identity via Genesis SBT
> - **SPL tokens (USDC)** — on-chain reward distribution
> - **Metaplex** — Genesis SBT minting for tester identity
>
> **Not a quest platform.** Quest platforms (Layer3, Galxe) reward speed and completion counts. TESTINGdApp rewards thoroughness and quality — testers who submit low-effort feedback get rejected and flagged.

*What changed: Added a clear "How it works" flow — builder → tester → output. Grant reviewers need to understand the product in 30 seconds. The competitive differentiation from quest platforms is now explicit because the research confirmed quest platforms are the most likely "why not just use X?" objection.*

---

### SLIDE 5 — COMMUNITY GATING

> **Every tester is a verified Solana Mobile device owner**
>
> Access requires a Genesis SBT minted through Seed Vault on a verified Saga or Seeker device. No SBT, no access.
>
> → **One device = one wallet = one tester profile** (enforced at the SBT level)
> → **Non-transferable** — tester identity is permanent and reputation-bearing
> → **Daily on-chain snapshot** of eligible wallets
> → **120,000+ Genesis Tokens minted** across Saga (~20,000) and Seeker (100,908 verified via SKR airdrop). This is the eligible tester pool. Day one.
>
> **What this blocks:** VPN farming, disposable email signups, automated quest bots, multi-wallet sybil attacks, wallet cycling
>
> **What no other platform can claim:** Every piece of feedback traces to a cryptographically verified Solana Mobile device owner with a persistent on-chain identity. Not self-reported device info (Applause, BetaFamily). Not honor-system wallet verification (quest platforms). On-chain, hardware-attested, non-transferable.

*What changed: Added the combined 120K+ Genesis holder number (Saga ~20K + Seeker 100K+) — concrete on-chain data is powerful. Added the competitive comparison to traditional QA platforms (Applause, BetaFamily do self-reported device info — from competitive landscape research). This slide now functions as both a feature description AND a competitive differentiation argument.*

---

### SLIDE 6 — SEQUENTIAL TESTING

> **Three stages. Test to win. Each stage filters.**
>
> **Stage 1: UX Walkthrough** (unlocked immediately)
> Tester walks the dApp's first-time experience on their Saga/Seeker. Structured prompts surface confusion points, onboarding friction, and drop-off triggers. Written feedback required (150+ chars). Completing this stage enters you into raffle prizes and unlocks Stage 2.
>
> **Stage 2: Core Feature Testing** (unlocks after Stage 1 approved)
> Builder-defined task list. Tests feature clarity, task completion, and comprehension. Every submission human-reviewed. Low-effort = rejected + flagged. Larger raffle prizes and bounty eligibility.
>
> **Stage 3: Proof of Interaction** (unlocks after Stage 2 approved)
> On-chain evidence of real usage: transaction confirmations, dApp Store reviews, screenshots, social proof. Proves the tester actually used the product. Eligible for top-feedback bounties (largest payouts) and final raffle wave.
>
> **Why sequential > parallel:**
> Casual participants exit at Stage 1. Farmers get filtered at Stage 2. Only committed, quality testers reach Stage 3. Builders get a progressively more qualified feedback funnel — not a blast of low-effort responses.

*What changed: Minimal copy changes from V2 — this was already strong. Added the "Why sequential > parallel" framing to pre-empt the reviewer asking "why not let testers do everything at once?"*

---

### SLIDE 7 — THE PROVING GROUND

> **Test to win. Best feedback wins the most.**
>
> **Prize Structure:** Each campaign has a USDC prize pool funded by the builder. Testers compete across multiple reward channels: raffle waves at each stage, top-feedback bounties judged by the builder and DAO working groups, referral bonuses for growing the tester pool, and completion milestones. The best testers win the most — not everyone gets paid the same.
>
> **Proven Tester Cohort:** Over time, the platform builds a ranked network of reliable testers — tracked by completion rate, feedback quality, and interaction proof. Builders launching new campaigns can target high-reputation testers.
>
> **Why builders pay for this:**
> A single critical bug caught before dApp Store launch is worth more than the entire campaign cost. One bad review from a Seeker user who hits a crash can tank an app's rating. TESTINGdApp is insurance — and the cheapest QA infrastructure in mobile.

*What changed: Added "Why builders pay for this" — making the business logic explicit. The grant reviewer needs to believe this is a real service people will pay for. The $1,500 number and the insurance framing do that.*

---

### SLIDE 8 — REWARDS STRUCTURE

> **Test to win — USDC prize pool, multiple ways to win**
>
> → **Raffle waves** at each stage — complete the stage, enter the draw
> → **Top-feedback bounties** — DAO working groups + builder team select the best testers for largest payouts
> → **Referral bonuses** — bring more qualified testers, earn more
> → **Completion milestones** — community-wide goals unlock additional prize pools
>
> **Quality enforcement:**
> - Every Stage 2+ submission is human-reviewed before prize eligibility
> - Low-effort responses are rejected; tester is flagged and ineligible for prizes
> - Repeated low-quality submissions reduce reputation score
> - Builders can add their own tokens alongside USDC to the prize pool
>
> **All rewards distributed on-chain via SPL token transfers, signed through Mobile Wallet Adapter.**

*What changed: Minor from V2. This slide was already solid.*

---

### SLIDE 9 — TRACTION & VALIDATION

> **This isn't a concept. We've already been paid to do this.**
>
> TESTINGdApp automates SagaDAO's Innovation Lab — a community QA operation that has been running structured testing campaigns manually since early 2026.
>
> **What we've done (manual process, pre-app):**
> - **11 Solana dApps tested** across multiple campaign rounds — scaling from small early campaigns to $1,500 prize pools
> - **Multiple paying clients** — including Dubs and &milo, each funding $1,500 campaigns with ~80% going directly to the tester prize pool
> - **2 pre-dApp prototypes evaluated** before public launch
> - **Critical bugs identified & resolved** before they hit users
> - **Measurable UX improvement** tracked between testing rounds
> - **Active tester community** completing campaigns today
>
> **SagaDAO's track record behind this:**
> - 20K+ X followers, 10K+ Discord members
> - Mainnet Solana validator with Foundation stake delegation
> - 14+ ecosystem partnerships including Solana Foundation, Ledger, Phase Labs, Sec3
> - SagaDAO House events at Breakpoint Abu Dhabi, NYC, Miami, Art Basel
> - Paul Barron Network, Jup & Juice media coverage
> - Gate.io Learn published overview
>
> **The app is already built and in testing. The grant funds the final integration, beta campaigns, and dApp Store launch.**

*What changed: MASSIVE upgrade. Opens with "we've already been paid" — the single most powerful sentence in the entire proposal per the grant writing research. Added SagaDAO's credibility stats (from traction research). The closing line uses the "already 80% done" framing — the #1 micro-grant tactic identified by the research.*

---

### NEW SLIDE — TEAM (insert after Traction, before Roadmap)

> **TEAM**
>
> **The team that built SagaDAO and ran 11 live QA campaigns for Solana mobile dApps**
>
> **Cloud King** — Community + Growth, Co-founder — @cloudkingtv
> **Absent D (Dioni)** — Business + Innovation, Partnerships + Strategy — @dioni_sol
> **Daemon** — Operations + Support, DAO Ops — @kaizenguru_sol
> **Ay0h** — Research + Development, R&D Lead — @ay0h_sol
> **Quark** — Lead Developer, Full-stack Engineering — @MoonManQuark
>
> **What we've shipped:**
> → Mainnet Solana validator (vote account: ELLB9...HcG) with Solana Foundation delegation
> → Unlock claims platform — Sec3 X-Ray audited smart contract, 1,000s of users
> → Innovation Lab — live testing campaigns for Solana mobile dApps (the manual version of TESTINGdApp)
> → On-chain Realms governance with published Codex charter
>
> Plus dozens of active contributors across working groups, events, moderation, and development.

*What changed: Team slide added — this was completely missing from V1 and is required by grant criteria #4 ("Team Ability to Execute"). Used the actual team names and handles from the SagaDAO traction research. Listed specific shipped products with verifiable on-chain references.*

---

### SLIDE 10 — COMPETITIVE LANDSCAPE (NEW SLIDE)

> **Nothing else like this exists in the Solana ecosystem**
>
> | Platform | What they do | Why they're not QA |
> |---|---|---|
> | **Layer3 / Galxe / Zealy** | Quest platforms for user acquisition | Reward speed, not quality. No bug reports. No device verification. |
> | **Immunefi** | Smart contract bug bounties | Finds code exploits, not UX bugs. Elite security researchers, not device owners. |
> | **UserTesting / Applause** | Enterprise QA ($30K-$100K/yr) | No crypto knowledge. Self-reported devices. Pricing excludes 99% of Solana teams. |
> | **Superteam Earn** | Freelance bounty board | One-off tasks. No structured campaigns. No device gating. |
> | **Informal Discord testing** | "Hey can someone test my app?" | Unstructured, inconsistent, sybil-vulnerable, zero accountability. |
>
> **TESTINGdApp is the only platform that combines:**
> Verified device ownership + structured sequential testing + crypto-native pricing + on-chain tester identity + human-reviewed quality enforcement
>
> No one else occupies this position. The closest analog is Apple's TestFlight — but decentralized, incentivized, and built for the open mobile ecosystem.

*What changed: New slide entirely. The competitive landscape research confirmed zero direct competitors. This slide makes that undeniable with a comparison table. The TestFlight comparison echoes Solana Mobile's own positioning as the "open alternative to Apple/Google."*

---

### SLIDE 11 — 90-DAY ROADMAP: MONTH 1

> **Month 1 — Final Integration + Internal QA (Days 1–30)**
>
> **Milestone: Production-ready app, fully tested on Saga & Seeker hardware**
>
> The app is already built and in internal testing. Month 1 focuses on hardening, not building from scratch.
>
> | Deliverable | Detail |
> |---|---|
> | MWA integration finalized | All auth, signing, and reward flows via Mobile Wallet Adapter |
> | Seed Vault tester auth | Genesis SBT verification through Seed Vault — tested on both Saga & Seeker |
> | Reward contract on devnet | USDC escrow + staged prize distribution, internally tested |
> | Push notifications | Campaign alerts, stage unlocks, prize notifications |
> | Website + onboarding copy | Final review and launch-ready |
>
> **Exit criteria:** Team can run a full 3-stage campaign end-to-end on a Seeker device with real USDC prize distribution.

---

### SLIDE 12 — 90-DAY ROADMAP: MONTHS 2 & 3

> **Month 2 — Controlled Beta (Days 31–60)**
>
> **Milestone: Live beta with real builders and real testers**
>
> | Deliverable | Detail |
> |---|---|
> | Beta with 3–5 dApp partners | Real campaigns with Solana Mobile builders |
> | 50+ verified testers | All SBT-gated, all on Saga/Seeker |
> | Tester profiles + reputation | Completion rates and quality scores visible to builders |
> | Quality benchmarks | Human review rejection rates and feedback quality baseline |
>
> **Exit criteria:** 3+ campaigns completed. Completion rates and quality metrics documented.
>
> ---
>
> **Month 3 — Public Launch (Days 61–90)**
>
> **Milestone: TESTINGdApp live in the Solana dApp Store**
>
> | Deliverable | Detail |
> |---|---|
> | dApp Store listing | Submitted and approved |
> | Self-service campaign builder | Any builder can create a testing campaign |
> | First fully automated round | Campaign → tester match → testing → USDC payout, no manual intervention |
> | Impact report | Published metrics: testers, campaigns, bugs found, quality scores |
>
> **Exit criteria:** Live in dApp Store. 1+ fully automated campaign completed. Impact report shared with Solana Mobile.

---

### SLIDE 13 — USE OF FUNDS

> **$15,000 USDC — Budget**
>
> | Category | Amount | What it covers |
> |---|---|---|
> | Mobile development | $4,000 | Final UI build, MWA + Seed Vault integration, Saga/Seeker device testing |
> | Smart contract + security | $1,500 | Reward distribution contract review, deployment to mainnet |
> | Backend infrastructure | $2,000 | Verification service, push notifications, SBT indexing |
> | Campaign seed liquidity | $4,500 | USDC pool for 5–8 beta testing campaigns to bootstrap the tester network |
> | dApp Store launch + QA | $1,500 | Submission compliance, launch monitoring, store optimization |
> | Contingency | $1,500 | Buffer for unforeseen costs during 90-day build |
> | **Total** | **$15,000** | |
>
> **Note:** TESTINGdApp generates revenue from builder-paid campaigns. This grant accelerates the productization timeline — not our survival. The platform will sustain itself post-grant through campaign fees.

*What changed: Added the sustainability note at the bottom. Grant writing research found that reviewers strongly prefer funding products that won't die after the grant. Your revenue model is the answer to "what happens at Day 91?"*

---

### SLIDE 14 — ECOSYSTEM IMPACT

> **What this does for the Solana Mobile ecosystem**
>
> → **For builders:** A structured, affordable way to QA mobile dApps before they go live in the dApp Store. Catches bugs that damage ratings and user trust.
>
> → **For the dApp Store:** As the store scales from 435 to 1,000+ apps, quality infrastructure becomes essential. TESTINGdApp provides the quality data layer that keeps the "permissionless but trustworthy" promise real.
>
> → **For Guardians:** Testing data complements Guardian curation. Guardians answer "should this app be trusted?" TESTINGdApp answers "does this app actually work?" Together, they give the dApp Store a quality assurance layer no other mobile ecosystem has in decentralized form.
>
> → **For Seeker owners:** A way to earn USDC by doing something useful — testing apps that will run on their own device. More testers = better apps = better Seeker experience for everyone.
>
> → **For the ecosystem narrative:** Every mature app platform has QA infrastructure. Apple has TestFlight. Google has Firebase. With TESTINGdApp, the Solana dApp Store gets its own — but community-driven and crypto-native.
>
> **Free campaign commitment:** We'll offer 2 free testing campaigns per quarter to early-stage Solana Mobile builders who can't yet afford paid QA. This ensures the platform serves the full ecosystem, not just funded teams.

*What changed: This replaces the old "Long-Term Vision" slide. The research showed that "ecosystem impact" framing is what wins grants — not "our company vision." Added the Guardians complement (from strategic priorities research). Added the free campaign commitment as the public-good angle — doesn't require open-sourcing anything, provides real community value, and costs you almost nothing if you're running campaigns anyway.*

---

### SLIDE 15 — CLOSING

> **TESTINGdApp**
>
> Better testing. Better launches. A better dApp Store.
>
> Built by SagaDAO — the community that's been running QA for Solana mobile dApps since before the tooling existed.
>
> **Let's build it. →**

---

## V1 → V3 COMPARISON MATRIX

| Grant Criteria | V1 | V3 |
|---|---|---|
| **Mobile-First** | Implied | Android, Saga/Seeker tested, dApp Store launch at Day 90 |
| **Solana Mobile Stack** | MWA once, Seed Vault never | MWA + Seed Vault + SPL + Metaplex named on every relevant slide |
| **Milestones** | Task lists | Named milestones, deliverable tables, exit criteria |
| **Team** | Missing entirely | 5 named team members + shipped products + on-chain references |
| **Budget** | Bullet list of categories | Dollar-allocated table with sustainability note |
| **Community & Public Good** | Missing entirely | Free campaigns for early-stage builders, Guardians complement, ecosystem impact framing |

---

## PRE-SUBMISSION ACTIONS (do these before sending)

Based on the traction research, these concrete steps will materially strengthen the proposal:

1. ~~**Get MiloOnChain / Dubs to tweet confirming the testing partnership**~~ — **DONE.** Dubs posted publicly on March 4, 2026: *"$1,500 up for grabs through our dApp testing partner @SagaMobileDAO"* → [Direct link](https://x.com/dubsdotapp/status/2029244200391172426). Include this link in the application as proof of paid client.
2. ~~**Create a @TESTINGdApp X account**~~ — **SKIP.** Post TESTINGdApp-specific content under @SagaDAO_xyz instead. A new empty account hurts more than it helps — keep the 20K+ follower credibility consolidated.
3. **Screenshot the on-chain Genesis Token data** — show the combined 120K+ minted tokens (Saga ~20K + Seeker 100,908 verified via SKR airdrop) as verifiable traction. Include block explorer links.
4. **Optional but powerful:** publish one Innovation Lab testing report — even a 1-page summary of a completed campaign showing methodology, bugs found, and outcomes.

Items 1–2 are handled. Item 3 is the single highest-ROI thing you can do before submitting.
