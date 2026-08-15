"""Registry mapping PHP exception class names to Python exceptions."""

from __future__ import annotations

from typing import NoReturn

from .exceptions import (
    BackboneBridgeError,
    ClassNotFoundError,
    ComponentError,
    ComponentNotFoundError,
    FromArrayMethodNotFoundError,
    HandlerError,
    HandlerNotFoundError,
    InvalidOperationIdError,
    InvalidParameterTypeError,
    JobError,
    JobNotFoundError,
    MissingParameterError,
    NoDeserializerFoundError,
    ObjectFactoryError,
    PackageError,
    PackageNotFoundError,
    ResolverError,
    ServiceError,
    ServiceNotFoundError,
    StrategyError,
    StrategyNotFoundError,
    WorkerError,
    WorkerNotFoundError,
)

# The two namespaces below, spelled out in full, push every entry in
# `_DEFAULT_MAPPING` past the configured line length (a single string key
# plus its value cannot be wrapped by `ruff format`, unlike a call's
# arguments) — so they are factored out into these two short aliases
# instead of shortening the class names themselves, which would make them
# harder to grep for.
_BB = 'Derafu\\Backbone\\Exception\\'
_BD = 'Derafu\\BackboneDispatcher\\Exception\\'

# Every exception class defined by `derafu/backbone` and
# `derafu/backbone-dispatcher` themselves, mapped to its Python mirror. A
# specific library's own domain exceptions are never listed here: each
# bridge built on top of this one registers its own through
# `ExceptionRegistry.register()`.
_DEFAULT_MAPPING: dict[str, type[BackboneBridgeError]] = {
    # `derafu/backbone`: Derafu\Backbone\Exception\*
    _BB + 'ServiceNotFoundException': ServiceNotFoundError,
    _BB + 'PackageNotFoundException': PackageNotFoundError,
    _BB + 'ComponentNotFoundException': ComponentNotFoundError,
    _BB + 'WorkerNotFoundException': WorkerNotFoundError,
    _BB + 'HandlerNotFoundException': HandlerNotFoundError,
    _BB + 'JobNotFoundException': JobNotFoundError,
    _BB + 'StrategyNotFoundException': StrategyNotFoundError,
    _BB + 'ServiceException': ServiceError,
    _BB + 'PackageException': PackageError,
    _BB + 'ComponentException': ComponentError,
    _BB + 'WorkerException': WorkerError,
    _BB + 'HandlerException': HandlerError,
    _BB + 'JobException': JobError,
    _BB + 'StrategyException': StrategyError,
    # `derafu/backbone-dispatcher`: Derafu\BackboneDispatcher\Exception\*
    _BD + 'ResolverException': ResolverError,
    _BD + 'InvalidOperationIdException': InvalidOperationIdError,
    _BD + 'InvalidParameterTypeException': InvalidParameterTypeError,
    _BD + 'MissingParameterException': MissingParameterError,
    _BD + 'ObjectFactoryException': ObjectFactoryError,
    _BD + 'ClassNotFoundException': ClassNotFoundError,
    _BD + 'FromArrayMethodNotFoundException': FromArrayMethodNotFoundError,
    _BD + 'NoDeserializerFoundException': NoDeserializerFoundError,
}


class ExceptionRegistry:
    """
    Map PHP exception class names to the Python exception they raise.

    Starts pre-populated with every exception `derafu/backbone` and
    `derafu/backbone-dispatcher` themselves define. A specific library's
    own bridge extends it with its own domain exceptions through
    `register()`; anything never registered still raises, as
    `BackboneBridgeError`, preserving the original PHP class name in
    `.php_class`.

    Deliberately has no knowledge of `phpy`: it only ever deals in plain
    strings, so it can be tested, and reasoned about, without a PHP
    interpreter involved at all.
    """

    def __init__(self) -> None:
        """Start from a copy of the default, package-provided mapping."""
        self._mapping: dict[str, type[BackboneBridgeError]] = dict(
            _DEFAULT_MAPPING,
        )

    def register(
        self,
        php_class: str,
        exception_class: type[BackboneBridgeError],
    ) -> None:
        """
        Map `php_class` to `exception_class`.

        Overrides any previous mapping already registered for it.
        """
        self._mapping[php_class] = exception_class

    def raise_for(self, php_class: str, message: str) -> NoReturn:
        """
        Raise the Python exception mapped to `php_class`.

        Falls back to `BackboneBridgeError` when nothing is registered
        for it.
        """
        exception_class = self._mapping.get(php_class, BackboneBridgeError)
        raise exception_class(message, php_class)
