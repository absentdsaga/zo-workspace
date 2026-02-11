---
name: workflow-orchestrator
description: Master orchestration skill that coordinates all other skills in optimal sequence. Manages dependencies, parallelizes work, tracks progress, and ensures quality at each stage.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  category: meta-workflow
  version: 1.0.0
---

# Workflow Orchestrator

Meta-skill that orchestrates complex multi-skill workflows with dependency management, parallel execution, and quality gates.

## Purpose

When building Spatial Worlds (or any complex project), many skills must execute in precise order:
- **isometric-sprite-gen** → **asset-pipeline-iso** → **phaser-iso-engine**
- **isometric-world-builder** → **multiplayer-sync-iso**
- **self-qa** after each major milestone

This skill automates that orchestration.

## Workflow Definition

### Spatial Worlds Build Workflow
```yaml
name: spatial-worlds-isometric-build
description: Build isometric Spatial Worlds from scratch

phases:
  - name: foundation
    parallel: false
    steps:
      - skill: phaser-iso-engine
        action: setup
        inputs:
          target: /home/workspace/Skills/spatial-worlds
        outputs:
          - engine-config
      
      - skill: isometric-world-builder
        action: init-tiled
        inputs:
          project: spatial-worlds
        outputs:
          - tiled-config
  
  - name: art-generation
    parallel: true
    steps:
      - skill: isometric-sprite-gen
        action: generate-base
        inputs:
          character: "warrior, red hair, blue armor"
          count: 50
        outputs:
          - sprites/characters/
      
      - skill: asset-pipeline-iso
        action: create-tilesets
        inputs:
          themes: [medieval, library, cyberpunk]
        outputs:
          - assets/tilesets/
  
  - name: world-building
    parallel: false
    depends_on: [art-generation]
    steps:
      - skill: isometric-world-builder
        action: create-world
        inputs:
          name: crossroads
          size: 50x50
          tileset: medieval
        outputs:
          - assets/worlds/crossroads.json
      
      - skill: self-qa
        action: test-world
        inputs:
          world: crossroads
        quality_gate: true
  
  - name: multiplayer
    parallel: false
    depends_on: [world-building]
    steps:
      - skill: multiplayer-sync-iso
        action: setup-server
        outputs:
          - server.ts
      
      - skill: multiplayer-sync-iso
        action: integrate-client
        outputs:
          - client-sync.ts
      
      - skill: self-qa
        action: test-multiplayer
        inputs:
          clients: 10
        quality_gate: true
  
  - name: voice-integration
    parallel: false
    depends_on: [multiplayer]
    steps:
      - skill: spatial-audio-zones
        action: setup-daily
        outputs:
          - voice-manager.ts
      
      - skill: self-qa
        action: test-voice
        inputs:
          users: 5
        quality_gate: true

quality_gates:
  - after: art-generation
    check: all sprites < 10KB
  - after: world-building
    check: 60 FPS in crossroads
  - after: multiplayer
    check: <100ms latency with 10 clients
  - after: voice-integration
    check: spatial audio working
```

## Orchestration Engine

