from __future__ import annotations

from abmforge.plugins.base import Plugin
from abmforge.plugins.context import PluginContext


class PluginManager:
    """Register, activate, and dispatch hooks to ABMForge plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        self._active: set[str] = set()

    def register(self, plugin: Plugin) -> None:
        """Register a plugin instance."""
        if not isinstance(plugin, Plugin):
            raise TypeError("plugin must be an instance of Plugin")

        if not isinstance(plugin.name, str) or not plugin.name.strip():
            raise ValueError("Plugin name must be a non-empty string")

        if plugin.name in self._plugins:
            raise ValueError(f"Plugin '{plugin.name}' is already registered")

        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> Plugin | None:
        """Remove and return a plugin by name."""
        plugin = self._plugins.get(name)

        if plugin is None:
            return None

        if name in self._active:
            self.deactivate(name)

        return self._plugins.pop(name)

    def get(self, name: str) -> Plugin | None:
        """Return a registered plugin by name."""
        return self._plugins.get(name)

    def plugins(self) -> tuple[Plugin, ...]:
        """Return registered plugins in insertion order."""
        return tuple(self._plugins.values())

    def activate(self, name: str) -> None:
        """Activate a registered plugin."""
        plugin = self._require_plugin(name)

        if name in self._active:
            return

        plugin.activate()
        self._active.add(name)

    def deactivate(self, name: str) -> None:
        """Deactivate a registered plugin."""
        plugin = self._require_plugin(name)

        if name not in self._active:
            return

        plugin.deactivate()
        self._active.remove(name)

    def is_active(self, name: str) -> bool:
        """Return whether a plugin is currently active."""
        self._require_plugin(name)
        return name in self._active

    def emit(self, hook_name: str, context: PluginContext) -> None:
        """Call a named hook on all active plugins in registration order."""
        if not isinstance(hook_name, str) or not hook_name.strip():
            raise ValueError("hook_name must be a non-empty string")

        if not isinstance(context, PluginContext):
            raise TypeError("context must be a PluginContext")

        for name, plugin in self._plugins.items():
            if name not in self._active:
                continue

            hook = getattr(plugin, hook_name, None)

            if hook is None:
                continue

            if not callable(hook):
                raise TypeError(
                    f"Plugin '{name}' hook '{hook_name}' must be callable"
                )

            hook(context)

    def emit_before_experiment(self, context: PluginContext) -> None:
        """Call before-experiment hooks on active plugins."""
        self.emit("before_experiment", context)

    def emit_after_experiment(self, context: PluginContext) -> None:
        """Call after-experiment hooks on active plugins."""
        self.emit("after_experiment", context)

    def _require_plugin(self, name: str) -> Plugin:
        plugin = self.get(name)

        if plugin is None:
            raise KeyError(f"Plugin '{name}' is not registered")

        return plugin