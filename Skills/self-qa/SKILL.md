---
name: self-qa
description: Autonomous quality assurance - test your own code, capture screenshots, analyze performance, and provide structured feedback for iteration.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  category: development-tools
  version: 1.0.0
---

# Self-QA — Autonomous Quality Assurance

A skill for testing your own work, capturing evidence, analyzing results, and providing structured feedback for rapid iteration.

## When to Use This Skill

Activate after completing any significant implementation:
- Web applications (capture screenshots, test flows)
- APIs (run test requests, validate responses)
- Games (measure FPS, test controls, capture gameplay)
- Scripts (run with test data, verify outputs)
- UIs (check responsive design, accessibility)

## How It Works

### 1. Automated Testing
Run your application and execute test scenarios:
```bash
# Start the service
# Navigate through key flows
# Capture metrics (performance, errors, behavior)
```

### 2. Visual QA
Capture screenshots/videos of:
- Initial load state
- User interactions
- Edge cases
- Error states
- Different viewports (desktop, mobile)

### 3. Performance Analysis
Measure and report:
- Load time
- FPS (for games/animations)
- Memory usage
- Network requests
- Bundle size

### 4. Structured Feedback
Generate a report with:
- ✅ **What works well** (strengths to preserve)
- ⚠️ **Issues found** (bugs, performance problems)
- 💡 **Improvement suggestions** (UX, code quality)
- 📋 **Next steps** (prioritized action items)

## Usage

```bash
# Test web application
bun run Skills/self-qa/scripts/test-web.ts \
  --url http://localhost:3000 \
  --scenarios scenarios.json \
  --output report.md

# Test game performance
bun run Skills/self-qa/scripts/test-game.ts \
  --url http://localhost:3000 \
  --duration 60 \
  --capture-video

# Test API
bun run Skills/self-qa/scripts/test-api.ts \
  --endpoint http://localhost:3000/api \
  --requests requests.json
```

## Output Format

The skill generates:
- `report.md` — Structured feedback report
- `screenshots/` — Visual evidence
- `metrics.json` — Performance data
- `video.mp4` — Gameplay/interaction recording (optional)

## Scripts

- `scripts/test-web.ts` — Web application testing with Playwright
- `scripts/test-game.ts` — Game performance testing (FPS, input lag)
- `scripts/test-api.ts` — API endpoint validation
- `scripts/analyze-bundle.ts` — Bundle size analysis
- `scripts/check-accessibility.ts` — A11y audit

## Integration with Build-Preview

This skill complements the `build-preview` skill:
- **build-preview**: Visual snapshot (what it looks like)
- **self-qa**: Functional testing (how it works)

Use both together for comprehensive quality assurance.
