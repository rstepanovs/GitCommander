# Copyright (c) 2026 Roman Stepanov
# SPDX-License-Identifier: MIT
"""Git Commander application context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class CommandContext:
    """Context passed to plugin handlers."""

    cwd: str
    env: Mapping[str, str]
    debug: bool = False
