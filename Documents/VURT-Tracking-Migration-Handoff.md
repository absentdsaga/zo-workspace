# VURT Tracking & Analytics Migration Handoff
**Last Updated:** 2026-04-16 (post-audit — Dioni-side bundle inspection complete)
**Owner:** Dioni
**Purpose:** Ensure zero data loss and zero attribution gaps when myvurt.com migrates from Enveu's codebase to the new dev team.

---

## TL;DR — The Principle

**Anything in Google Tag Manager survives the migration. Anything hardcoded in Enveu's codebase dies unless rebuilt.**

Our goal is to have as much tracking as possible routed through GTM *before* the migration starts, so the new dev team only has to do one thing: inject the GTM snippet.

---

## VERIFIED OWNERSHIP (Confirmed 2026-04-16)

Audit on myvurt.com + console checks by Dioni:

| Asset | ID | Owner | Confirmed Via |
|---|---|---|---|
| GTM container | `GTM-MN8TR3CR` | VURT (dioni@myvurt.com, Admin) | tagmanager.google.com |
| Meta Pixel | `659791066496981` | VURT Business Portfolio | business.facebook.com |
| TikTok Pixel | `D7GJKJBC77UBV63HQDUG` (VURT Web Pixel) | VURT_bc_7a8ics Business Center | ads.tiktok.com — 21 events received |
| Firebase project | `vurt-bd356` | **VURT** (dioni@myvurt.com) | console.firebase.google.com — project visible |
| GA4 measurement ID | `G-F13X2NV8D0` | VURT (property 518738893, auto-created by Firebase) | linked to Firebase project above |
| AdSense publisher | `pub-7040941372655125` | **VURT** (dioni@myvurt.com) | adsense.google.com — onboarding visible; site PENDING approval (Apr 14 email) |
| Angular SSR bundle | `main-GJKUJBAK.js` | **Enveu** (codebase) | served from myvurt.com, built by Enveu |
| Video assets CDN | `resources-us1.enveu.tv` | **Enveu** | serves og:image + media |
| NPAW/Youbora | system_code `vurt` | VURT account, Enveu-instrumented | api.youbora.com |

**What this means for migration:**
- **No Firebase risk.** VURT owns the project. New team re-uses the same config → user history, GA4 history, Firebase events all preserved.
- **No AdSense risk.** VURT owns the publisher ID. Site is still pending Google approval — if approval comes through before migration, preserve the ad code on new site.
- **No pixel risk.** All three pixel platforms (GTM, Meta, TikTok) belong to VURT accounts.
- **Asset CDN risk = low.** New dev team confirmed asset migration is fast. Enveu's `resources-us1.enveu.tv` will need to be replaced with a VURT-owned CDN on the new site.
- **Codebase risk = expected.** Angular SSR bundle disappears with Enveu — that's the point of the rebuild.

### GDPR / UK-EU compliance — OPEN ISSUE

VURT currently runs paid social ads targeting **UK users** (Simple Social — Alex/Christian/Ariella). When UK users click through to myvurt.com, the site fires Meta Pixel + TikTok Pixel + GA4 + Firebase Analytics **before** consent — all with `consent default { analytics_storage: granted, ad_storage: granted }`. This is a GDPR + UK-GDPR violation.

**Short-term mitigations (before new codebase launches):**
- [ ] Confirm with Simple Social which campaigns target UK / EU geographies
- [ ] Consider excluding UK/EU from ad targeting until Consent Mode v2 is compliant
- [ ] Document which UTM sources/campaign IDs are UK-targeted (for exclusion rules in GA4 audience filters)

**Long-term (new codebase requirements):**
- [ ] Consent Mode v2 must initialize BEFORE GTM loads (default = denied for EU/UK, granted for US)
- [ ] Consent banner on first visit for EU/UK users (IP geolocation check)
- [ ] Banner must offer: Accept / Reject / Customize
- [ ] Trigger `gtag('consent', 'update', ...)` on user action
- [ ] Meta Pixel, TikTok Pixel, GA4 all respect consent state via GTM triggers

