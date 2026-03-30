#!/usr/bin/env python3
"""
VURT Analytics Insights Engine
Contextually-aware analysis tied to VURT's business model, growth stage, and strategic goals.

Business context this engine understands:
- VURT is an ad-supported micro-drama platform (NOT pay-per-episode like ReelShort/DramaBox)
- Soft launch Feb 23, official launch Mar 17, 2026
- Current audience skews female 40s — growth target is 18-30
- Flywheel: content → distribution → community → interactivity → IRL → ads
- Key moats: cultural authenticity, creator ownership, no paywall
- Web is enveu Angular SPA (bad SEO, no SSR). App experience is 10x better.
- Revenue model is AVOD + product placement (not yet live)
- 80 series in library, notable talent (Kevin Hart, Vivica A. Fox, etc.)
- Competitor benchmarks: ReelShort ~$1.2B gross, DramaBox $323M rev
"""

from ga4_client import fmt_num, fmt_duration, fmt_pct, wow_delta


def generate_insights(data):
    """Analyze all collected data and return structured insights with priority levels."""
    insights = []

    yd = data.get("yesterday", {})
    db = data.get("day_before", {})
    tw = data.get("this_week", {})
    lw = data.get("last_week", {})
    sources = data.get("sources", [])
    platforms = data.get("platforms", [])
    retention = data.get("retention", [])
    trend = data.get("trend", [])
    geo = data.get("geo", [])
    devices = data.get("devices", [])
    landing = data.get("landing", [])
    hours = data.get("hours", [])
    pages = data.get("pages", [])
    events = data.get("events", [])

    # =========================================================================
    # 0. TOP SIGNAL TODAY — the single most important thing that changed
    # =========================================================================
    top_signal = _top_signal_today(data)
    if top_signal:
        insights.append(top_signal)

    # =========================================================================
    # 1. HEALTH SCORE — quick pulse check
    # =========================================================================
    health = _calculate_health_score(data)
    if health:
        insights.append(health)

    # =========================================================================
    # 2. ACQUISITION QUALITY — are we buying the right eyeballs?
    # =========================================================================
    insights.extend(_analyze_acquisition(sources, tw))

    # =========================================================================
    # 3. PLATFORM CONVERSION — web is leaking, app retains
    # =========================================================================
    insights.extend(_analyze_platform_gap(platforms, data))

    # =========================================================================
    # 4. RETENTION & STICKINESS — are people coming back?
    # =========================================================================
    insights.extend(_analyze_retention(retention, tw, lw))

    # =========================================================================
    # 5. CONTENT PERFORMANCE — GA4 pages + NPAW video signals
    # =========================================================================
    insights.extend(_analyze_content(pages, landing))
    npaw_top = data.get("npaw_top")
    npaw_daily = data.get("npaw_daily")
    if npaw_top and npaw_daily:
        insights.extend(_analyze_npaw_content(npaw_top, npaw_daily))

    # =========================================================================
    # 6. GROWTH TRAJECTORY — momentum check
    # =========================================================================
    insights.extend(_analyze_growth(trend, tw, lw))

    # =========================================================================
    # 7. AUDIENCE TIMING — when to reach them
    # =========================================================================
    insights.extend(_analyze_timing(hours, data.get("timezone", "UTC")))

    # =========================================================================
    # 8. GEO EXPANSION — international signals
    # =========================================================================
    insights.extend(_analyze_geo(geo))

    # =========================================================================
    # 9. STRATEGIC IMPLICATIONS — connecting data to VURT's flywheel
    # =========================================================================
    insights.extend(_strategic_implications(data))

    return insights


