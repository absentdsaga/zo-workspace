#!/usr/bin/env python3
"""Cross-match every transcribed Frame.io clip to @myvurt TikTok posts.

Ground truth = Frame.io Status tag ("Posted" / "Approved" / "Needs Review" /
"Denied" / "Feedback Given" / "Scheduled to Post"). Dialogue matching is used
only to link Posted clips to their TikTok post metrics. Tag wins over match.

Writes per-show CLIP_MAP.md + cross-show CROSS_SHOW_SUMMARY.json.
"""
import json, os, re

INV = "/home/workspace/Skills/vurt-captions/footage/inventory.json"
TT = "/home/workspace/Skills/vurt-post-log/data/tiktok_user_url_scrape.json"
FOOTAGE = "/home/workspace/Skills/vurt-captions/footage"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def norm(s):
    return re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower())


def fragments(text, n=5, step=3):
    w = norm(text).split()
    return [" ".join(w[i:i+n]) for i in range(0, max(1, len(w)-n+1), step)]


def load_posts():
    d = json.load(open(TT))
    posts = d if isinstance(d, list) else d.get("posts", d.get("data", []))
    out = []
    for p in posts:
        cap = p.get("caption") or p.get("desc") or p.get("text") or ""
        out.append({
            "id": p.get("video_id") or p.get("id"),
            "v": p.get("views") or p.get("play_count") or 0,
            "l": p.get("likes") or p.get("digg_count") or 0,
            "s": p.get("saves") or p.get("collect_count") or 0,
            "sh": p.get("shares") or p.get("share_count") or 0,
            "c": p.get("comments") or p.get("comment_count") or 0,
            "cap": cap,
            "cap_n": norm(cap),
        })
    return out


def find_match(transcript_text, posts):
    if not transcript_text.strip():
        return None, 0
    frags = fragments(transcript_text)
    best = None
    best_hits = 0
    for p in posts:
        if not p["cap_n"]:
            continue
        hits = sum(1 for f in frags if f in p["cap_n"])
        if hits > best_hits:
            best_hits = hits
            best = p
    return (best, best_hits) if best_hits >= 1 else (None, 0)


# Tag → bucket mapping. Posted and Approved are the two actionable buckets.
BUCKET = {
    "Posted": "posted",
    "Approved": "ready",
    "Scheduled to Post": "scheduled",
    "Needs Review": "needs_review",
    "Feedback Given": "feedback_given",
    "Denied": "denied",
}
BUCKET_LABEL = {
    "posted": "Posted (live or archived)",
    "ready": "Approved — ready to post",
    "scheduled": "Scheduled to post",
    "needs_review": "Needs review",
    "feedback_given": "Feedback given (blocked)",
    "denied": "Denied",
    "untagged_matched": "Untagged — dialogue matches a live post",
    "untagged_silent": "Untagged — silent/visual only",
    "untagged_unknown": "Untagged — status unclear",
}
BUCKET_ORDER = [
    "posted", "ready", "scheduled", "needs_review",
    "feedback_given", "denied",
    "untagged_matched", "untagged_unknown", "untagged_silent",
]


def main():
    inv = json.load(open(INV))
    posts = load_posts()
    summary = {}

    for show, meta in inv.items():
        sslug = slug(show)
        tdir = f"{FOOTAGE}/{sslug}/transcripts"
        rows = []
        for clip in meta["clips"]:
            fid = clip.get("file_id") or clip.get("id")
            txt_path = f"{tdir}/{fid}.txt"
            transcript = open(txt_path).read().strip() if os.path.exists(txt_path) else ""
            jpath = f"{tdir}/{fid}.json"
            dur = json.load(open(jpath)).get("audio_duration", 0) if os.path.exists(jpath) else 0
            rs = clip.get("review_status") or ""

            match, hits = find_match(transcript, posts)

            if rs in BUCKET:
                bucket = BUCKET[rs]
            else:
                if match:
                    bucket = "untagged_matched"
                elif not transcript:
                    bucket = "untagged_silent"
                else:
                    bucket = "untagged_unknown"

            rows.append({
                "name": clip["name"],
                "id": fid,
                "size": clip.get("file_size", 0),
                "dur": dur,
                "review_status": rs,
                "breadcrumb": clip.get("breadcrumb", ""),
                "transcript": transcript[:1200],
                "bucket": bucket,
                "match": match,
                "match_hits": hits,
            })
        summary[show] = rows

    for show, rows in summary.items():
        sslug = slug(show)
        os.makedirs(f"{FOOTAGE}/{sslug}", exist_ok=True)
        by_bucket = {b: [r for r in rows if r["bucket"] == b] for b in BUCKET_ORDER}

        with open(f"{FOOTAGE}/{sslug}/CLIP_MAP.md", "w") as f:
            f.write(f"# {show} — Frame.io Clip Map\n\n")
            f.write("_Ground truth: Frame.io Status tag. Dialogue match links Posted clips to TikTok metrics._\n\n")
            f.write("## Counts by status\n\n")
            f.write("| Bucket | Count |\n|---|---:|\n")
            for b in BUCKET_ORDER:
                if by_bucket[b]:
                    f.write(f"| {BUCKET_LABEL[b]} | {len(by_bucket[b])} |\n")
            f.write("\n")

            for b in BUCKET_ORDER:
                bucket_rows = by_bucket[b]
                if not bucket_rows:
                    continue
                f.write(f"## {BUCKET_LABEL[b]}\n\n")
                for r in bucket_rows:
                    f.write(f"### {r['name']}\n")
                    f.write(f"- Frame.io id: `{r['id']}` | dur {r['dur']}s | tag: {r['review_status'] or 'Untagged'}\n")
                    f.write(f"- Folder: {r['breadcrumb']}\n")
                    if r["match"]:
                        m = r["match"]
                        lpct = (m['l']/m['v']*100) if m['v'] else 0
                        spct = (m['s']/m['v']*100) if m['v'] else 0
                        f.write(f"- TikTok match ({r['match_hits']} ngram hits): **{m['v']}v / {m['l']}L / {m['s']}S** ({lpct:.1f}% L, {spct:.2f}% S)\n")
                        f.write(f"- Caption: `{m['cap'][:240]}`\n")
                    if r["transcript"]:
                        f.write(f"- Dialogue: {r['transcript'][:400]}\n")
                    f.write("\n")

    agg = {}
    for show, rows in summary.items():
        counts = {b: 0 for b in BUCKET_ORDER}
        for r in rows:
            counts[r["bucket"]] += 1
        posted_rows = [r for r in rows if r["bucket"] == "posted" and r["match"]]
        agg[show] = {
            "total": len(rows),
            "counts": counts,
            "posted_views": sum(r["match"]["v"] for r in posted_rows),
            "posted_likes": sum(r["match"]["l"] for r in posted_rows),
            "posted_saves": sum(r["match"]["s"] for r in posted_rows),
            "ready_count": counts["ready"],
        }
    with open(f"{FOOTAGE}/CROSS_SHOW_SUMMARY.json", "w") as f:
        json.dump(agg, f, indent=2)

    print("Per-show CLIP_MAP.md written. Summary:")
    print(f"{'Show':<32} | posted | ready | NR | denied | untag_m | untag_? | silent")
    print("-"*100)
    for show, a in agg.items():
        c = a["counts"]
        print(f"{show:<32} | {c['posted']:>6} | {c['ready']:>5} | {c['needs_review']:>2} | {c['denied']:>6} | {c['untagged_matched']:>7} | {c['untagged_unknown']:>7} | {c['untagged_silent']:>6}")


if __name__ == "__main__":
    main()
