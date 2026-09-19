r"""Generic dispatch over any real `SafeDispatcherInterface` PHP object."""

from __future__ import annotations

import os
from typing import Any

import phpy

from ._phpy_conversions import collect, metadata_from_php, problem_from_php
from .exception_registry import ExceptionRegistry
from .exceptions import BootstrapError
from .operation_result import OperationResult


class GenericDispatcher:
    r"""
    Dispatch operations by id through a real `SafeDispatcherInterface`.

    Boots the `SafeDispatcherInterface` itself: includes a PHP autoloader
    and calls a static bootstrap method through `phpy`, so a specific
    library's own bridge never has to import `phpy` at all — it only
    names its own `bootstrap_class`/`bootstrap_method`/`bootstrap_args`,
    and (optionally) where to find its own PHP autoloader.

    Knows nothing about any specific library otherwise: a specific
    library's own bridge subclasses this, pre-wiring its own
    `bootstrap_class` and registering its own domain exceptions on top of
    the ones already known to `self.exceptions`.
    """

    _AUTOLOAD_PATH_ENV = 'BACKBONE_DISPATCHER_AUTOLOAD'
    _OPERATION_REQUEST_CLASS = (
        'Derafu\\BackboneDispatcher\\ValueObject\\OperationRequest'
    )

    def __init__(
        self,
        bootstrap_class: str,
        bootstrap_method: str = 'boot',
        bootstrap_args: tuple[Any, ...] = (),
        exception_registry: ExceptionRegistry | None = None,
        autoload_path: str | None = None,
    ) -> None:
        """
        Boot a real `SafeDispatcherInterface` and wrap it.

        `autoload_path`, if omitted, falls back to the
        `BACKBONE_DISPATCHER_AUTOLOAD` environment variable. Raises
        `ValueError` if neither resolves to a path.

        `bootstrap_args` is passed positionally to `bootstrap_method` via
        `phpy.call()`, with no type checking on either side of that call:
        it must match the exact positional signature the PHP method
        declares, in order. A signature change on the PHP side (an added,
        removed, reordered or retyped parameter) breaks this silently or
        with an opaque error from `phpy`, never a Python-side type error
        caught before the call.
        """
        resolved_path = autoload_path or os.environ.get(
            self._AUTOLOAD_PATH_ENV,
        )
        if resolved_path is None:
            raise ValueError(
                f'No autoload_path resolved: pass it explicitly or set '
                f'the {self._AUTOLOAD_PATH_ENV} environment variable.',
            )

        try:
            phpy.include(resolved_path)
            self._safe_dispatcher = phpy.call(
                f'{bootstrap_class}::{bootstrap_method}',
                *bootstrap_args,
            )
        except Exception as err:
            raise BootstrapError(
                f"Failed to boot '{bootstrap_class}::{bootstrap_method}': "
                f'{err}',
            ) from err

        self.exceptions = (
            exception_registry
            if exception_registry is not None
            else ExceptionRegistry()
        )

    def dispatch(self, operation_id: str, **params: Any) -> OperationResult:
        """
        Dispatch `operation_id` with `params` as keyword parameters.

        `operation_id` has the "package.component.worker::operation" form.
        Returns an `OperationResult` (the operation's own return value
        plus `ExecutionMetadata`) on success. Raises a
        `BackboneBridgeError` (or one of its subclasses, per
        `self.exceptions`) on failure, carrying the same `ExecutionMetadata`
        plus the full `Problem` — this never lets a `phpy` call itself
        fail with an opaque error, since `SafeDispatcherInterface` never
        throws on the PHP side either.
        """
        request = phpy.call(
            f'{self._OPERATION_REQUEST_CLASS}::fromId',
            operation_id,
            params,
        )
        result = self._safe_dispatcher.call('dispatch', request)
        metadata = metadata_from_php(result.call('getMetadata'))

        if result.call('isSuccess'):
            value = collect(result.call('getValue'))
            data_type = str(result.call('getDataType'))

            return OperationResult(
                value=value,
                metadata=metadata,
                data_type=data_type,
            )

        problem = problem_from_php(result.call('getProblem'))
        self.exceptions.raise_for(problem, metadata)
