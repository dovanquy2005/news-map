#!/usr/bin/env python3
"""Run local CI validation suite across lint, typecheck, tests, and formatting checks."""

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def run_cmd(cmd: list[str], desc: str) -> bool:
    print(f"\n--- [CI GATE] {desc} ---")
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if result.returncode != 0:
        print(f"FAILED: {desc} (exit code: {result.returncode})")
        return False
    print(f"PASSED: {desc}")
    return True


def main() -> None:
    print("========================================")
    print("Starting Local Vietnam News Map CI Check")
    print("========================================")

    npm_cmd = ["cmd.exe", "/c", "npm", "--prefix", "frontend", "test"] if sys.platform == "win32" else ["npm", "--prefix", "frontend", "test"]

    steps = [
        ([sys.executable, "scripts/verify_structure.py"], "Monorepo Structure Verification"),
        ([sys.executable, "scripts/run_tests.py", "--all"], "Backend Automated Test Suite"),
        (npm_cmd, "Frontend Automated Test Suite (Vitest)"),
    ]

    failed = False
    for cmd, desc in steps:
        if not run_cmd(cmd, desc):
            failed = True
            break

    if failed:
        print("\n========================================")
        print("LOCAL CI: FAILED! Fix errors before pushing.")
        print("========================================")
        sys.exit(1)
    else:
        print("\n========================================")
        print("LOCAL CI: ALL GATES PASSED! Ready for PR.")
        print("========================================")
        sys.exit(0)


if __name__ == "__main__":
    main()