### Workflow Executor
```typescript
class WorkflowOrchestrator {
  async execute(workflow: Workflow): Promise<WorkflowResult> {
    const results: Map<string, any> = new Map();
    
    for (const phase of workflow.phases) {
      console.log(`\n🚀 Phase: ${phase.name}`);
      
      if (phase.parallel) {
        // Execute steps in parallel
        const promises = phase.steps.map(step => 
          this.executeStep(step, results)
        );
        await Promise.all(promises);
      } else {
        // Execute steps sequentially
        for (const step of phase.steps) {
          await this.executeStep(step, results);
        }
      }
      
      // Quality gate check
      if (phase.quality_gate) {
        const passed = await this.checkQualityGate(phase, results);
        if (!passed) {
          throw new Error(`Quality gate failed: ${phase.name}`);
        }
      }
    }
    
    return { success: true, results };
  }
  
  async executeStep(step: WorkflowStep, context: Map<string, any>): Promise<any> {
    console.log(`  ⚙️  ${step.skill}.${step.action}`);
    
    // Load skill
    const skill = await this.loadSkill(step.skill);
    
    // Resolve inputs (may reference previous outputs)
    const inputs = this.resolveInputs(step.inputs, context);
    
    // Execute skill action
    const result = await skill.execute(step.action, inputs);
    
    // Store outputs
    if (step.outputs) {
      step.outputs.forEach(output => {
        context.set(output, result[output]);
      });
    }
    
    console.log(`  ✅ ${step.skill}.${step.action} complete`);
    
    return result;
  }
  
  async checkQualityGate(phase: WorkflowPhase, results: Map<string, any>): Promise<boolean> {
    const gate = workflow.quality_gates.find(g => g.after === phase.name);
    if (!gate) return true;
    
    console.log(`  🔍 Quality gate: ${gate.check}`);
    
    // Run quality check
    const passed = await this.runQualityCheck(gate.check, results);
    
    if (passed) {
      console.log(`  ✅ Quality gate passed`);
    } else {
      console.log(`  ❌ Quality gate FAILED`);
    }
    
    return passed;
  }
}
```

## Dependency Resolution

### Smart Caching
```typescript
class DependencyCache {
  private cache = new Map<string, any>();
  
  async resolve(dependency: string, context: Map<string, any>): Promise<any> {
    // Check cache first
    if (this.cache.has(dependency)) {
      console.log(`  📦 Using cached: ${dependency}`);
      return this.cache.get(dependency);
    }
    
    // Check context (previous step output)
    if (context.has(dependency)) {
      const value = context.get(dependency);
      this.cache.set(dependency, value);
      return value;
    }
    
    // Dependency not found
    throw new Error(`Dependency not found: ${dependency}`);
  }
}
```

## Progress Tracking

### Real-Time Dashboard
```typescript
class ProgressTracker {
  private total = 0;
  private completed = 0;
  
  track(workflow: Workflow) {
    // Count total steps
    this.total = workflow.phases.reduce(
      (sum, phase) => sum + phase.steps.length,
      0
    );
    
    // Update as steps complete
    setInterval(() => {
      this.renderProgress();
    }, 1000);
  }
  
  renderProgress() {
    const percent = Math.round((this.completed / this.total) * 100);
    const bar = '█'.repeat(Math.floor(percent / 2)) + '░'.repeat(50 - Math.floor(percent / 2));
    
    console.clear();
    console.log(`\n📊 Spatial Worlds Build Progress\n`);
    console.log(`[${bar}] ${percent}%`);
    console.log(`${this.completed} / ${this.total} steps complete\n`);
  }
}
```

## Error Recovery

### Retry & Rollback
```typescript
class ErrorRecovery {
  async executeWithRetry(step: WorkflowStep, maxRetries = 3): Promise<any> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await this.executeStep(step);
      } catch (error) {
        console.error(`  ⚠️  Attempt ${attempt} failed: ${error.message}`);
        
        if (attempt === maxRetries) {
          // Rollback
          await this.rollback(step);
          throw error;
        }
        
        // Wait before retry (exponential backoff)
        await this.sleep(Math.pow(2, attempt) * 1000);
      }
    }
  }
  
  async rollback(step: WorkflowStep) {
    console.log(`  ↩️  Rolling back: ${step.skill}.${step.action}`);
    
    // Undo changes made by this step
    if (step.outputs) {
      step.outputs.forEach(output => {
        // Delete generated files, revert state
      });
    }
  }
}
```

## Parallelization Strategy

