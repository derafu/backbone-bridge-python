r"""
Generic Python bridge for any `derafu/backbone`-based PHP library.

Exposed through real `Derafu\BackboneDispatcher\Contract\
SafeDispatcherInterface`/`SafeExplorerInterface` PHP objects (each booted
however that library's own bridge decides to), via `swoole/phpy`.

This package knows nothing about any specific library. A specific
library's own bridge subclasses `GenericDispatcher`/`GenericExplorer`,
pre-wiring how each is booted and registering its own domain exceptions on
top of the ones already known here.
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
    InvalidDiscoveryIdError,
    InvalidOperationIdError,
    InvalidParameterTypeError,
    JobError,
    JobNotFoundError,
    MissingParameterError,
    NoDeserializerFoundError,
    ObjectFactoryError,
    OperationNotAllowedError,
    OperationNotFoundError,
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
from .execution_metadata import ExecutionMetadata
from .generic_dispatcher import GenericDispatcher
from .generic_explorer import GenericExplorer
from .operation_result import OperationResult
from .problem import Problem, SafeThrowable

__all__ = [
    'BackboneBridgeError',
    'BootstrapError',
    'ClassNotFoundError',
    'ComponentError',
    'ComponentNotFoundError',
    'ExceptionRegistry',
    'ExecutionMetadata',
    'FromArrayMethodNotFoundError',
    'GenericDispatcher',
    'GenericExplorer',
    'HandlerError',
    'HandlerNotFoundError',
    'InvalidDiscoveryIdError',
    'InvalidOperationIdError',
    'InvalidParameterTypeError',
    'JobError',
    'JobNotFoundError',
    'MissingParameterError',
    'NoDeserializerFoundError',
    'ObjectFactoryError',
    'OperationNotAllowedError',
    'OperationNotFoundError',
    'OperationResult',
    'PackageError',
    'PackageNotFoundError',
    'Problem',
    'ResolverError',
    'SafeThrowable',
    'ServiceError',
    'ServiceNotFoundError',
    'StrategyError',
    'StrategyNotFoundError',
    'WorkerError',
    'WorkerNotFoundError',
]
