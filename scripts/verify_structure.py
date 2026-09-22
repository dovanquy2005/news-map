"""Structural verification test for TASK-001.

Validates that the project directory structure strictly satisfies:
- docs/03-backend-architecture.md
- tasks/TASK-001-project-bootstrap.md
- adr/001-modular-monolith.md
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

EXPECTED_FILES = [
    ".gitignore",
    ".editorconfig",
    "pyproject.toml",
    "README.md",
    "prd.md",
    "backend/app/__init__.py",
    "backend/app/api/__init__.py",
    "backend/app/common/__init__.py",
    "backend/app/common/auth/__init__.py",
    "backend/app/common/errors/__init__.py",
    "backend/app/common/logging/__init__.py",
    "backend/app/common/security/__init__.py",
    "backend/app/common/db/__init__.py",
    "backend/app/common/cache/__init__.py",
    "backend/app/common/queue/__init__.py",
    "backend/app/modules/sources/__init__.py",
    "backend/app/modules/articles/__init__.py",
    "backend/app/modules/events/__init__.py",
    "backend/app/modules/locations/__init__.py",
    "backend/app/modules/clustering/__init__.py",
    "backend/app/modules/search/__init__.py",
    "backend/app/modules/analytics/__init__.py",
    "backend/app/modules/admin/__init__.py",
    "workers/__init__.py",
    "workers/ingestion/__init__.py",
    "workers/extraction/__init__.py",
    "workers/geocoding/__init__.py",
    "workers/clustering/__init__.py",
    "workers/summarization/__init__.py",
]

EXPECTED_DIRS = [
    "frontend/src/components",
    "frontend/src/layouts",
    "frontend/src/hooks",
    "frontend/src/services",
    "frontend/src/styles",
    "frontend/src/types",
]


def verify() -> int:
    missing_items = []

    for file_rel in EXPECTED_FILES:
        full_path = ROOT_DIR / file_rel
        if not full_path.is_file():
            missing_items.append(f"[MISSING FILE] {file_rel}")

    for dir_rel in EXPECTED_DIRS:
        full_path = ROOT_DIR / dir_rel
        if not full_path.is_dir():
            missing_items.append(f"[MISSING DIR]  {dir_rel}")

    if missing_items:
        print("VERIFICATION FAILED! The following required components are missing:")
        for item in missing_items:
            print(f"  - {item}")
        return 1

    # Verify .gitignore contains critical exclusions
    gitignore_path = ROOT_DIR / ".gitignore"
    gitignore_content = gitignore_path.read_text(encoding="utf-8")
    critical_patterns = [".env", "__pycache__", ".venv", "node_modules"]
    for pattern in critical_patterns:
        if pattern not in gitignore_content:
            print(f"VERIFICATION FAILED! .gitignore is missing critical pattern: {pattern}")
            return 1

    print("SUCCESS: Monorepo layout strictly complies with docs/03-backend-architecture.md and TASK-001.")
    print(f"Verified {len(EXPECTED_FILES)} files and {len(EXPECTED_DIRS)} directories.")
    return 0


if __name__ == "__main__":
    sys.exit(verify())
