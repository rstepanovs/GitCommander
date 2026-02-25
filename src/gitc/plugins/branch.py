# Copyright (c) 2026 Roman Stepanov
# SPDX-License-Identifier: MIT
"""Branch picker plugin for Git Commander."""

from __future__ import annotations

import subprocess
import sys
from typing import Any

from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style

from gitc.context import CommandContext
from gitc.registry import PluginRegistry


def setup(reg: PluginRegistry) -> None:
    """Register the branch picker plugin."""
    # New syntax: %qbranch or %qbranch:scope where scope is 'local' or 'remote'
    reg.register(
        name="qbranch-picker",
        pattern=r"%qbranch(?:\:(?P<scope>local|remote))?",
        handler=_handle_branch,
        priority=10,
    )


def _handle_branch(m: Any, ctx: CommandContext) -> str:
    """
    Handle branch selection via TUI dialog.

    Args:
        m: Regex match object
        ctx: Command context

    Returns:
        Selected branch name

    Raises:
        KeyboardInterrupt: If user cancels
        RuntimeError: If no branches found
    """
    # Get scope from match; if not specified, use "all"
    scope = m.groupdict().get("scope") or "all"
    branches = _list_branches(scope)

    if not branches:
        raise RuntimeError("No branches found (are you inside a git repository?)")

    # (value, label) tuples for dialog
    values = [(b, b) for b in branches]

    # Midnight Commander-ish blue theme
    style = Style.from_dict(
        {
            "dialog": "bg:#0000aa #ffffff",
            "dialog frame.label": "bg:#0000aa #ffffff bold",
            "button": "bg:#0000aa #ffffff",
            "button.focused": "bg:#ffffff #0000aa bold",
            "radiolist": "bg:#0000aa #ffffff",
            "radiolist focused": "bg:#ffffff #0000aa",
        }
    )

    result = radiolist_dialog(
        title="Select branch",
        text="Choose a branch:",
        values=values,
        style=style,
    ).run()

    if result is None:
        raise KeyboardInterrupt()

    return result


def _list_branches(scope: str) -> list[str]:
    """
    Fetch list of branches from git.

    Args:
        scope: "local", "remote", or "all" (combines both)

    Returns:
        List of branch names
    """
    branches: list[str] = []

    # Local branches
    if scope in ("local", "all"):
        cmd = [
            "git",
            "for-each-ref",
            "--format=%(refname:short)",
            "refs/heads",
        ]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p.returncode == 0:
            branches.extend([line.strip() for line in p.stdout.splitlines() if line.strip()])

    # Remote branches
    if scope in ("remote", "all"):
        cmd = [
            "git",
            "for-each-ref",
            "--format=%(refname:short)",
            "refs/remotes",
        ]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p.returncode == 0:
            branches.extend([line.strip() for line in p.stdout.splitlines() if line.strip()])

    # If nothing was found, report error to stderr
    if not branches:
        sys.stderr.write("No branches found (are you inside a git repository?)\n")

    # Remove duplicates while preserving order
    seen = set()
    unique_branches: list[str] = []
    for b in branches:
        if b not in seen:
            seen.add(b)
            unique_branches.append(b)

    return unique_branches
