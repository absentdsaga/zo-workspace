# Spatial Worlds — Skills Ecosystem Map

**Complete skill dependency graph and execution plan for building isometric multiplayer worlds.**

---

## Skill Inventory

### 🎨 **Art Generation**
1. **`isometric-sprite-gen`** — Generate Chrono Trigger-style sprites on elevated platforms
2. **`asset-pipeline-iso`** — Automated pipeline from AI to production assets

### 🏗️ **World Building**
3. **`isometric-world-builder`** — Design multi-level tactical worlds in Tiled

### ⚙️ **Game Engine**
4. **`phaser-iso-engine`** — Isometric rendering, depth sorting, 8-direction movement

### 🌐 **Multiplayer**
5. **`multiplayer-sync-iso`** — Real-time state sync with elevation awareness

### 🔊 **Audio**
6. **`spatial-audio-zones`** — 3D spatial audio with reverb zones and elevation

### 🔧 **Workflow**
7. **`workflow-orchestrator`** — Coordinate skills, manage dependencies, quality gates
8. **`self-qa`** — Autonomous testing and feedback generation

### 📱 **Platform Support** (Future)
9. **`mobile-touch-iso`** — Virtual joystick for isometric movement
10. **`build-preview`** — Visual QA and screenshot capture (existing)
11. **`efficient-referencing`** — Credit optimization (existing)

---

## Dependency Graph

```
                    workflow-orchestrator
                            |
          +-----------------+------------------+
          |                 |                  |
    Foundation          Art Pipeline      Multiplayer
          |                 |                  |
   phaser-iso-engine   isometric-sprite-gen   |
          |              |        |            |
          |     asset-pipeline-iso|            |
          |              |        |            |
    isometric-world-builder      |      multiplayer-sync-iso
                   |              |            |
                   +------+-------+------------+
                          |
                   spatial-audio-zones
                          |
                       self-qa
```

### Execution Order (Sequential)

**Phase 1: Foundation** (parallel where possible)
```
1. phaser-iso-engine.setup()
   ├─ Install dependencies
   ├─ Configure Phaser for isometric
   └─ Implement depth sorting system

2. isometric-world-builder.init()
   ├─ Setup Tiled with isometric orientation
   └─ Create tileset templates
```

**Phase 2: Art Pipeline** (parallel)
```
3. isometric-sprite-gen.generate_base()
   ├─ Create warrior sprite (first test)
   └─ Validate style matches reference

4. asset-pipeline-iso.setup()
   ├─ Configure AI generation
   ├─ Setup palette quantization
   └─ Create sprite packing scripts

5. asset-pipeline-iso.batch_generate()
   ├─ Generate 50 character sprites
   └─ Create isometric tilesets

6. isometric-world-builder.create_world("crossroads")
   ├─ Design 50×50 map with 4 levels
   └─ Define acoustic zones
```

**Phase 3: Integration** (sequential)
```
7. phaser-iso-engine.integrate_assets()
   ├─ Load sprites and tilesets
   ├─ Setup 8-direction animations
   └─ Test depth sorting

8. self-qa.test_rendering()
   ├─ Verify 60 FPS with 50 sprites
   └─ Check depth sorting accuracy
```

**Phase 4: Multiplayer** (sequential)
```
9. multiplayer-sync-iso.setup_server()
   ├─ WebSocket server with elevation
   └─ Authoritative collision

10. multiplayer-sync-iso.integrate_client()
    ├─ Client prediction (8-direction)
    └─ Remote player interpolation

11. self-qa.test_multiplayer()
    ├─ Simulate 10 clients
    └─ Measure latency
```

**Phase 5: Voice** (sequential)
```
12. spatial-audio-zones.setup_daily()
    ├─ Configure Daily.co
    └─ Implement 3D proximity

13. spatial-audio-zones.define_zones()
    ├─ Load from Tiled maps
    └─ Setup reverb profiles

14. self-qa.test_voice()
    ├─ Test elevation-aware volume
    └─ Verify room transitions
```

---

## Skill-to-Deliverable Mapping

