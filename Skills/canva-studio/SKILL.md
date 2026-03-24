---
name: canva-studio
description: "Full-stack Canva design automation via MCP API. Generate, edit, export, and organize designs programmatically. Supports all 25+ design types, brand kit enforcement, batch operations, asset management, and multi-format export. Use this skill whenever the user needs to create or manage Canva assets at scale."
compatibility: "Created for Zo Computer. Requires Canva MCP connector."
metadata:
  author: "dioni.zo.computer"
  version: "1.0.0"
---

# Canva Studio — Design Automation Skill

## When to Activate
- User asks to create any design asset (social posts, presentations, docs, logos, flyers, etc.)
- User wants to edit existing Canva designs programmatically
- User needs batch design generation (e.g., "make IG posts for the whole week")
- User wants to export designs to specific formats
- User asks to organize their Canva workspace (folders, search, move)
- User wants to upload assets or swap images in existing designs
- User mentions brand kit enforcement or on-brand design generation
- Any VURT content calendar item needs visual assets created

## Architecture

### Tool Groups

**1. GENERATE — Create new designs from scratch**
```
generate-design          → 25 design types (social, print, docs, video)
request-outline-review   → Presentation outline builder (REQUIRED before presentation gen)
generate-design-structured → Generate from approved outline
create-design-from-candidate → Convert AI candidate into editable design
```

**2. EDIT — Modify existing designs**
```
start-editing-transaction    → Open edit session (returns transaction_id)
perform-editing-operations   → Execute edits (replace text, swap media, format, position, resize, delete)
commit-editing-transaction   → Save changes
cancel-editing-transaction   → Discard changes
```

**3. READ — Inspect designs**
```
get-design            → Metadata (owner, title, URLs, timestamps)
get-design-content    → Text content (richtexts)
get-design-pages      → Page list with thumbnails
get-design-thumbnail  → Thumbnail for specific page
get-presenter-notes   → Speaker notes from presentations
get-assets            → Asset metadata and thumbnails
get-export-formats    → Available export formats for a design
```

**4. ORGANIZE — Manage Canva workspace**
```
search-designs       → Find designs by keyword
search-folders       → Find folders
list-folder-items    → Browse folder contents
create-folder        → Create new folders
move-item-to-folder  → Move designs/folders/images
```

**5. EXPORT — Download designs**
```
export-design → PDF, PNG, JPG, GIF, PPTX, MP4
               Supports quality levels, page selection, custom dimensions,
               transparent backgrounds, single-image merge
```

**6. ASSETS & BRAND**
```
upload-asset-from-url  → Upload images/videos into Canva from URL
list-brand-kits        → Get available brand kits
import-design-from-url → Import external files as Canva designs
```

**7. COLLABORATE**
```
comment-on-design    → Add comments
reply-to-comment     → Reply to existing comments
list-comments        → View all comments
list-replies         → View replies to a comment
```

**8. UTILITY**
```
resize-design        → Resize to preset or custom dimensions
resolve-shortlink    → Resolve canva.link URLs to design IDs
```

---

## Workflows

### Workflow 1: Generate a Single Design

```
1. (Optional) list-brand-kits → get brand_kit_id
2. generate-design(query, design_type, brand_kit_id?)
   → Returns candidate previews
3. User picks a candidate
4. create-design-from-candidate(job_id, candidate_id)
   → Returns design_id
5. (Optional) Edit with editing transaction
6. (Optional) export-design(design_id, format)
```

**Supported design_type values:**
business_card, card, desktop_wallpaper, doc, document, facebook_cover, facebook_post, flyer, infographic, instagram_post, invitation, logo, phone_wallpaper, photo_collage, pinterest_pin, postcard, poster, presentation, proposal, report, resume, twitter_post, your_story, youtube_banner, youtube_thumbnail

### Workflow 2: Generate a Presentation

```
1. request-outline-review(topic, pages[], audience?, style?, length?)
   → User reviews outline in widget
2. User approves or requests changes (loop back to step 1)
3. generate-design-structured(topic, audience, style, length, presentation_outlines)
   → Returns candidate previews
4. create-design-from-candidate(job_id, candidate_id)
5. (Optional) Edit slides via editing transaction
6. (Optional) export-design(design_id, {type: "pptx"})
```

### Workflow 3: Edit an Existing Design

```
1. search-designs(query) or resolve-shortlink(id) → get design_id
2. start-editing-transaction(design_id) → transaction_id + element list
3. Identify elements to change from the returned richtexts/fills
4. perform-editing-operations(transaction_id, operations[], page_index)
   Operations:
   - replace_text(element_id, text)
   - find_and_replace_text(element_id, find_text, replace_text)
   - update_fill(element_id, asset_type, asset_id, alt_text)
   - insert_fill(page_id, asset_type, asset_id, alt_text, position?)
   - delete_element(element_id)
   - position_element(element_id, top, left)
   - resize_element(element_id, width?, height?, preserve_aspect_ratio?)
   - format_text(element_id, formatting{color, font_size, font_weight, ...})
   - update_title(title)
5. Show preview to user
6. commit-editing-transaction(transaction_id) OR cancel-editing-transaction
```

