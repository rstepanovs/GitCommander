#!/usr/bin/env python3
# Copyright (c) 2026 Roman Stepanov
# SPDX-License-Identifier: MIT
"""Test script for new qbranch syntax."""

import subprocess
import re


def test_pattern_matching():
    """Test that the new qbranch pattern matches correctly."""
    pattern = r"%qbranch(?:\:(?P<scope>local|remote))?"

    test_cases = [
        ("%qbranch", {"scope": None}, True),
        ("%qbranch:local", {"scope": "local"}, True),
        ("%qbranch:remote", {"scope": "remote"}, True),
        ("%branch", None, False),  # Old syntax should NOT match
        ("%qbranch()", None, False),  # Parentheses syntax should NOT match
    ]

    print("Testing qbranch pattern matching:\n")
    print(f"{'Test Case':<20} {'Expected':<20} {'Result':<10} {'Status':<10}")
    print("-" * 60)

    passed = 0
    failed = 0

    regex = re.compile(pattern)
    for test_input, expected_groups, should_match in test_cases:
        match = regex.fullmatch(test_input)

        if should_match:
            if match:
                groups = match.groupdict()
                if groups == expected_groups:
                    status = "✅ PASS"
                    passed += 1
                else:
                    status = "❌ FAIL (wrong groups)"
                    failed += 1
            else:
                status = "❌ FAIL (no match)"
                failed += 1
        else:
            if match:
                status = "❌ FAIL (matched)"
                failed += 1
            else:
                status = "✅ PASS"
                passed += 1

        result = f"Matched: {expected_groups}" if should_match and match else "No match"
        print(f"{test_input:<20} {str(expected_groups):<20} {result:<10} {status:<10}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")

    return failed == 0


def test_git_command():
    """Test that gitc recognizes the new syntax."""
    print("Testing gitc command parsing:\n")

    # Test that plugins are loaded
    result = subprocess.run(["gitc", "plugins"], capture_output=True, text=True)

    if "qbranch-picker" in result.stdout:
        print("✅ PASS: qbranch-picker plugin found in registry")
        print(f"\n{result.stdout}")
        return True
    else:
        print("❌ FAIL: qbranch-picker plugin not found")
        print(f"\n{result.stdout}")
        return False


if __name__ == "__main__":
    test1 = test_pattern_matching()
    test2 = test_git_command()

    exit_code = 0 if (test1 and test2) else 1
    exit(exit_code)
