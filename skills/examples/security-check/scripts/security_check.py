#!/usr/bin/env python3
"""Simple security checker script."""

import re
import sys


def check_file_for_secrets(filepath: str) -> list:
    """Check a file for potential secrets."""
    secrets_found = []

    # Patterns for common secrets
    patterns = {
        "api_key": r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]([a-zA-Z0-9_-]{32,})['\"]",
        "password": r"(?i)password\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
        "token": r"(?i)(token|secret)\s*[=:]\s*['\"]([a-zA-Z0-9_-]{20,})['\"]",
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for secret_type, pattern in patterns.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        secrets_found.append(
                            {
                                "type": secret_type,
                                "line": line_num,
                                "context": line.strip(),
                            }
                        )
    except Exception as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)

    return secrets_found


def check_file_for_unsafe_functions(filepath: str) -> list:
    """Check for unsafe function calls."""
    unsafe_found = []

    unsafe_functions = ["eval", "exec", "__import__", "compile"]

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for func in unsafe_functions:
                    if f"{func}(" in line:
                        unsafe_found.append(
                            {
                                "function": func,
                                "line": line_num,
                                "context": line.strip(),
                            }
                        )
    except Exception as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)

    return unsafe_found


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: security_check.py <filepath>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    print(f"Checking {filepath} for security issues...")

    secrets = check_file_for_secrets(filepath)
    unsafe = check_file_for_unsafe_functions(filepath)

    if secrets:
        print("\n🔴 Secrets found:")
        for secret in secrets:
            print(f"  - {secret['type'].title()}: line {secret['line']}")
            print(f"    Context: {secret['context']}")

    if unsafe:
        print("\n⚠️  Unsafe function calls found:")
        for item in unsafe:
            print(f"  - {item['function']}: line {item['line']}")
            print(f"    Context: {item['context']}")

    if not secrets and not unsafe:
        print("\n✅ No obvious security issues found")