### Optimal Concurrency
```typescript
class ParallelExecutor {
  async executeParallel(steps: WorkflowStep[], maxConcurrency = 5): Promise<any[]> {
    const queue = [...steps];
    const results: any[] = [];
    const inProgress: Promise<any>[] = [];
    
    while (queue.length > 0 || inProgress.length > 0) {
      // Start new tasks up to max concurrency
      while (inProgress.length < maxConcurrency && queue.length > 0) {
        const step = queue.shift()!;
        const promise = this.executeStep(step).then(result => {
          results.push(result);
        });
        inProgress.push(promise);
      }
      
      // Wait for at least one to complete
      await Promise.race(inProgress);
      
      // Remove completed
      inProgress.splice(
        inProgress.findIndex(p => p === Promise.resolve()),
        1
      );
    }
    
    return results;
  }
}
```

## Usage

### CLI Interface
```bash
# Run full Spatial Worlds workflow
bun run Skills/workflow-orchestrator/scripts/run.ts \
  --workflow spatial-worlds-isometric-build \
  --parallel \
  --max-concurrency 5

# Run specific phase only
bun run scripts/run.ts \
  --workflow spatial-worlds-isometric-build \
  --phase art-generation

# Dry run (show plan, don't execute)
bun run scripts/run.ts \
  --workflow spatial-worlds-isometric-build \
  --dry-run
```

### Programmatic API
```typescript
import { WorkflowOrchestrator } from './orchestrator';

const orchestrator = new WorkflowOrchestrator();
const result = await orchestrator.execute({
  name: 'spatial-worlds-build',
  phases: [/* ... */],
});

console.log('Build complete!', result);
```

## Monitoring & Logging

### Structured Logs
```typescript
class WorkflowLogger {
  log(event: WorkflowEvent) {
    const entry = {
      timestamp: new Date().toISOString(),
      phase: event.phase,
      step: event.step,
      status: event.status,
      duration: event.duration,
      error: event.error,
    };
    
    // Write to file
    fs.appendFileSync('workflow.log', JSON.stringify(entry) + '\n');
    
    // Send to monitoring (optional)
    if (process.env.MONITORING_URL) {
      fetch(process.env.MONITORING_URL, {
        method: 'POST',
        body: JSON.stringify(entry),
      });
    }
  }
}
```

## Quality Metrics

### Automated Checks
```typescript
class QualityMetrics {
  async check(metric: string, threshold: any): Promise<boolean> {
    switch (metric) {
      case 'sprite-size':
        return await this.checkSpriteSize(threshold);
      
      case 'fps':
        return await this.checkFPS(threshold);
      
      case 'latency':
        return await this.checkLatency(threshold);
      
      default:
        return true;
    }
  }
  
  async checkFPS(minFPS: number): Promise<boolean> {
    // Run performance test
    const result = await exec('bun run test-fps.ts');
    const fps = JSON.parse(result.stdout).averageFPS;
    return fps >= minFPS;
  }
}
```

## Integration with Other Skills

### Skill Registry
```typescript
class SkillRegistry {
  private skills = new Map<string, Skill>();
  
  register(name: string, skill: Skill) {
    this.skills.set(name, skill);
  }
  
  get(name: string): Skill {
    const skill = this.skills.get(name);
    if (!skill) {
      throw new Error(`Skill not found: ${name}`);
    }
    return skill;
  }
  
  // Auto-discover skills
  async discover() {
    const skillDirs = await glob('Skills/*/SKILL.md');
    
    for (const skillPath of skillDirs) {
      const skillName = path.basename(path.dirname(skillPath));
      const skill = await this.loadSkill(skillName);
      this.register(skillName, skill);
    }
  }
}
```

## Workflow Templates

Includes pre-built workflows for:
- `spatial-worlds-isometric-build` — Full build from scratch
- `spatial-worlds-art-only` — Just generate art assets
- `spatial-worlds-multiplayer-only` — Just networking layer
- `spatial-worlds-qa-suite` — Comprehensive testing
- `spatial-worlds-deploy` — Production deployment

## Scripts

- `scripts/run.ts` — Execute workflow
- `scripts/validate.ts` — Validate workflow definition
- `scripts/visualize.ts` — Generate workflow diagram
- `scripts/estimate.ts` — Estimate completion time

This skill is the **conductor** that orchestrates all other skills for optimal execution.
