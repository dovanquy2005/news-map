"""Distributed locking abstraction for scheduler and singleton worker execution.

Strictly complies with:
- docs/03-backend-architecture.md (Transaction rules, Idempotency)
- tasks/TASK-005-redis-queue-foundation.md
"""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from typing import Generator, Optional

import redis

from backend.app.common.cache.redis import get_redis_client

LOCK_PREFIX = "vnm:lock:"

# Safe unlock Lua script: only delete key if the stored value matches the unique holder token
RELEASE_LOCK_LUA = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


class LockAcquisitionError(Exception):
    """Raised when acquiring a distributed lock fails within the timeout window."""

    pass


class DistributedLock:
    """OOP Distributed lock abstraction wrapping Redis SET NX EX."""

    def __init__(
        self,
        client: Optional[redis.Redis] = None,
        lock_key: str = "vnm:lock:default",
        ttl_seconds: int = 30,
    ) -> None:
        self.client = client or get_redis_client()
        self.lock_key = lock_key if lock_key.startswith("vnm:lock:") else f"{LOCK_PREFIX}{lock_key}"
        self.ttl_seconds = ttl_seconds
        self.token = str(uuid.uuid4())
        self._acquired = False

    def acquire(self) -> bool:
        """Attempt to acquire lock once."""
        ok = bool(self.client.set(self.lock_key, self.token, ex=self.ttl_seconds, nx=True))
        self._acquired = ok
        return ok

    def release(self) -> bool:
        """Release lock safely using Lua token check."""
        if not self._acquired:
            return False
        try:
            res = self.client.eval(RELEASE_LOCK_LUA, 1, self.lock_key, self.token)
            self._acquired = False
            return bool(res)
        except Exception:
            return False


@contextmanager
def redis_distributed_lock(
    resource_name: str,
    lease_seconds: int = 30,
    timeout_seconds: float = 5.0,
    client: Optional[redis.Redis] = None,
) -> Generator[str, None, None]:
    """Context manager granting exclusive distributed lock on a named resource.

    Args:
        resource_name: Unique identifier for the shared lock.
        lease_seconds: Automatic lock expiration TTL to prevent permanent deadlocks.
        timeout_seconds: Maximum time to wait attempting to acquire the lock.
        client: Optional Redis client.

    Yields:
        token: Unique UUID string representing lock ownership.

    Raises:
        LockAcquisitionError: If the lock cannot be acquired within timeout_seconds.
    """
    redis_client = client or get_redis_client()
    lock_key = f"{LOCK_PREFIX}{resource_name}"
    token = str(uuid.uuid4())

    start_time = time.perf_counter()
    acquired = False

    while (time.perf_counter() - start_time) < timeout_seconds:
        # Atomic set-if-not-exists with expiration
        if redis_client.set(lock_key, token, ex=lease_seconds, nx=True):
            acquired = True
            break
        time.sleep(0.05)

    if not acquired:
        raise LockAcquisitionError(
            f"Failed to acquire distributed lock for '{resource_name}' within {timeout_seconds}s"
        )

    try:
        yield token
    finally:
        # Release lock strictly if token matches
        try:
            redis_client.eval(RELEASE_LOCK_LUA, 1, lock_key, token)
        except Exception:
            pass
