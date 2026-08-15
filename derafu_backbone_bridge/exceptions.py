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


class BackboneBridgeError(Exception):
    """
    Base exception for an error `SafeDispatcher` caught on the PHP side.

    Always carries the original PHP exception's fully-qualified class name
    in `php_class`, so callers can still discriminate on it even when no
    dedicated subclass exists for it.
    """

    def __init__(self, message: str, php_class: str) -> None:
        """Store the message and the originating PHP exception class."""
        super().__init__(message)
        self.php_class = php_class


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
# ResolverException and its subclasses. Raised while resolving and
# validating the parameters of an operation before invoking it.
class ResolverError(BackboneBridgeError):
    """An operation's parameters could not be resolved."""


class InvalidOperationIdError(ResolverError):
    """Operation id does not match "package.component.worker:operation"."""


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
