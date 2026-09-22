"""Explainable event confidence scoring engine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EventConfidenceDTO(BaseModel):
    """Explainable confidence breakdown for an event."""

    score: int = Field(..., ge=0, le=100)
    level: str = Field(..., description="HIGH, MEDIUM, or LOW")
    factors: Dict[str, float] = Field(default_factory=dict)
    positive_indicators: List[str] = Field(default_factory=list)
    warning_indicators: List[str] = Field(default_factory=list)


class ConfidenceScoringEngine:
    """Calculates multi-factor confidence score (0-100) with explainable provenance."""

    def calculate_confidence(
        self,
        source_count: int,
        location_confidence: float,
        has_conflicts: bool = False,
        time_span_hours: float = 0.0,
        has_official_source: bool = False,
    ) -> EventConfidenceDTO:
        # Factor 1: Independent source count (35%)
        if source_count >= 5:
            f1_pts = 100.0
        elif source_count >= 3:
            f1_pts = 80.0
        elif source_count == 2:
            f1_pts = 50.0
        else:
            f1_pts = 20.0

        # Factor 2: Location precision & consistency (25%)
        if location_confidence >= 0.85:
            f2_pts = 100.0
        elif location_confidence >= 0.60:
            f2_pts = 75.0
        elif location_confidence >= 0.30:
            f2_pts = 40.0
        else:
            f2_pts = 10.0

        # Factor 3: Temporal consistency (15%)
        if time_span_hours <= 12.0:
            f3_pts = 100.0
        elif time_span_hours <= 48.0:
            f3_pts = 70.0
        else:
            f3_pts = 30.0

        # Factor 4: Fact consensus (15%)
        f4_pts = 40.0 if has_conflicts else 100.0

        # Factor 5: Source diversity (10%)
        if has_official_source or source_count >= 3:
            f5_pts = 100.0
        elif source_count == 2:
            f5_pts = 70.0
        else:
            f5_pts = 40.0

        # Weighted composite score
        total_score = (
            0.35 * f1_pts
            + 0.25 * f2_pts
            + 0.15 * f3_pts
            + 0.15 * f4_pts
            + 0.10 * f5_pts
        )
        int_score = int(round(total_score))
        int_score = max(0, min(100, int_score))

        # Qualitative tier
        if int_score >= 80:
            level = "HIGH"
        elif int_score >= 50:
            level = "MEDIUM"
        else:
            level = "LOW"

        # Explainable factors
        positive: List[str] = []
        warnings: List[str] = []

        if source_count >= 2:
            positive.append(f"Được {source_count} nguồn báo chí độc lập đưa tin")
        else:
            warnings.append("Chỉ có 1 nguồn duy nhất đưa tin")

        if location_confidence >= 0.85:
            positive.append("Địa điểm được xác định chính xác ở cấp đường / địa danh")
        elif location_confidence < 0.50:
            warnings.append("Vị trí gần đúng — chỉ xác định được ở cấp tỉnh / thành")

        if has_conflicts:
            warnings.append("Có một số chi tiết dữ kiện chưa thống nhất giữa các nguồn")
        else:
            positive.append("Các dữ kiện sự kiện có độ đồng thuận cao")

        if has_official_source:
            positive.append("Có thông tin hoặc phát ngôn từ cơ quan chức năng")

        return EventConfidenceDTO(
            score=int_score,
            level=level,
            factors={
                "source_count": f1_pts,
                "location_precision": f2_pts,
                "temporal_consistency": f3_pts,
                "fact_consensus": f4_pts,
                "source_diversity": f5_pts,
            },
            positive_indicators=positive,
            warning_indicators=warnings,
        )
