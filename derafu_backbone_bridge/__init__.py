r"""
Generic Python bridge for any `derafu/backbone`-based PHP library.

Exposed through a real `Derafu\BackboneDispatcher\Contract\
SafeDispatcherInterface` PHP object (booted however that library's own
bridge decides to), via `swoole/phpy`.

This package knows nothing about any specific library. A specific
library's own bridge subclasses `GenericDispatcher`, pre-wiring how its
`SafeDispatcherInterface` is booted and registering its own domain
exceptions on top of the ones already known here.
"""

from .exception_registry import ExceptionRegistry
from .exceptions import (
    BackboneBridgeError,
    BootstrapError,
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
from .generic_dispatcher import GenericDispatcher

__all__ = [
    'BackboneBridgeError',
    'BootstrapError',
    'ClassNotFoundError',
    'ComponentError',
    'ComponentNotFoundError',
    'ExceptionRegistry',
    'FromArrayMethodNotFoundError',
    'GenericDispatcher',
    'HandlerError',
    'HandlerNotFoundError',
    'InvalidOperationIdError',
    'InvalidParameterTypeError',
    'JobError',
    'JobNotFoundError',
    'MissingParameterError',
    'NoDeserializerFoundError',
    'ObjectFactoryError',
    'PackageError',
    'PackageNotFoundError',
    'ResolverError',
    'ServiceError',
    'ServiceNotFoundError',
    'StrategyError',
    'StrategyNotFoundError',
    'WorkerError',
    'WorkerNotFoundError',
]
