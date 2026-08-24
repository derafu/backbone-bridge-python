r"""
The outcome of one successful `GenericDispatcher.dispatch()` call.

Deliberately does not import `phpy`: a plain, immutable data holder,
buildable and testable with no PHP interpreter involved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .execution_metadata import ExecutionMetadata


@dataclass(frozen=True)
class OperationResult:
    r"""
    The outcome of one successful operation, value plus metadata.

    Mirrors PHP's `Derafu\BackboneDispatcher\Contract\
    OperationResultInterface`, minus its `problem`: a failed dispatch
    raises a `BackboneBridgeError` (carrying its own `Problem`) instead of
    returning one of these, so there is never a failure case to represent
    here — only ever a successful one.

    `data_type` is the type of `value` before PHP's own
    `SafeDispatcherInterface` serializes it (`get_class()` for an object,
    `gettype()` otherwise) — e.g. `"Derafu\\Certificate\\Certificate"`.
    Never `None` here, unlike the PHP interface: a failure never reaches
    this class at all (see above), so there is no failure case for it to
    be `None` for.
    """

    value: Any
    metadata: ExecutionMetadata
    data_type: str
