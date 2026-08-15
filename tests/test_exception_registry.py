"""
Tests for `ExceptionRegistry`.

Deliberately does not use `phpy` or the `dispatcher`/`safe_dispatcher`
fixtures at all: `ExceptionRegistry` only ever deals in plain strings, so
it is tested the same way, with no PHP interpreter involved.
"""

import pytest

from derafu_backbone_bridge import (
    BackboneBridgeError,
    ExceptionRegistry,
    PackageNotFoundError,
)


def test_raise_for_uses_the_default_mapping():
    """A PHP class from the default mapping raises its mirrored error."""
    registry = ExceptionRegistry()

    with pytest.raises(PackageNotFoundError) as exc_info:
        registry.raise_for(
            'Derafu\\Backbone\\Exception\\PackageNotFoundException',
            'The package billing does not exist.',
        )

    assert str(exc_info.value) == 'The package billing does not exist.'
    php_class = 'Derafu\\Backbone\\Exception\\PackageNotFoundException'
    assert exc_info.value.php_class == php_class


def test_raise_for_falls_back_to_backbone_bridge_error():
    """An unregistered PHP class raises the generic `BackboneBridgeError`."""
    registry = ExceptionRegistry()

    with pytest.raises(BackboneBridgeError) as exc_info:
        registry.raise_for('App\\Exception\\SomeDomainException', 'Oops.')

    assert type(exc_info.value) is BackboneBridgeError
    assert exc_info.value.php_class == 'App\\Exception\\SomeDomainException'


def test_register_adds_a_mapping_for_a_previously_unmapped_class():
    """`register()` makes an unmapped PHP class raise a chosen exception."""

    class DomainError(BackboneBridgeError):
        """A stand-in for a specific library's own domain exception."""

    registry = ExceptionRegistry()
    registry.register('App\\Exception\\SomeDomainException', DomainError)

    with pytest.raises(DomainError):
        registry.raise_for('App\\Exception\\SomeDomainException', 'Oops.')


def test_register_overrides_an_existing_mapping():
    """`register()` can also override one of the default mappings."""

    class CustomPackageError(BackboneBridgeError):
        """A stand-in for a caller preferring its own exception here."""

    registry = ExceptionRegistry()
    php_class = 'Derafu\\Backbone\\Exception\\PackageNotFoundException'
    registry.register(php_class, CustomPackageError)

    with pytest.raises(CustomPackageError):
        registry.raise_for(php_class, 'The package billing does not exist.')


def test_register_does_not_affect_other_registry_instances():
    """Each `ExceptionRegistry` instance owns an independent mapping."""
    registered = ExceptionRegistry()
    untouched = ExceptionRegistry()

    class DomainError(BackboneBridgeError):
        """A stand-in for a specific library's own domain exception."""

    registered.register('App\\Exception\\SomeDomainException', DomainError)

    with pytest.raises(BackboneBridgeError) as exc_info:
        untouched.raise_for('App\\Exception\\SomeDomainException', 'Oops.')

    assert type(exc_info.value) is BackboneBridgeError
