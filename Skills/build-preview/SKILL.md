---
name: build-preview
description: Preview and review web builds visually. Captures screenshots of deployed sites and local servers to verify work, catch issues, and iterate on improvements. Use this skill after deploying or updating any web project.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

# Build Preview Skill

This skill allows Zo to visually review web builds by capturing screenshots, comparing before/after states, and identifying issues.

## When to Use

- After deploying a new site or updating an existing one
- When the user reports a visual bug or broken element
- To verify responsive design on different viewport sizes
- Before sharing a link with the user

## Usage

### Capture a Screenshot
```bash
python /home/workspace/Skills/build-preview/scripts/preview.py capture <url> [--name <name>] [--mobile] [--full]
```

Options:
- `--name`: Custom name for the screenshot (default: auto-generated from URL)
- `--mobile`: Capture at mobile viewport (375x812)
- `--full`: Capture full page scroll

### Compare Screenshots
```bash
python /home/workspace/Skills/build-preview/scripts/preview.py compare <before> <after>
```

Outputs a visual diff highlighting changes.

### List Recent Previews
```bash
python /home/workspace/Skills/build-preview/scripts/preview.py list
```

### Review a Build
```bash
python /home/workspace/Skills/build-preview/scripts/preview.py review <url>
```

Captures desktop + mobile screenshots and outputs a checklist of common issues to verify.

## Workflow

1. After deploying/updating a build, run `review <url>`
2. Examine the captured screenshots using `read_file`
3. Note any visual issues (broken images, layout problems, etc.)
4. Fix issues and re-run `review` to verify
5. Share the link with user only after visual verification passes

## Output Location

Screenshots are saved to: `/home/.z/workspaces/<conversation>/previews/`
