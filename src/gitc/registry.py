# Copyright (c) 2026 Roman Stepanov
# SPDX-License-Identifier: MIT
"""Plugin registry and autoloading system."""

from __future__ import annotations

import importlib
import importlib.util
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Pattern

from importlib.metadata import entry_points

from gitc.context import CommandContext

Handler = Callable[[re.Match[str], CommandContext], str | list[str]]


@dataclass(frozen=True)
class PluginRule:
    """Represents a registered plugin rule."""

    name: str
    pattern: Pattern[str]
    handler: Handler
    priority: int = 100


class PluginRegistry:
    """Registry for plugin rules and handlers."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self._rules: list[PluginRule] = []

    def register(
        self,
        *,
        name: str,
        pattern: str,
        handler: Handler,
        priority: int = 100,
    ) -> None:
        """
        Register a new plugin rule.

        Args:
            name: Plugin name
            pattern: Regex pattern to match (uses fullmatch)
            handler: Callable that processes the match
            priority: Lower values are processed first
        """
        compiled = re.compile(pattern)
        self._rules.append(
            PluginRule(name=name, pattern=compiled, handler=handler, priority=priority)
        )
        self._rules.sort(key=lambda r: r.priority)

    def transform_argv(self, argv: list[str], ctx: CommandContext) -> list[str]:
        """
        Transform command-line arguments by applying plugin rules.

        Args:
            argv: Original command-line arguments
            ctx: Command context

        Returns:
            Transformed arguments

        Raises:
            KeyboardInterrupt: If a plugin cancels the operation
        """
        out: list[str] = []
        for arg in argv:
            replaced = False
            for rule in self._rules:
                m = rule.pattern.fullmatch(arg)
                if not m:
                    continue

                if ctx.debug:
                    print(f"gitc: plugin '{rule.name}' activated by arg={arg!r}")

                res = rule.handler(m, ctx)
                if isinstance(res, list):
                    out.extend(res)
                else:
                    out.append(res)

                replaced = True
                break

            if not replaced:
                out.append(arg)

        return out


def autoload_plugins(
    reg: PluginRegistry,
    *,
    debug: bool = False,
    extra_plugin_dirs: list[str] | None = None,
) -> None:
    """
    Autoload plugins from entry points and plugin directories.

    Args:
        reg: PluginRegistry to populate
        debug: Enable debug output
        extra_plugin_dirs: Additional directories to search for plugins
    """
    # --- 0) Built-in plugins ---
    try:
        from gitc.plugins.branch import setup as setup_branch
        setup_branch(reg)
        if debug:
            print("gitc: loaded built-in plugin: branch")
    except Exception as e:
        if debug:
            print(f"gitc: failed to load built-in branch plugin: {e}")

    # --- 1) Entry points (separate packages) ---
    try:
        eps = entry_points()
        # Handle both old and new API
        if hasattr(eps, "select"):
            group = eps.select(group="gitc.plugins")
        else:
            group = eps.get("gitc.plugins", [])
    except Exception as e:
        if debug:
            print(f"gitc: entry_points load failed: {e}")
        group = []

    for ep in group:
        try:
            setup_fn = ep.load()
            setup_fn(reg)
            if debug:
                print(f"gitc: loaded plugin entry-point: {ep.name} -> {ep.value}")
        except Exception as e:
            if debug:
                print(f"gitc: failed to load plugin {ep.name}: {e}")

    # --- 2) Plugin directories ---
    dirs: list[Path] = []
    if extra_plugin_dirs:
        dirs.extend(Path(p).expanduser() for p in extra_plugin_dirs)

    # Standard path: ~/.config/gitc/plugins
    dirs.append(Path("~/.config/gitc/plugins").expanduser())

    for d in dirs:
        if not d.exists() or not d.is_dir():
            continue
        for py in sorted(d.glob("*.py")):
            _load_plugin_file(py, reg, debug=debug)


def _load_plugin_file(path: Path, reg: PluginRegistry, *, debug: bool) -> None:
    """
    Load a plugin from a Python file.

    Args:
        path: Path to the plugin file
        reg: PluginRegistry to register with
        debug: Enable debug output
    """
    module_name = f"gitc_user_plugin_{path.stem}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        if spec is None or spec.loader is None:
            raise RuntimeError("spec_from_file_location failed")

        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]

        setup = getattr(mod, "setup", None)
        if not callable(setup):
            if debug:
                print(f"gitc: {path} has no callable setup(reg), skipped")
            return

        setup(reg)
        if debug:
            print(f"gitc: loaded file plugin: {path}")
    except Exception as e:
        if debug:
            print(f"gitc: failed to load file plugin {path}: {e}")
