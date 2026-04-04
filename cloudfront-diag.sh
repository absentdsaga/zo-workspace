#!/usr/bin/env bash
# CloudFront/CDN Diagnostic for myvurt.com
# Run: bash cloudfront-diag.sh > output.txt 2>&1

OUT="/home/.z/workspaces/con_v55GP1lr46UmN5fa/cloudfront-diag.txt"
TMPDIR=$(mktemp -d)

echo "============================================================" | tee "$OUT"
echo "  MYVURT.COM CLOUDFRONT/CDN DIAGNOSTIC" | tee -a "$OUT"
echo "  $(date -u '+%Y-%m-%d %H:%M:%S UTC')" | tee -a "$OUT"
echo "============================================================" | tee -a "$OUT"

# ─────────────────────────────────────────────────────────────
# 1. HTML CACHING CHECK
# ─────────────────────────────────────────────────────────────
echo "" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"
echo "# 1. HTML CACHING CHECK — Response Headers" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"

URLS=(
  "https://www.myvurt.com/"
  "https://www.myvurt.com/detail/micro_series/come-back-dad"
  "https://www.myvurt.com/detail/micro_series/come-back-dad?fbclid=PAZXh0bgNhZW0test"
  "https://www.myvurt.com/signup"
)

for url in "${URLS[@]}"; do
  echo "" | tee -a "$OUT"
  echo "--- $url ---" | tee -a "$OUT"
  curl -sS -D - -o /dev/null \
    -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
    --connect-timeout 10 --max-time 30 \
    "$url" 2>&1 | tee -a "$OUT"
  echo "" | tee -a "$OUT"
done

# ─────────────────────────────────────────────────────────────
# 2. JS BUNDLE CHECK
# ─────────────────────────────────────────────────────────────
echo "" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"
echo "# 2. JS BUNDLE CHECK — Angular bundles" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"

# Fetch homepage HTML
HOMEPAGE_HTML=$(curl -sS --connect-timeout 10 --max-time 30 \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
  "https://www.myvurt.com/")

# Extract JS bundles
echo "" | tee -a "$OUT"
echo "JS bundles found in HTML source:" | tee -a "$OUT"
JS_URLS=$(echo "$HOMEPAGE_HTML" | grep -oP 'src="([^"]*\.js)"' | sed 's/src="//;s/"//' | head -20)
echo "$JS_URLS" | tee -a "$OUT"

echo "" | tee -a "$OUT"
echo "Checking JS bundle headers, size, and compression:" | tee -a "$OUT"

