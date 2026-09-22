"""Lightweight Prometheus-compatible in-memory metrics registry.

Strictly complies with:
- docs/11-performance-scalability.md
- docs/12-observability.md (Metrics collection)
- tasks/TASK-010-observability-foundation.md
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict


class MetricsRegistry:
    """Collects counters and gauges without requiring heavy external dependencies."""

    def __init__(self):
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)

    def inc_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] | None = None) -> None:
        """Increment a named metric counter."""
        label_str = self._format_labels(labels)
        key = f"{name}{label_str}"
        self._counters[key] += value

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] | None = None) -> None:
        """Set a gauge value."""
        label_str = self._format_labels(labels)
        key = f"{name}{label_str}"
        self._gauges[key] = value

    def get_counter(self, name: str, labels: Dict[str, str] | None = None) -> float:
        """Retrieve counter value."""
        label_str = self._format_labels(labels)
        return self._counters.get(f"{name}{label_str}", 0.0)

    def get_gauge(self, name: str, labels: Dict[str, str] | None = None) -> float:
        """Retrieve gauge value."""
        label_str = self._format_labels(labels)
        return self._gauges.get(f"{name}{label_str}", 0.0)

    def _format_labels(self, labels: Dict[str, str] | None) -> str:
        if not labels:
            return ""
        pairs = [f'{k}="{v}"' for k, v in sorted(labels.items())]
        return "{" + ",".join(pairs) + "}"

    def export_prometheus_text(self) -> str:
        """Export metrics formatted for Prometheus scrapers."""
        lines = []
        for key, val in sorted(self._counters.items()):
            lines.append(f"{key} {val}")
        for key, val in sorted(self._gauges.items()):
            lines.append(f"{key} {val}")
        return "\n".join(lines) + "\n"


_GLOBAL_METRICS = MetricsRegistry()


def get_metrics() -> MetricsRegistry:
    """Retrieve global metrics registry."""
    return _GLOBAL_METRICS
