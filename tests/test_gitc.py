#!/usr/bin/env python3
# Copyright (c) 2026 Roman Stepanov
# SPDX-License-Identifier: MIT
"""Test script to verify gitc functionality."""

import subprocess
import sys


def run_test(description: str, cmd: list[str]) -> bool:
    """Run a test command and report results."""
    print(f"\n{'=' * 60}")
    print(f"TEST: {description}")
    print(f"{'=' * 60}")
    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=False)
    success = result.returncode == 0

    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status} (exit code: {result.returncode})")
    return success


def main() -> int:
    """Run all tests."""
    print("\n" + "=" * 60)
    print("GIT COMMANDER TEST SUITE")
    print("=" * 60)

    tests = [
        ("Show gitc help", ["gitc", "--help"]),
        ("List registered plugins", ["gitc", "plugins"]),
        ("Dry-run: simple checkout", ["gitc", "--dry-run", "checkout", "main"]),
        ("Debug mode: simple command", ["gitc", "--debug", "--dry-run", "status"]),
        ("No-plugins mode", ["gitc", "--no-plugins", "--dry-run", "log", "--oneline"]),
    ]

    passed = 0
    failed = 0

    for desc, cmd in tests:
        if run_test(desc, cmd):
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