**Risk if ignored:** Meta has started suspending ad accounts running UK campaigns from non-compliant landing pages. Loss of ad inventory would hurt more than a potential fine.

### Meta Business access — clarification

VURT's Meta Business Portfolio is NOT accessed via `dioni@myvurt.com` (Google Workspace). Meta access is tied to a **Facebook personal profile** that has been added to the VURT Business Portfolio as Admin. When communicating with ad partners (e.g., Simple Social / Alex), the email to share for Meta Ads Manager access is whatever email that personal FB profile uses, NOT `dioni@myvurt.com`.

Dioni to confirm personal FB email via business.facebook.com → profile menu (top-right) and document below:

- Meta Business login email: **`dioni.vasquez@yahoo.com`** (personal Yahoo, tied to personal FB profile)

---

## Part 1 — What Dioni Has to Do BEFORE Migration

### A. Audit what's currently live (ASAP)

Request from **Enveu**:
1. Full list of hardcoded tracking calls (`gtag`, `fbq`, `ttq`, `logEvent`, etc.) with event names and parameters
2. How GA4 is initialized (direct gtag snippet? inside Angular service? via GTM?)
3. How Firebase is initialized — SDK version, project ID, config object
4. How Meta Pixel is currently installed (if via GTM, confirm; if hardcoded, flag)
5. Consent Mode v2 implementation location
6. **User accounts backend (CRITICAL — Firebase Auth shows zero users):**
   - Where is the user database stored? (Which DB engine? Which schema?)
   - How do we export the user table?
   - How does authentication work today — custom JWT? session cookies? OAuth?
   - How does age-gate state persist across sessions?
   - Full backend API endpoint list used by web + mobile apps
   - How does the 10th-video signup rule count video views (client or server-side)?

Request from **Simple Social (Alex/Ariella)**:
- Confirm which Meta ad accounts and TikTok ad accounts are tied to which pixel IDs
- Confirm custom audiences that depend on pixel events (these break if events change)

Request from **Ari (YouTube)**:
- OAuth access for YouTube Analytics API from `ari@thesourcegroups.com` (already flagged as pending)

### B. Consolidate into GTM (while you still have Enveu)

For each hardcoded tracking call Enveu identifies, ask them to:
1. Replace with `dataLayer.push({event: '...', ...params})`
2. Leave the GTM snippet (`GTM-MN8TR3CR`) in place

You then create the matching tag in GTM. End state: tracking logic lives in GTM, code only pushes events.

**Priority order if you have limited Enveu runway:**
1. GA4 — highest priority (most historical data at stake)
2. Meta Pixel custom events (signup, video_play, age_gate_passed)
3. Firebase Analytics events
4. Everything else

### C. Document Firebase project details

Firebase is the one thing that **must** stay hardcoded but **must** preserve the same project.

**Firebase web config (verified 2026-04-16 from Firebase Console):**

```js
const firebaseConfig = {
  apiKey: "AIzaSyC9knYkkhpDdkNifqwUNrv0ppf9I0ri2A0",
  authDomain: "vurt-bd356.firebaseapp.com",
  projectId: "vurt-bd356",
  storageBucket: "vurt-bd356.firebasestorage.app",
  messagingSenderId: "522377718476",
  appId: "1:522377718476:web:1da661ac8972e7de5ab069",
  measurementId: "G-F13X2NV8D0"
};
```

These values are safe to share — they ship in the browser bundle already. They are public identifiers, not secrets. Security is enforced by Firebase Security Rules, not by the config.

**Registered apps on project `vurt-bd356`:**
- Android: `VURT` (`com.vurt.mobile`)
- iOS: `VURT iOS` (`com.vurt.mobile`)
- iOS QA: `VURT iOS-QA` (`com.vurt.mobile.qa`)
- Web: `VURT web` (App ID `1:522377718476:web:1da661ac8972e7de5ab069`)
- Parent GCP org: `thesourcegroups.com` (VURT-side entity, unrelated to Enveu)
- Support email: `developer@myvurt.com` (accessible to Dioni)
- Environment: Production

