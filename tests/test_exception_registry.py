"""
Tests for `ExceptionRegistry`.

Deliberately does not use `phpy` or the `dispatcher`/`safe_dispatcher`
fixtures at all: `ExceptionRegistry` only ever deals in plain, phpy-free
`Problem`/`ExecutionMetadata` dataclasses, so it is tested the same way,
with no PHP interpreter involved.
"""

import pytest

from derafu_backbone_bridge import (
    BackboneBridgeError,
    ExceptionRegistry,
    ExecutionMetadata,
    InvalidDiscoveryIdError,
    OperationNotAllowedError,
    OperationNotFoundError,
    PackageNotFoundError,
    Problem,
    SafeThrowable,
)


def _problem(php_class: str, detail: str = 'Oops.') -> Problem:
    """Build a stand-in `Problem` for a given PHP exception class."""
    return Problem(
        type='about:blank',
        title=php_class,
        detail=detail,
        instance=None,
        context={},
        timestamp='2026-01-01T00:00:00+00:00',
        environment='test',
        debug=True,
        throwable=SafeThrowable(
            php_class=php_class,
            code=0,
            message=detail,
            file='/app/src/Service.php',
            line=42,
            trace=[],
            previous=None,
        ),
    )


def _metadata() -> ExecutionMetadata:
    """Build a stand-in `ExecutionMetadata`, values are irrelevant here."""
    return ExecutionMetadata(
        started_at='2026-01-01T00:00:00+00:00',
        finished_at='2026-01-01T00:00:00+00:00',
        real_time=0.0,
        user_time=0.0,
        system_time=0.0,
        memory_used=0,
        peak_memory=0,
        pid=1,
        load_average_1min=0.0,
        load_average_5min=0.0,
        load_average_15min=0.0,
    )


def test_raise_for_uses_the_default_mapping():
    """A PHP class from the default mapping raises its mirrored error."""
    registry = ExceptionRegistry()
    php_class = 'Derafu\\Backbone\\Exception\\PackageNotFoundException'
    problem = _problem(php_class, 'The package billing does not exist.')
    metadata = _metadata()

    with pytest.raises(PackageNotFoundError) as exc_info:
        registry.raise_for(problem, metadata)

    assert str(exc_info.value) == 'The package billing does not exist.'
    assert exc_info.value.php_class == php_class
    assert exc_info.value.problem is problem
    assert exc_info.value.metadata is metadata


@pytest.mark.parametrize(
    ('php_class_name', 'expected_error'),
    [
        ('OperationNotFoundException', OperationNotFoundError),
        ('OperationNotAllowedException', OperationNotAllowedError),
        ('InvalidDiscoveryIdException', InvalidDiscoveryIdError),
    ],
)
def test_raise_for_maps_the_explorer_specific_exceptions(
    php_class_name: str,
    expected_error: type[BackboneBridgeError],
):
    """
    Each raises its own dedicated error, not the generic fallback.

    `OperationNotFoundException`/`OperationNotAllowedException` are also
    reachable through `dispatch()`, via `DirectDispatcher`'s existence and
    policy guards. `InvalidDiscoveryIdException` is reachable only through
    `SafeExplorerInterface::describe()`/`tree()`.
    """
    registry = ExceptionRegistry()
    php_class = f'Derafu\\BackboneDispatcher\\Exception\\{php_class_name}'

    with pytest.raises(expected_error) as exc_info:
        registry.raise_for(_problem(php_class), _metadata())

    assert exc_info.value.php_class == php_class


def test_raise_for_falls_back_to_backbone_bridge_error():
    """An unregistered PHP class raises the generic `BackboneBridgeError`."""
    registry = ExceptionRegistry()
    php_class = 'App\\Exception\\SomeDomainException'

    with pytest.raises(BackboneBridgeError) as exc_info:
        registry.raise_for(_problem(php_class), _metadata())

    assert type(exc_info.value) is BackboneBridgeError
    assert exc_info.value.php_class == php_class


def test_register_adds_a_mapping_for_a_previously_unmapped_class():
    """`register()` makes an unmapped PHP class raise a chosen exception."""

    class DomainError(BackboneBridgeError):
        """A stand-in for a specific library's own domain exception."""

    registry = ExceptionRegistry()
    php_class = 'App\\Exception\\SomeDomainException'
    registry.register(php_class, DomainError)

    with pytest.raises(DomainError):
        registry.raise_for(_problem(php_class), _metadata())


def test_register_overrides_an_existing_mapping():
    """`register()` can also override one of the default mappings."""

    class CustomPackageError(BackboneBridgeError):
        """A stand-in for a caller preferring its own exception here."""

    registry = ExceptionRegistry()
    php_class = 'Derafu\\Backbone\\Exception\\PackageNotFoundException'
    registry.register(php_class, CustomPackageError)

    with pytest.raises(CustomPackageError):
        registry.raise_for(_problem(php_class), _metadata())


def test_register_does_not_affect_other_registry_instances():
    """Each `ExceptionRegistry` instance owns an independent mapping."""
    registered = ExceptionRegistry()
    untouched = ExceptionRegistry()
    php_class = 'App\\Exception\\SomeDomainException'

    class DomainError(BackboneBridgeError):
        """A stand-in for a specific library's own domain exception."""

    registered.register(php_class, DomainError)

    with pytest.raises(BackboneBridgeError) as exc_info:
        untouched.raise_for(_problem(php_class), _metadata())

    assert type(exc_info.value) is BackboneBridgeError


def test_register_with_a_namespace_prefix_groups_every_exception_in_it():
    r"""A key ending in `'\'` catches any class under that namespace."""

    class DomainError(BackboneBridgeError):
        """A stand-in for a specific library's own domain exception."""

    registry = ExceptionRegistry()
    registry.register('App\\Exception\\', DomainError)

    with pytest.raises(DomainError):
        registry.raise_for(
            _problem('App\\Exception\\AnyClassNeverListed'),
            _metadata(),
        )


def test_an_exact_match_wins_over_a_namespace_prefix():
    """A registered exact FQCN takes priority over a broader prefix."""

    class DomainError(BackboneBridgeError):
        """A stand-in for a broad, namespace-wide domain exception."""

    class SpecificError(BackboneBridgeError):
        """A stand-in for one specific, more precisely mapped exception."""

    registry = ExceptionRegistry()
    registry.register('App\\Exception\\', DomainError)
    registry.register('App\\Exception\\SpecificException', SpecificError)

    with pytest.raises(SpecificError):
        registry.raise_for(
            _problem('App\\Exception\\SpecificException'),
            _metadata(),
        )

    with pytest.raises(DomainError):
        registry.raise_for(
            _problem('App\\Exception\\OtherException'),
            _metadata(),
        )


def test_the_longest_matching_prefix_wins():
    """A more specific, longer prefix wins over a broader, shorter one."""

    class BroadError(BackboneBridgeError):
        """A stand-in for a broad, top-level namespace exception."""

    class NarrowError(BackboneBridgeError):
        """A stand-in for a narrower, nested namespace exception."""

    registry = ExceptionRegistry()
    registry.register('App\\', BroadError)
    registry.register('App\\Billing\\', NarrowError)

    with pytest.raises(NarrowError):
        registry.raise_for(
            _problem('App\\Billing\\SomeException'),
            _metadata(),
        )

    with pytest.raises(BroadError):
        registry.raise_for(
            _problem('App\\Other\\SomeException'),
            _metadata(),
        )
