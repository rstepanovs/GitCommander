# Copyright (c) 2026 Roman Stepanov
# SPDX-License-Identifier: MIT
"""Main GitCommander application."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass

from gitc.context import CommandContext
from gitc.registry import PluginRegistry, autoload_plugins


@dataclass
class GitCommander:
    """Main GitCommander application."""

    registry: PluginRegistry | None = None

    def run(self, argv: list[str]) -> int:
        """
        Run git command with plugin preprocessing.

        Args:
            argv: Command-line arguments (without program name)

        Returns:
            Exit code from git command
        """
        # Handle built-in commands (plugins, help, etc.)
        if argv and argv[0] == "plugins":
            reg = self.registry or PluginRegistry()
            autoload_plugins(reg, debug=False)
            return self._list_plugins(reg)

        dry_run = False
        debug = False
        passthrough: list[str] = []

        it = iter(argv)
        for a in it:
            if a == "--dry-run":
                dry_run = True
            elif a == "--debug":
                debug = True
            elif a == "--no-plugins":
                passthrough = list(it)
                argv = passthrough
                break
            else:
                passthrough.append(a)

        argv = passthrough

        reg = self.registry or PluginRegistry()
        autoload_plugins(reg, debug=debug)

        ctx = CommandContext(
            cwd=os.getcwd(),
            env=dict(os.environ),
            debug=debug,
        )

        # 1) Apply plugins to arguments
        try:
            new_argv = reg.transform_argv(argv, ctx)
        except KeyboardInterrupt:
            return 130
        except Exception as e:
            if debug:
                raise
            print(f"gitc: error: {e}")
            return 2

        # 2) Show result if dry-run
        if dry_run:
            print("git " + " ".join(_shell_escape(arg) for arg in new_argv))
            return 0

        # 3) Execute git
        p = subprocess.run(["git", *new_argv])
        return p.returncode

    def _list_plugins(self, registry: PluginRegistry) -> int:
        """
        Display registered plugins.

        Args:
            registry: PluginRegistry with loaded plugins

        Returns:
            Exit code (0)
        """
        rules = registry._rules

        if not rules:
            print("No plugins registered.")
            return 0

        print("Git Commander – Registered Plugins:\n")
        print(f"{'Name':<20} {'Pattern':<30} {'Priority':<10}")
        print("-" * 60)

        for rule in rules:
            print(f"{rule.name:<20} {rule.pattern.pattern:<30} {rule.priority:<10}")

        print(f"\nTotal: {len(rules)} plugin(s) loaded")
        return 0


def _shell_escape(s: str) -> str:
    """Escape string for display purposes."""
    if not s or any(c.isspace() for c in s) or any(c in "\"'\\$`" for c in s):
        return "'" + s.replace("'", "'\"'\"'") + "'"
    return s
