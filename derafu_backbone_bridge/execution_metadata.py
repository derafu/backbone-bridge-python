r"""
Statistics about one execution.

Mirrors PHP's `Derafu\BackboneDispatcher\Contract\
ExecutionMetadataInterface`. Deliberately does not import `phpy`: this is
a plain, immutable data holder, buildable and testable with no PHP
interpreter involved. The `phpy`-aware conversion from a live PHP object
lives in `GenericDispatcher` instead.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionMetadata:
    r"""
    Assumes Linux/macOS, same as the PHP side: no Windows support.

    `timestamp` is the same moment as `finished_at`, as a Unix epoch
    (seconds since 1970-01-01, sub-second precision) instead of an ISO
    string — kept for flexible reuse (sorting, arithmetic) without having
    to parse `finished_at` back.

    `real_time`/`user_time`/`system_time` are the "real"/"user"/"sys" of
    the `time` command — wall-clock elapsed vs. actual CPU seconds spent.
    `memory_used` is a delta (can be negative, if the garbage collector
    freed more than this execution allocated); `peak_memory` is the whole
    process's peak up to this point, not scoped to only this execution but
    stable against that same GC noise.
    """

    started_at: str
    finished_at: str
    timestamp: float
    real_time: float
    user_time: float
    system_time: float
    memory_used: int
    peak_memory: int
    pid: int
    load_average_1min: float
    load_average_5min: float
    load_average_15min: float
