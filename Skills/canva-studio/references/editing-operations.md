# Canva Editing Operations Reference

## Transaction Lifecycle

```
start-editing-transaction(design_id)
  ↓ returns transaction_id + elements (richtexts, fills)
perform-editing-operations(transaction_id, operations, page_index)
  ↓ returns updated elements + first page thumbnail
  ↓ (repeat for more edits)
commit-editing-transaction(transaction_id)  ← saves
cancel-editing-transaction(transaction_id)  ← discards
```

## Operation Types

### 1. replace_text
Replace the entire content of a text element.
```json
{"type": "replace_text", "element_id": "e123", "text": "New full text content"}
```

### 2. find_and_replace_text
Replace a substring within a text element. Preserves formatting of unchanged text.
```json
{"type": "find_and_replace_text", "element_id": "e123", "find_text": "old word", "replace_text": "new word"}
```
**Prefer this over replace_text when changing only part of a text element.**

### 3. update_fill
Replace an image or video in an existing element.
```json
{"type": "update_fill", "element_id": "e456", "asset_type": "image", "asset_id": "abc123", "alt_text": "Description of image"}
```
**When a page has multiple images:** Always call get-assets first to identify which element to target.

### 4. insert_fill
Add a new image or video to a page.
```json
{
  "type": "insert_fill",
  "page_id": "p1",
  "asset_type": "image",
  "asset_id": "abc123",
  "alt_text": "Description",
  "left": 100,
  "top": 200,
  "width": 500,
  "height": 300,
  "opacity": 1.0,
  "rotation": 0
}
```

### 5. delete_element
Remove a text or media element.
```json
{"type": "delete_element", "element_id": "e789"}
```

### 6. position_element
Move an element to new coordinates.
```json
{"type": "position_element", "element_id": "e123", "top": 100, "left": 200}
```

### 7. resize_element
Change element dimensions.
```json
{"type": "resize_element", "element_id": "e123", "width": 500, "height": 300, "preserve_aspect_ratio": false}
```
**For text elements:** Only specify width (height auto-calculates).
**For images with aspect ratio:** Specify only width OR height with `preserve_aspect_ratio: true`.

### 8. format_text
Apply formatting to a text element.
```json
{
  "type": "format_text",
  "element_id": "e123",
  "formatting": {
    "color": "#FF6B6B",
    "font_size": 48,
    "font_weight": "bold",
    "font_style": "italic",
    "text_align": "center",
    "decoration": "underline",
    "strikethrough": "none",
    "line_height": 1.5,
    "link": "https://vfrttv.com",
    "list_level": 1,
    "list_marker": "disc"
  }
}
```
**Note:** Font family changes are NOT supported.

### 9. update_title
Change the design's title (metadata, not visual).
```json
{"type": "update_title", "title": "New Design Title"}
```

## Bulk Operations

Multiple operations can (and should) be batched in a single perform-editing-operations call:
```json
{
  "transaction_id": "txn_abc",
  "page_index": 1,
  "operations": [
    {"type": "find_and_replace_text", "element_id": "e1", "find_text": "2025", "replace_text": "2026"},
    {"type": "find_and_replace_text", "element_id": "e2", "find_text": "Q4", "replace_text": "Q1"},
    {"type": "update_fill", "element_id": "e3", "asset_type": "image", "asset_id": "new_img", "alt_text": "Updated hero"},
    {"type": "format_text", "element_id": "e1", "formatting": {"color": "#8B5CF6"}}
  ]
}
```

## Common Patterns

### Template Refresh
Update a recurring design (weekly post, monthly report):
1. start-editing-transaction on the template
2. find_and_replace_text for dates, numbers, names
3. update_fill for new images
4. commit

### Brand Color Update
Apply new brand colors across a design:
1. start-editing-transaction
2. format_text on each text element with new color
3. commit

### Localization
Translate a design:
1. start-editing-transaction → get all text elements
2. Translate each text externally
3. replace_text for each element with translated content
4. commit
