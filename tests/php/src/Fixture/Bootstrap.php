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

use Derafu\BackboneDispatcher\Contract\SafeDispatcherInterface;
use Derafu\BackboneDispatcher\Service\Caster;
use Derafu\BackboneDispatcher\Service\DirectDispatcher;
use Derafu\BackboneDispatcher\Service\FromArrayDeserializer;
use Derafu\BackboneDispatcher\Service\Inspector;
use Derafu\BackboneDispatcher\Service\ObjectFactoryRegistry;
use Derafu\BackboneDispatcher\Service\Resolver;
use Derafu\BackboneDispatcher\Service\SafeDispatcher;
use Derafu\BackboneDispatcher\Service\Serializer;
use Derafu\BackboneDispatcher\Service\TypedDispatcher;
use Derafu\BackboneDispatcher\Service\Validator;
use Invoker\Invoker;

/**
 * Builds a real `SafeDispatcherInterface`, wired by hand (no DI container
 * needed, on purpose: this fixture only exists to give the Python test
 * suite something real to dispatch against, not to exercise DI wiring).
 */
final class Bootstrap
{
    public static function boot(): SafeDispatcherInterface
    {
        $worker = new ExampleWorker();
        $component = new ExampleComponent(['example_worker' => $worker]);
        $package = new ExamplePackage(['example_component' => $component]);

        $registry = new ExamplePackageRegistry();
        $registry->registerPackage('example_package', $package);

        $directDispatcher = new DirectDispatcher(
            $registry,
            new Resolver(
                new Inspector(),
                new Caster(new ObjectFactoryRegistry(fallback: new FromArrayDeserializer())),
                new Validator(),
            ),
            new Invoker(),
        );

        return new SafeDispatcher(
            new TypedDispatcher($directDispatcher),
            new Serializer(),
            'test',
            true,
        );
    }
}
