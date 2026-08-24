"""
Shared pytest fixtures: boot the real PHP fixture chain for every test.

Requires `phpy` (only available inside the `docker-python3.14-caddy-server`
container built with `PHPY_ENABLED=true`) and the fixture's own Composer
dependencies installed under `tests/php/vendor` (`composer install` inside
`tests/php`).
"""

import os

import pytest

from derafu_backbone_bridge import GenericDispatcher, GenericExplorer

_AUTOLOAD_PATH = os.path.join(
    os.path.dirname(__file__),
    'php',
    'vendor',
    'autoload.php',
)
_BOOTSTRAP_CLASS = 'Derafu\\TestsBackboneBridgePython\\Fixture\\Bootstrap'


@pytest.fixture
def dispatcher():
    """Build a fresh `GenericDispatcher`, wrapping a freshly booted fixture."""
    return GenericDispatcher(_BOOTSTRAP_CLASS, autoload_path=_AUTOLOAD_PATH)


@pytest.fixture
def explorer():
    """Build a fresh `GenericExplorer`, wrapping a freshly booted fixture."""
    return GenericExplorer(
        _BOOTSTRAP_CLASS,
        bootstrap_method='bootExplorer',
        autoload_path=_AUTOLOAD_PATH,
    )


@pytest.fixture
def autoload_path():
    """Expose the real fixture chain's `vendor/autoload.php` path."""
    return _AUTOLOAD_PATH


@pytest.fixture
def bootstrap_class():
    """Expose the real fixture chain's `Bootstrap` class name."""
    return _BOOTSTRAP_CLASS
