# Copyright (c) 2026 Roman Stepanov
# SPDX-License-Identifier: MIT
"""Unit tests for gitc PluginRegistry and autoloading."""

from __future__ import annotations

import re
import textwrap
from typing import Any

import pytest

from gitc.registry import PluginRegistry, autoload_plugins
from gitc.context import CommandContext


class DummyMatch:
    """Simple wrapper to emulate re.Match for handler tests."""

    def __init__(self, groups: dict[str, Any]):
        self._groups = groups

    def groupdict(self) -> dict[str, Any]:
        return self._groups


@pytest.fixture
def ctx() -> CommandContext:
    return CommandContext(cwd="/", env={}, debug=False)


def test_register_and_transform_single(ctx: CommandContext) -> None:
    reg = PluginRegistry()

    def handler(m, c):
        return "BAR"

    reg.register(name="foo", pattern=r"%foo", handler=handler)

    out = reg.transform_argv(["%foo", "x"], ctx)
    assert out == ["BAR", "x"]


def test_handler_returns_list(ctx: CommandContext) -> None:
    reg = PluginRegistry()

    def handler(m, c):
        return ["a", "b"]

    reg.register(name="alist", pattern=r"%alist", handler=handler)

    out = reg.transform_argv(["%alist"], ctx)
    assert out == ["a", "b"]


def test_priority_order(ctx: CommandContext) -> None:
    reg = PluginRegistry()

    def h1(m, c):
        return "ONE"

    def h2(m, c):
        return "TWO"

    # h1 has higher priority (lower number) and should run first
    reg.register(name="h2", pattern=r"%x", handler=h2, priority=20)
    reg.register(name="h1", pattern=r"%x", handler=h1, priority=10)

    out = reg.transform_argv(["%x"], ctx)
    assert out == ["ONE"]


def test_no_match_passes_through(ctx: CommandContext) -> None:
    reg = PluginRegistry()

    out = reg.transform_argv(["literal", "%unknown"], ctx)
    assert out == ["literal", "%unknown"]


def test_handler_keyboardinterrupt_propagates(ctx: CommandContext) -> None:
    reg = PluginRegistry()

    def handler(m, c):
        raise KeyboardInterrupt()

    reg.register(name="cancel", pattern=r"%cancel", handler=handler)

    with pytest.raises(KeyboardInterrupt):
        reg.transform_argv(["%cancel"], ctx)


def test_autoload_file_plugin(tmp_path, ctx: CommandContext) -> None:
    # Create a temporary plugin file that registers %tmp -> 'ok'
    plugin_code = textwrap.dedent(
        """
        def setup(reg):
            def handler(m, ctx):
                return 'OK'
            reg.register(name='tmp-plugin', pattern=r'%tmp', handler=handler)
        """
    )

    p = tmp_path / "tmp_plugin.py"
    p.write_text(plugin_code)

    reg = PluginRegistry()
    autoload_plugins(reg, debug=True, extra_plugin_dirs=[str(tmp_path)])

    # After autoload, %tmp should be handled
    out = reg.transform_argv(["%tmp"], ctx)
    assert out == ["OK"]


def test_builtin_qbranch_loaded(ctx: CommandContext) -> None:
    reg = PluginRegistry()
    autoload_plugins(reg, debug=False)

    # find qbranch-picker rule
    names = [r.name for r in reg._rules]
    assert any("qbranch-picker" == n for n in names)
