"""Bounded request sizing for steps that fan out over Stages.

This module is deliberately pure: no provider, database, or prompt knowledge.
Each step chooses its own limit because the cost of a call differs by step; a
global "batch size" would silently couple unrelated stages of the pipeline.
"""

import asyncio
from collections.abc import Awaitable, Callable, Iterable


def chunked[T](items: Iterable[T], size: int) -> list[list[T]]:
    """Split into consecutive chunks, preserving order.

    A limit below 1 is a programming error, not a request to disable batching:
    silently treating it as "no limit" is how a bounded call becomes unbounded.
    """
    if size < 1:
        raise ValueError("chunk size must be at least 1")
    values = list(items)
    return [values[start : start + size] for start in range(0, len(values), size)]


async def bounded_map[T, R](
    items: list[T],
    operation: Callable[[T], Awaitable[R]],
    *,
    concurrency: int,
) -> list[R]:
    """Map with a fixed concurrency ceiling, returning results in input order.

    Steps used to `gather` every process at once. That is fine for two calls and
    a rate-limit storm for a dozen; the ceiling belongs here, next to the calls,
    not in a global provider semaphore that would couple unrelated steps.
    """
    if concurrency < 1:
        raise ValueError("concurrency must be at least 1")
    limit = asyncio.Semaphore(concurrency)

    async def run(item: T) -> R:
        async with limit:
            return await operation(item)

    return list(await asyncio.gather(*(run(item) for item in items)))
