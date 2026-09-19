r"""Generic exploration over any real `SafeExplorerInterface` PHP object."""

from __future__ import annotations

import os
from typing import Any

import phpy

from ._phpy_conversions import collect, problem_from_php
from .exception_registry import ExceptionRegistry
from .exceptions import BootstrapError


class GenericExplorer:
    r"""
    Explore a package tree through a real `SafeExplorerInterface`.

    Boots the `SafeExplorerInterface` itself, the same way `GenericDispatcher`
    boots a `SafeDispatcherInterface`: includes a PHP autoloader and calls a
    static bootstrap method through `phpy`, so a specific library's own
    bridge never has to import `phpy` at all — it only names its own
    `bootstrap_class`/`bootstrap_method`/`bootstrap_args`, and (optionally)
    where to find its own PHP autoloader.

    Every method mirrors one of `SafeExplorerInterface`'s, one to one:
    never raises an opaque error, since `SafeExplorerInterface` never
    throws on the PHP side either — a failure comes back as a
    `DiscoveryResultInterface` whose problem this class turns into the
    matching `BackboneBridgeError` subclass instead.

    Knows nothing about any specific library otherwise: a specific
    library's own bridge subclasses this, pre-wiring its own
    `bootstrap_class` and registering its own domain exceptions on top of
    the ones already known to `self.exceptions`.
    """

    _AUTOLOAD_PATH_ENV = 'BACKBONE_DISPATCHER_AUTOLOAD'

    def __init__(
        self,
        bootstrap_class: str,
        bootstrap_method: str = 'boot',
        bootstrap_args: tuple[Any, ...] = (),
        exception_registry: ExceptionRegistry | None = None,
        autoload_path: str | None = None,
    ) -> None:
        """
        Boot a real `SafeExplorerInterface` and wrap it.

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
            self._safe_explorer = phpy.call(
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

    def get_packages(self) -> Any:
        """Return every package, as `ExplorerInterface.getPackages()` would."""
        return self._unwrap(self._safe_explorer.call('getPackages'))

    def get_components(self, package: str) -> Any:
        """Return `package`'s components."""
        return self._unwrap(self._safe_explorer.call('getComponents', package))

    def get_workers(self, package: str, component: str) -> Any:
        """Return `component`'s workers."""
        return self._unwrap(
            self._safe_explorer.call('getWorkers', package, component),
        )

    def get_operations(self, package: str, component: str, worker: str) -> Any:
        """Return `worker`'s operations."""
        return self._unwrap(
            self._safe_explorer.call(
                'getOperations',
                package,
                component,
                worker,
            ),
        )

    def get_package(self, package: str, with_components: bool = False) -> Any:
        """Return `package`'s own data, nesting its components if asked."""
        return self._unwrap(
            self._safe_explorer.call('getPackage', package, with_components),
        )

    def get_component(
        self,
        package: str,
        component: str,
        with_workers: bool = False,
    ) -> Any:
        """Return `component`'s own data, nesting its workers if asked."""
        return self._unwrap(
            self._safe_explorer.call(
                'getComponent',
                package,
                component,
                with_workers,
            ),
        )

    def get_worker(
        self,
        package: str,
        component: str,
        worker: str,
        with_operations: bool = False,
    ) -> Any:
        """Return `worker`'s own data, nesting its operations if asked."""
        return self._unwrap(
            self._safe_explorer.call(
                'getWorker',
                package,
                component,
                worker,
                with_operations,
            ),
        )

    def get_operation(
        self,
        package: str,
        component: str,
        worker: str,
        operation: str,
    ) -> Any:
        """Return the doc of exactly `operation`."""
        return self._unwrap(
            self._safe_explorer.call(
                'getOperation',
                package,
                component,
                worker,
                operation,
            ),
        )

    def describe(self, discovery_id: str | None = None) -> Any:
        """
        Resolve a discovery id to whichever level it names.

        `discovery_id` has the "package[.component[.worker[::operation]]]"
        form. `None` (or omitted) lists every package.
        """
        return self._unwrap(self._safe_explorer.call('describe', discovery_id))

    def tree(self, discovery_id: str | None = None) -> Any:
        """Resolve like `describe()`, nesting every level's children."""
        return self._unwrap(self._safe_explorer.call('tree', discovery_id))

    def _unwrap(self, result: Any) -> Any:
        """
        Turn a `DiscoveryResultInterface` into its value, or raise.

        Raises a `BackboneBridgeError` (or one of its subclasses, per
        `self.exceptions`) when `result` is a failure — this never lets a
        `phpy` call itself fail with an opaque error, since
        `SafeExplorerInterface` never throws on the PHP side either. No
        `ExecutionMetadata` comes with it: `SafeExplorerInterface` does
        not measure one (yet), unlike `SafeDispatcherInterface`.
        """
        if result.call('isSuccess'):
            return collect(result.call('getValue'))

        self.exceptions.raise_for(problem_from_php(result.call('getProblem')))
