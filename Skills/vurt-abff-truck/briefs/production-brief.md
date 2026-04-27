# Production brief — VURT × ABFF Truck

One-page version for editors, designers, LPMG handoff.

## Deliverables (to LPMG)
Submit via Dropbox/WeTransfer/zip:

| File | Spec | Face | Variation |
|------|------|------|-----------|
| `vurt_abff_v1_rear.jpg` | 1500×1500 @ 300 DPI, JPEG | Rear | V1 — Launch Party (Fri 5/29) |
| `vurt_abff_v1_rear.mp4` | 1080×1080, H.264, no audio, 10s loop | Rear | V1 — Launch Party (Fri 5/29) |
| `vurt_abff_v1_side.jpg` | 2400×1200 @ 300 DPI, JPEG | Side | V1 — Launch Party (Fri 5/29) |
| `vurt_abff_v1_side.mp4` | 1920×1080, H.264, **no audio** (MB §46-152), 15s | Side | V1 — Launch Party (Fri 5/29) |
| `vurt_abff_v2_rear.jpg` | 1500×1500 @ 300 DPI, JPEG | Rear | V2 — General |
| `vurt_abff_v2_rear.mp4` | 1080×1080, H.264, no audio, 10s loop | Rear | V2 — General |
| `vurt_abff_v2_side.jpg` | 2400×1200 @ 300 DPI, JPEG | Side | V2 — General |
| `vurt_abff_v2_side.mp4` | 1920×1080, H.264, **no audio** (MB §46-152), 20s | Side | V2 — General |

## Brand guardrails (from VURT)
- VURT logo visible every second of runtime
- No white-on-white; no skinny fonts
- Brand language: "culture" (organizes around), "community" (mechanism). Never swap.
- No em dashes in any on-screen copy
- Destination: `myvurt.com/abff` (V1), `myvurt.com` (V2). Never app stores.
- Sign-up not pitched anywhere on the truck (AVOD rule)
- **Do NOT mention "ABFF" on-screen.** Use dates only ("Fri 5.29 · Miami Beach"). VURT is not an official sponsor.

## Tracking plan
- V1 QR → `myvurt.com/abff?utm_source=truck&utm_medium=dooh&utm_campaign=miami-2026&utm_content=v1-rsvp`
- V2 QR → `myvurt.com?utm_source=truck&utm_medium=dooh&utm_campaign=miami-2026&utm_content=v2-general`
- GA4 events to confirm firing on landing: `page_view`, `video_start` (auto-play), `form_submit` (V1 only), `scroll_depth_50`
- Meta Pixel + CAPI on landing page — every scanner auto-builds a 14-day retarget Custom Audience
- Report daily during truck run; run postmortem 6/1

## Landing page requirements (`myvurt.com/abff`)
1. Date-aware render: before 5/29 shows **split CTA**: (A) "Request rooftop invite" — gated RSVP form; (B) "Ground floor walk-in" — address + doors open info + lightweight email capture. After 5/29 shows recap reel.
2. Auto-plays a 90-second highlight reel (muted, captions on).
3. Rooftop RSVP form asks: first name, phone (required), email (required), "how we know you" free-text. Routes to internal guestlist review before approval.
4. Walk-in capture asks: email only. Adds to general VURT list.
5. Mobile-first; renders in <1 second on 4G.
6. `og:image` branded with VURT (no ABFF references) so shared links preview well.

## Handoff checklist (before shipping to LPMG)
- [ ] All 8 files named per convention
- [ ] QR codes tested on 3 devices (iOS Safari, Android Chrome, tiny-screen iPhone SE)
- [ ] 40-ft legibility test (print at actual scale on tabloid paper, stand across the room)
- [ ] Both side videos confirmed **silent** (no audio track) — Miami Beach §46-152 bans vehicle audio
- [ ] Talent releases signed for anyone on-camera — OOH-specific. Licensed/non-original content (Rotimi etc.) requires written sign-off from rights holder if featured on panel.
- [ ] Legal: no "ABFF" on-screen — dates only. Confirm brand tokens match `Documents/VURT-master.md`.
