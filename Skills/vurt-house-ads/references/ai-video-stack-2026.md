# VURT House Ads — AI Video Stack (April 2026)

Working reference for 15-30s ad creatives. Every tool listed here has been verified as shipping/current as of April 2026.

---

## 1. Text-to-Video / Image-to-Video (B-roll, product, lifestyle)

### Top pick: Google Veo 3.1
- **Best for:** Photoreal b-roll, product shots, lifestyle scenes with native audio in one pass. Highest quality ceiling in 2026, up to 4K, 8-16s clips.
- **Access:** Google Flow (bundled with Gemini Advanced / Google AI Pro), Vertex AI, Gemini API. Also available inside Adobe Firefly.
- **Cost:** Gemini API ~$0.40/sec (standard), $0.10/sec (Fast), $0.05/sec (Lite). Free tier in Flow with daily credits.
- **Limitations:** Credit-gated; Fast/Lite trade quality for speed; tight content filters on brand/people.

### Top pick: Runway Gen-4.5 (+ Aleph for editing)
- **Best for:** Production workflow — keyframes, camera motion control, video-to-video, multi-shot narratives, and Aleph for AI-native editing passes (object swap, relight, style). Most granular creative control.
- **Cost:** $12 Standard / $28 Pro / $76 Unlimited per month. Commercial use on all paid plans.
- **Limitations:** Silent output (no native audio — you must score/VO separately). Gen-4.5 no longer wins raw Elo benchmarks, but the workspace is the moat.

### Situational: Kling 2.5 Turbo / 3.0
- **Best for:** Cinematic human motion, fluid physics, cheap per-clip. Strong at photorealistic people. Now native inside Adobe Firefly.
- **Cost:** Standard $10/mo, Pro tiers up from there; API via fal.ai ~$0.029/sec.
- **Limitations:** Native 4K is consumer-platform-only (API caps at 1080p).

### Situational: Luma Ray 3 / Ray 2
- **Best for:** Fast, cinematic image-to-video. Ray 3 is the first "reasoning" video model; strong on composition and motion coherence. Good fallback when Veo/Runway filters reject a prompt.
- **Cost:** Luma subscription or API via fal.ai (~$0.08/sec for Ray at 1080p).

### Cheap-at-scale: Seedance 2.0 (ByteDance)
- **Best for:** High-volume b-roll and rapid prototyping before committing to a Veo render. Cheapest per-second of any top-tier model — ~$0.05 per 5-sec 720p clip via third-party endpoints (fal.ai, PiAPI); official ByteDance rate ~$0.14/sec. Native multi-shot text-to-video and image-to-video, synchronized native audio (2.0), strong prompt adherence. Accepts up to 9 ref images + 3 ref videos per prompt — ideal for product-anchored b-roll.
- **Access:** BytePlus (international) or Volcengine (CN). Third-party hosts via fal.ai, PiAPI.
- **Limitations:** Native 720p/1080p; 2K via upscale, no native 4K. Hard **15s clip cap on web, 10s on mobile** — stitch for 30s spots. No visible watermark but carries an invisible content-ID watermark. Commercial use permitted on paid tiers; verify ToS on whichever endpoint VURT uses (terms vary BytePlus vs. Dreamina vs. Runway-hosted).

### Shot-language layer: Higgsfield AI
- **Best for:** Directing the *shot*, not generating it. Higgsfield is a wrapper over 15+ external models (Veo 3.1, Kling 3.0, Seedance, Sora 2, WAN 2.5) layered with **Cinema Studio** — 70+ cinematic camera presets (crash zoom, dolly, 360 orbit, crane, boltcam) and the ability to **stack up to 3 simultaneous camera moves** per shot. Use it when the camera language is the point (ad intros, pattern-interrupt openers) and you want to iterate fast across base models without separate subs.
- **Cost:** Starter $15/mo, Plus $34/mo, Ultra $84/mo, Business $49/seat. Credit-based — Kling 3.0 ≈ 6 credits/clip, Veo 3.1 / Sora 2 ≈ 40–70 credits/clip.
- **Limitations:** Output quality capped by whichever underlying model you call — Higgsfield itself doesn't generate. **Vendor-risk flag:** Higgsfield's X account was suspended Feb 2026 amid creator-payment / pricing-transparency allegations. Don't build the whole workflow around it; use it for shot-language iteration, render finals through Veo/Runway direct.