**Firebase services audit (verified 2026-04-16 by Dioni in console):**

| Service | Status | Notes |
|---|---|---|
| Hosting | ❌ Not used | myvurt.com is on Enveu infra, not Firebase Hosting |
| Authentication | ❌ **Zero users** | "No users for this project yet" — user accounts are NOT in Firebase Auth |
| Firestore | ❌ Not used | |
| Realtime Database | ❌ Not used | |
| Storage | ❌ Not used | Requires Blaze plan to enable |
| Functions | ❌ Not used | Requires Blaze plan to enable |
| Extensions | ❌ None installed | |
| Analytics (app) | ✅ Active | 69 DAU (Android 30 + iOS 39 + iOS-QA 0) |
| Analytics (web) | ✅ Active | Via `measurementId: G-F13X2NV8D0` (GA4) |
| Crashlytics | ✅ Active | Mobile crash data |
| Performance | ✅ Active | Mobile performance data |
| Plan | Spark (free) | No paid backend services |
| Service accounts | Default only | `firebase-adminsdk-fbsvc@vurt-bd356.iam.gserviceaccount.com`. No custom. |

**Simplification for migration:** Firebase on the web is *only* an analytics loader. The new dev team's Firebase obligation on the web build is minimal:
1. Copy the `firebaseConfig` object into the new web bundle
2. Call `initializeApp(firebaseConfig)` + `getAnalytics(app)` on page load
3. Done — no Auth, Firestore, Storage, or Functions wiring needed

**CRITICAL FINDING — User accounts are NOT in Firebase Auth.** VURT has a 10th-video signup rule that creates user accounts, but Firebase Authentication shows zero users. This means user accounts are stored in **Enveu's own backend**, not Firebase. This is a much larger migration risk than tracking — losing Enveu's user DB = losing every VURT user account.

**Must ask Enveu (NEW — added to Part 1.A audit list):**
- Where does the user database live? (Which DB? Which schema?)
- How do you export the user table?
- How does auth work today — custom JWT? session cookies? OAuth to a third party?
- How does age-gate state persist across sessions?
- What is the backend API endpoint list used by web + mobile apps?

**Why preserving the Firebase project still matters:** GA4 history (property `518738893`, ID `G-F13X2NV8D0`) is auto-provisioned by this Firebase project. Lose the project = lose GA4 historical data. Crashlytics + Performance baselines for mobile apps also tied to this project.

### D. Export historical data before switch-off