def _calculate_health_score(data):
    """Overall platform health score out of 100."""
    tw = data.get("this_week", {})
    lw = data.get("last_week", {})
    sources = data.get("sources", [])
    platforms = data.get("platforms", [])
    retention = data.get("retention", [])

    if not tw:
        return None

    scores = {}

    # Growth (0-25): DAU trend
    tw_users = float(tw.get("activeUsers", 0))
    lw_users = float(lw.get("activeUsers", 0)) if lw else 0
    if lw_users > 0:
        growth_rate = (tw_users - lw_users) / lw_users
        scores["Growth"] = min(25, max(0, int(growth_rate * 5)))  # 500%+ = 25
    else:
        scores["Growth"] = 25 if tw_users > 100 else 5

    # Engagement (0-25): engagement rate
    eng_rate = float(tw.get("engagementRate", 0))
    scores["Engagement"] = min(25, int(eng_rate * 100))  # 25%+ = 25

    # Retention (0-25): returning user %
    tw_rows = [r for r in retention if r.get("dateRange") == "date_range_0"]
    tw_ret = next((r for r in tw_rows if r.get("newVsReturning") == "returning"), None)
    tw_new = next((r for r in tw_rows if r.get("newVsReturning") == "new"), None)
    if tw_ret and tw_new:
        ret_users = float(tw_ret.get("activeUsers", 0))
        new_users = float(tw_new.get("activeUsers", 0))
        total = ret_users + new_users
        ret_pct = (ret_users / total * 100) if total > 0 else 0
        scores["Retention"] = min(25, int(ret_pct * 1.25))  # 20%+ = 25
    else:
        scores["Retention"] = 3  # No data = concerning

    # Traffic Quality (0-25): % of traffic that's organic or direct
    if sources:
        total_sessions = sum(float(s.get("sessions", 0)) for s in sources)
        quality_sessions = sum(
            float(s.get("sessions", 0)) for s in sources
            if s.get("sessionDefaultChannelGroup", "") in ["Direct", "Organic Search", "Organic Social", "Referral"]
        )
        quality_pct = (quality_sessions / total_sessions * 100) if total_sessions > 0 else 0
        scores["Traffic Quality"] = min(25, int(quality_pct / 2))  # 50%+ = 25
    else:
        scores["Traffic Quality"] = 5

    total = sum(scores.values())

    # Build the score display with explanations
    bar_items = []
    for name, score in scores.items():
        bar_items.append(f"{name}: {score}/25")

    grade = "A" if total >= 80 else "B" if total >= 60 else "C" if total >= 40 else "D" if total >= 20 else "F"

    # Build scoring methodology explanation
    explanations = []

    # Growth explanation
    if lw_users > 0:
        growth_rate = (tw_users - lw_users) / lw_users
        explanations.append(f"Growth ({scores['Growth']}/25): WoW user growth {growth_rate*100:.0f}% — 500%+ = 25/25")
    else:
        explanations.append(f"Growth ({scores['Growth']}/25): No prior week baseline")

    # Engagement explanation
    explanations.append(f"Engagement ({scores['Engagement']}/25): {eng_rate*100:.1f}% engagement rate — 25%+ = 25/25")

    # Retention explanation
    if tw_ret and tw_new:
        explanations.append(f"Retention ({scores['Retention']}/25): {ret_pct:.1f}% returning users — 20%+ = 25/25")
    else:
        explanations.append(f"Retention ({scores['Retention']}/25): GA4 not reporting new vs returning — scored 3 (data gap)")

    # Traffic Quality explanation
    if sources:
        explanations.append(f"Traffic Quality ({scores['Traffic Quality']}/25): {quality_pct:.0f}% organic/direct traffic — 50%+ = 25/25")

    return (
        f"**Platform Health Score: {total}/100 ({grade})**\n"
        f"   {' | '.join(bar_items)}\n"
        f"   **How it's scored:** " + " | ".join(explanations) + "\n"
        f"   *For a 4-week-old platform, focus on Engagement and Retention — Growth can be bought, stickiness can't.*"
    )


def _analyze_acquisition(sources, tw):
    """Deep analysis of traffic acquisition quality."""
    insights = []
    if not sources:
        return insights

    total_sessions = sum(float(s.get("sessions", 0)) for s in sources)
    total_engaged = sum(float(s.get("engagedSessions", 0)) for s in sources)

    # Build channel quality map
    channels = []
    for s in sources:
        ch = s.get("sessionDefaultChannelGroup", "")
        sessions = float(s.get("sessions", 0))
        eng_rate = float(s.get("engagementRate", 0))
        avg_dur = float(s.get("averageSessionDuration", 0))
        engaged = float(s.get("engagedSessions", 0))
        share = (sessions / total_sessions * 100) if total_sessions > 0 else 0
        channels.append({
            "name": ch, "sessions": sessions, "eng_rate": eng_rate,
            "avg_dur": avg_dur, "engaged": engaged, "share": share
        })

    # Identify the dominant channel
    dominant = max(channels, key=lambda c: c["sessions"])
    if dominant["share"] > 70 and dominant["eng_rate"] < 0.15:
        # Calculate cost-per-engaged-user proxy
        total_dom_sessions = dominant["sessions"]
        dom_engaged = dominant["engaged"]
        waste_pct = ((total_dom_sessions - dom_engaged) / total_dom_sessions * 100) if total_dom_sessions > 0 else 0

        insights.append(
            f"**Acquisition efficiency problem:** {dominant['name']} is {dominant['share']:.0f}% of traffic "
            f"but {waste_pct:.0f}% of those sessions don't engage (avg {dominant['avg_dur']:.0f}s). "
            f"That's ~{fmt_num(str(total_dom_sessions - dom_engaged))} wasted sessions this week. "
            f"**Action:** Test deep-linking ads to specific series pages (Favorite Son, Girl In The Closet) "
            f"instead of the homepage. Test video-first ad creative showing actual show clips. "
            f"Tighten targeting to 18-50 interest-based audiences."
        )

    # Highlight organic channels
    organic_channels = [c for c in channels if c["name"] in ["Organic Search", "Organic Social", "Direct", "Referral"]]
    if organic_channels:
        total_organic = sum(c["sessions"] for c in organic_channels)
        total_organic_engaged = sum(c["engaged"] for c in organic_channels)
        organic_eng = (total_organic_engaged / total_organic) if total_organic > 0 else 0
        organic_share = (total_organic / total_sessions * 100) if total_sessions > 0 else 0

        best = max(organic_channels, key=lambda c: c["eng_rate"])
        insights.append(
            f"**Organic signal:** {organic_share:.0f}% of traffic is organic/direct, "
            f"but it drives {organic_eng*100:.0f}% engagement — {organic_eng / max(dominant['eng_rate'], 0.01):.0f}x "
            f"more valuable per session than paid. Best channel: {best['name']} at "
            f"{best['eng_rate']*100:.0f}% engagement, {fmt_duration(str(best['avg_dur']))} avg. "
            f"**Action:** Prioritize the SEO fixes from the dev call — "
            f"auto-populated sitemap, SSR/pre-rendering for Angular, unique episode URLs, "
            f"and per-page meta tags. Each fix directly grows this high-value channel."
        )

    return insights


