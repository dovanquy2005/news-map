"""Verification test for Frontend Foundation (TASK-008).

Validates that the frontend application layout strictly complies with:
- docs/08-ui-ux-responsive.md
- tasks/TASK-008-frontend-responsive-foundation.md
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent / "frontend"

REQUIRED_FILES = [
    "package.json",
    "index.html",
    "vite.config.ts",
    ".env.example",
    "src/styles/index.css",
    "src/types/index.ts",
    "src/components/Header.tsx",
    "src/components/MapContainer.tsx",
    "src/components/SidePanel.tsx",
    "src/components/BottomSheet.tsx",
    "src/layouts/AppLayout.tsx",
    "src/App.tsx",
    "src/main.tsx",
]

REQUIRED_CSS_TOKENS = [
    "--bg-primary",
    "--accent-primary",
    "min-width: 768px",
    "min-width: 1024px",
    ".side-panel",
    ".bottom-sheet",
]


def verify() -> int:
    missing = []
    for rel_file in REQUIRED_FILES:
        full_path = ROOT_DIR / rel_file
        if not full_path.is_file():
            missing.append(f"[MISSING FILE] {rel_file}")

    if missing:
        print("FRONTEND VERIFICATION FAILED:")
        for item in missing:
            print(f"  - {item}")
        return 1

    css_path = ROOT_DIR / "src/styles/index.css"
    css_content = css_path.read_text(encoding="utf-8")
    for token in REQUIRED_CSS_TOKENS:
        if token not in css_content:
            print(f"FRONTEND VERIFICATION FAILED: index.css missing required token: {token}")
            return 1

    print("SUCCESS: Frontend Responsive Foundation satisfies docs/08-ui-ux-responsive.md and TASK-008.")
    return 0


if __name__ == "__main__":
    sys.exit(verify())
