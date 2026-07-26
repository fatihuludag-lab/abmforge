from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from abmforge.plugins.context import PluginContext


class Plugin:
    """Base class for ABMForge plugins."""

    name: str = ""
    version: str = ""

    def activate(self) -> None:
        """Activate the plugin."""

    def deactivate(self) -> None:
        """Deactivate the plugin."""

    def before_experiment(self, context: PluginContext) -> None:
        """Run before an experiment begins."""

    def after_experiment(self, context: PluginContext) -> None:
        """Run after an experiment finishes."""
