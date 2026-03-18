# VURT Audit — Action Items
**Prepared:** March 18, 2026 | **Audit Date:** March 17, 2026

---

## For Engineering / Enveu

These are all changes that need to happen in the Enveu CMS or codebase.

### 1. Mobile footer is completely broken
The website footer renders at `height: 0` on mobile. Everything inside it — social links, App Store badge, Google Play badge — is invisible to mobile visitors. The hamburger menu has a social section container but Angular renders it empty (no icons). This means **mobile visitors have no way to find VURT's social accounts or download the app** from the website.

**What to do:**


- Check why `<app-footer>` collapses to 0px on mobile viewports. Likely a CSS rule tied to the bottom nav bar that's hiding the footer entirely instead of restructuring it.
- Either fix the footer to render on mobile, or move social links and app download badges into the hamburger menu (the `header-social-link` container already exists but is empty).
- This is the highest-impact fix — every mobile visitor from the TechCrunch article is hitting this.

### 2. Add Apple Smart App Banner
There's no `<meta name="apple-itunes-app">` tag in the page source. This is the tag that makes Safari on iPhone show a native "VURT — Open" banner at the top of the page, linking directly to the App Store. It's the highest-converting iOS install mechanism and it's free.

**What to do:**

- Add this to the `<head>` of `index.html`:
  ```html
  <meta name="apple-itunes-app" content="app-id=6757593810">
  ```
- That's it. One line.

### 3. Fix iOS App Store link region
The App Store link in the footer points to `https://apps.apple.com/in/app/vurt/id6757593810`. The `/in/` is India. This may cause issues for users in other regions.

**What to do:**

- Change the link to regionless: `https://apps.apple.com/app/vurt/id6757593810`
- Apple will auto-redirect users to their local store.

### 4. Replace QA CDN assets
All 7 footer images (5 social icons + 2 app store badges) are served from `resources-qa.enveu.tv/PowerNews/`. "PowerNews" is a different Enveu customer, and this is their **QA** environment — not production. The images work today, but they'll break without warning if that client's QA environment is recycled or taken down.

**Affected image paths:**

- `resources-qa.enveu.tv/PowerNews/statics/web/icons/facebook.png`
- `resources-qa.enveu.tv/PowerNews/statics/web/icons/instagram.png`
- `resources-qa.enveu.tv/PowerNews/statics/web/icons/Twitter-x.png`
- `resources-qa.enveu.tv/PowerNews/statics/web/icons/LinkedIn.png`
- `resources-qa.enveu.tv/PowerNews/statics/web/icons/youtube.png`
- `resources-qa.enveu.tv/PowerNews/statics/web/icons/apple-store.png`
- `resources-qa.enveu.tv/PowerNews/statics/web/icons/google-play.png`

**What to do:**

- Upload VURT's own icon assets to VURT's production CDN (`resources-us1.enveu.tv/VURT_...`) and update the references. Ask Enveu why the default template is pulling from another client's QA bucket.

### 5. Fix footer social link URLs
The social links in the footer point to incorrect URLs:
- `tiktok.com/myvurt` → should be `tiktok.com/@myvurt` (missing `@`)
- `twitter.com/myvurt` → should be `x.com/myvurt` (Twitter rebranded to X)
- `youtube.com/vurticals` → confirm whether this is the right channel or if it should be `youtube.com/@myVURT1`

**What to do:**

- Update all three URLs in the Enveu CMS footer settings.

### 6. Fix Terms of Service typo
Section 7 heading says "SUBISSION" instead of "SUBMISSION".

**What to do:**

- Find and replace in the ToS page content. One word fix.

---

## For Social / Marketing

### 7. Kill @VURT_Official handles
`@VURT_Official` is dead on both Instagram ("Sorry, this page isn't available") and TikTok ("Couldn't find this account").

**What to do:**

- Check if these handles were ever owned by VURT. If yes, try to recover through platform support.
- If they were never VURT's, make sure no VURT materials reference them. Search all bios, link trees, email signatures, and printed materials for any mention.
- Consider registering them if available, even just to redirect or prevent squatting.

### 8. Build a real TikTok presence
@myvurt on TikTok has **1 follower and 4 videos**. For a vertical-first streaming platform, TikTok should be the strongest channel. Right now it's the weakest.

