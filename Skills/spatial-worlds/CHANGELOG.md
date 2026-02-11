# Changelog - Spatial Worlds

## v21 - 100% Test Pass Rate (2026-02-10)

**Achievement: All 11 automated tests passing!**

### Added
- Favicon (isometric diamond icon in green)
- Favicon route handler in server
- Favicon link tag in HTML

### Fixed
- Console error for missing favicon (404)
- Test suite now reports 0 console errors

### Test Results
- **Pass Rate:** 100% (11/11)
- **Console Errors:** 0
- **Duration:** 29s

---

## v20 - Visual Fixes + Auto-Elevation (2026-02-10)

### Fixed
- **Invisible Legs:** Regenerated all 17 sprite files without platforms
- **Green Platforms:** Removed platforms from sprite generation
- **Auto-Elevation:** Added map offset parameters to collision detection

### Changed
- Sprite size: 48x48 (was 48x64)
- Sprites now include: character + small shadow only
- Cache-busting version bump: `main-iso.js?v=20`

### Test Results
- **Pass Rate:** 90.9% (10/11)
- **Failing:** Console Errors (favicon 404 only)

---

## v19 - Multiplayer Foundation (2026-02-09)

### Added
- Real-time multiplayer synchronization
- WebSocket server with proximity broadcasting
- Client-side prediction
- Position interpolation (lerp smoothing)
- 8-direction movement system
- Isometric sprite rendering
- Depth sorting by Y + elevation
- Multi-level platform support (L0-L3)

### Features
- 60 FPS target performance
- 8-direction character animations
- Elevation-aware collision detection
- Smooth movement transitions
- Remote player rendering

### Test Results
- Initial automated test suite created
- WebGL support not yet configured (tests failing)

---

## Version History Summary

| Version | Date | Tests Passing | Key Achievement |
|---------|------|---------------|-----------------|
| v21 | 2026-02-10 | 11/11 (100%) | Production ready |
| v20 | 2026-02-10 | 10/11 (90.9%) | Visual fixes complete |
| v19 | 2026-02-09 | 0/11 (0%) | Multiplayer foundation |
