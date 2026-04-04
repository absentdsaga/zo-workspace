# Fastly CDN Diagnosis Checklist for Enveu

## Critical Questions (Need Answers Immediately)

### 1. Origin Shield
**"Is Origin Shield enabled on our Fastly service? If so, which POP is designated as shield, and where is our origin server located?"**

Why: If not enabled, every Fastly POP independently fetches segments from origin on cache miss. 30 POPs = 30x origin load. CloudFlare enables tiered caching by default — this alone could explain why CloudFlare works and Fastly doesn't.

### 2. Cache Hit Ratio
**"What is our current Fastly cache hit ratio for the video delivery service? Share the Fastly real-time stats dashboard screenshot."**

Why: For VOD, CHR should be 90%+. If under 50%, caching is effectively broken.

### 3. Origin Response Headers
**"What Cache-Control, Vary, and Set-Cookie headers does our origin send on video segment responses (.ts, .m4s files)? Run: `curl -sI <segment-url>` and share output."**

Why: `Vary: Cookie`, `Set-Cookie`, or `Cache-Control: private/no-store` on segments disables all caching.

### 4. Streaming Miss
**"Is `beresp.do_stream = true` set in Fastly VCL for video segment requests?"**

Why: Without it, Fastly buffers the entire origin response before forwarding to client.

### 5. CORS Headers
**"Are CORS headers (`Access-Control-Allow-Origin`) configured at the Fastly edge for video segment responses?"**

Why: Missing CORS = silent failures on mobile web. Native app has no CORS restrictions. This is a classic "works in app, breaks in browser" pattern.

### 6. CDN Routing
**"Does the mobile web player use Fastly while the native app uses CloudFlare? Or do both use the same CDN?"**

Why: If the app routes to CloudFlare and web routes to Fastly, that directly explains the engagement gap.

### 7. Cache Key Construction
**"Are there authentication tokens or unique session parameters in video segment URLs that fragment the cache key?"**

Why: Per-user tokens in URLs make every request unique = zero cache hits.

## Settings to Verify

| Setting | Target | Check |
|---------|--------|-------|
| Origin Shield | Enabled, POP near origin | Fastly dashboard → Origins |
| Streaming Miss | `beresp.do_stream = true` for .ts/.m4s/.mp4 | VCL config |
| Segmented Caching | Enabled if serving large files | VCL config |
| Cache-Control on segments | `public, max-age=86400` | `curl -sI` |
| Vary header on segments | None or `Accept-Encoding` only | `curl -sI` |
| Set-Cookie on segments | Must NOT exist | `curl -sI` |
| CORS | `Access-Control-Allow-Origin: *` on segments | `curl -sI` |
| Origin timeouts | Connect: 1s, First Byte: 2s, Between Bytes: 2s | Fastly dashboard |
| Request collapsing | ON | Fastly dashboard |

## How to Test from Our Side

```bash
# Check if a segment is cached on Fastly (need a segment URL from browser devtools)
curl -sI -H "Fastly-Debug: 1" "<fastly-segment-url>" | grep -E "X-Cache|Age|X-Served-By|Fastly"

# Expected for cached: X-Cache: HIT, Age: >0
# Bad sign: X-Cache: MISS, Age: 0 (every request goes to origin)
```