Pre-migration exports to have in your pocket:
- **GA4:** BigQuery export enabled + verify data is flowing there (if not, enable now and wait 24–48hr)
- **Meta Pixel:** download custom audience definitions (they're portable)
- **TikTok Pixel:** download pixel event history from Events Manager
- **NPAW:** ensure dashboards/reports are exportable; the account itself is tied to myvurt.com domain, not codebase
- **Firebase Analytics:** link to BigQuery export if not already

### E. Domain & DNS checks

Confirm these are **NOT** tied to Enveu's infrastructure:
- `myvurt.com` DNS — who controls the registrar?
- CloudFlare — whose account?
- SSL certs — auto-renewed via CloudFlare or managed by Enveu?
- Subdomains (www, api, admin, etc.) — where are they pointed?

If anything is in Enveu's CloudFlare/registrar, get it transferred to a VURT-owned account before migration.

### F. Verification environment

Ask new dev team to spin up a **staging domain** (e.g., `staging.myvurt.com` or `new.myvurt.com`) during rebuild. You'll need this to:
- Test GTM snippet installation
- Verify pixels fire
- Run UX tests with stealth browser
- Validate consent mode

---

## Part 2 — What the New Dev Team Must Preserve

### Non-negotiable: install on day 1 of the new build

**1. Google Tag Manager snippet**
- Container ID: `GTM-MN8TR3CR`
- Must be injected in `<head>` (high priority) and `<body>` (noscript fallback) on every page
- This is the single most important thing. Everything else flows through it.

**2. Firebase SDK**
- Use the existing Firebase project (config provided by Dioni)
- Preserve all `logEvent` calls currently in Enveu's codebase (Dioni will provide the audit)
- Preserve Firebase Auth setup (if user accounts are tied to Firebase)

**3. Consent Mode v2**
- Must initialize BEFORE GTM loads
- Default state: consent denied (if in EU) / granted (if US)
- Update on user consent action
- Dioni will confirm current implementation from Enveu audit

**4. Domain verification meta tags** (in `<head>`)
- Meta domain verification tag for `myvurt.com`
- TikTok domain verification tag
- Google Search Console verification tag
- Any others Dioni confirms from platform dashboards

### Nice-to-haves

**5. Server-side considerations**
- If keeping SSR (Angular Universal or equivalent), ensure GTM doesn't fire server-side
- Cloudflare/CDN headers should not strip tracking cookies
- Test rapid navigation scenarios (SPA route changes) — GTM must re-trigger PageView

**6. `dataLayer` push events to preserve**
Dioni will provide a full list post-Enveu audit. Expected set:
- `page_view` — standard
- `age_gate_passed` — user clears the age gate
- `video_play_start` — video begins playback
- `video_play_milestone_25/50/75/100` — completion tracking
- `signup_prompt_shown` — the 10th-video prompt appears
- `signup_complete` — user creates account
- `show_detail_view` — user lands on a show page

### What NOT to rebuild

- Do NOT re-install the Meta Pixel directly. It lives in GTM.
- Do NOT re-install the TikTok Pixel directly. It lives in GTM.
- Do NOT add GA4 via direct gtag snippet (it will live in GTM post-consolidation).
- Do NOT create a new Firebase project.
- Do NOT create a new GA4 property.

---

## Part 3 — Complete Integration Inventory

| Integration | Location | Migrates How | Risk if Missed |
|---|---|---|---|
| Meta Pixel | GTM (`GTM-MN8TR3CR`) | Auto (via GTM snippet) | Low — survives if GTM installed |
| TikTok Pixel (`D7GJKJBC77UBV63HQDUG`) | GTM (`GTM-MN8TR3CR`) | Auto (via GTM snippet) | Low — survives if GTM installed |
| GA4 | TBD (audit pending) | Via GTM post-consolidation | HIGH if hardcoded — historical reports break |
| Firebase Analytics | Hardcoded in Angular | Manual — preserve SDK init + events | HIGH — user history, crashlytics baselines |
| Firebase Auth | Hardcoded in Angular | Manual — preserve SDK init | CRITICAL — user accounts break |
| Consent Mode v2 | Hardcoded in Angular | Manual — port to new codebase | Medium — compliance exposure |
| NPAW | Video player integration | Depends on Mux/player setup | Medium — video analytics baseline |
| Mux video | API-based | Survives (account-level) | Low — unless player code changes |
| CloudFlare CDN | DNS/account-level | Survives (account-level) | None if VURT controls account |
| TikTok Events API (future) | Server-side | Needs re-implementation | N/A — not live yet |

---

## Part 4 — Pre-Migration Checklist

### Dioni's side
- [ ] Request audit from Enveu (items in Part 1.A)
- [ ] Request Firebase config export from Enveu
- [ ] Verify DNS/CloudFlare ownership (not Enveu's account)
- [ ] Enable BigQuery export for GA4 (if not already)
- [ ] Enable BigQuery export for Firebase Analytics
- [ ] Download Meta custom audience definitions
- [ ] Download TikTok pixel event history
- [ ] Export NPAW dashboards/reports
- [ ] Ask Enveu to migrate hardcoded tags → dataLayer (priority order: GA4 → Meta → Firebase)
- [ ] Document every custom event currently firing
- [ ] Confirm domain verification meta tags (Meta, TikTok, Google)
- [ ] Get staging/preview URL from new dev team
- [ ] Test GTM snippet on staging before go-live

### New dev team's side
- [ ] Inject `GTM-MN8TR3CR` in `<head>` and `<body>` on every page
- [ ] Preserve all meta verification tags
- [ ] Use existing Firebase project config (no new project)
- [ ] Preserve all `dataLayer.push` calls Dioni specifies
- [ ] Implement Consent Mode v2 (init before GTM)
- [ ] Ensure SSR doesn't interfere with client-side GTM firing
- [ ] Provide staging URL to Dioni for verification
- [ ] Do NOT install Meta, TikTok, or GA4 directly — they're in GTM

### Day-of-migration verification
- [ ] GTM snippet fires on staging (check via GTM Preview mode)
- [ ] Meta Pixel Helper shows PageView firing
- [ ] TikTok Pixel Helper shows PageView firing
- [ ] GA4 real-time shows traffic from staging
- [ ] Firebase events appear in DebugView
- [ ] Domain verification tags present in `<head>`
- [ ] Consent Mode v2 blocks/allows based on banner interaction
- [ ] Run stealth-browser UX test on staging
- [ ] Compare 24hr data from old vs new — events match in volume

---

## Part 5 — Known Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Enveu is unresponsive to audit request | Work from assumption that everything is hardcoded; budget rebuild effort for GA4 + Firebase events |
| New Firebase project gets created | Hard block — refuse to launch until same project is used |
| Custom audiences break due to event name changes | Preserve exact event names from Enveu audit; document in handoff |
| Consent Mode breaks (fires before consent) | Require DebugView verification before any ad spend resumes |
| SSR breaks GTM (tags fire server-side) | Test on staging with rapid route changes |
| Pixel data gap during cutover | Keep old site live until new one is verified; use DNS switch only after 24hr parallel run |

---

## Part 6 — Open Questions

- Does VURT control the Enveu CloudFlare account or does Enveu?
- ~~Is GA4 currently installed via direct gtag or via GTM?~~ **ANSWERED (2026-04-16):** GA4 is initialized by the Firebase SDK — `ep.origin=firebase` on collect requests. Firebase auto-loads gtag.js with measurement ID `G-F13X2NV8D0`. GA4 is NOT in GTM as a standalone tag. Preserving Firebase = preserving GA4 automatically.
- Are there any active Firebase A/B tests or Remote Config flags that need to be preserved?
- Is the 10th-video signup rule enforced client-side, server-side, or via Firebase Auth state?
- Does the TikTok Events API (server-side, pending dev app approval) need to be implemented on the new codebase from day 1?
- Is AdSense approval expected to come through before migration? If yes, preserve ad code on new site.

---

**Next steps:**
1. Send audit request to Enveu (Part 1.A)
2. Brief new dev team with this doc
3. Schedule 30-min call with both teams to walk through the handoff checklist together

---

## Part 7 — Dioni-Side Audit Results (2026-04-16)

Rather than wait on Enveu, Dioni performed a direct audit of the production bundle served by `myvurt.com` + reviewed the GTM container + Enveu CMS. Everything below is **verified from live artifacts**, not inferred.

### 7.1 GTM Container Inventory (VERIFIED from GTM UI — 2026-04-16)

Container `GTM-MN8TR3CR` — **Workspace Default Workspace**:

| Asset | Count | Details |
|---|---|---|
| Tags | **2** | Meta Pixel (Custom HTML), TikTok Pixel (TikTok Pixel template from Gallery) |
| Triggers | **0** | (No custom triggers — tags rely on built-in All Pages) |
| Variables | **0 custom** | Only built-in variables active |
| Folders | 0 | |
| Templates | 1 | TikTok Pixel (community template, imported) |

**Implication:** GTM is currently doing ONLY pixel delivery for Meta + TikTok. Every other tracking call (GA4, Firebase, Consent Mode, AdSense, NPAW) is **hardcoded in the Enveu Angular bundle**, NOT in GTM.

### 7.2 Hardcoded Tracking Inventory (VERIFIED from bundle)

Pulled directly from `https://www.myvurt.com/` — `index.html`, `main.js`, and all 14 lazy-loaded chunks. Findings grouped by system:

#### (a) Bundle build metadata (flagged — see 7.3)

From `index.html`:
```
// BUILD_NUMBER_99
// BRANCH:staging
var VERSION_NUMBER = 'v-26.04.15.02';
```

#### (b) Firebase (initialized inline via `<script>` in `<head>`)

Config matches what's documented in Part 1.C. Initialized via Firebase JS SDK compat build. SDK auto-loads gtag.js for GA4 (property `518738893`, measurement ID `G-F13X2NV8D0`).

#### (c) Custom Firebase Analytics events (11 discovered in bundle)

Found in `chunk-VVAE3LSX.js` as named constants — these are the events the app actively fires via `logEvent(...)`:

| Constant | Event name | Fired by |
|---|---|---|
| `ScreenViewed` | `screen_viewed` | Page/route changes (`firebaseScreenCall` in `main.js`) |
| `ContentPlay` | `content_play` | Video player start |
| `ContentPause` | `content_pause` | Video player pause |
| `ContentCompleted` | `content_completed` | Video end |
| `ContentSeclect` (sic) | `content_select` | Content tile click |
| `AddToWatchlist` | `add_to_watchlist` | Watchlist add |
| `RemoveFromWatchlist` | `remove_watchlist` | Watchlist remove |
| `ShareContent` | `share_content` | Share action |
| `SearchContentSelect` | `search_content_select` | Search result click |
| `RailSelect` | `rail_select` | Rail/row click on home |
| `Logout` | `logout` | User signs out |

**Migration note:** The new codebase must preserve these 11 event names verbatim. Any renamed event = broken GA4 reports + broken Meta/TikTok custom audiences built on `content_play` or `screen_viewed`.

**`user_engagement` IS firing (verified 2026-04-16):** Direct network-capture test on myvurt.com shows `user_engagement` hits via `ep.origin=firebase`. Timeline from test run:

| t | Event | `_et` (engagement_time_msec) | Trigger |
|---|---|---|---|
| 6.37s | `page_view` | — | Initial load |
| 27.46s | **`user_engagement`** | 19,218 ms | visibilitychange → hidden |
| 37.67s | `screen_viewed` + **`user_engagement`** | 3,764 ms | SPA navigation |
| 56.84s | `page_view` | — | Detail page hydrated |

Firebase Web SDK's GA4 wrapper is relaying `user_engagement` on this site. **My earlier claim that Firebase doesn't fire it was wrong — retracted.**

Test results: `/tmp/engagement-test-results.json`. Reproducible via `/tmp/engagement-test.py`.

**Implication for the paid-ads engagement gap:** the documented "SSR broke engagement" phase (~99.6% bounce) cannot be explained by `user_engagement` being absent — it fires fine under normal flow. The real cause is more likely one or more of: (a) users bouncing under ~1s before JS hydration, (b) SSR serving degraded HTML that didn't boot Firebase at all, (c) Consent Mode / ad-tracker blockers. Needs a separate investigation with archived bundle from the bounce-spike period, not this audit.

#### (d) Consent Mode v2 (hardcoded as "granted")

In `index.html` — fires BEFORE GTM loads:
```js
gtag('consent', 'default', {
  analytics_storage: 'granted',
  ad_storage: 'granted',
});
```

No geolocation check. No consent banner. No `update` call. Every visitor (including UK/EU) gets full pixel firing immediately. **GDPR / UK-GDPR violation** (see existing note under VERIFIED OWNERSHIP).

#### (e) Google AdSense loader (hardcoded)

In `index.html` `<head>`:
```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7040941372655125" crossorigin="anonymous"></script>
```

Loads on every page, regardless of AdSense approval status. Publisher ID matches Dioni's AdSense account (pending approval).

#### (f) Firebase Dynamic Links (hardcoded — DEPRECATED)

Bundle references Firebase Dynamic Links short links. **Google is shutting Firebase Dynamic Links down — service retirement announced.** Any deep-link flow relying on FDL will break by that date. The new codebase must NOT use Firebase Dynamic Links. Replace with:
- Apple Universal Links + Android App Links (recommended), or
- A third-party deep link service (Branch, Adjust, AppsFlyer)

Separately: Enveu's CMS also has a "Linkly" deep link system. Unclear whether the FDL links in the bundle are generated by Linkly or are a separate legacy system — flag for Enveu.

#### (g) NPAW / Youbora

Video player instruments NPAW with `accountCode: 'vurt'`. Data posts to `api.youbora.com`. Independent of Firebase — survives as long as the new video player's NPAW config keeps the same `accountCode`.

### 7.3 Current-Site Observations (Enveu bundle audit — documentation only)

These are findings about the CURRENT Enveu-served site. The new build is net-new; it will NOT inherit these. Listed here as documentation and as clarifying asks for Enveu.

| # | Finding | Evidence | Why it matters NOW |
|---|---|---|---|
| 1 | Production site bundle is labeled `BRANCH:staging` | `BRANCH:staging` comment in live `index.html`; version tag `v-26.04.15.02` | Unclear — could be CI convention or could indicate unreviewed deploys. Ask Enveu to clarify whether a separate `main`/`production` branch exists. No evidence linking this to bounce performance. |
| 2 | QA CDN asset leak in production bundle | References to `https://resources-qa.enveu.tv/PowerNews/statics/web/icons/...` in `chunk-D53A6YBJ.js` | Low impact — ask Enveu to confirm it's benign. |
| 3 | Mixed Enveu API endpoints | Bundle references both `*.enveu.tv` and `*.enveu.io` hosts | Ask Enveu to clarify which is authoritative. |
| 4 | Consent Mode hardcoded `granted` for all geographies | See 7.2(d) | **GDPR / UK-GDPR exposure on currently-live site.** Matters for the paid ads campaign running NOW, not for the new build. |
| 5 | Firebase Dynamic Links referenced in bundle | See 7.2(f) | Only relevant if current-site deep links are in active use. New build chooses its own deep link solution. |

### 7.4 End-User Account Location (VERIFIED from Enveu CMS — 2026-04-16)

Confirmed via Enveu CMS (`studio-beta-us1.enveu.tv`) home dashboard: the left nav exposes **Subscriptions & Payments → Customer** as the user backend.

**Verified user counts (CMS → Subscription Manager Dashboard → Customers, Mar 18–Apr 16 window):**

| Metric | Count |
|---|---|
| Registered Customers From Apps | 1,199 |
| Registered Customers From CMS | 0 |
| Active Customers | 1,199 |
| Blocked Customers | 0 |
| Active Accounts | 1,220 |
| Platform split | Web 82.66% / iOS 9.44% / Android 7.90% |

- **Firebase Auth: zero users.** (Already verified in Part 1.C.)
- **Enveu CMS → Customer table: holds all 1,199+ VURT end-user accounts.** This is the authoritative source.
- Registered app channels on the Enveu project: Android Mobile App, iOS Mobile App, Web Desktop App.
- Signup gate counts: `firstSignUp: 5`, `secondSignUp: 10` — found in the app's ng-state config JSON embedded in `index.html`.

**Migration requirement — add to Enveu ask list:**
- [ ] Full export of Customer table (with PII handling: email, age-gate status, watchlist, view history)
- [ ] Schema definition of Customer table
- [ ] Documentation of auth flow (how the Enveu backend issues/validates sessions for the web + mobile apps)
- [ ] API endpoint list that the web bundle hits for auth / content / watchlist
- [ ] Clarify mobile vs web auth separation (both platforms' users are in the same Customer table, but auth mechanisms may differ)

### 7.5 What The New Build MUST Preserve vs. What's Net-New Decision

The new codebase is net-new. Only items below are non-negotiable preservations. Everything else is the new team's call.

**MUST preserve (preservation items):**

| Item | Why | How |
|---|---|---|
| GTM container `GTM-MN8TR3CR` | Keeps Meta + TikTok pixels alive without re-approval | Inject snippet in `<head>` + `<body>` |
| Firebase project `vurt-bd356` | Preserves GA4 property 518738893 history + mobile Crashlytics/Performance baselines | Re-use same `firebaseConfig` in web init |
| GA4 measurement ID `G-F13X2NV8D0` | History continuity | Auto-preserved if Firebase config is preserved |
| 11 custom event names (7.2c) | Preserves Meta / TikTok custom audiences + GA4 reports built on these names | Fire identical event names from new code (mechanism up to new team) |
| NPAW account code `vurt` | Preserves video QoE historical baseline | Set `accountCode: 'vurt'` in new video player NPAW config |
| Domain verification meta tags | Preserves Meta/TikTok/Google Search Console domain trust | Copy `<meta>` tags to new `<head>` |
| **End-user accounts (1,199+ customers)** | Losing these = losing every VURT user | Export Customer table from Enveu CMS → import to new backend |

**New team decides (not preservation items — their architecture call):**

- Whether to use Firebase Web SDK for GA4 loading (current method, verified working for `user_engagement`), or raw gtag.js / GTM
- Which deep link solution (Universal Links, App Links, Branch, Adjust — NOT Firebase Dynamic Links since it's being retired)
- Consent Mode v2 banner implementation (must be correct for GDPR, but architecture is theirs)
- Whether to adopt the existing 11 custom event names exactly (recommended for history) or add/rename (breaks history)
- SSR vs CSR, framework choice, CDN, auth mechanism, everything backend

**Not relevant to new build (Enveu-specific, dies with Enveu):**

- `BRANCH:staging` build label
- `resources-qa.enveu.tv/PowerNews/...` asset references
- `enveu.tv` / `enveu.io` endpoint references
- Enveu CMS's Linkly deep link system
- The specific Firebase Dynamic Links URLs embedded in current bundle
- Hardcoded consent `granted` default

### 7.6 Updated Asks to Enveu (consolidated)

Replace Part 1.A items 1–5 with this — Dioni has now done #1 independently, but Enveu still owns authoritative answers on the rest:

1. ~~Hardcoded tracking call list~~ ✅ Dioni has done this (see 7.2). Enveu to confirm completeness.
2. Why is the production bundle on `BRANCH:staging`? Is there a separate `main`/`production` branch? If so, what differs?
3. Explain the Linkly vs Firebase Dynamic Links split — which system is currently generating deep links, and what depends on each?
4. Confirm the `resources-qa.enveu.tv/PowerNews/...` references are safe to ignore (or provide a patched bundle).
5. **User accounts / backend (the blocker):**
    - Full schema of the Customer table (Subscriptions & Payments → Customer in CMS)
    - Export format + export process
    - Authentication flow documentation (session/JWT/OAuth mechanics)
    - Full backend API endpoint list used by Web + Android + iOS
    - How age-gate state persists
    - How signup gate counts (`firstSignUp: 5`, `secondSignUp: 10`) are enforced (client vs server)
6. Documentation of any Firebase Remote Config / A/B Test flags currently live (if any).

### 7.7 Questions Now Answered (from Part 6)

- ~~Is GA4 installed via direct gtag or via GTM?~~ **Via Firebase SDK auto-load. Not in GTM.**
- ~~What's in the GTM container?~~ **Only 2 tags: Meta Pixel + TikTok Pixel. No triggers, no custom variables.**
- ~~Where are user accounts stored?~~ **Enveu CMS → Subscriptions & Payments → Customer table. NOT Firebase Auth.**
- ~~Is the 10th-video signup rule configurable?~~ **Yes — `firstSignUp: 5`, `secondSignUp: 10` in the app config JSON. Enforcement mechanism (client vs server) still TBD.**