### Workflow 4: Batch Social Media Suite

For creating a full suite of platform-specific assets from one concept:

```
1. Generate the hero design (e.g., instagram_post)
2. create-design-from-candidate → design_id
3. resize-design(design_id, {type: "custom", width: W, height: H}) for each platform:
   - Instagram Post: 1080×1080
   - Instagram Story: 1080×1920
   - Facebook Post: 1200×630
   - Twitter Post: 1600×900
   - YouTube Thumbnail: 1280×720
   - Pinterest Pin: 1000×1500
4. Export each resized design
5. Organize into a Canva folder
```

### Workflow 5: Asset Pipeline (Upload → Insert → Export)

```
1. Generate or find an image (via Zo's generate_image or image_search)
2. upload-asset-from-url(url, name) → asset_id
3. Use asset_id in:
   - generate-design(query, asset_ids=[asset_id]) — new design with uploaded image
   - perform-editing-operations(update_fill/insert_fill) — swap into existing design
4. export-design → download final
```

### Workflow 6: Organize Canva Workspace

```
1. create-folder(name, parent_folder_id="root")
2. search-designs(query) → find designs
3. move-item-to-folder(item_id, to_folder_id)
4. list-folder-items(folder_id) → verify
```

### Workflow 7: Design Review & Feedback

```
1. get-design(design_id) → metadata + URLs
2. get-design-content(design_id, ["richtexts"]) → read all text
3. get-design-pages(design_id) → thumbnails per page
4. comment-on-design(design_id, message) → leave feedback
5. list-comments(design_id) → read existing feedback
6. reply-to-comment(design_id, comment_id, message)
```

---

## Platform Dimension Reference

| Platform | Type | Dimensions |
|---|---|---|
| Instagram Post | instagram_post | 1080×1080 |
| Instagram Story | your_story | 1080×1920 |
| Facebook Post | facebook_post | 1200×630 |
| Facebook Cover | facebook_cover | 1640×924 |
| Twitter/X Post | twitter_post | 1600×900 |
| YouTube Thumbnail | youtube_thumbnail | 1280×720 |
| YouTube Banner | youtube_banner | 2560×1440 |
| Pinterest Pin | pinterest_pin | 1000×1500 |
| LinkedIn Post | (custom resize) | 1200×627 |
| TikTok Cover | (custom resize) | 1080×1920 |
| Poster | poster | Various |
| Flyer | flyer | Various |
| Business Card | business_card | Various |
| Presentation | presentation | 1920×1080 |

---

## Critical Rules

1. **user_intent is REQUIRED** on every Canva tool call. Always include a concise description of what the user is trying to accomplish.

2. **Presentations MUST go through outline review** — never call generate-design-structured without first calling request-outline-review and getting user approval.

3. **Editing is transactional** — always start-editing-transaction before perform-editing-operations, and always commit or cancel when done. transaction_id must be preserved across the session.

4. **Brand kits** — always ask the user if they want on-brand designs before generating. Use list-brand-kits to show options.

5. **Generated designs are candidates** — they must be converted via create-design-from-candidate before they can be edited, exported, or resized.

6. **Export format check** — call get-export-formats before export-design to confirm the format is supported.

7. **Asset uploads require public URLs** — use Zo's proxy or hosting to make local files accessible if needed.

8. **Shortlinks** — if user provides a canva.link URL, always resolve-shortlink first.

9. **Multi-image edits** — when a page has multiple images and user wants to swap one, always call get-assets first to identify the correct element.

10. **Batch operations** — when doing batch generation, organize results into Canva folders automatically for clean workspace management.

---

## Integration with VURT Ecosystem

This skill connects to:
- **vurt-content-calendar** → Calendar entries can trigger design generation for scheduled posts
- **vurt-strategy** → Brand voice and visual identity guidelines inform design queries
- **vurt-analytics** → Performance data can inform which design types to prioritize
- **Zo image generation** → generate_image / edit_image can create source assets, then upload-asset-from-url pipes them into Canva designs

### Example: Content Calendar → Canva Pipeline
```
1. Read content calendar entry (platform, topic, date)
2. Pull brand guidelines from vurt-strategy
3. generate-design(detailed_query_with_brand_context, design_type_for_platform)
4. create-design-from-candidate
5. export-design → save to workspace or upload
6. Organize in dated Canva folder
```