| Skill | Deliverables | Used By |
|-------|--------------|---------|
| `phaser-iso-engine` | Isometric renderer, depth sorting, 8-dir movement | All game scenes |
| `isometric-sprite-gen` | 50 character sprites (48×64px, 8-dir) | Phaser scenes, asset pipeline |
| `asset-pipeline-iso` | Optimized sprite atlases, tilesets | Phaser asset loader |
| `isometric-world-builder` | Tiled maps (JSON), acoustic zones | Phaser tilemap system |
| `multiplayer-sync-iso` | WebSocket server, client sync | Networking layer |
| `spatial-audio-zones` | Daily.co integration, voice manager | Audio system |
| `workflow-orchestrator` | Build automation, dependency mgmt | Development process |
| `self-qa` | Test reports, performance metrics | Quality assurance |

---

## Skill Interfaces

### Input/Output Contracts

#### `isometric-sprite-gen`
```typescript
interface Input {
  character: string; // "warrior with red hair"
  platform: 'grass' | 'stone' | 'wood';
  style: 'chrono-trigger';
}

interface Output {
  sprite: ImageData; // 48×64px
  palette: string[]; // 64 colors
  metadata: {
    directions: 8;
    frames: 4;
    platform: true;
  };
}
```

#### `isometric-world-builder`
```typescript
interface Input {
  name: string; // "crossroads"
  size: { width: number, height: number };
  elevationLevels: number; // 4
  theme: 'medieval' | 'library' | 'cyberpunk';
}

interface Output {
  tiledMap: string; // JSON path
  acousticZones: AcousticZone[];
  collisionLayers: CollisionLayer[];
}
```

#### `phaser-iso-engine`
```typescript
interface Input {
  assets: {
    sprites: string[]; // Paths to atlases
    tilesets: string[]; // Paths to tilesets
    maps: string[]; // Paths to Tiled JSON
  };
}

interface Output {
  gameScene: Phaser.Scene;
  depthManager: DepthManager;
  movementController: IsoMovementController;
}
```

---

## Quality Gates

### After Each Skill Execution

**`phaser-iso-engine`**:
- ✅ Depth sorting works (no Z-fighting)
- ✅ 60 FPS with 100 test sprites
- ✅ 8-direction movement smooth

**`isometric-sprite-gen`**:
- ✅ Sprite size exactly 48×64px
- ✅ Platform visible and correct
- ✅ ≤64 colors (Chrono Trigger palette)
- ✅ Shadow present on platform

**`isometric-world-builder`**:
- ✅ Map exports without errors
- ✅ All tiles have collision data
- ✅ Acoustic zones defined
- ✅ Elevation levels consistent

**`multiplayer-sync-iso`**:
- ✅ <100ms latency with 10 clients
- ✅ Position sync accurate (±5px)
- ✅ Elevation changes synchronized
- ✅ No desyncs after 60s

**`spatial-audio-zones`**:
- ✅ Voice volume changes with distance
- ✅ Elevation penalty applied correctly
- ✅ Room transitions seamless (<500ms)
- ✅ No audio dropouts

---

## Parallelization Strategy

### What Can Run in Parallel

**Phase 2 (Art)**: All independent
- Generate sprites (50 concurrent AI calls)
- Create tilesets (5 themes in parallel)
- Design worlds (3 worlds simultaneously)

**Phase 4 (Integration)**: Cannot parallelize
- Must integrate sequentially (dependencies)

**Phase 5 (Testing)**: Parallel QA
- Render tests (separate process)
- Network tests (separate process)
- Audio tests (separate process)

### Optimal Execution Plan

```bash
# Phase 1: Foundation (5 min)
workflow run --phase foundation --sequential

# Phase 2: Art (30 min, parallel)
workflow run --phase art-generation --parallel --max-workers 10

# Phase 3: Integration (10 min)
workflow run --phase integration --sequential

# Phase 4: Multiplayer (15 min)
workflow run --phase multiplayer --sequential

# Phase 5: Voice (10 min)
workflow run --phase voice --sequential

# Total: ~70 minutes for full build
```

---

## Skill Communication Protocol

### Inter-Skill Data Passing