def _analyze_platform_gap(platforms, data):
    """Analyze the web vs. app experience gap."""
    insights = []
    if not platforms:
        return insights

    web = next((p for p in platforms if p.get("platform") == "web"), None)
    ios = next((p for p in platforms if p.get("platform") == "iOS"), None)
    android = next((p for p in platforms if p.get("platform") == "Android"), None)

    if not web or not (ios or android):
        return insights

    web_eng = float(web.get("engagementRate", 0))
    web_dur = float(web.get("averageSessionDuration", 0))
    web_users = float(web.get("activeUsers", 0))

    app_platforms = [p for p in [ios, android] if p]
    app_eng = sum(float(p.get("engagementRate", 0)) for p in app_platforms) / len(app_platforms)
    app_dur = sum(float(p.get("averageSessionDuration", 0)) for p in app_platforms) / len(app_platforms)
    app_users = sum(float(p.get("activeUsers", 0)) for p in app_platforms)

    if app_eng > web_eng * 2:
        insights.append(
            f"**The app is the product, the web is the funnel:** App engagement is "
            f"{app_eng*100:.0f}% with {fmt_duration(str(app_dur))} sessions. "
            f"Web is {web_eng*100:.0f}% with {fmt_duration(str(web_dur))}. "
            f"That's a {app_eng/max(web_eng, 0.01):.0f}x gap — {fmt_num(str(web_users))} web users "
            f"vs {fmt_num(str(app_users))} on app. "
            f"**Action:** Measure web-to-app conversion rate. "
            f"Ensure app download CTAs are prominent on mobile web (above the fold, post-episode). "
            f"Given the {app_eng/max(web_eng, 0.01):.0f}x engagement difference, "
            f"every percentage point of web→app conversion meaningfully grows engaged users."
        )

    # Platform-specific metrics
    if ios and android:
        ios_dur = float(ios.get("averageSessionDuration", 0))
        android_dur = float(android.get("averageSessionDuration", 0))
        ios_users = float(ios.get("activeUsers", 0))
        android_users = float(android.get("activeUsers", 0))

        if android_dur > ios_dur * 1.5 and android_users > 20:
            # Build app store comparison from live data
            app_store_note = ""
            app_stores = data.get("app_stores", {})
            ios_store = app_stores.get("ios", {})
            android_store = app_stores.get("android", {})

            store_parts = []
            ios_rating = ios_store.get("rating")
            ios_count = ios_store.get("rating_count")
            android_rating = android_store.get("rating")
            android_count = android_store.get("rating_count")

            if ios_rating is not None:
                store_parts.append(f"iOS: {ios_rating:.1f}★ ({ios_count or 0} ratings)")
            if android_rating is not None:
                store_parts.append(f"Android: {android_rating:.1f}★ ({android_count or 0} ratings)")
            elif android_store.get("rating_count") == 0 and not android_store.get("error"):
                store_parts.append(f"Android: 0 ratings")
            elif android_store.get("error"):
                store_parts.append(f"Android: could not fetch rating")

            if store_parts:
                app_store_note = f" Store ratings: {', '.join(store_parts)}."
            elif ios_store.get("error") and android_store.get("error"):
                app_store_note = " (Could not fetch app store ratings — verify manually.)"

            insights.append(
                f"**Android users are power viewers:** {fmt_duration(str(android_dur))} avg sessions "
                f"vs {fmt_duration(str(ios_dur))} on iOS. Only {fmt_num(str(android_users))} Android users "
                f"vs {fmt_num(str(ios_users))} iOS — but they watch longer.{app_store_note}"
            )

    return insights


