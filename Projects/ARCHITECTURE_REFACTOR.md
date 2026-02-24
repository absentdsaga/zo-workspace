# Architecture Refactor: Apply @legendaryy Principles

**Date**: 2026-02-15
**Source**: https://x.com/legendaryy/status/2022695573866893375

## Current Problems

### 1. **Context Bloat (750K+ tokens)**
- **survival-agent**: Market scanning, DexScreener fetches, shocked token analysis all happen in main session
- **polymarket-bot**: Historical data scraping, market analysis, calibration builds all inline
- **Result**: Massive context windows, slow responses, high costs, degraded performance

### 2. **Fragile Configuration**
- No `.patch()` pattern - full config overwrites everywhere
- One failed apply can nuke entire setup
- No rollback mechanism

### 3. **DOM Scraping Over APIs**
- Some Twitter/X research uses browser automation
- Heavy DOM snapshots bloat context
- Slower than direct API calls

### 4. **No Circuit Breakers**
- Embedding provider failures cascade
- No retry queue for failures
- Death spiral when external services fail

---

## Solutions (Based on @legendaryy Principles)

### 1. ✅ Sub-Agent Architecture for Heavy Tasks

**Move these to parallel `/zo/ask` invocations:**

#### survival-agent
```typescript
// BEFORE: Inline in main session (bloats context)
const tokens = await scanner.scanPumpFun();
const metrics = await Promise.all(tokens.map(t => tracker.getMetrics(t)));

// AFTER: Parallel sub-agents
const scanResults = await parallelScan([
  { task: "Scan pump.fun for new tokens", limit: 20 },
  { task: "Scan shocked tokens with score > 30", limit: 10 },
  { task: "Scan DexScreener for high momentum tokens", limit: 15 }
]);
```

**Implementation**:
- Create `Projects/survival-agent/core/sub-agent-coordinator.ts`
- Handles parallel market scanning via `/zo/ask` API
- Returns only essential data (token address, score, key metrics)
- Keeps main session clean

#### polymarket-bot
```python
# BEFORE: Inline historical scraping (massive context)
markets = scrape_all_markets()  # Returns 1000+ markets
calibration = build_calibration_data(markets)  # Huge dataset

# AFTER: Parallel sub-agents
scan_results = await parallel_market_scan([
    {"category": "politics", "time_range": "30-40"},
    {"category": "crypto", "time_range": "30-40"},
    {"category": "sports", "time_range": "30-40"}
])
```

**Implementation**:
- Create `Projects/polymarket-bot/core/sub_agent_coordinator.py`
- Delegates historical analysis to parallel Zo invocations
- Returns only calibration curves and edge signals
- Main session only sees final actionable data

---

### 2. ✅ config.patch > config.apply

**Pattern**:
```typescript
// BAD: Full overwrite
config.apply({
  maxPositions: 10,
  // Missing other fields = lost config
});

// GOOD: Partial update
config.patch({
  maxPositions: 10
  // Other fields preserved
});
```

**Files to Update**:
- `Projects/survival-agent/testing/paper-trade-bot.ts` - Add `.patch()` for config updates
- `Projects/polymarket-bot/monitor.py` - Add partial config updates
- Create base `ConfigManager` class with `.patch()` and `.rollback()`

---

### 3. ✅ API Calls Over DOM Scraping

**Current Issues**:
- Some workflows use browser automation when APIs exist
- DOM snapshots bloat context unnecessarily

**Fix**:
- Twitter/X: Use `x_search` tool instead of browser automation
- DexScreener: Already using API ✅
- Shocked tokens: PDF extraction is necessary (no API)
- Polymarket: Use REST API instead of web scraping where possible

**Action Items**:
- Audit all browser automation calls
- Replace with API equivalents where available
- Document when browser automation is actually necessary

---

### 4. ✅ Circuit Breaker Pattern

**Implementation**:
```typescript
class CircuitBreaker {
  private failures = new Map<string, number>();
  private lastAttempt = new Map<string, number>();
  private readonly MAX_FAILURES = 3;
  private readonly COOLDOWN_MS = 60000; // 1 minute

  async execute<T>(
    key: string,
    fn: () => Promise<T>,
    fallback?: () => T
  ): Promise<T> {
    // Check if circuit is open
    const failures = this.failures.get(key) || 0;
    const lastAttempt = this.lastAttempt.get(key) || 0;

    if (failures >= this.MAX_FAILURES) {
      const timeSince = Date.now() - lastAttempt;
      if (timeSince < this.COOLDOWN_MS) {
        console.log(`⚠️  Circuit breaker open for ${key}, using fallback`);
        if (fallback) return fallback();
        throw new Error(`Circuit breaker open for ${key}`);
      }
      // Reset after cooldown
      this.failures.set(key, 0);
    }

    try {
      const result = await fn();
      this.failures.set(key, 0); // Success - reset
      return result;
    } catch (error) {
      this.failures.set(key, failures + 1);
      this.lastAttempt.set(key, Date.now());

      if (fallback) {
        console.log(`⚠️  ${key} failed, using fallback`);
        return fallback();
      }
      throw error;
    }
  }
}
```

**Usage**:
```typescript
const breaker = new CircuitBreaker();

// DexScreener API
const metrics = await breaker.execute(
  'dexscreener',
  () => fetchDexScreenerData(token),
  () => ({ confidence: 0, reasons: ['Service unavailable'] })
);

// Jupiter quote
const quote = await breaker.execute(
  'jupiter-quote',
  () => fetchJupiterQuote(params),
  () => null // Queue for retry later
);
```

**Files to Create**:
- `Projects/survival-agent/core/circuit-breaker.ts`
- `Projects/polymarket-bot/core/circuit_breaker.py`

**Integration Points**:
- DexScreener API calls
- Jupiter quote fetching
- Shocked PDF extraction
- Polymarket API calls
- Any external service dependency

---

## Implementation Plan

### Phase 1: Sub-Agent Coordinator (Highest Impact)
1. Create `sub-agent-coordinator.ts` for survival-agent
2. Create `sub_agent_coordinator.py` for polymarket-bot
3. Move heavy scanning tasks to parallel `/zo/ask` invocations
4. Test context size reduction (target: <50K tokens per session)

### Phase 2: Circuit Breaker Pattern
1. Create base `CircuitBreaker` class
2. Wrap all external API calls
3. Add failure queues for retry
4. Test resilience under provider failures

### Phase 3: Config Management
1. Create `ConfigManager` with `.patch()` and `.rollback()`
2. Replace all full config overwrites
3. Add config versioning
4. Test rollback on failed updates

### Phase 4: API-First Approach
1. Audit all browser automation
2. Replace with API calls where possible
3. Document remaining browser automation use cases
4. Measure context size improvement

---

## Success Metrics

### Context Size
- **Before**: 750K+ tokens in main session
- **Target**: <50K tokens in main session
- **Method**: Heavy tasks offloaded to sub-agents

### Resilience
- **Before**: Provider failure = death spiral
- **Target**: Provider failure = graceful degradation + retry queue
- **Method**: Circuit breakers on all external calls

### Configuration Safety
- **Before**: One bad apply = lost config
- **Target**: Failed apply = automatic rollback
- **Method**: `.patch()` pattern + versioning

### Performance
- **Before**: Slow responses from context bloat
- **Target**: Fast responses from clean context
- **Method**: Sub-agent parallelization

---

## Next Steps

1. ✅ Create this architecture doc
2. Create sub-agent coordinators
3. Implement circuit breaker pattern
4. Add config management with `.patch()`
5. Test and validate improvements
6. Document new patterns in AGENTS.md files
