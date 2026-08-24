r"""
A PHP error.

Mirrors `Derafu\BackboneDispatcher\Contract\ProblemDetailInterface`/
`SafeThrowableInterface`. Deliberately does not import `phpy`: these are
plain, immutable data holders, buildable and testable with no PHP
interpreter involved. The `phpy`-aware conversion from a live PHP object
lives in `GenericDispatcher` instead.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SafeThrowable:
    r"""
    A safe, serializable snapshot of a PHP `Throwable`.

    `php_class` (not `class`, a reserved word in Python) is the
    throwable's fully-qualified PHP class name, e.g.
    `"Derafu\\Backbone\\Exception\\PackageNotFoundException"`.
    """

    php_class: str
    code: int
    message: str
    file: str
    line: int
    trace: list
    previous: SafeThrowable | None


@dataclass(frozen=True)
class Problem:
    r"""
    An RFC 7807 (Problem Details) error, without anything HTTP-specific.

    `throwable` is always populated here, unlike PHP's own
    `ProblemDetail::toArray()`, which omits it unless `debug` is on (to
    avoid leaking file paths/stack traces to an untrusted HTTP consumer).
    That gate does not apply to this bridge: `phpy` is an in-process,
    same-machine, trusted boundary, not a public HTTP response, so
    `getThrowable()` (which PHP itself never gates — only its
    serialization does) is read directly regardless of `debug`.

    `debug` is kept here purely as the informational flag PHP reported,
    not as something this class uses to decide anything.
    """

    type: str
    title: str
    detail: str
    instance: str | None
    context: dict
    timestamp: str
    environment: str
    debug: bool
    throwable: SafeThrowable