TOTAL_SIZE=0
for js in $JS_URLS; do
  # Make absolute URL if relative
  if [[ "$js" == /* ]]; then
    js_url="https://www.myvurt.com${js}"
  elif [[ "$js" != http* ]]; then
    js_url="https://www.myvurt.com/${js}"
  else
    js_url="$js"
  fi

  echo "" | tee -a "$OUT"
  echo "--- $js_url ---" | tee -a "$OUT"

  # Fetch with Accept-Encoding to test compression
  RESP=$(curl -sS -D "$TMPDIR/jsheaders.txt" -o "$TMPDIR/jsbody.bin" -w '%{size_download}' \
    -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
    -H "Accept-Encoding: gzip, deflate, br" \
    --connect-timeout 10 --max-time 30 \
    "$js_url" 2>&1)

  SIZE=$RESP
  TOTAL_SIZE=$((TOTAL_SIZE + SIZE))

  echo "Transfer size: ${SIZE} bytes" | tee -a "$OUT"
  echo "Headers:" | tee -a "$OUT"
  cat "$TMPDIR/jsheaders.txt" | grep -iE "cache-control|age|x-cache|via|content-encoding|content-length|cf-cache|server|etag|last-modified|expires|vary|content-type" | tee -a "$OUT"
done

echo "" | tee -a "$OUT"
echo "TOTAL JS transfer size: ${TOTAL_SIZE} bytes ($(echo "scale=2; $TOTAL_SIZE / 1024 / 1024" | bc) MB)" | tee -a "$OUT"

# ─────────────────────────────────────────────────────────────
# 3. COMPARE RESPONSES — Cache behavior
# ─────────────────────────────────────────────────────────────
echo "" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"
echo "# 3. COMPARE RESPONSES — Cache behavior" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"

echo "" | tee -a "$OUT"
echo "--- Age Header Increment Test (homepage, 2 hits 3s apart) ---" | tee -a "$OUT"
echo "Hit 1:" | tee -a "$OUT"
curl -sS -D - -o /dev/null \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
  --connect-timeout 10 --max-time 30 \
  "https://www.myvurt.com/" 2>&1 | grep -iE "^(HTTP|cache-control|age|x-cache|via|cf-cache|x-amz|server)" | tee -a "$OUT"

sleep 3

echo "" | tee -a "$OUT"
echo "Hit 2 (3s later):" | tee -a "$OUT"
curl -sS -D - -o /dev/null \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
  --connect-timeout 10 --max-time 30 \
  "https://www.myvurt.com/" 2>&1 | grep -iE "^(HTTP|cache-control|age|x-cache|via|cf-cache|x-amz|server)" | tee -a "$OUT"

echo "" | tee -a "$OUT"
echo "--- fbclid vs Clean URL Comparison (detail page) ---" | tee -a "$OUT"
echo "Clean URL:" | tee -a "$OUT"
CLEAN_HEADERS=$(curl -sS -D - -o "$TMPDIR/clean.html" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
  --connect-timeout 10 --max-time 30 \
  "https://www.myvurt.com/detail/micro_series/come-back-dad" 2>&1)
echo "$CLEAN_HEADERS" | grep -iE "^(HTTP|cache-control|age|x-cache|via|cf-cache|vary|x-amz|server)" | tee -a "$OUT"

echo "" | tee -a "$OUT"
echo "With fbclid:" | tee -a "$OUT"
FBCLID_HEADERS=$(curl -sS -D - -o "$TMPDIR/fbclid.html" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
  --connect-timeout 10 --max-time 30 \
  "https://www.myvurt.com/detail/micro_series/come-back-dad?fbclid=PAZXh0bgNhZW0test" 2>&1)
echo "$FBCLID_HEADERS" | grep -iE "^(HTTP|cache-control|age|x-cache|via|cf-cache|vary|x-amz|server)" | tee -a "$OUT"

echo "" | tee -a "$OUT"
echo "Vary header (full, from clean URL):" | tee -a "$OUT"
echo "$CLEAN_HEADERS" | grep -i "^vary:" | tee -a "$OUT"

echo "" | tee -a "$OUT"
echo "HTML body diff (clean vs fbclid):" | tee -a "$OUT"
if diff -q "$TMPDIR/clean.html" "$TMPDIR/fbclid.html" > /dev/null 2>&1; then
  echo "IDENTICAL — same HTML served for both URLs" | tee -a "$OUT"
else
  echo "DIFFERENT — HTML differs between clean and fbclid URLs" | tee -a "$OUT"
  diff --brief "$TMPDIR/clean.html" "$TMPDIR/fbclid.html" | tee -a "$OUT"
  echo "First 20 diff lines:" | tee -a "$OUT"
  diff "$TMPDIR/clean.html" "$TMPDIR/fbclid.html" | head -40 | tee -a "$OUT"
fi

# ─────────────────────────────────────────────────────────────
# 4. BOT vs USER-AGENT TEST
# ─────────────────────────────────────────────────────────────
echo "" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"
echo "# 4. BOT vs USER-AGENT TEST" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"

declare -A AGENTS
AGENTS["Chrome"]="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
AGENTS["Googlebot"]="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
AGENTS["Facebook"]="facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatype.php)"

for name in "Chrome" "Googlebot" "Facebook"; do
  ua="${AGENTS[$name]}"
  echo "" | tee -a "$OUT"
  echo "--- User-Agent: $name ---" | tee -a "$OUT"

  curl -sS -D "$TMPDIR/ua_${name}_headers.txt" -o "$TMPDIR/ua_${name}_body.html" \
    -H "User-Agent: $ua" \
    --connect-timeout 10 --max-time 30 \
    "https://www.myvurt.com/detail/micro_series/come-back-dad" 2>&1

  echo "Response headers:" | tee -a "$OUT"
  cat "$TMPDIR/ua_${name}_headers.txt" | grep -iE "^(HTTP|cache-control|age|x-cache|via|cf-cache|vary|content-type|server|x-amz)" | tee -a "$OUT"

  BODY_SIZE=$(wc -c < "$TMPDIR/ua_${name}_body.html")
  echo "Body size: ${BODY_SIZE} bytes" | tee -a "$OUT"

  # Check for SSR/prerender indicators
  echo "Has <title>: $(grep -c '<title>' "$TMPDIR/ua_${name}_body.html")" | tee -a "$OUT"
  TITLE=$(grep -oP '<title>[^<]+</title>' "$TMPDIR/ua_${name}_body.html" | head -1)
  echo "Title: $TITLE" | tee -a "$OUT"

  # Check for meta og tags (important for Facebook)
  OG_COUNT=$(grep -c 'og:' "$TMPDIR/ua_${name}_body.html" 2>/dev/null || echo 0)
  echo "OG meta tags: $OG_COUNT" | tee -a "$OUT"
  grep -oP '<meta[^>]*property="og:[^"]*"[^>]*>' "$TMPDIR/ua_${name}_body.html" | head -5 | tee -a "$OUT"

  # Check for <app-root> content (Angular SSR check)
  APP_ROOT_EMPTY=$(grep -c '<app-root></app-root>' "$TMPDIR/ua_${name}_body.html" 2>/dev/null || echo 0)
  APP_ROOT_CONTENT=$(grep -c '<app-root' "$TMPDIR/ua_${name}_body.html" 2>/dev/null || echo 0)
  echo "Empty <app-root>: $APP_ROOT_EMPTY (1 = CSR only, 0 = SSR/prerendered)" | tee -a "$OUT"
  echo "<app-root> tags total: $APP_ROOT_CONTENT" | tee -a "$OUT"
done

echo "" | tee -a "$OUT"
echo "Body size comparison:" | tee -a "$OUT"
for name in "Chrome" "Googlebot" "Facebook"; do
  sz=$(wc -c < "$TMPDIR/ua_${name}_body.html")
  echo "  $name: $sz bytes" | tee -a "$OUT"
done

echo "" | tee -a "$OUT"
echo "Body content diff (Chrome vs Googlebot):" | tee -a "$OUT"
if diff -q "$TMPDIR/ua_Chrome_body.html" "$TMPDIR/ua_Googlebot_body.html" > /dev/null 2>&1; then
  echo "IDENTICAL" | tee -a "$OUT"
else
  echo "DIFFERENT" | tee -a "$OUT"
  diff "$TMPDIR/ua_Chrome_body.html" "$TMPDIR/ua_Googlebot_body.html" | head -30 | tee -a "$OUT"
fi

echo "" | tee -a "$OUT"
echo "Body content diff (Chrome vs Facebook):" | tee -a "$OUT"
if diff -q "$TMPDIR/ua_Chrome_body.html" "$TMPDIR/ua_Facebook_body.html" > /dev/null 2>&1; then
  echo "IDENTICAL" | tee -a "$OUT"
else
  echo "DIFFERENT" | tee -a "$OUT"
  diff "$TMPDIR/ua_Chrome_body.html" "$TMPDIR/ua_Facebook_body.html" | head -30 | tee -a "$OUT"
fi

# ─────────────────────────────────────────────────────────────
# 5. SSL / REDIRECT CHAIN
# ─────────────────────────────────────────────────────────────
echo "" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"
echo "# 5. SSL / REDIRECT CHAIN" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"

REDIRECT_URLS=(
  "http://myvurt.com"
  "https://myvurt.com"
  "http://www.myvurt.com"
  "https://www.myvurt.com"
)

for url in "${REDIRECT_URLS[@]}"; do
  echo "" | tee -a "$OUT"
  echo "--- $url ---" | tee -a "$OUT"
  curl -sS -L -D - -o /dev/null \
    -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
    --connect-timeout 10 --max-time 30 \
    -w "\nFinal URL: %{url_effective}\nTotal redirects: %{num_redirects}\nTotal time: %{time_total}s\n" \
    "$url" 2>&1 | tee -a "$OUT"
done

# ─────────────────────────────────────────────────────────────
# 6. SUMMARY / KEY FINDINGS
# ─────────────────────────────────────────────────────────────
echo "" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"
echo "# 6. DNS + IP CHECK" | tee -a "$OUT"
echo "###########################################################" | tee -a "$OUT"

echo "" | tee -a "$OUT"
echo "DNS lookup for www.myvurt.com:" | tee -a "$OUT"
dig +short www.myvurt.com 2>&1 | tee -a "$OUT"
echo "" | tee -a "$OUT"
echo "DNS lookup for myvurt.com:" | tee -a "$OUT"
dig +short myvurt.com 2>&1 | tee -a "$OUT"
echo "" | tee -a "$OUT"
echo "CNAME chain:" | tee -a "$OUT"
dig www.myvurt.com CNAME +short 2>&1 | tee -a "$OUT"

# Cleanup
rm -rf "$TMPDIR"

echo "" | tee -a "$OUT"
echo "============================================================" | tee -a "$OUT"
echo "  DIAGNOSTIC COMPLETE" | tee -a "$OUT"
echo "============================================================" | tee -a "$OUT"
echo "" | tee -a "$OUT"
echo "Results saved to: $OUT" | tee -a "$OUT"
