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
    """

    value: Any
    metadata: ExecutionMetadata
