# Copyright (c) 2026 Roman Stepanov
# SPDX-License-Identifier: MIT
"""File picker plugin for Git Commander."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style

from gitc.context import CommandContext
from gitc.registry import PluginRegistry


def setup(reg: PluginRegistry) -> None:
    """Register the file picker plugin."""
    # Syntax: %qfile or %qfile:/path/to/dir
    reg.register(
        name="qfile-picker",
        pattern=r"%qfile(?::(?P<path>.*))?",
        handler=_handle_file,
        priority=10,
    )


def _handle_file(m: Any, ctx: CommandContext) -> str:
    """
    Handle file selection via TUI dialog.

    Args:
        m: Regex match object with optional 'path' group
        ctx: Command context

    Returns:
        Selected file/directory path

    Raises:
        KeyboardInterrupt: If user cancels
        RuntimeError: If path is invalid or no files found
    """
    # Get path from match; if not specified, use current directory
    path_spec = m.groupdict().get("path")
    start_dir = path_spec if path_spec else "."

    # Resolve to absolute path
    try:
        start_path = Path(start_dir).resolve()
        if not start_path.exists():
            raise RuntimeError(f"Path does not exist: {start_dir}")
        if not start_path.is_dir():
            raise RuntimeError(f"Path is not a directory: {start_dir}")
    except Exception as e:
        raise RuntimeError(f"Invalid path: {e}")

    items = _list_files(start_path)

    if not items:
        raise RuntimeError(f"No files or directories found in: {start_path}")

    # (value, label) tuples for dialog
    values = [(item["path"], item["label"]) for item in items]

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
        title="Select file or directory",
        text=f"Choose from: {start_path}",
        values=values,
        style=style,
    ).run()

    if result is None:
        raise KeyboardInterrupt()

    return result


def _list_files(directory: Path) -> list[dict[str, str]]:
    """
    List files and directories in a given directory.

    Args:
        directory: Path object for the directory to list

    Returns:
        List of dicts with 'path' and 'label' keys
    """
    items: list[dict[str, str]] = []

    try:
        entries = sorted(directory.iterdir())
    except (OSError, PermissionError) as e:
        raise RuntimeError(f"Cannot list directory: {e}")

    for entry in entries:
        # Skip hidden files by default
        if entry.name.startswith("."):
            continue

        # Determine label: show directory indicator
        if entry.is_dir():
            label = f"[DIR] {entry.name}"
        else:
            label = f"[FILE] {entry.name}"

        # Store relative path for convenience (absolute if outside cwd)
        try:
            rel_path = entry.relative_to(Path.cwd())
        except ValueError:
            rel_path = entry

        items.append(
            {
                "path": str(rel_path),
                "label": label,
            }
        )

    return items
