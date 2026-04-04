# Quick Wins to Reduce VURT Buffering — Ordered by Impact

## 1. Force Mobile Web to CloudFlare (IMMEDIATE — 1-2 hours)
**Impact: Eliminates the problem for users right now**

CloudFlare buffer ratio: 2.6%. Fastly: 42-77%. Change the player config on myvurt.com to use CloudFlare CDN URLs instead of Fastly. This is a workaround, not a fix, but it stops the bleeding while Fastly gets diagnosed.

## 2. Enable Origin Shield on Fastly (30 minutes)
**Impact: Reduces origin load by 10-50x, dramatically improves CHR**

Single setting in Fastly dashboard. Pick the POP closest to origin server. If this isn't enabled, this alone is likely the root cause.

## 3. Enable Streaming Miss (30 minutes)
**Impact: Eliminates edge buffering on cache misses**

Add to VCL: `if (req.url ~ "\.(ts|m4s|mp4|m4v)$") { set beresp.do_stream = true; }`

## 4. Fix Origin Cache-Control Headers (1-2 hours)
**Impact: Makes video segments actually cacheable**

Segments: `Cache-Control: public, max-age=86400`. VOD manifests: `Cache-Control: public, max-age=3600`. Remove Set-Cookie, Vary: Cookie, Cache-Control: private from video responses.

## 5. Strip Query Params from Cache Key (30 minutes)
**Impact: Prevents cache fragmentation from tokens/tracking**

In Fastly VCL, strip auth tokens and tracking params from cache key for video segments.

## 6. Configure CORS at Fastly Edge (1 hour)
**Impact: Fixes silent cross-origin failures on mobile web**

Handle OPTIONS preflight synthetically at edge. Add `Access-Control-Allow-Origin: *` on video segment responses.

## 7. Add Low-Bitrate ABR Rendition (2-4 hours)
**Impact: Ensures mobile users on slower connections get watchable video**

Add 400-600kbps rendition if lowest is above 1Mbps. Requires re-encoding.

## 8. Tune HLS.js Player Config on Mobile Web (1-2 hours)
**Impact: Makes player more conservative on mobile**

```js
{
  maxBufferLength: 30,
  maxMaxBufferLength: 60,
  startLevel: -1,        // auto, start low
  abrBandWidthFactor: 0.7 // conservative bandwidth estimation
}
```
