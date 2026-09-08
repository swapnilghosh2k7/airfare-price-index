"""Domain-aware rate limiter supporting async and sync workflows with randomized jitter.
"""
import asyncio
import logging
import random
import time
import urllib.parse
from typing import Dict

logger = logging.getLogger("scraper.rate_limiter")


class RateLimiter:
    """Thread-safe and asyncio-friendly per-domain rate limiter."""

    def __init__(self, min_delay: float = 2.0, max_delay: float = 4.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request_times: Dict[str, float] = {}
        self._async_locks: Dict[str, asyncio.Lock] = {}

    def _extract_domain(self, target: str) -> str:
        if "://" in target:
            parsed = urllib.parse.urlparse(target)
            return parsed.netloc.lower() or target.lower()
        return target.lower()

    def _get_async_lock(self, domain: str) -> asyncio.Lock:
        if domain not in self._async_locks:
            self._async_locks[domain] = asyncio.Lock()
        return self._async_locks[domain]

    def _calculate_delay(self, domain: str) -> float:
        now = time.time()
        last = self._last_request_times.get(domain, 0.0)
        elapsed = now - last
        target_delay = random.uniform(self.min_delay, self.max_delay)
        wait_time = max(0.0, target_delay - elapsed)
        return wait_time

    async def acquire_async(self, target: str) -> float:
        """Asynchronously wait until domain rate-limit delay has elapsed."""
        domain = self._extract_domain(target)
        lock = self._get_async_lock(domain)
        async with lock:
            wait_time = self._calculate_delay(domain)
            if wait_time > 0:
                logger.debug("Rate limiting [%s]: pausing for %.2fs", domain, wait_time)
                await asyncio.sleep(wait_time)
            self._last_request_times[domain] = time.time()
            return wait_time

    def acquire_sync(self, target: str) -> float:
        """Synchronously wait until domain rate-limit delay has elapsed."""
        domain = self._extract_domain(target)
        wait_time = self._calculate_delay(domain)
        if wait_time > 0:
            logger.debug("Rate limiting [%s]: pausing for %.2fs", domain, wait_time)
            time.sleep(wait_time)
        self._last_request_times[domain] = time.time()
        return wait_time


# Shared default instance
default_rate_limiter = RateLimiter(min_delay=2.0, max_delay=4.0)


async def limit_rate(target: str, min_delay: float = 2.0, max_delay: float = 4.0) -> float:
    """Async convenience helper for rate limiting."""
    if min_delay != default_rate_limiter.min_delay or max_delay != default_rate_limiter.max_delay:
        limiter = RateLimiter(min_delay=min_delay, max_delay=max_delay)
        return await limiter.acquire_async(target)
    return await default_rate_limiter.acquire_async(target)
