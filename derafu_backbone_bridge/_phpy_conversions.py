r"""
Shared, `phpy`-aware conversions from live PHP objects to plain dataclasses.

Every function here takes a live `phpy` object/value and returns one of
this package's own `phpy`-free value objects (`Problem`, `SafeThrowable`,
`ExecutionMetadata`) or a plain Python `dict`/`list`/scalar. Kept in one
place so `GenericDispatcher` and `GenericExplorer` never duplicate the
same conversion logic — both need it, since both wrap something that can
fail with a real `ProblemDetailInterface`.
"""

from __future__ import annotations

from typing import Any

import phpy

from .execution_metadata import ExecutionMetadata
from .problem import Problem, SafeThrowable


def collect(value: Any) -> Any:
    """
    Convert a `phpy.Array` to a native Python `dict`/`list`, recursively.

    Anything else PHP could have produced (scalars, `phpy` objects with no
    further array to unwrap) is returned unchanged.
    """
    return value.collect() if isinstance(value, phpy.Array) else value


def metadata_from_php(metadata: Any) -> ExecutionMetadata:
    """Build an `ExecutionMetadata` from a live PHP metadata object."""
    data = collect(metadata.call('toArray'))

    return ExecutionMetadata(
        started_at=data['started_at'],
        finished_at=data['finished_at'],
        timestamp=data['timestamp'],
        real_time=data['real_time'],
        user_time=data['user_time'],
        system_time=data['system_time'],
        memory_used=data['memory_used'],
        peak_memory=data['peak_memory'],
        pid=data['pid'],
        load_average_1min=data['load_average_1_min'],
        load_average_5min=data['load_average_5_min'],
        load_average_15min=data['load_average_15_min'],
    )


def _safe_throwable_from_php(throwable: Any) -> SafeThrowable | None:
    """
    Build a `SafeThrowable` from a live `SafeThrowableInterface`.

    Read through explicit getter calls, not `toArray()`: PHP never gates
    `getThrowable()`/`getPrevious()` behind `isDebug()` — only
    `ProblemDetail::toArray()`'s own serialization does, to avoid leaking
    file paths/stack traces to an untrusted HTTP consumer. That does not
    apply here: `phpy` is an in-process, trusted boundary.
    """
    if throwable is None:
        return None

    return SafeThrowable(
        php_class=str(throwable.call('getClass')),
        code=int(throwable.call('getCode')),
        message=str(throwable.call('getMessage')),
        file=str(throwable.call('getFile')),
        line=int(throwable.call('getLine')),
        trace=collect(throwable.call('getTrace')),
        previous=_safe_throwable_from_php(throwable.call('getPrevious')),
    )


def problem_from_php(problem: Any) -> Problem:
    """Build a `Problem` from a live `ProblemDetailInterface`."""
    instance = problem.call('getInstance')
    throwable = _safe_throwable_from_php(problem.call('getThrowable'))

    return Problem(
        type=str(problem.call('getType')),
        title=str(problem.call('getTitle')),
        detail=str(problem.call('getDetail')),
        instance=str(instance) if instance is not None else None,
        context=collect(problem.call('getContext')),
        timestamp=float(problem.call('getTimestamp')),
        environment=str(problem.call('getEnvironment')),
        debug=bool(problem.call('isDebug')),
        throwable=throwable,
    )