### Skip / deprioritize
- **Sora 2** — still usable (Sora 2 Pro API via aggregators), but OpenAI announced Sora wind-down/transitions in early 2026; don't build a workflow around it.
- **Pika 2.2** — fine for quick social, weak for paid-ad quality bar. Standard plan has NO commercial rights and watermarks; requires Pro ($28-35/mo) for clean export.

---

## 2. Performance Transfer / Face & Body Animation

### Top pick: Runway Act-Two
- **Best for:** Shoot the founder once, drive unlimited expression/dialogue variants from a phone-recorded performance. Captures eye-lines, micro-expressions, full body gesture. Works on character stills or existing footage of a real person.
- **Cost:** Included in Runway paid plans (Standard $12+).
- **Limitations:** Best results with clean, front-lit driver video; extreme head rotation still breaks. Lip-sync accuracy degrades on fast speech — pair with ElevenLabs lip-sync for critical dialogue.

### Alternative: Kling 3.0 Motion Control
- **Best for:** Cinematic body motion / expression transfer where Act-Two output feels too "rigged." Many creators report Kling edges Act-Two on dramatic/stylized shots.
- **Cost:** Kling Pro tier.

### Alternative: ElevenLabs Lip-Sync (OmniHuman / Veed nodes in Flows)
- **Best for:** Tight lip-sync on an existing take when you only need to swap the audio line. Drop-in node inside ElevenLabs Flows.

---

## 3. Voice / VO / Music

### Voice: ElevenLabs v3
- **Best for:** VO and founder voice cloning. v3 is the most realistic TTS shipping. Use Instant Voice Clone for founder VO variants (need written consent on file).
- **Cost:** Creator $22/mo minimum for commercial use; Pro $99/mo for higher-quality clones and longer context.
- **Note:** ElevenLabs Flows (March 2026) chains image → video → VO → music → lip-sync on one canvas. Useful for batch ad variant generation.

### Music: Suno v4 (Suno III)
- **Best for:** Full songs or 15-30s beds from a text prompt, with commercial license on paid plans. Fastest path to a bespoke ad bed.
- **Cost:** Pro $10/mo (commercial rights), Premier $30/mo for higher throughput.
- **Limitations:** Stems/separation still imperfect — if you need tight sync cuts, generate shorter and loop rather than trim.

### Alt music: Udio — use if Suno output feels generic for a given genre.

---

## 4. Upscaling & Finishing

### Top pick: Topaz Video AI (Astra / Starlight models)
- **Best for:** Live-action and mixed footage upscale, deinterlace, frame interpolation to 60fps, grain/noise cleanup. Industry standard for finishing.
- **Cost:** $299 perpetual license (with 1yr updates) or monthly.
- **Limitations:** Can over-smooth AI-generated footage — use Magnific for AI source material.

### Top pick: Magnific Video Upscaler
- **Best for:** AI-generated clips 720p/1080p → 2K/4K. Adds organic detail (skin, fabric, micro-texture) instead of just sharpening. Pairs perfectly with Veo/Runway output.
- **Cost:** Magnific subscription (from ~$39/mo).
- **Limitations:** Supports 720p/1080p inputs; not designed for live-action.

### Rule of thumb
- AI-generated source → **Magnific**.
- Camera-captured source → **Topaz**.

---

## 5. Edit-Assist / Timeline Tools

### Top pick: Adobe Premiere Pro (Firefly + partner models)
- **Best for:** Final assembly. 2026 Firefly inside Premiere includes Generative Extend, object removal, and direct access to Veo, Runway Gen-4, Kling 2.5, Pika, Luma inside the timeline. Keeps color/sound workflow pro-grade.
- **Cost:** $22.99/mo + generative credits.

### Top pick: Descript
- **Best for:** Script-based rough cuts, founder talking-head trims, filler-word removal, Studio Sound, eye-contact correction. Fastest path from raw founder interview to a polished 30s.
- **Cost:** Creator $15/mo, Pro $30/mo.

