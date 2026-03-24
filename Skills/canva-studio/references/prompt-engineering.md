# Canva Design Prompt Engineering

## Why This Matters

The `query` parameter in `generate-design` is the single biggest lever for quality. Vague queries produce generic results. Detailed, structured queries produce professional, on-brand output.

## Query Structure Formula

```
[DESIGN PURPOSE] for [AUDIENCE/BRAND] featuring [KEY VISUAL ELEMENTS].
Style: [AESTHETIC DIRECTION]. Color palette: [COLORS].
Text to include: [HEADLINE] / [SUBTEXT] / [CTA].
Mood: [EMOTIONAL TONE]. Layout: [COMPOSITION PREFERENCE].
```

## Examples by Design Type

### Instagram Post
```
query: "Instagram post for VURT, a culture-first micro-drama streaming platform.
Dark cinematic aesthetic with neon accent lighting. Feature a silhouetted figure
watching a screen in a moody urban environment. Text: 'Stories That Hit Different'
in bold sans-serif. Subtext: 'New Episodes Every Friday'. Brand colors: deep black
background, electric purple (#8B5CF6) and hot coral (#FF6B6B) accents. Mood: edgy,
premium, youth culture. Square 1080x1080 format."
```

### YouTube Thumbnail
```
query: "YouTube thumbnail for a gaming culture documentary episode. High contrast,
bold typography. Feature dramatic lighting on a gaming setup with RGB glow.
Large text 'THE RISE OF ESPORTS' in Impact-style font with glow effect.
Colors: black, neon green, electric blue. Style: cinematic, high-energy.
Must be eye-catching at small preview sizes."
```

### Presentation / Deck
```
topic: "VURT Investor Update Q1 2026"
style: "minimalist"
audience: "professional investors"
```

### Business Proposal (Doc)
```
query: "Professional business proposal document for VURT entertainment platform.
Clean modern layout with sections for Executive Summary, Market Opportunity,
Product Overview, Team, and Financial Projections. Minimal design with
sophisticated typography. Brand accent color: electric purple on white/dark
backgrounds. Include placeholder areas for charts and metrics."
```

### Social Media Story
```
query: "Instagram Story for a new show premiere announcement on VURT platform.
Vertical 9:16 format. Dramatic reveal style with movie-poster energy. Dark
background with cinematic lighting. Show title 'NIGHTCRAWL' in large distressed
font. 'Premieres March 28' in clean sans-serif below. Swipe up CTA at bottom.
Colors: black, deep red, gold accent."
```

### Event Flyer
```
query: "Event flyer for VURT culture night - a live screening and DJ event.
Location: Miami. Date: April 15. Aesthetic: underground club meets film premiere.
Dark background with neon typography. Include space for venue details and lineup.
QR code placeholder for tickets. Style: raw, authentic, not corporate."
```

## Anti-Patterns (What NOT to Do)

| Bad Query | Why It Fails | Better Version |
|---|---|---|
| "Make me an Instagram post" | Too vague, produces generic templates | Include topic, brand, colors, mood |
| "Cool poster" | No context for AI to work with | Describe the event, audience, aesthetic |
| "Professional presentation" | Every presentation is "professional" | Specify industry, audience, visual style |
| "Logo for my company" | No brand personality or direction | Include industry, values, color preferences, style references |

## Query Modifiers That Work

**Visual style keywords:** cinematic, minimalist, brutalist, editorial, retro, futuristic, organic, geometric, hand-drawn, collage, glitch, neon, vintage, luxury, streetwear, vaporwave

**Mood keywords:** bold, subtle, energetic, calm, mysterious, playful, serious, provocative, warm, cold, raw, polished, underground, premium

**Layout keywords:** centered, asymmetric, grid-based, full-bleed, whitespace-heavy, layered, overlapping, split-screen, diagonal

**Typography keywords:** bold sans-serif, elegant serif, monospace, handwritten, display type, condensed, expanded, stacked, all-caps

## Brand Kit Integration

When using brand_kit_id, the AI applies your brand's colors, fonts, and logo automatically. But you should still be specific in the query — the brand kit handles visual identity, not content direction.

```
Best practice:
1. list-brand-kits → find your kit ID
2. Include brand_kit_id in generate-design
3. Still write a detailed query for content/layout direction
4. The kit handles colors/fonts, your query handles everything else
```

## Asset Integration Tips

When using asset_ids to include custom images:
- Assets are inserted in order — put the most important image first
- For designs with few image slots, only supply the images you actually want
- Upload assets via upload-asset-from-url before referencing them
- Use descriptive alt text for accessibility
