"""
CIRCUIT BREAKER PATTERN (Python)

Implements @legendaryy's principle #4:
"Embedding provider crashes shouldn't take down your gateway.
Consider a retry circuit breaker or just queue the failures
instead of death-spiraling"
"""

import time
from typing import Callable, TypeVar, Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class CircuitState(Enum):
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Too many failures, reject immediately
    HALF_OPEN = "HALF_OPEN"  # After cooldown, allow limited retries


@dataclass
class QueuedFailure:
    """A failed operation queued for retry"""
    key: str
    fn: Callable
    fallback: Optional[Callable]
    timestamp: float
    retries: int = 0


T = TypeVar('T')


class CircuitBreaker:
    """Circuit breaker for resilient external API calls"""

    def __init__(
        self,
        max_failures: int = 3,
        cooldown_ms: int = 60000,
        half_open_retries: int = 1,
        failure_queue_size: int = 100
    ):
        self.max_failures = max_failures
        self.cooldown_ms = cooldown_ms
        self.half_open_retries = half_open_retries
        self.failure_queue_size = failure_queue_size

        self.failures: Dict[str, int] = {}
        self.last_attempt: Dict[str, float] = {}
        self.failure_queue: List[QueuedFailure] = []

    def execute(
        self,
        key: str,
        fn: Callable[[], T],
        fallback: Optional[Callable[[], T]] = None
    ) -> T:
        """
        Execute a function with circuit breaker protection

        Args:
            key: Unique identifier for this circuit
            fn: Function to execute
            fallback: Optional fallback function if circuit is open

        Returns:
            Result from fn or fallback

        Raises:
            Exception if circuit is open and no fallback provided
        """
        state = self._get_state(key)

        if state == CircuitState.OPEN:
            # Circuit is open, use fallback or queue
            if fallback:
                print(f"⚠️  Circuit breaker OPEN for {key}, using fallback")
                return fallback()

            # Queue for retry later
            self._queue_failure(key, fn, fallback)
            raise Exception(f"Circuit breaker OPEN for {key}, queued for retry")

        elif state == CircuitState.HALF_OPEN:
            # Try limited retries
            print(f"🔄 Circuit breaker HALF_OPEN for {key}, attempting retry")
            return self._attempt_retry(key, fn, fallback)

        else:  # CLOSED
            # Normal execution
            return self._attempt_execution(key, fn, fallback)

    def _get_state(self, key: str) -> CircuitState:
        """Get current circuit state"""
        failures = self.failures.get(key, 0)
        last_attempt = self.last_attempt.get(key, 0)
        time_since = (time.time() * 1000) - last_attempt

        if failures >= self.max_failures:
            if time_since < self.cooldown_ms:
                return CircuitState.OPEN
            return CircuitState.HALF_OPEN

        return CircuitState.CLOSED

    def _attempt_execution(
        self,
        key: str,
        fn: Callable[[], T],
        fallback: Optional[Callable[[], T]]
    ) -> T:
        """Attempt normal execution (CLOSED state)"""
        try:
            result = fn()
            # Success - reset failures
            self.failures[key] = 0
            return result
        except Exception as e:
            # Failure - increment counter
            failures = self.failures.get(key, 0) + 1
            self.failures[key] = failures
            self.last_attempt[key] = time.time() * 1000

            print(f"❌ {key} failed ({failures}/{self.max_failures}): {e}")

            if fallback:
                print(f"⚠️  Using fallback for {key}")
                return fallback()

            raise

    def _attempt_retry(
        self,
        key: str,
        fn: Callable[[], T],
        fallback: Optional[Callable[[], T]]
    ) -> T:
        """Attempt retry (HALF_OPEN state)"""
        try:
            result = fn()
            # Success - reset circuit
            self.failures[key] = 0
            print(f"✅ {key} recovered, circuit CLOSED")
            return result
        except Exception as e:
            # Still failing - reopen circuit
            self.failures[key] = self.max_failures
            self.last_attempt[key] = time.time() * 1000

            print(f"❌ {key} retry failed, circuit OPEN again")

            if fallback:
                return fallback()

            raise

    def _queue_failure(
        self,
        key: str,
        fn: Callable,
        fallback: Optional[Callable]
    ) -> None:
        """Queue a failed operation for later retry"""
        if len(self.failure_queue) >= self.failure_queue_size:
            print("⚠️  Failure queue full, dropping oldest entry")
            self.failure_queue.pop(0)

        self.failure_queue.append(QueuedFailure(
            key=key,
            fn=fn,
            fallback=fallback,
            timestamp=time.time(),
            retries=0
        ))

        print(f"📥 Queued {key} for retry (queue size: {len(self.failure_queue)})")

    def process_queue(self) -> None:
        """
        Process queued failures
        Call this periodically (e.g., every 5 minutes)
        """
        if not self.failure_queue:
            return

        print(f"🔄 Processing {len(self.failure_queue)} queued failures...")

        to_process = self.failure_queue.copy()
        self.failure_queue.clear()

        for item in to_process:
            try:
                self.execute(item.key, item.fn, item.fallback)
                print(f"✅ Successfully processed queued {item.key}")
            except Exception:
                # Still failing, requeue if under retry limit
                if item.retries < 3:
                    item.retries += 1
                    self.failure_queue.append(item)
                    print(f"⚠️  {item.key} still failing, requeued (attempt {item.retries}/3)")
                else:
                    print(f"❌ {item.key} exceeded retry limit, dropping")

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker stats"""
        stats = {}

        for key in self.failures.keys():
            stats[key] = {
                'failures': self.failures.get(key, 0),
                'state': self._get_state(key).value,
                'last_attempt': self.last_attempt.get(key, 0)
            }

        return {
            'circuits': stats,
            'queue_size': len(self.failure_queue)
        }

    def reset(self, key: str) -> None:
        """Manually reset a circuit"""
        if key in self.failures:
            del self.failures[key]
        if key in self.last_attempt:
            del self.last_attempt[key]
        print(f"🔄 Reset circuit for {key}")

    def reset_all(self) -> None:
        """Reset all circuits"""
        self.failures.clear()
        self.last_attempt.clear()
        self.failure_queue.clear()
        print("🔄 Reset all circuits")


# Global circuit breaker instance
global_circuit_breaker = CircuitBreaker(
    max_failures=3,
    cooldown_ms=60000,  # 1 minute
    half_open_retries=1,
    failure_queue_size=100
)