def _analyze_retention(retention, tw, lw):
    """Analyze user retention and stickiness."""
    insights = []

    tw_rows = [r for r in retention if r.get("dateRange") == "date_range_0"]
    lw_rows = [r for r in retention if r.get("dateRange") == "date_range_1"]

    tw_new = next((r for r in tw_rows if r.get("newVsReturning") == "new"), None)
    tw_ret = next((r for r in tw_rows if r.get("newVsReturning") == "returning"), None)

    if tw_new and tw_ret:
        new_users = float(tw_new.get("activeUsers", 0))
        ret_users = float(tw_ret.get("activeUsers", 0))
        total = new_users + ret_users
        ret_pct = (ret_users / total * 100) if total > 0 else 0
        ret_eng = float(tw_ret.get("engagementRate", 0))
        ret_dur = float(tw_ret.get("averageSessionDuration", 0))
        new_eng = float(tw_new.get("engagementRate", 0))
        new_dur = float(tw_new.get("averageSessionDuration", 0))

        if ret_pct < 5:
            insights.append(
                f"**Retention is the #1 problem to solve:** Only {ret_pct:.1f}% returning users "
                f"({fmt_num(str(ret_users))} of {fmt_num(str(total))}). "
                f"Returning users engage at {ret_eng*100:.0f}% for {fmt_duration(str(ret_dur))} — "
                f"they're {ret_eng/max(new_eng, 0.001):.0f}x more valuable than new users. "
                f"**This is normal for week 4 of launch with paid acquisition**, but it needs to trend up. "
                f"**Actions:** (1) Push notification strategy for episode drops. "
                f"(2) Email capture on first visit — 'New episodes drop every week.' "
                f"(3) 'Continue watching' feature prominent on homepage. "
                f"(4) Cliffhanger previews in share links to pull people back."
            )
        elif ret_pct >= 5 and ret_pct < 15:
            insights.append(
                f"**Retention building:** {ret_pct:.1f}% returning users — early but trending. "
                f"Returning users stay {fmt_duration(str(ret_dur))} vs {fmt_duration(str(new_dur))} for new. "
                f"Focus on converting the {eng_pct:.0f}% who engage on first visit into repeat visitors."
            )
        elif ret_pct >= 15:
            insights.append(
                f"**Retention is healthy:** {ret_pct:.1f}% returning users with "
                f"{ret_eng*100:.0f}% engagement. This is strong for a new platform."
            )

        # WoW retention trend
        lw_ret = next((r for r in lw_rows if r.get("newVsReturning") == "returning"), None)
        lw_new = next((r for r in lw_rows if r.get("newVsReturning") == "new"), None)
        if lw_ret and lw_new:
            lw_ret_users = float(lw_ret.get("activeUsers", 0))
            lw_total = float(lw_new.get("activeUsers", 0)) + lw_ret_users
            lw_ret_pct = (lw_ret_users / lw_total * 100) if lw_total > 0 else 0
            ret_abs_change = ret_users - lw_ret_users
            if ret_abs_change > 0:
                insights.append(
                    f"**Returning users grew:** {fmt_num(str(lw_ret_users))} → {fmt_num(str(ret_users))} "
                    f"returning users WoW (+{fmt_num(str(ret_abs_change))}). "
                    f"Rate shifted {lw_ret_pct:.1f}% → {ret_pct:.1f}% (rate may drop as new users flood in — "
                    f"watch the absolute number, not the percentage)."
                )
    elif not tw_new and not tw_ret:
        insights.append(
            f"**Retention data gap:** GA4 isn't splitting new vs returning users cleanly. "
            f"This may be a data stream configuration issue — worth flagging to enveu's dev team."
        )

    # Sessions per user as stickiness proxy
    if tw:
        spu = float(tw.get("sessionsPerUser", 0))
        if spu < 1.2:
            insights.append(
                f"**Low session depth:** {spu:.1f} sessions per user means almost nobody comes back "
                f"within the same week. For a content platform, target is 2.0+. "
                f"**This is the leaky bucket:** paid ads bring people in, they watch once (or bounce), "
                f"and don't return. Solve this before scaling ad spend further."
            )

    return insights


def _analyze_content(pages, landing):
    """Analyze content performance and discovery."""
    insights = []

    if pages:
        # Find high-engagement content — skip unidentifiable entries
        skip_names = {"(not set)", "", " ", "not set"}
        for p in pages:
            name = p.get("unifiedScreenName", "").strip()
            if not name or name.lower() in skip_names:
                continue
            views = float(p.get("screenPageViews", 0))
            users = float(p.get("activeUsers", 0))
            eng_time = float(p.get("userEngagementDuration", 0))

            if users > 0 and eng_time > 0:
                avg_time_per_user = eng_time / users
                if avg_time_per_user > 300 and users > 5:  # 5+ min avg, meaningful sample
                    insights.append(
                        f"**Sticky content:** '{name[:45]}' averages {fmt_duration(str(avg_time_per_user))} "
                        f"per user ({fmt_num(str(users))} users, {fmt_num(str(views))} views). "
                        f"This is content worth promoting in ads and social."
                    )
                    break  # Only flag the best one

        # Flag "(not set)" as a tracking issue if it has significant engagement
        not_set = [p for p in pages if p.get("unifiedScreenName", "").strip() in skip_names or not p.get("unifiedScreenName", "").strip()]
        for ns in not_set:
            ns_users = float(ns.get("activeUsers", 0))
            ns_eng = float(ns.get("userEngagementDuration", 0))
            if ns_users > 50 and ns_eng > 0:
                avg_t = ns_eng / ns_users
                if avg_t > 180:  # 3+ min avg = real engagement being uncategorized
                    insights.append(
                        f"**Tracking gap:** {fmt_num(str(ns_users))} users spent avg {fmt_duration(str(avg_t))} "
                        f"on content GA4 labels '(not set)'. This means screen names aren't being passed in "
                        f"GA4 screen_view events for these views. **Action for dev team:** Ensure every screen_view "
                        f"event includes the series/episode title so this engagement can be properly attributed."
                    )
                    break

    if landing:
        # Find landing pages with 0% engagement — but be careful about conclusions
        zero_eng = [l for l in landing if
                    float(l.get("sessions", 0)) >= 5 and
                    float(l.get("engagementRate", 0)) == 0 and
                    "/detail/" in l.get("landingPagePlusQueryString", "")]

        # Check for GA4 tracking inconsistency (duration > 0 but 0 engaged = tracking bug)
        tracking_bugs = [l for l in zero_eng if float(l.get("averageSessionDuration", 0)) > 30]
        true_zero = [l for l in zero_eng if float(l.get("averageSessionDuration", 0)) <= 5]

        if true_zero:
            paths = [l.get("landingPagePlusQueryString", "?")[:50] for l in true_zero[:3]]
            total_wasted = sum(float(l.get("sessions", 0)) for l in true_zero)
            insights.append(
                f"**Series pages with 0% engagement on direct landing:** "
                f"{', '.join(paths)} ({fmt_num(str(total_wasted))} sessions, 100% bounce, 0s duration). "
                f"**Needs investigation.** Possible causes (in order of likelihood): "
                f"(1) Ad bot/crawler traffic inflating session counts, "
                f"(2) Angular SPA not hydrating on direct URL access — content doesn't render, "
                f"(3) Slow page load causing users to leave before GA4 engagement threshold (10s). "
                f"**Test:** Open these URLs directly in a browser and verify content loads."
            )

        if tracking_bugs:
            paths = [l.get("landingPagePlusQueryString", "?")[:50] for l in tracking_bugs[:2]]
            insights.append(
                f"**GA4 tracking inconsistency:** {', '.join(paths)} show long session durations "
                f"but 0 engaged sessions — GA4 engagement events may not be firing correctly "
                f"on series detail pages. Flag to dev team: check GA4 enhanced measurement settings."
            )

        # Check for fbclid query parameter fragmentation
        fbclid_pages = [l for l in landing if "fbclid=" in l.get("landingPagePlusQueryString", "")]
        if len(fbclid_pages) > 3:
            fb_sessions = sum(float(l.get("sessions", 0)) for l in fbclid_pages)
            insights.append(
                f"**Tracking noise:** {len(fbclid_pages)} landing page entries are the same page "
                f"split by Facebook click IDs ({fmt_num(str(fb_sessions))} sessions fragmented). "
                f"This muddies the data. **Action:** Configure GA4 to strip query parameters "
                f"(fbclid, gclid, etc.) from page path reporting, or set up URL normalization."
            )

        # Homepage as landing page analysis
        home = next((l for l in landing if l.get("landingPagePlusQueryString", "") == "/"), None)
        if home:
            home_sessions = float(home.get("sessions", 0))
            home_eng = float(home.get("engagementRate", 0))
            total_landing = sum(float(l.get("sessions", 0)) for l in landing)
            home_pct = (home_sessions / total_landing * 100) if total_landing > 0 else 0

            if home_pct > 30:
                insights.append(
                    f"**Homepage funneling:** {home_pct:.0f}% of sessions land on '/' with "
                    f"{home_eng*100:.0f}% engagement. "
                    f"**Action:** The homepage needs to surface content immediately — "
                    f"hero clip auto-playing, trending series, 'Start watching' CTA above the fold. "
                    f"Every second a user spends figuring out what to watch is a second closer to bouncing."
                )

    return insights