### Situational: CapCut Desktop Pro
- **Best for:** Social-first edits, auto-captions (95-97% accuracy), AI transitions, mobile/desktop parity. Fine for organic posts; watch commercial-use licensing on CapCut stock assets and AI effects.
- **Cost:** Free tier is capable; Pro ~$8-10/mo.

---

## Recommended VURT House-Ad Stack (April 2026)

| Step | Tool |
|---|---|
| Concept boards / stills | Midjourney v7 or Flux |
| B-roll / product / lifestyle | **Veo 3.1** (primary) → Runway Gen-4.5 (fallback for control) → **Seedance 2.0** (scale/cheap prototypes) |
| Camera-language / shot-direction | **Higgsfield Cinema Studio** (stacked camera presets across models) |
| Founder performance extend | **Runway Act-Two** |
| VO / founder clone | **ElevenLabs v3** |
| Music bed | **Suno v4** |
| Upscale AI clips | **Magnific Video** |
| Upscale live clips | **Topaz Video AI** |
| Rough cut from interview | **Descript** |
| Final assembly / color | **Premiere Pro** (Firefly panel for in-timeline gen) |

## Watchouts
- **Silent Runway:** Always budget separate audio — Runway is the only major platform still outputting silent video.
- **Commercial rights:** Confirm tier. Pika Standard and CapCut free-library assets are non-commercial. Runway paid, Veo paid, Kling paid, Suno Pro, ElevenLabs Creator+ all clear.
- **Face cloning consent:** Written consent on file before any ElevenLabs clone or Act-Two founder extension. Required by platform TOS and sensible for VURT.
- **Don't bet the workflow on Sora 2** — OpenAI signaled wind-down; treat as experimental only.

---

## 6. What to AI vs. What to Shoot Real (working reference for the editor)

This is the decision framework for every shot in the VURT house-ad campaign. Editors: when you hit a shot and wonder "can I just AI this?", check here first. When in doubt, shoot real — but the list below has been tested against 2026 model output and reflects what's actually passing as live footage right now.

### AI IS 1:1 with live in 2026 (generate it, save the shoot day)

These shot types can be generated with **Veo 3.1** or **Kling 2.5 Turbo** using a real product still as image-to-video reference, and no viewer will clock them:

