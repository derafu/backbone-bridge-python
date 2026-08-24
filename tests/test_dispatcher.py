"""
Real, end-to-end tests for `GenericDispatcher`.

Every test dispatches through a real, booted `SafeDispatcherInterface`
(`tests/php/src/Fixture/Bootstrap.php`) via `phpy` — no mocks anywhere in
the chain.
"""

import pytest

from derafu_backbone_bridge import (
    BackboneBridgeError,
    BootstrapError,
    ComponentNotFoundError,
    GenericDispatcher,
    MissingParameterError,
    PackageNotFoundError,
    WorkerNotFoundError,
)
from derafu_backbone_bridge.exceptions import (
    InvalidParameterTypeError,
)

_WORKER = 'example_package.example_component.example_worker'


def test_missing_autoload_path_raises_value_error(
    monkeypatch,
    bootstrap_class,
):
    """No `autoload_path` and no env var set raises `ValueError`."""
    monkeypatch.delenv('BACKBONE_DISPATCHER_AUTOLOAD', raising=False)

    with pytest.raises(ValueError, match='BACKBONE_DISPATCHER_AUTOLOAD'):
        GenericDispatcher(bootstrap_class)


def test_falls_back_to_the_autoload_path_env_var(
    monkeypatch,
    bootstrap_class,
    autoload_path,
):
    """An omitted `autoload_path` falls back to the env var."""
    a, b = 5, 7
    monkeypatch.setenv('BACKBONE_DISPATCHER_AUTOLOAD', autoload_path)
    dispatcher = GenericDispatcher(bootstrap_class)

    result = dispatcher.dispatch(f'{_WORKER}::sum', a=a, b=b)

    assert result.value == a + b


def test_raises_bootstrap_error_when_the_bootstrap_method_is_wrong(
    bootstrap_class,
    autoload_path,
):
    """A boot failure raises `BootstrapError`, not a raw `phpy` one."""
    with pytest.raises(BootstrapError):
        GenericDispatcher(
            bootstrap_class,
            bootstrap_method='not_a_real_method',
            autoload_path=autoload_path,
        )


def test_dispatch_returns_the_operations_value_on_success(dispatcher):
    """A successful dispatch returns the operation's own return value."""
    a, b = 5, 7
    result = dispatcher.dispatch(f'{_WORKER}::sum', a=a, b=b)

    assert result.value == a + b


def test_dispatch_returns_real_execution_metadata_on_success(dispatcher):
    """A successful dispatch's metadata reflects a real measurement."""
    result = dispatcher.dispatch(f'{_WORKER}::sum', a=5, b=7)

    metadata = result.metadata
    assert metadata.real_time >= 0.0
    assert metadata.user_time >= 0.0
    assert metadata.system_time >= 0.0
    assert metadata.peak_memory > 0
    assert metadata.pid > 0
    assert metadata.load_average_1min >= 0.0


def test_dispatch_uses_the_operations_own_default_parameters(dispatcher):
    """An omitted optional parameter falls back to the PHP default."""
    a, default_b = 5, 10
    result = dispatcher.dispatch(f'{_WORKER}::sum', a=a)

    assert result.value == a + default_b


def test_dispatch_raises_missing_parameter_error(dispatcher):
    """A missing required parameter raises `MissingParameterError`."""
    with pytest.raises(MissingParameterError):
        dispatcher.dispatch(f'{_WORKER}::sum')


def test_dispatch_raises_invalid_parameter_type_error(dispatcher):
    """A wrongly-typed parameter raises `InvalidParameterTypeError`."""
    with pytest.raises(InvalidParameterTypeError):
        dispatcher.dispatch(f'{_WORKER}::sum', a=['not', 'an', 'int'])


def test_dispatch_raises_package_not_found_error(dispatcher):
    """An unknown package raises `PackageNotFoundError`."""
    with pytest.raises(PackageNotFoundError):
        dispatcher.dispatch('unknown_package.x.y::z')


def test_dispatch_raises_component_not_found_error(dispatcher):
    """An unknown component raises `ComponentNotFoundError`."""
    with pytest.raises(ComponentNotFoundError):
        dispatcher.dispatch('example_package.unknown_component.y::z')


def test_dispatch_raises_worker_not_found_error(dispatcher):
    """An unknown worker raises `WorkerNotFoundError`."""
    with pytest.raises(WorkerNotFoundError):
        dispatcher.dispatch(
            'example_package.example_component.unknown_worker::z',
        )


def test_dispatch_raises_backbone_bridge_error_for_an_unmapped_exception(
    dispatcher,
):
    """
    An operation's own, unmapped exception raises `BackboneBridgeError`.

    Not one of its subclasses: nothing in `ExceptionRegistry`'s default
    mapping recognizes a plain `RuntimeException`, and this bridge does not
    invent a mapping for a specific library's own domain exceptions.
    """
    with pytest.raises(BackboneBridgeError) as exc_info:
        dispatcher.dispatch(f'{_WORKER}::fail')

    assert exc_info.value.php_class == 'RuntimeException'
    assert type(exc_info.value) is BackboneBridgeError


def test_dispatch_failure_carries_the_real_problem_and_metadata(dispatcher):
    """A failed dispatch's exception carries a real `Problem`/metadata."""
    with pytest.raises(BackboneBridgeError) as exc_info:
        dispatcher.dispatch(f'{_WORKER}::fail')

    problem = exc_info.value.problem
    assert problem.detail == (
        'Something went wrong while running the operation.'
    )
    assert problem.instance == f'{_WORKER}::fail'
    assert problem.throwable.php_class == 'RuntimeException'
    assert problem.throwable.previous is None

    metadata = exc_info.value.metadata
    assert metadata.real_time >= 0.0
    assert metadata.pid > 0


def test_register_lets_a_caller_add_its_own_exception_mapping(dispatcher):
    """`exceptions.register()` overrides what a PHP class raises."""

    class DomainSpecificError(BackboneBridgeError):
        """A stand-in for a specific library's own domain exception."""

    dispatcher.exceptions.register('RuntimeException', DomainSpecificError)

    with pytest.raises(DomainSpecificError):
        dispatcher.dispatch(f'{_WORKER}::fail')