def _analyze_growth(trend, tw, lw):
    """Analyze growth trajectory and momentum."""
    insights = []

    if trend and len(trend) >= 7:
        daus = [float(t.get("activeUsers", 0)) for t in trend]
        eng_rates = [float(t.get("engagementRate", 0)) for t in trend]

        # 3-day moving averages
        recent_3 = daus[-3:]
        prior_3 = daus[-6:-3] if len(daus) >= 6 else daus[:3]
        recent_avg = sum(recent_3) / 3
        prior_avg = sum(prior_3) / 3

        if prior_avg > 0:
            growth = ((recent_avg - prior_avg) / prior_avg) * 100
            if growth > 100:
                insights.append(
                    f"**Explosive growth phase:** 3-day avg DAU at {fmt_num(str(recent_avg))}, "
                    f"up {growth:.0f}% from prior 3 days. This is paid-driven hockey stick growth. "
                    f"**Critical question:** Is engagement growing proportionally? "
                    f"Watch engaged sessions as the leading indicator, not raw DAU."
                )
            elif growth < -25:
                # Check if it's a weekend/weekday pattern or real decline
                insights.append(
                    f"**DAU cooling:** 3-day avg dropped to {fmt_num(str(recent_avg))} "
                    f"(down {abs(growth):.0f}%). Check: did ad spend decrease? Content gap? "
                    f"Or is this natural daily variance?"
                )

        # Engagement rate trend (are we diluting quality?)
        if len(eng_rates) >= 7:
            early_eng = sum(eng_rates[:3]) / 3
            recent_eng = sum(eng_rates[-3:]) / 3
            if early_eng > 0.20 and recent_eng < 0.12:
                insights.append(
                    f"**Quality dilution pattern:** Engagement rate fell from "
                    f"{early_eng*100:.0f}% (pre-scale) to {recent_eng*100:.0f}% (current). "
                    f"This is the classic paid acquisition tradeoff — more users, lower quality per user. "
                    f"**Not alarming yet**, but if engaged sessions plateau while DAU grows, "
                    f"you're buying vanity metrics. The target: grow engaged sessions 20%+ WoW."
                )

        # Volatility check
        recent_7 = daus[-7:]
        if len(recent_7) >= 2:
            max_dau, min_dau = max(recent_7), min(recent_7)
            if min_dau > 0 and max_dau / min_dau > 5:
                insights.append(
                    f"**DAU volatility:** {fmt_num(str(min_dau))} to {fmt_num(str(max_dau))} "
                    f"range in 7 days ({max_dau/min_dau:.0f}x swing). Traffic is campaign-dependent. "
                    f"**Organic baseline** (pre-paid days) appears to be ~{fmt_num(str(min_dau))}. "
                    f"Goal: raise that organic floor through SEO, social, and retention."
                )

    # WoW engaged sessions (the metric that matters most)
    if tw and lw:
        tw_engaged = float(tw.get("engagedSessions", 0))
        lw_engaged = float(lw.get("engagedSessions", 0))
        if lw_engaged > 0:
            engaged_growth = ((tw_engaged - lw_engaged) / lw_engaged) * 100
            tw_total = float(tw.get("sessions", 0))
            engaged_pct = (tw_engaged / tw_total * 100) if tw_total > 0 else 0

            if engaged_growth > 0:
                insights.append(
                    f"**Engaged sessions (the real metric): {fmt_num(str(tw_engaged))}** "
                    f"(+{engaged_growth:.0f}% WoW). That's {engaged_pct:.0f}% of total sessions. "
                    f"These are people who actually watched content. "
                    f"{'Strong growth.' if engaged_growth > 50 else 'Growing but monitor closely.'}"
                )

    return insights


