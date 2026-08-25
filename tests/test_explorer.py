"""
Real, end-to-end tests for `GenericExplorer`.

Every test explores through a real, booted `SafeExplorerInterface`
(`tests/php/src/Fixture/Bootstrap.php::bootExplorer`) via `phpy` — no mocks
anywhere in the chain.
"""

import pytest

from derafu_backbone_bridge import (
    GenericExplorer,
    InvalidDiscoveryIdError,
    OperationNotFoundError,
    PackageNotFoundError,
)

_PACKAGE = 'example_package'
_COMPONENT = 'example_component'
_WORKER = 'example_worker'
_PATH = f'{_PACKAGE}.{_COMPONENT}.{_WORKER}'


def test_get_packages_lists_the_registered_package(explorer: GenericExplorer):
    """`get_packages()` returns every package the registry holds."""
    packages = explorer.get_packages()

    assert [p['id'] for p in packages] == [_PACKAGE]


def test_get_components_lists_the_packages_components(
    explorer: GenericExplorer,
):
    """`get_components()` returns the named package's components."""
    components = explorer.get_components(_PACKAGE)

    assert [c['id'] for c in components] == [f'{_PACKAGE}.{_COMPONENT}']


def test_get_workers_lists_the_components_workers(explorer: GenericExplorer):
    """`get_workers()` returns the named component's workers."""
    workers = explorer.get_workers(_PACKAGE, _COMPONENT)

    assert [w['id'] for w in workers] == [_PATH]


def test_get_operations_lists_the_workers_operations(
    explorer: GenericExplorer,
):
    """`get_operations()` includes the worker's real operations."""
    operations = explorer.get_operations(_PACKAGE, _COMPONENT, _WORKER)

    names = [o['name'] for o in operations]
    assert 'sum' in names
    assert 'fail' in names


def test_get_package_nests_components_when_asked(explorer: GenericExplorer):
    """`get_package(with_components=True)` nests the package's components."""
    package = explorer.get_package(_PACKAGE, with_components=True)

    assert package['id'] == _PACKAGE
    assert [c['id'] for c in package['components']] == [
        f'{_PACKAGE}.{_COMPONENT}'
    ]


def test_get_component_nests_workers_when_asked(explorer: GenericExplorer):
    """`get_component(with_workers=True)` nests the component's workers."""
    component = explorer.get_component(_PACKAGE, _COMPONENT, with_workers=True)

    assert component['id'] == f'{_PACKAGE}.{_COMPONENT}'
    assert [w['id'] for w in component['workers']] == [_PATH]


def test_get_worker_nests_operations_when_asked(explorer: GenericExplorer):
    """`get_worker(with_operations=True)` nests the worker's operations."""
    worker = explorer.get_worker(
        _PACKAGE,
        _COMPONENT,
        _WORKER,
        with_operations=True,
    )

    assert worker['id'] == _PATH
    names = [o['name'] for o in worker['operations']]
    assert 'sum' in names


def test_get_operation_returns_the_doc_of_exactly_that_operation(
    explorer: GenericExplorer,
):
    """`get_operation()` returns exactly the requested operation's doc."""
    operation = explorer.get_operation(_PACKAGE, _COMPONENT, _WORKER, 'sum')

    assert operation['id'] == f'{_PATH}::sum'
    assert operation['name'] == 'sum'


def test_describe_with_no_id_lists_every_package(explorer: GenericExplorer):
    """`describe(None)` lists every package, same as `get_packages()`."""
    described = explorer.describe()

    assert 'description' in described
    assert [p['id'] for p in described['packages']] == [_PACKAGE]


def test_describe_resolves_a_full_path_to_the_worker(
    explorer: GenericExplorer,
):
    """`describe()` with a full path resolves down to that worker."""
    described = explorer.describe(_PATH)

    assert described['id'] == _PATH


def test_tree_nests_every_level_down_to_operations(explorer: GenericExplorer):
    """`tree()` nests components, workers and operations in one call."""
    tree = explorer.tree()

    assert 'description' in tree
    assert tree['packages'][0]['id'] == _PACKAGE
    component = tree['packages'][0]['components'][0]
    assert component['id'] == f'{_PACKAGE}.{_COMPONENT}'
    worker = component['workers'][0]
    assert worker['id'] == _PATH
    names = [o['name'] for o in worker['operations']]
    assert 'sum' in names


def test_get_components_raises_package_not_found_error(
    explorer: GenericExplorer,
):
    """An unknown package raises `PackageNotFoundError`."""
    with pytest.raises(PackageNotFoundError):
        explorer.get_components('unknown_package')


def test_get_operation_raises_operation_not_found_error(
    explorer: GenericExplorer,
):
    """An unknown operation raises `OperationNotFoundError`."""
    with pytest.raises(OperationNotFoundError):
        explorer.get_operation(_PACKAGE, _COMPONENT, _WORKER, 'doesNotExist')


def test_describe_raises_invalid_discovery_id_error(explorer: GenericExplorer):
    """A malformed discovery id raises `InvalidDiscoveryIdError`."""
    with pytest.raises(InvalidDiscoveryIdError):
        explorer.describe('a.b.c.d')


def test_tree_raises_invalid_discovery_id_error(explorer: GenericExplorer):
    """`tree()` validates its id the same way `describe()` does."""
    with pytest.raises(InvalidDiscoveryIdError):
        explorer.tree('a.b.c.d')