```typescript
// Shared context (in-memory during workflow)
interface WorkflowContext {
  assets: {
    sprites: Map<string, SpriteData>;
    tilesets: Map<string, TilesetData>;
    maps: Map<string, TiledMapData>;
  };
  config: {
    targetFPS: 60;
    maxPlayers: 100;
    voiceRange: 500;
  };
  performance: {
    fps: number;
    latency: number;
    memoryMB: number;
  };
}

// Skills read from and write to context
class Skill {
  async execute(input: any, context: WorkflowContext): Promise<any> {
    // Read dependencies from context
    const sprites = context.assets.sprites;
    
    // Do work
    const result = await this.process(input, sprites);
    
    // Write outputs to context
    context.assets.maps.set(input.name, result.map);
    
    return result;
  }
}
```

---

## Error Handling & Recovery

### Retry Strategy

```typescript
const retryConfig = {
  'isometric-sprite-gen': {
    maxRetries: 3,
    backoff: 'exponential',
    fallback: 'use-placeholder',
  },
  'multiplayer-sync-iso': {
    maxRetries: 5,
    backoff: 'linear',
    fallback: 'single-player-mode',
  },
  'spatial-audio-zones': {
    maxRetries: 2,
    backoff: 'exponential',
    fallback: 'disable-voice',
  },
};
```

### Rollback Points

After each phase, create snapshot:
- Phase 1 complete → Checkpoint 1
- Phase 2 complete → Checkpoint 2
- Phase 3 complete → Checkpoint 3
- Phase 4 complete → Checkpoint 4
- Phase 5 complete → Checkpoint 5

If phase fails after retry, rollback to previous checkpoint.

---

## Monitoring & Observability

### Skill Execution Metrics

```typescript
interface SkillMetrics {
  skill: string;
  startTime: number;
  endTime: number;
  duration: number;
  success: boolean;
  error?: string;
  outputs: Record<string, any>;
  qualityGate: {
    passed: boolean;
    metrics: Record<string, number>;
  };
}
```

### Real-Time Dashboard

```
┌─ Spatial Worlds Build Progress ──────────────────────────────┐
│                                                                │
│  Phase 1: Foundation          [████████████████████] 100%     │
│  Phase 2: Art Generation      [██████████░░░░░░░░░░]  50%     │
│  Phase 3: Integration         [░░░░░░░░░░░░░░░░░░░░]   0%     │
│  Phase 4: Multiplayer         [░░░░░░░░░░░░░░░░░░░░]   0%     │
│  Phase 5: Voice               [░░░░░░░░░░░░░░░░░░░░]   0%     │
│                                                                │
│  Current: isometric-sprite-gen.batch_generate                 │
│  Progress: 25 / 50 sprites generated                          │
│  ETA: 15 minutes                                               │
│                                                                │
│  Quality Gates: ✅ 3 passed  ⏳ 2 pending                      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Usage Examples

### Full Build (Automated)

```bash
# One command to build everything
bun run Skills/workflow-orchestrator/scripts/run.ts \
  --workflow spatial-worlds-isometric-build \
  --parallel \
  --verbose
```

### Partial Build (Specific Phase)

```bash
# Just regenerate art assets
bun run Skills/workflow-orchestrator/scripts/run.ts \
  --workflow spatial-worlds-isometric-build \
  --phase art-generation \
  --parallel
```

### Manual Skill Execution

```bash
# Run single skill manually
bun run Skills/isometric-sprite-gen/scripts/generate-character.ts \
  --character "warrior, red hair" \
  --platform grass \
  --output warrior
```

---

## Total Skill Ecosystem Stats

| Metric | Count |
|--------|-------|
| **Total Skills** | 11 |
| **Core Skills** | 6 |
| **Meta Skills** | 2 (orchestrator, self-qa) |
| **Support Skills** | 3 |
| **Total Scripts** | ~40 |
| **Total Lines of Code** | ~8,000 (estimated) |
| **Automated Tests** | 15+ quality gates |

---

## Success Criteria

**Ecosystem Complete When**:
- ✅ All 11 skills implemented
- ✅ Full workflow runs end-to-end
- ✅ All quality gates pass
- ✅ Build time <90 minutes
- ✅ Zero manual intervention required

**Spatial Worlds Launch Ready When**:
- ✅ 5 worlds fully playable
- ✅ 50 character sprites available
- ✅ 60 FPS with 50 concurrent sprites
- ✅ Voice working with 100 users
- ✅ Mobile-compatible

---

*This ecosystem represents a **top 0.01% engineering approach** to building complex multiplayer games with full automation, quality assurance, and workflow orchestration.*
