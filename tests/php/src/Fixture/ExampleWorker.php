<?php

declare(strict_types=1);

/**
 * Derafu: Backbone Bridge Python - Generic Python Bridge for Backbone Services.
 *
 * Copyright (c) 2026 Esteban De La Fuente Rubio / Derafu <https://www.derafu.dev>
 * Licensed under the MIT License.
 * See LICENSE file for more details.
 */

namespace Derafu\TestsBackboneBridgePython\Fixture;

use Derafu\Backbone\Contract\WorkerInterface;
use Derafu\Backbone\Trait\HandlersAwareTrait;
use Derafu\Backbone\Trait\JobsAwareTrait;
use Derafu\Config\Trait\OptionsAwareTrait;
use RuntimeException;

/**
 * A real worker (uses the actual production traits of `derafu/backbone` and
 * `derafu/config`), with just enough real operations to exercise every kind
 * of outcome the Python side needs to tell apart: success, a resolver
 * failure (missing/invalid parameter), and an unmapped domain failure.
 */
class ExampleWorker implements WorkerInterface
{
    use JobsAwareTrait;
    use HandlersAwareTrait;
    use OptionsAwareTrait;

    public function getId(): int|string
    {
        return 'example_worker';
    }

    public function getName(): string
    {
        return 'Example Worker';
    }

    public function __toString(): string
    {
        return $this->getName();
    }

    /**
     * A required and an optional scalar parameter, to exercise a
     * successful dispatch and, when called with a missing or
     * wrongly-typed `$a`, a `ResolverError` on the Python side.
     */
    public function sum(int $a, int $b = 10): int
    {
        return $a + $b;
    }

    /**
     * An operation that always fails with a plain, unmapped exception, to
     * verify it surfaces as `BackboneBridgeError` (not one of its
     * subclasses) on the Python side.
     */
    public function fail(): never
    {
        throw new RuntimeException('Something went wrong while running the operation.');
    }
}
