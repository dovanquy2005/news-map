#!/usr/bin/env python3
"""CLI Test Runner for Vietnam News Map.

Usage:
    python scripts/run_tests.py --all
    python scripts/run_tests.py --unit
    python scripts/run_tests.py --integration
    python scripts/run_tests.py --security
"""

import argparse
import sys
import unittest
import time
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


def run_test_suite(suite_type: str = "all") -> int:
    loader = unittest.TestLoader()
    start_time = time.time()

    if suite_type == "unit":
        suite = loader.discover("tests/unit", pattern="test_*.py")
    elif suite_type == "integration":
        suite = loader.discover("tests/integration", pattern="test_*.py")
    elif suite_type == "security":
        suite = loader.discover("tests/security", pattern="test_*.py")
    else:
        suite = loader.discover("tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    print(f"=== Running {suite_type.upper()} test suite ===")
    result = runner.run(suite)
    elapsed = time.time() - start_time

    print(f"\nCompleted {result.testsRun} tests in {elapsed:.2f}s")
    if result.wasSuccessful():
        print("RESULT: ALL TESTS PASSED [OK]")
        return 0
    else:
        print(f"RESULT: FAILED (Errors={len(result.errors)}, Failures={len(result.failures)})")
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Vietnam News Map Test Runner")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--unit", action="store_true", help="Run only unit tests")
    group.add_argument("--integration", action="store_true", help="Run only integration tests")
    group.add_argument("--security", action="store_true", help="Run only security tests")
    group.add_argument("--all", action="store_true", default=True, help="Run all tests")

    args = parser.parse_args()

    if args.unit:
        mode = "unit"
    elif args.integration:
        mode = "integration"
    elif args.security:
        mode = "security"
    else:
        mode = "all"

    sys.exit(run_test_suite(mode))


if __name__ == "__main__":
    main()
