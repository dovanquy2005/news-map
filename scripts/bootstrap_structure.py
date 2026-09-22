"""Bootstrap directory structure and placeholder modules for Vietnam News Map.

Adheres strictly to:
- docs/03-backend-architecture.md
- tasks/TASK-001-project-bootstrap.md
- adr/001-modular-monolith.md
"""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# Backend Modules per docs/03-backend-architecture.md
BACKEND_MODULES = [
    ("sources", "Source configuration, polling scheduler, health, and enable/disable management."),
    ("articles", "Article ingestion, canonicalization, deduplication, and provenance tracking."),
    ("events", "Event lifecycle, summaries, multi-source links, and chronological timeline."),
    ("locations", "Location extraction, hierarchical normalization, geocoding, and spatial resolution."),
    ("clustering", "Candidate retrieval, multi-signal similarity scoring, and same-event decision engine."),
    ("search", "Full-text search, spatial bounding box filtering, and query resolution."),
    ("analytics", "Historical snapshots, event counts, metrics collection, and trend engine baseline."),
    ("admin", "Source monitoring, ingestion/processing queue monitor, review queue, and audit logs."),
]

# Common sub-packages per docs/03-backend-architecture.md
COMMON_PACKAGES = [
    ("auth", "Authentication, RBAC authorization, and API key verification."),
    ("errors", "Standardized error codes, exception handlers, and response envelopes."),
    ("logging", "Structured logging, correlation ID tracking, and redaction filters."),
    ("security", "Security policies, SSRF defenses, CORS, rate limiting, and sanitizers."),
    ("db", "PostgreSQL + PostGIS database connection, session handling, and base models."),
    ("cache", "Redis cache adapters, key schemes, and cache invalidation policies."),
    ("queue", "Redis-backed background queue abstraction and job producers."),
]

# Worker Categories per docs/03-backend-architecture.md
WORKER_CATEGORIES = [
    ("ingestion", "RSS feed polling and raw article normalization worker."),
    ("extraction", "NLP/LLM entity extraction and event validation worker."),
    ("geocoding", "Spatial resolution and geocoding persistence worker."),
    ("clustering", "Event similarity matching and provenance linking worker."),
    ("summarization", "Multi-source event summary and timeline generator worker."),
]

# Frontend directories
FRONTEND_DIRS = [
    "components",
    "layouts",
    "hooks",
    "services",
    "styles",
    "types",
]


def bootstrap():
    created_count = 0

    # 1. Backend structure
    backend_app = ROOT_DIR / "backend" / "app"
    backend_app.mkdir(parents=True, exist_ok=True)
    (backend_app / "__init__.py").write_text('"""Backend application root package."""\n', encoding="utf-8")

    api_dir = backend_app / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    (api_dir / "__init__.py").write_text('"""API routing and controller layer."""\n', encoding="utf-8")

    for mod_name, doc in BACKEND_MODULES:
        mod_dir = backend_app / "modules" / mod_name
        mod_dir.mkdir(parents=True, exist_ok=True)
        init_file = mod_dir / "__init__.py"
        init_file.write_text(f'"""Module: {mod_name}\n\n{doc}\n"""\n', encoding="utf-8")
        created_count += 1

    for pkg_name, doc in COMMON_PACKAGES:
        pkg_dir = backend_app / "common" / pkg_name
        pkg_dir.mkdir(parents=True, exist_ok=True)
        init_file = pkg_dir / "__init__.py"
        init_file.write_text(f'"""Common: {pkg_name}\n\n{doc}\n"""\n', encoding="utf-8")
        created_count += 1

    common_root = backend_app / "common" / "__init__.py"
    common_root.write_text('"""Shared common utilities, security, database, and infrastructure abstractions."""\n', encoding="utf-8")

    # 2. Worker structure
    workers_dir = ROOT_DIR / "workers"
    workers_dir.mkdir(parents=True, exist_ok=True)
    (workers_dir / "__init__.py").write_text('"""Asynchronous background worker processes."""\n', encoding="utf-8")

    for w_name, doc in WORKER_CATEGORIES:
        w_dir = workers_dir / w_name
        w_dir.mkdir(parents=True, exist_ok=True)
        init_file = w_dir / "__init__.py"
        init_file.write_text(f'"""Worker category: {w_name}\n\n{doc}\n"""\n', encoding="utf-8")
        created_count += 1

    # 3. Frontend structure
    frontend_src = ROOT_DIR / "frontend" / "src"
    frontend_src.mkdir(parents=True, exist_ok=True)
    for f_dir in FRONTEND_DIRS:
        target = frontend_src / f_dir
        target.mkdir(parents=True, exist_ok=True)
        (target / ".gitkeep").write_text("", encoding="utf-8")
        created_count += 1

    print(f"Successfully bootstrapped monorepo structure ({created_count} modules/packages created).")


if __name__ == "__main__":
    bootstrap()