- **Product in motion** — fabric swirling, a pot hitting flame, oil splashing, gummies falling into a hand, a bottle cap twisting off, steam rising, liquid pouring. These shots are macro + motion + texture. AI crushes them. Budget: ~$0.05–$0.40/sec.
- **Macro textures** — thread through fabric, grain in leather, cream into coffee, a candle flickering, fibers in a ceramic surface, sweat on a glass. Already AI-native in most 2026 Hollywood ads.
- **Environmental b-roll** — Miami skyline, ocean at golden hour, rain on a window, empty countertop with morning light, an atelier window with pattern paper visible. Zero tells.
- **"Anonymous body" lifestyle cuts** — woman walking on a boat (back of head), hand reaching into a bowl, bare feet on tile, a body in swimwear turning away from camera, hands folding fabric. Face never in frame, no recognizable person = no likeness-rights issue.
- **Telenovela-style b-roll** (SinFiltros 30s #2 "Day 24") — a couple mid-argument from behind, walking into a bathroom, leaning on a door. Wide-to-medium crops of anonymous bodies. AI handles this perfectly; real-actor performance isn't needed for these beats.
- **"Crowd" and lifestyle inserts** — a woman at a desk with a heating pad, on a couch, laughing at a dinner table — as long as nobody is face-forward or speaking, these pass.

### AI is close but not quite there — use with caution

- **Face-forward dialogue / speaking performance** — AI can generate a face talking, but in audio-on, non-skippable contexts (which VURT is), the tells are cumulative: eyes don't track naturally, lip-sync drifts on fast speech, micro-expressions feel too "smooth." **Every face-forward line of dialogue in this campaign must be real person, real camera.** Runway Act-Two can *extend* a real performance with cloned speech, but the source performance must be filmed.
- **Hands doing complex skilled work** — AI is strong at "hand stitching" one or two frames but can drift on longer shots (finger count, thread physics). If the shot is >3s, shoot it real.
- **Known-face cameos** — we're using Trick's archival footage, not AI-generating him. Do NOT generate Trick's likeness under any circumstance — right-of-publicity trap even with his consent. Arielle and Valentina both appear real or extended from real footage via Act-Two with signed consent.

### Shoot real — AI can't fake this yet

- **Founder on-camera dialogue** — Arielle's 18–24s and 22–27s moments in Rielli 30s #1 and 30s #2. Valentina's 0–3s and 18–25s moments in SinFiltros 30s #1. These are the emotional spine of each campaign.
- **Founder VO** — Valentina and Arielle voicing their own lines. Trick's VO can come from (a) a 5-min phone VO session with him, or (b) ElevenLabs Instant Voice Clone trained on cooking-show audio **with signed consent**. Never clone without consent.
- **Archival talent footage** — Trick's cooking show is an irreplaceable asset. The spot is built from it, not generated.
- **Phone-shot creator-register cuts** — SinFiltros 15s #4. The whole point is it looks like Valentina's organic TikTok. AI-generating a "fake-organic" spot reads as fake immediately.

### Campaign-by-campaign AI/live split

**Rielli** — ~60% AI, 40% live:
- AI: all fabric-in-motion macros, atelier wides, skyline, boat/beach b-roll, hanger shots, body shots where no face is forward. If we can't access the atelier at all, AI-generate it.
- Live: Arielle's two on-camera deliveries (~11s total across both 30s), a handful of hand-cutaways where her hands are in frame, her VO.
- IRL shoot cost: **one 2-hour phone shoot** at her space (or any window-lit room). No crew required.

**SinFiltros** — ~50% AI, 50% live:
- AI: product shots (bottles on terracotta, gummy into palm, bundle box), morning-ritual inserts (coffee pour, counter shots), all lifestyle b-roll where no face is forward, the couple-argument cold open in 30s #2.
- Live: Valentina's ~13 seconds of on-camera dialogue across 4 spots, all her VO, 15s #4 in full (phone-shot by her).
- IRL shoot cost: **one 3-hour phone shoot** at Valentina's place. No crew required. She self-shoots 15s #4 that same day or the next.

**Trick Daddy Pots** — ~20% AI, 30% live, 50% archive:
- AI: transitional b-roll only (pot on flame inserts if the archive can't cover, lid-lifting macros). Product laydowns are live.
- Live: one half-day product-laydown shoot, maybe 5-min remote phone VO with Trick.
- Archive: all guest beats, all Trick-on-camera, all cooking action. Never generate his face or voice without explicit consent.
- IRL shoot cost: **half-day product laydown.** That's it.

### How to prompt AI video for 1:1 output

1. **Always feed a real product still as image-to-video reference** when available. Veo 3.1 and Kling 2.5 can both do this. Quality jump vs. text-only: night and day.
2. **Reference the grade + lens.** Prompts should say "shot on A7S III, 50mm, natural window light, slight film grain, warm tungsten accent" — not "cinematic." "Cinematic" triggers the generic-stock-footage look.
3. **Constrain the camera move.** "Static locked-off, no camera move" or "slow dolly in, 6 inches per second" beats "dynamic camera" every time. Camera moves are where AI models still reveal themselves.
4. **Short clips beat long clips.** Generate in 4–6s beats and cut, not 15s continuous. Longer clips drift on physics and continuity.
5. **Finish with Magnific Video.** AI source → Magnific (adds organic detail back into skin/fabric/texture); live source → Topaz. Never skip the finish — untreated AI output looks "smooth" and reads as generated.

### Consent checklist (before any clone/extension)

- **Trick:** text/SMS consent thread acceptable given the close relationship + investor tie. Screenshot + save to `assets/consent/trick/`. Specific scope: pots campaign, VURT distribution, cooking-show audio source for ElevenLabs.
- **Arielle (Rielli):** same — text consent is fine given founder status; save to `assets/consent/rielli/`. Scope: her own voice + likeness in her own brand's ads.
- **Valentina (SinFiltros):** same; `assets/consent/sinfiltros/`.
- For ElevenLabs specifically: they now require consent attestation inside the product flow (checkbox + audio sample of the voice owner confirming). Keep the attestation audio in the same consent folder.
