r"""
Python-native exceptions raised for errors coming from the PHP side.

Mirrors the exception hierarchy of `derafu/backbone` and
`derafu/backbone-dispatcher` one level deep: every PHP exception class in
those two packages has a matching Python class here, under the same parent
relationship, so callers can catch broadly (e.g. `ServiceNotFoundError` for
any "not found" case) or narrowly (e.g. `PackageNotFoundError`) exactly as
they would on the PHP side.

A specific library's own domain exceptions are not, and should not be,
listed here: they are registered by that library's own bridge package
through `ExceptionRegistry.register()`.
"""

from __future__ import annotations

from .execution_metadata import ExecutionMetadata
from .problem import Problem


class BackboneBridgeError(Exception):
    """
    Base exception for an error caught on the PHP side.

    Always carries the full `Problem` that caused it (in `problem`) — a
    real failure, from either `SafeDispatcherInterface` or
    `SafeExplorerInterface`, always produces one on the PHP side.
    `metadata` is `None` unless the failure came from
    `SafeDispatcherInterface::dispatch()`: `SafeExplorerInterface` does
    not measure `ExecutionMetadata` (yet), so there is honestly none to
    carry for a failed `GenericExplorer` call.

    `php_class` is not stored separately: it would only duplicate
    `problem.throwable.php_class`, so it is exposed as a read-only
    shortcut to that instead.
    """

    def __init__(
        self,
        problem: Problem,
        metadata: ExecutionMetadata | None = None,
    ) -> None:
        """Store the problem and, when there is one, the execution metadata."""
        super().__init__(problem.detail)
        self.problem = problem
        self.metadata = metadata

    @property
    def php_class(self) -> str:
        """The fully-qualified PHP class name of the original exception."""
        return self.problem.throwable.php_class


# `derafu/backbone`: Derafu\Backbone\Exception\ServiceNotFoundException and
# its subclasses. Raised when a package, component, worker, handler, job or
# strategy is looked up by a name that is not registered.
class ServiceNotFoundError(BackboneBridgeError):
    """A package, component, worker, handler, job or strategy is missing."""


class PackageNotFoundError(ServiceNotFoundError):
    """The named package does not exist."""


class ComponentNotFoundError(ServiceNotFoundError):
    """The named component does not exist in its package."""


class WorkerNotFoundError(ServiceNotFoundError):
    """The named worker does not exist in its component."""


class HandlerNotFoundError(ServiceNotFoundError):
    """The named handler does not exist."""


class JobNotFoundError(ServiceNotFoundError):
    """The named job does not exist."""


class StrategyNotFoundError(ServiceNotFoundError):
    """The named strategy does not exist."""


# `derafu/backbone`: Derafu\Backbone\Exception\ServiceException and its
# subclasses. Raised for errors that are not about a missing name, but about
# how a package, component, worker, handler, job or strategy misbehaves.
class ServiceError(BackboneBridgeError):
    """A package, component, worker, handler, job or strategy failed."""


class PackageError(ServiceError):
    """A package failed."""


class ComponentError(ServiceError):
    """A component failed."""


class WorkerError(ServiceError):
    """A worker failed."""


class HandlerError(ServiceError):
    """A handler failed."""


class JobError(ServiceError):
    """A job failed."""


class StrategyError(ServiceError):
    """A strategy failed."""


# `derafu/backbone-dispatcher`: Derafu\BackboneDispatcher\Exception\
# InvalidOperationIdException. Unrelated to ResolverException: raised while
# parsing the operation id itself, before any package/component/worker has
# even been identified.
class InvalidOperationIdError(BackboneBridgeError):
    """Operation id does not match "package.component.worker::operation"."""


# `derafu/backbone-dispatcher`: Derafu\BackboneDispatcher\Exception\
# OperationNotFoundException. Raised when an operation does not exist as a
# public method of the targeted worker, regardless of which
# OperationPolicyInterface is active — whether it exists is a fact about
# the worker, not a policy decision.
class OperationNotFoundError(BackboneBridgeError):
    """The named operation does not exist on its worker."""


# `derafu/backbone-dispatcher`: Derafu\BackboneDispatcher\Exception\
# OperationNotAllowedException. Raised when an operation exists but the
# active OperationPolicyInterface rejects it.
class OperationNotAllowedError(BackboneBridgeError):
    """The named operation exists but the active policy rejects it."""


# `derafu/backbone-dispatcher`: Derafu\BackboneDispatcher\Exception\
# InvalidDiscoveryIdException. Raised by ExplorerInterface (and
# SafeExplorerInterface's describe()/tree()) for a discovery id that does
# not match "package[.component[.worker[::operation]]]".
class InvalidDiscoveryIdError(BackboneBridgeError):
    """Discovery id does not match "package[.component[.worker[::op]]]"."""


# `derafu/backbone-dispatcher`: Derafu\BackboneDispatcher\Exception\
# ResolverException and its subclasses. Raised while resolving and
# validating the parameters of an operation that has already been
# identified.
class ResolverError(BackboneBridgeError):
    """An operation's parameters could not be resolved."""


class InvalidParameterTypeError(ResolverError):
    """A parameter has the wrong type for the operation being invoked."""


class MissingParameterError(ResolverError):
    """A required parameter is missing."""


# `derafu/backbone-dispatcher`: Derafu\BackboneDispatcher\Exception\
# ObjectFactoryException and its subclasses. Raised while deserializing
# array/string data into the object an operation's parameter expects.
class ObjectFactoryError(BackboneBridgeError):
    """A parameter's data could not be turned into the object it needs."""


class ClassNotFoundError(ObjectFactoryError):
    """The `fromArray()` deserialization target class does not exist."""


class FromArrayMethodNotFoundError(ObjectFactoryError):
    """The deserialization target class has no `fromArray()` method."""


class NoDeserializerFoundError(ObjectFactoryError):
    """No registered or fallback deserializer could build the class."""


class BootstrapError(Exception):
    """
    The underlying PHP failed to boot.

    Unlike `BackboneBridgeError` and its subclasses, this does not mirror
    any specific PHP exception caught by a `SafeDispatcherInterface`: it
    is raised for anything that goes wrong before one even exists (a
    missing autoloader, a broken dependency, a bootstrap class or method
    that does not exist), so it carries no `php_class`.
    """
