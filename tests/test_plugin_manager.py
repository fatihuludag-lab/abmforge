from __future__ import annotations

import pytest

from abmforge.plugins import Plugin, PluginContext, PluginManager


class ExamplePlugin(Plugin):
    """Minimal plugin used by registry tests."""

    name = "example"
    version = "1.0.0"


def test_plugin_manager_registers_and_returns_plugin() -> None:
    manager = PluginManager()
    plugin = ExamplePlugin()

    manager.register(plugin)

    assert manager.get("example") is plugin
    assert manager.plugins() == (plugin,)


def test_plugin_manager_rejects_duplicate_name() -> None:
    manager = PluginManager()

    manager.register(ExamplePlugin())

    with pytest.raises(
        ValueError,
        match="Plugin 'example' is already registered",
    ):
        manager.register(ExamplePlugin())


def test_plugin_manager_unregisters_plugin() -> None:
    manager = PluginManager()
    plugin = ExamplePlugin()
    manager.register(plugin)

    removed = manager.unregister("example")

    assert removed is plugin
    assert manager.get("example") is None
    assert manager.plugins() == ()


def test_plugin_manager_rejects_plugin_without_name() -> None:
    class NamelessPlugin(Plugin):
        version = "1.0.0"

    manager = PluginManager()

    with pytest.raises(
        ValueError,
        match="Plugin name must be a non-empty string",
    ):
        manager.register(NamelessPlugin())


def test_plugin_manager_rejects_non_plugin_objects() -> None:
    manager = PluginManager()

    with pytest.raises(
        TypeError,
        match="plugin must be an instance of Plugin",
    ):
        manager.register(object())  # type: ignore[arg-type]


def test_plugin_manager_activates_plugin() -> None:
    class ActivatingPlugin(Plugin):
        name = "activate"
        version = "1.0"

        def __init__(self) -> None:
            self.activated = False

        def activate(self) -> None:
            self.activated = True

    manager = PluginManager()
    plugin = ActivatingPlugin()

    manager.register(plugin)
    manager.activate("activate")

    assert plugin.activated is True

def test_plugin_context_stores_extension_state() -> None:
    context = PluginContext(
        experiment="experiment",
        archive="archive",
        metadata={"source": "test"},
    )

    assert context.experiment == "experiment"
    assert context.archive == "archive"
    assert context.scenario is None
    assert context.result is None
    assert context.metadata == {"source": "test"}

def test_plugin_manager_emits_before_experiment_to_active_plugins() -> None:
    calls: list[PluginContext] = []

    class HookPlugin(Plugin):
        name = "hook"
        version = "1.0"

        def before_experiment(self, context: PluginContext) -> None:
            calls.append(context)

    manager = PluginManager()
    plugin = HookPlugin()
    context = PluginContext(experiment="experiment")

    manager.register(plugin)
    manager.activate("hook")
    manager.emit_before_experiment(context)

    assert calls == [context]

def test_plugin_manager_emits_after_experiment_to_active_plugins() -> None:
    calls: list[PluginContext] = []

    class HookPlugin(Plugin):
        name = "after-hook"
        version = "1.0"

        def after_experiment(self, context: PluginContext) -> None:
            calls.append(context)

    manager = PluginManager()
    plugin = HookPlugin()
    context = PluginContext(
        experiment="experiment",
        result="result",
    )

    manager.register(plugin)
    manager.activate("after-hook")
    manager.emit_after_experiment(context)

    assert calls == [context]

def test_plugin_manager_emits_named_hook_to_active_plugins() -> None:
    calls: list[PluginContext] = []

    class HookPlugin(Plugin):
        name = "generic-hook"
        version = "1.0"

        def before_experiment(self, context: PluginContext) -> None:
            calls.append(context)

    manager = PluginManager()
    context = PluginContext(experiment="experiment")

    manager.register(HookPlugin())
    manager.activate("generic-hook")
    manager.emit("before_experiment", context)

    assert calls == [context]

def test_plugin_manager_does_not_emit_to_inactive_plugins() -> None:
    calls: list[str] = []

    class InactivePlugin(Plugin):
        name = "inactive"
        version = "1.0"

        def before_experiment(self, context: PluginContext) -> None:
            calls.append("called")

    manager = PluginManager()
    manager.register(InactivePlugin())

    manager.emit(
        "before_experiment",
        PluginContext(experiment="experiment"),
    )

    assert calls == []


def test_plugin_manager_emits_hooks_in_registration_order() -> None:
    calls: list[str] = []

    class FirstPlugin(Plugin):
        name = "first"
        version = "1.0"

        def before_experiment(self, context: PluginContext) -> None:
            calls.append(self.name)

    class SecondPlugin(Plugin):
        name = "second"
        version = "1.0"

        def before_experiment(self, context: PluginContext) -> None:
            calls.append(self.name)

    manager = PluginManager()
    manager.register(FirstPlugin())
    manager.register(SecondPlugin())
    manager.activate("first")
    manager.activate("second")

    manager.emit(
        "before_experiment",
        PluginContext(experiment="experiment"),
    )

    assert calls == ["first", "second"]