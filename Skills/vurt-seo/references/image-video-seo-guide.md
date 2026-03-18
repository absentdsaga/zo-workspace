# VURT Image & Video SEO Standards

## Filename Convention
Every image and video file must follow this naming pattern:

### Images
```
vurt-[series-name]-[descriptor]-[optional-episode].jpg
```
Examples:
- `vurt-karma-in-heels-poster-s1.jpg`
- `vurt-come-back-dad-tatyana-ali-ep3-still.jpg`
- `vurt-miami-kingpins-cast-group-shot.jpg`
- `vurt-platform-homepage-screenshot-2026.jpg`
- `vurt-logo-gold-on-black.png`
- `vurt-app-ios-screenshot-browse.jpg`

**Rules:**
- All lowercase, hyphens between words
- Always start with `vurt-`
- Be specific — describe what's IN the image, not just the category
- No hashes, UUIDs, or auto-generated strings (`IMG_3847.jpg` = bad)
- Keep under 60 characters when possible

### Videos
```
vurt-[series-name]-[type]-[descriptor].mp4
```
Examples:
- `vurt-karma-in-heels-trailer-s1.mp4`
- `vurt-liberty-city-history-cultural-clip.mp4`
- `vurt-this-is-vurt-launch-promo.mp4`

## Alt Text Standards

### Rules
1. **Unique per image** — never duplicate alt text across images
2. **Describe what you see** — not what you want the crawler to think
3. **Include relevant keywords naturally** — don't stuff
4. **Include series/talent names when applicable**
5. **Keep under 125 characters**
6. **Don't start with "Image of..." or "Photo of..."**

### Examples
- GOOD: `Tatyana Ali and Charles S. Dutton in Come Back Dad, a VURT micro-series about family reconciliation`
- GOOD: `VURT app browse screen showing vertical micro-drama series thumbnails on mobile`
- BAD: `come-back-dad image` (too vague)
- BAD: `VURT streaming platform Black drama micro-series vertical cinema free app` (keyword stuffed)
- BAD: `Image of a scene from the show` (generic, starts with "Image of")

## EXIF Metadata

Embed the following EXIF/IPTC fields in every image before upload:

| Field | What to put |
|-------|-------------|
| Title | Series/asset name — e.g., "Karma In Heels - Season 1 Poster" |
| Description | Unique description of what the image shows + context |
| Copyright | "© 2026 VURT Corporation. All Rights Reserved." |
| Keywords | Comma-separated: series name, talent names, genre, "VURT", "vertical cinema", "micro-drama" |
| Author | "VURT" |
| Source | "myvurt.com" |

### How to batch-embed EXIF
```bash
# Using exiftool (install: apt install libimage-exiftool-perl)
exiftool -Title="Karma In Heels - Season 1 Poster" \
         -Description="Promotional poster for Karma In Heels, a VURT original micro-series about revenge and reinvention in Dallas" \
         -Copyright="© 2026 VURT Corporation" \
         -Keywords="Karma In Heels, VURT, micro-drama, vertical cinema, drama, Dallas, revenge" \
         -Author="VURT" \
         -Source="myvurt.com" \
         vurt-karma-in-heels-poster-s1.jpg
```

## Open Graph Tags (per page/series)

Every series page should have unique OG tags:
```html
<meta property="og:title" content="Karma In Heels | VURT" />
<meta property="og:description" content="A naive Southern freshman's brutal fraternity betrayal leads to a calculated revenge years later. Watch free on VURT." />
<meta property="og:image" content="https://www.myvurt.com/images/vurt-karma-in-heels-poster-s1.jpg" />
<meta property="og:image:width" content="1080" />
<meta property="og:image:height" content="1920" />
<meta property="og:type" content="video.tv_show" />
<meta property="og:url" content="https://www.myvurt.com/series/karma-in-heels" />
<meta property="og:site_name" content="VURT" />
```

## Twitter Card Tags
```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@VURT_Official" />
<meta name="twitter:title" content="Karma In Heels | VURT" />
<meta name="twitter:description" content="A naive Southern freshman's brutal fraternity betrayal leads to a calculated revenge years later. Watch free on VURT." />
<meta name="twitter:image" content="https://www.myvurt.com/images/vurt-karma-in-heels-poster-s1.jpg" />
```

## Video Schema Markup (JSON-LD)

Every series/episode page should include:
```json
{
  "@context": "https://schema.org",
  "@type": "TVSeries",
  "name": "Karma In Heels",
  "description": "A naive Southern freshman moves to Dallas for love and college, but a brutal fraternity betrayal shatters her life. Years later, she returns with a new identity and a plan for revenge.",
  "genre": ["Drama", "Thriller"],
  "inLanguage": "en",
  "productionCompany": {
    "@type": "Organization",
    "name": "VURT Corporation",
    "url": "https://www.myvurt.com"
  },
  "numberOfSeasons": 1,
  "containsSeason": {
    "@type": "TVSeason",
    "seasonNumber": 1,
    "numberOfEpisodes": 10,
    "episode": [
      {
        "@type": "TVEpisode",
        "episodeNumber": 1,
        "name": "Episode 1",
        "duration": "PT3M",
        "video": {
          "@type": "VideoObject",
          "name": "Karma In Heels - Episode 1",
          "description": "...",
          "thumbnailUrl": "https://www.myvurt.com/images/vurt-karma-in-heels-ep1-thumbnail.jpg",
          "uploadDate": "2026-03-17",
          "contentUrl": "https://www.myvurt.com/watch/karma-in-heels/s1/e1",
          "embedUrl": "https://www.myvurt.com/embed/karma-in-heels/s1/e1",
          "isFamilyFriendly": false
        }
      }
    ]
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.7",
    "ratingCount": "11",
    "bestRating": "5"
  },
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "category": "free"
  }
}
```

## Thumbnail Optimization for Search
- Thumbnails should be unique per episode (not series-level generic)
- Include text overlay with series name when it appears in search results
- Optimal size: 1280x720 (16:9) for YouTube/Google, 1080x1920 (9:16) for vertical platforms
- File size: under 200KB for web performance
- Format: WebP preferred, JPG fallback