def _analyze_timing(hours, timezone="UTC"):
    """Analyze user activity patterns with timezone awareness."""
    insights = []
    if not hours or len(hours) < 12:
        return insights

    # Find peak hours
    by_users = sorted(hours, key=lambda h: float(h.get("activeUsers", 0)), reverse=True)
    peak = by_users[:3]

    def fmt_hour(h):
        h = int(h) % 24
        ampm = "AM" if h < 12 else "PM"
        h12 = h if h <= 12 else h - 12
        if h12 == 0: h12 = 12
        return f"{h12}{ampm}"

    peak_hour_ints = [int(h.get("hour", 0)) for h in peak]
    peak_users = sum(float(h.get("activeUsers", 0)) for h in peak)

    # Determine the timezone GA4 reports in, and convert to ET if needed
    is_utc = timezone in ("UTC", "Etc/UTC", "GMT", "Etc/GMT")
    is_us_eastern = "New_York" in timezone or "Eastern" in timezone

    if is_utc:
        # Convert UTC hours to ET for behavioral interpretation
        try:
            from zoneinfo import ZoneInfo
            from datetime import datetime as dt
            utc_now = dt.now(ZoneInfo("UTC"))
            et_now = utc_now.astimezone(ZoneInfo("America/New_York"))
            et_offset = int(et_now.utcoffset().total_seconds() // 3600)
        except Exception:
            et_offset = -5  # Default to EST

        et_peak_hours = [(h + et_offset) % 24 for h in peak_hour_ints]
        ga4_peak_strs = [fmt_hour(h) for h in peak_hour_ints]
        et_peak_strs = [fmt_hour(h) for h in et_peak_hours]
        tz_context = f"GA4 reports in UTC. Peak: {', '.join(ga4_peak_strs)} UTC = **{', '.join(et_peak_strs)} ET**"
        check_hours = et_peak_hours  # Use ET hours for behavioral interpretation
    elif is_us_eastern:
        et_peak_strs = [fmt_hour(h) for h in peak_hour_ints]
        tz_context = f"Peak: {', '.join(et_peak_strs)} ET"
        check_hours = peak_hour_ints
    else:
        # Other timezone — report as-is, convert to ET for interpretation
        tz_label = timezone.split("/")[-1].replace("_", " ")
        try:
            from zoneinfo import ZoneInfo
            from datetime import datetime as dt
            local_now = dt.now(ZoneInfo(timezone))
            et_now = local_now.astimezone(ZoneInfo("America/New_York"))
            et_offset = int((et_now.utcoffset() - local_now.utcoffset()).total_seconds() // 3600)
        except Exception:
            et_offset = 0
        et_peak_hours = [(h + et_offset) % 24 for h in peak_hour_ints]
        local_strs = [fmt_hour(h) for h in peak_hour_ints]
        et_peak_strs = [fmt_hour(h) for h in et_peak_hours]
        tz_context = f"Peak: {', '.join(local_strs)} {tz_label} = **{', '.join(et_peak_strs)} ET**"
        check_hours = et_peak_hours

    # Behavioral interpretation using ET hours
    is_late_night = all(h >= 22 or h <= 4 for h in check_hours)
    is_evening = all(h >= 19 or h <= 23 for h in check_hours)

    if is_late_night:
        insights.append(
            f"**Late-night audience confirmed:** {tz_context} "
            f"({fmt_num(str(peak_users))} users). This aligns with VURT's target demo — "
            f"phone-in-bed, wind-down viewing. "
            f"**Actions:** Schedule content drops and push notifications for 8-9 PM ET. "
            f"Late-night is when micro-dramas win against long-form."
        )
    elif is_evening:
        insights.append(
            f"**Evening prime-time audience:** {tz_context} "
            f"({fmt_num(str(peak_users))} users). Classic wind-down viewing window. "
            f"**Actions:** Schedule content drops for 7-8 PM ET. "
            f"Social posts 1-2 hours before peak to prime the pipeline."
        )
    else:
        insights.append(
            f"**Peak activity:** {tz_context} "
            f"({fmt_num(str(peak_users))} users combined). "
            f"Schedule content and social posts 1-2 hours before peak."
        )

    return insights


def _analyze_geo(geo):
    """Analyze geographic distribution and international opportunities."""
    insights = []
    if not geo:
        return insights

    total_users = sum(float(g.get("activeUsers", 0)) for g in geo)
    top = geo[0] if geo else {}
    top_users = float(top.get("activeUsers", 0))
    top_name = top.get("country", "?")
    top_pct = (top_users / total_users * 100) if total_users > 0 else 0

    if top_pct > 95:
        intl_users = total_users - top_users
        insights.append(
            f"**{top_name}-concentrated ({top_pct:.0f}% of top-10 countries):** "
            f"Only {fmt_num(str(intl_users))} international users in top 10. "
            f"Fine for launch — but VURT's cultural content has global appeal. "
            f"When ready to expand, look for organic traction signals below."
        )

    # Find international markets with high engagement
    intl_signals = []
    for g in geo[1:]:
        g_eng = float(g.get("engagementRate", 0))
        g_dur = float(g.get("averageSessionDuration", 0))
        g_users = float(g.get("activeUsers", 0))
        country = g.get("country", "?")
        if g_eng > 0.30 and g_users >= 8:
            intl_signals.append({
                "country": country, "eng": g_eng, "dur": g_dur, "users": g_users
            })

    if intl_signals:
        top_intl = sorted(intl_signals, key=lambda x: x["eng"] * x["users"], reverse=True)[:3]
        signal_strs = [
            f"{s['country']} ({fmt_num(str(s['users']))} users, {s['eng']*100:.0f}% eng, {fmt_duration(str(s['dur']))})"
            for s in top_intl
        ]
        max_users = max(s["users"] for s in top_intl)
        size_caveat = " (small sample sizes — directional signal only, not statistically significant)" if max_users < 200 else ""
        insights.append(
            f"**International traction{size_caveat}:** {'; '.join(signal_strs)}. "
            f"These are organic viewers finding VURT without targeting. "
            f"No action needed yet — bookmark for future expansion planning."
        )

    return insights


def _top_signal_today(data):
    """Return the single most significant metric shift day-over-day."""
    yd = data.get("yesterday", {})
    db = data.get("day_before", {})
    if not yd or not db:
        return None

    checks = [
        ("engagedSessions", "Engaged sessions"),
        ("activeUsers", "DAU"),
        ("engagementRate", "Engagement rate"),
        ("averageSessionDuration", "Avg session duration"),
        ("sessions", "Sessions"),
    ]

    best = None
    for key, label in checks:
        try:
            yd_val = float(yd.get(key, 0))
            db_val = float(db.get(key, 0))
            if db_val <= 0:
                continue
            pct = (yd_val - db_val) / db_val * 100
            if best is None or abs(pct) > abs(best[0]):
                best = (pct, label, yd_val, db_val, key)
        except (ValueError, TypeError):
            continue

    if not best:
        return None

    pct, label, yd_val, db_val, key = best
    arrow = "▲" if pct > 0 else "▼"
    sign = "+" if pct > 0 else ""

    if key == "engagementRate":
        yd_fmt = f"{yd_val * 100:.1f}%"
        db_fmt = f"{db_val * 100:.1f}%"
    elif key == "averageSessionDuration":
        yd_fmt = fmt_duration(str(yd_val))
        db_fmt = fmt_duration(str(db_val))
    else:
        yd_fmt = fmt_num(str(yd_val))
        db_fmt = fmt_num(str(db_val))

    context = ""
    if key == "engagedSessions" and pct < -20:
        context = " — biggest drop in a key metric. Check if ad spend changed or if there's a content gap today."
    elif key == "engagedSessions" and pct > 20:
        context = " — strong engagement growth. Something is working today; identify what drove it."
    elif key == "activeUsers" and pct > 50:
        context = " — traffic spike. Likely an ad campaign push; watch if engaged sessions scale proportionally."
    elif key == "activeUsers" and pct < -30:
        context = " — sharp traffic drop. Check if ad spend paused or if there's a targeting issue."
    elif key == "engagementRate" and pct > 10:
        context = " — audience quality improving. More visitors are actually watching content."
    elif key == "engagementRate" and pct < -10:
        context = " — quality diluting. More traffic, less engagement — ad targeting may need tightening."

    return (
        f"**{arrow} TODAY'S KEY SIGNAL — {label}: {sign}{pct:.0f}% day-over-day** "
        f"({db_fmt} → {yd_fmt}){context}"
    )


def _analyze_npaw_content(npaw_top_raw, npaw_daily_raw):
    """Surface content performance signals from NPAW video data."""
    import re as _re
    import math as _math
    insights = []

    try:
        from npaw_client import _extract_grouped_metrics, _extract_metrics, _engagement_score
    except ImportError:
        return insights

    # Video error rate
    try:
        m = _extract_metrics(npaw_daily_raw)
        views = m.get("views")
        errors = m.get("errors")
        if views and errors and float(views) > 0:
            error_rate = float(errors) / float(views) * 100
            if error_rate > 5:
                insights.append(
                    f"**High video error rate:** {error_rate:.1f}% of plays errored today "
                    f"({int(float(errors))} errors / {int(float(views))} plays). "
                    f"Investigate in NPAW — likely CDN, encoding, or device-specific."
                )
    except Exception:
        pass

    # Content signals from top content
    try:
        rows = _extract_grouped_metrics(npaw_top_raw)
        if not rows:
            return insights

        for row in rows:
            try:
                row["_score"] = _engagement_score(row.get("views", 0), row.get("completionRate", 0))
            except Exception:
                row["_score"] = 0.0

        valid = [r for r in rows if r.get("completionRate") and float(r.get("completionRate", 0)) > 0]

        # Best completion rate — use in retargeting
        if valid:
            top_cr = max(valid, key=lambda r: float(r.get("completionRate", 0)))
            cr = float(top_cr.get("completionRate", 0))
            plays = float(top_cr.get("views", 0))
            if cr > 25 and plays > 50:
                insights.append(
                    f"**Best completion rate (7d) — '{top_cr['title']}':** {cr:.1f}% watch-through "
                    f"({int(plays):,} plays). This is your highest-quality content signal. "
                    f"**Use it in retargeting ads** — viewers who finish content are your best conversion target."
                )

        # High volume, low completion — drop-off alarm
        drop_off = [
            r for r in valid
            if float(r.get("views", 0)) > 300 and float(r.get("completionRate", 0)) < 8
        ]
        for r in drop_off[:1]:
            plays = float(r.get("views", 0))
            cr = float(r.get("completionRate", 0))
            finished = int(plays * cr / 100)
            insights.append(
                f"**Drop-off alert — '{r['title']}':** {int(plays):,} plays, only {cr:.1f}% completion "
                f"(~{finished} people finished). Something is breaking in the first 30-60 seconds — "
                f"hook, loading issue, or quality gap. Watch the first minute on mobile and check NPAW error rate for this title."
            )

        # Episode-to-episode retention (series funnel)
        series_map = {}
        for r in rows:
            title = r.get("title", "")
            match = _re.match(r"Episode\s+(\d+)\s*[-–]\s*(.+)", title, _re.IGNORECASE)
            if match:
                ep_num = int(match.group(1))
                series = match.group(2).strip()
                if series not in series_map:
                    series_map[series] = {}
                series_map[series][ep_num] = r

        for series, eps in series_map.items():
            if 1 in eps and 2 in eps:
                ep1_plays = float(eps[1].get("views", 0))
                ep2_plays = float(eps[2].get("views", 0))
                if ep1_plays > 50 and ep2_plays > 0:
                    retention_pct = ep2_plays / ep1_plays * 100
                    if retention_pct > 40:
                        insights.append(
                            f"**Strong series funnel — '{series}':** {retention_pct:.0f}% of Ep1 viewers "
                            f"went to Ep2 ({int(ep1_plays):,} → {int(ep2_plays):,} plays). "
                            f"High episode retention. Prioritize this series in paid ads — "
                            f"viewers who start are likely to continue."
                        )
                    elif retention_pct < 15 and ep1_plays > 200:
                        insights.append(
                            f"**Series funnel leak — '{series}':** Only {retention_pct:.0f}% of Ep1 viewers "
                            f"reached Ep2 ({int(ep1_plays):,} → {int(ep2_plays):,}). "
                            f"Check: Is Ep1's ending strong enough to drive 'next episode'? "
                            f"Is Ep2 auto-surfaced immediately after Ep1 ends on the platform?"
                        )

    except Exception:
        pass

    return insights


def _strategic_implications(data):
    """Connect the data to VURT's strategic flywheel and business model."""
    insights = []
    tw = data.get("this_week", {})
    sources = data.get("sources", [])
    platforms = data.get("platforms", [])

    if not tw:
        return insights

    tw_users = float(tw.get("activeUsers", 0))
    tw_engaged = float(tw.get("engagedSessions", 0))
    tw_eng_time = float(tw.get("userEngagementDuration", 0))  # in seconds

    # Ad revenue readiness check
    if tw_eng_time > 0:
        total_watch_hours = tw_eng_time / 3600
        # Benchmarks (verified Q1 2026):
        # - AVOD platforms (Tubi, Pluto TV): $15-25 CPM range (Adwave, 2025)
        # - CTV median: $20-40 CPM (AI Digital industry analysis)
        # - Ad load: AVOD standard 4-6 min/hr (Tubi model, ~5 ad breaks)
        # Using conservative AVOD floor, not premium CTV rates
        ads_per_hour = 5
        cpm_low = 0.015   # $15 CPM (AVOD floor, Adwave verified)
        cpm_high = 0.025  # $25 CPM (AVOD ceiling, Adwave verified)
        est_weekly_impressions = total_watch_hours * ads_per_hour
        est_weekly_rev_low = est_weekly_impressions * cpm_low
        est_weekly_rev_high = est_weekly_impressions * cpm_high

        if total_watch_hours > 10:
            insights.append(
                f"**Ad revenue potential (projection, not current revenue):** {total_watch_hours:.0f} total watch-hours this week. "
                f"Using AVOD benchmark range of $15-25 CPM (Adwave, verified for Pluto TV/Tubi tier) "
                f"with ~5 ads/hr (industry standard ad load), est. ${est_weekly_rev_low:.0f}-${est_weekly_rev_high:.0f}/week at current scale. "
                f"VURT is not yet running ads. This is a scaling model, not a forecast. "
                f"The direct lever is growing engaged watch-hours."
            )

    # Flywheel status
    paid_share = 0
    if sources:
        total_s = sum(float(s.get("sessions", 0)) for s in sources)
        paid = sum(float(s.get("sessions", 0)) for s in sources
                   if "paid" in s.get("sessionDefaultChannelGroup", "").lower())
        paid_share = (paid / total_s * 100) if total_s > 0 else 0

    if paid_share > 80:
        insights.append(
            f"**Flywheel check:** {paid_share:.0f}% of traffic is paid — the flywheel hasn't kicked in yet. "
            f"VURT's thesis is: content → distribution → community → retention → organic growth. "
            f"Right now it's: money → eyeballs → bounce. "
            f"**The unlock:** shareable content moments. Clips people screenshot and repost. "
            f"The share link fix (vurt.enveu.link → myvurt.com) is prerequisite #1. "
            f"Community features (comments, watchlists, fan theories) are prerequisite #2. "
            f"Until these exist, paid will remain the only growth engine."
        )

    return insights
