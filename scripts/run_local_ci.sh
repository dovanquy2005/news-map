#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "Starting Local Vietnam News Map CI Check"
echo "========================================"

python scripts/verify_structure.py
python scripts/run_tests.py --all

echo "========================================"
echo "LOCAL CI: ALL GATES PASSED! Ready for PR."
echo "========================================"