**What to do:**

- Stop cross-posting Instagram content to TikTok — it doesn't perform the same way.
- Create TikTok-native content: scene clips from titles with trending audio, behind-the-scenes with creators, "what to watch on VURT" series, reaction-style hooks.
- Post at minimum 1x/day for the first 30 days to build algorithmic momentum.
- Engage with vertical storytelling and indie film communities on TikTok.

### 9. Drive Google Play installs and reviews
Google Play has **10+ downloads and zero reviews**. iOS has 11 ratings at 4.7 stars. The gap is significant.

**What to do:**

- Add in-app review prompts for Android users after positive moments (finishing a title, adding to My List).
- Include Google Play link alongside App Store link in all social posts and bios.
- Consider a small paid install campaign targeting Android users in key demographics.

### 10. Promote Snapchat
@myvurt on Snapchat is actively posting (last updated March 16) with a solid bio and branded content, but it's not promoted anywhere — not in the website footer, not in Instagram bio, not in any link trees.

**What to do:**

- Add Snapchat to the website footer alongside the other social icons.
- Add to Instagram/TikTok link trees.
- Cross-promote Snapchat content on Stories across platforms.

### 11. Match posting cadence across platforms
Instagram is at 21 posts in ~4 weeks — solid. TikTok, YouTube, and Facebook are significantly behind.

**What to do:**

- Set a minimum posting schedule: TikTok 1x/day, YouTube Shorts 3x/week, Facebook 3x/week.
- Repurpose content across platforms but adapt format/captions for each (don't just cross-post identical content).

### 12. YouTube Shorts are working — double down
The Overtown/Black Miami history Short hit **1.1K views** organically with only 7 subscribers. Cultural/historical content is resonating.

**What to do:**

- Produce more cultural history Shorts — this is a discovery funnel into the VURT catalog.
- Pin the best-performing Short to the channel page.
- Add end screens or pinned comments linking to related VURT titles.

### 13. Leverage the TechCrunch piece everywhere
The TechCrunch feature by Lauren Forristal is the biggest press hit to date. It should be working harder.

**What to do:**

- Pin the TechCrunch announcement post on Instagram, TikTok, Facebook, and YouTube.
- Add "As featured in TechCrunch" badge or quote to myvurt.com homepage.
- Use the article link in all creator outreach emails.
- Create a highlight/story on Instagram dedicated to press coverage.
- Share with existing creators on the platform so they can reshare to their audiences.

### 14. Claim unclaimed handles
- **Vimeo:** `myvurt` is available — register even if not using immediately.
- **Kick:** `vurt` appears unclaimed — register if the platform is relevant.
- **Discord:** `discord.com/invite/myvurt` returns "Invite Invalid" — set up a fresh server for community building.

### 15. Get creator testimonials
Filmmakers who've submitted content to VURT should be posting about their experience. This is the social proof that drives the creator flywheel.

**What to do:**

- Reach out to creators currently on the platform and ask for a short quote or video about their experience.
- Reshare creator testimonials across all VURT social channels.
- Feature creator spotlights as a recurring content series.

---

## For App Store / Product

### 16. Google Play data safety inconsistency
The data safety section claims "no data collected" but also lists data shared with third parties. This is a contradiction that could get flagged by Google.

**What to do:**

- Review and correct the data safety declaration in Google Play Console to accurately reflect what data is collected and shared.

### 17. Push iOS ratings volume
4.7 stars from 11 ratings is great quality but low volume. More ratings build trust and improve App Store search ranking.

**What to do:**

- Implement `SKStoreReviewController` to prompt ratings after positive engagement moments (finishing a title, 3rd session, adding to My List).
- Don't over-prompt — Apple limits when the dialog appears.

### 18. Consolidate email addresses
Four different email addresses are listed across the site with no guide on which to use:
- `info@myvurt.com` (Terms page)
- `support@myvurt.com` (Terms + FAQ)
- `contact@myvurt.com` (Contact page)
- `submissions@myvurt.com` (Facebook + FAQ)

**What to do:**

- Decide on a clear routing: one for general inquiries, one for creator submissions, one for support.
- Update all pages to use consistent contact info. Consider consolidating to 2 addresses max.
