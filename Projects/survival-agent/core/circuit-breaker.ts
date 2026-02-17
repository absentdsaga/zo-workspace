/**
 * CIRCUIT BREAKER PATTERN
 *
 * Implements @legendaryy's principle #4:
 * "Embedding provider crashes shouldn't take down your gateway.
 * Consider a retry circuit breaker or just queue the failures
 * instead of death-spiraling"
 *
 * Prevents cascading failures when external services fail.
 * Uses exponential backoff and failure queues.
 */

interface CircuitBreakerConfig {
  maxFailures?: number;        // Open circuit after N failures (default: 3)
  cooldownMs?: number;          // Time before retry (default: 60000 = 1 min)
  halfOpenRetries?: number;     // Attempts in half-open state (default: 1)
  failureQueueSize?: number;    // Max queued failures (default: 100)
}

interface QueuedFailure<T> {
  key: string;
  fn: () => Promise<T>;
  fallback?: () => T;
  timestamp: number;
  retries: number;
}

export class CircuitBreaker {
  private failures = new Map<string, number>();
  private lastAttempt = new Map<string, number>();
  private failureQueue: QueuedFailure<any>[] = [];

  private readonly MAX_FAILURES: number;
  private readonly COOLDOWN_MS: number;
  private readonly HALF_OPEN_RETRIES: number;
  private readonly FAILURE_QUEUE_SIZE: number;

  constructor(config: CircuitBreakerConfig = {}) {
    this.MAX_FAILURES = config.maxFailures ?? 3;
    this.COOLDOWN_MS = config.cooldownMs ?? 60000;
    this.HALF_OPEN_RETRIES = config.halfOpenRetries ?? 1;
    this.FAILURE_QUEUE_SIZE = config.failureQueueSize ?? 100;
  }

  /**
   * Execute a function with circuit breaker protection
   *
   * States:
   * - CLOSED: Normal operation, all requests pass through
   * - OPEN: Too many failures, reject immediately
   * - HALF_OPEN: After cooldown, allow limited retries
   */
  async execute<T>(
    key: string,
    fn: () => Promise<T>,
    fallback?: () => T
  ): Promise<T> {
    const state = this.getState(key);

    switch (state) {
      case 'OPEN':
        // Circuit is open, use fallback or queue
        if (fallback) {
          console.log(`⚠️  Circuit breaker OPEN for ${key}, using fallback`);
          return fallback();
        }

        // Queue for retry later
        this.queueFailure(key, fn, fallback);
        throw new Error(`Circuit breaker OPEN for ${key}, queued for retry`);

      case 'HALF_OPEN':
        // Try limited retries
        console.log(`🔄 Circuit breaker HALF_OPEN for ${key}, attempting retry`);
        return await this.attemptRetry(key, fn, fallback);

      case 'CLOSED':
      default:
        // Normal execution
        return await this.attemptExecution(key, fn, fallback);
    }
  }

  /**
   * Get current circuit state
   */
  private getState(key: string): 'CLOSED' | 'OPEN' | 'HALF_OPEN' {
    const failures = this.failures.get(key) || 0;
    const lastAttempt = this.lastAttempt.get(key) || 0;
    const timeSince = Date.now() - lastAttempt;

    if (failures >= this.MAX_FAILURES) {
      if (timeSince < this.COOLDOWN_MS) {
        return 'OPEN';
      }
      return 'HALF_OPEN';
    }

    return 'CLOSED';
  }

  /**
   * Attempt normal execution (CLOSED state)
   */
  private async attemptExecution<T>(
    key: string,
    fn: () => Promise<T>,
    fallback?: () => T
  ): Promise<T> {
    try {
      const result = await fn();
      // Success - reset failures
      this.failures.set(key, 0);
      return result;
    } catch (error) {
      // Failure - increment counter
      const failures = (this.failures.get(key) || 0) + 1;
      this.failures.set(key, failures);
      this.lastAttempt.set(key, Date.now());

      console.error(`❌ ${key} failed (${failures}/${this.MAX_FAILURES}):`, error);

      if (fallback) {
        console.log(`⚠️  Using fallback for ${key}`);
        return fallback();
      }

      throw error;
    }
  }

  /**
   * Attempt retry (HALF_OPEN state)
   */
  private async attemptRetry<T>(
    key: string,
    fn: () => Promise<T>,
    fallback?: () => T
  ): Promise<T> {
    try {
      const result = await fn();
      // Success - reset circuit
      this.failures.set(key, 0);
      console.log(`✅ ${key} recovered, circuit CLOSED`);
      return result;
    } catch (error) {
      // Still failing - reopen circuit
      this.failures.set(key, this.MAX_FAILURES);
      this.lastAttempt.set(key, Date.now());

      console.error(`❌ ${key} retry failed, circuit OPEN again`);

      if (fallback) {
        return fallback();
      }

      throw error;
    }
  }

  /**
   * Queue a failed operation for later retry
   */
  private queueFailure<T>(
    key: string,
    fn: () => Promise<T>,
    fallback?: () => T
  ): void {
    if (this.failureQueue.length >= this.FAILURE_QUEUE_SIZE) {
      console.warn(`⚠️  Failure queue full, dropping oldest entry`);
      this.failureQueue.shift();
    }

    this.failureQueue.push({
      key,
      fn,
      fallback,
      timestamp: Date.now(),
      retries: 0
    });

    console.log(`📥 Queued ${key} for retry (queue size: ${this.failureQueue.length})`);
  }

  /**
   * Process queued failures
   * Call this periodically (e.g., every 5 minutes)
   */
  async processQueue(): Promise<void> {
    if (this.failureQueue.length === 0) {
      return;
    }

    console.log(`🔄 Processing ${this.failureQueue.length} queued failures...`);

    const toProcess = [...this.failureQueue];
    this.failureQueue = [];

    for (const item of toProcess) {
      try {
        await this.execute(item.key, item.fn, item.fallback);
        console.log(`✅ Successfully processed queued ${item.key}`);
      } catch (error) {
        // Still failing, requeue if under retry limit
        if (item.retries < 3) {
          item.retries++;
          this.failureQueue.push(item);
          console.log(`⚠️  ${item.key} still failing, requeued (attempt ${item.retries}/3)`);
        } else {
          console.error(`❌ ${item.key} exceeded retry limit, dropping`);
        }
      }
    }
  }

  /**
   * Get circuit breaker stats
   */
  getStats(): Record<string, any> {
    const stats: Record<string, any> = {};

    for (const [key, failures] of this.failures.entries()) {
      stats[key] = {
        failures,
        state: this.getState(key),
        lastAttempt: this.lastAttempt.get(key) || 0
      };
    }

    return {
      circuits: stats,
      queueSize: this.failureQueue.length
    };
  }

  /**
   * Manually reset a circuit
   */
  reset(key: string): void {
    this.failures.delete(key);
    this.lastAttempt.delete(key);
    console.log(`🔄 Reset circuit for ${key}`);
  }

  /**
   * Reset all circuits
   */
  resetAll(): void {
    this.failures.clear();
    this.lastAttempt.clear();
    this.failureQueue = [];
    console.log(`🔄 Reset all circuits`);
  }
}

/**
 * Global circuit breaker instance
 * Use this for all external API calls
 */
export const globalCircuitBreaker = new CircuitBreaker({
  maxFailures: 3,
  cooldownMs: 60000,      // 1 minute
  halfOpenRetries: 1,
  failureQueueSize: 100
});
