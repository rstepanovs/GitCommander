# Copyright (c) 2026 Roman Stepanov
# SPDX-License-Identifier: MIT
"""Entry point for gitc command-line interface."""

from __future__ import annotations

import sys

from gitc.app import GitCommander


def main() -> None:
    """Main entry point for the gitc application."""
    app = GitCommander()
    raise SystemExit(app.run(sys.argv[1:]))


if __name__ == "__main__":
    main()
