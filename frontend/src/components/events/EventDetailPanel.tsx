/**
 * Event Detail Panel Component.
 * Slide-over drawer on desktop/tablet, full-screen overlay on mobile.
 * Implements all 6 core sections defined in prd.md Section 16 & TASK-038.
 */

import React, { useEffect } from "react";
import { useEventDetail } from "../../hooks/useEventDetail";
import { getCategoryConfig } from "../map/icons";

export interface EventDetailPanelProps {
  eventId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onSelectRelatedEvent?: (relatedId: string) => void;
}

export const EventDetailPanel: React.FC<EventDetailPanelProps> = ({
  eventId,
  isOpen,
  onClose,
  onSelectRelatedEvent,
}) => {
  const { detail, loading, error } = useEventDetail(eventId);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const catConfig = detail ? getCategoryConfig(detail.category) : getCategoryConfig("OTHER");

  const formatICT = (dateString?: string) => {
    if (!dateString) return "Chưa cập nhật";
    return new Intl.DateTimeFormat("vi-VN", {
      timeZone: "Asia/Ho_Chi_Minh",
      hour: "2-digit",
      minute: "2-digit",
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }).format(new Date(dateString));
  };

  return (
    <div
      className="event-detail-backdrop"
      onClick={onClose}
      data-testid="event-detail-backdrop"
    >
      <aside
        className="event-detail-drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Chi tiết sự kiện"
        data-testid="event-detail-panel"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Sticky Header */}
        <div className="detail-drawer-header">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span
              className={`category-badge ${detail?.category || "OTHER"}`}
              style={{
                backgroundColor: catConfig.badgeBg,
                color: catConfig.badgeText,
                borderColor: catConfig.badgeBorder,
              }}
            >
              {catConfig.nameVi}
            </span>
            <span className="brand-pill" style={{ fontSize: "0.6875rem" }}>
              {detail?.status === "VERIFIED"
                ? "ĐÃ XÁC THỰC"
                : detail?.status === "RESOLVED"
                ? "ĐÃ GIẢI QUYẾT"
                : "ĐANG DIỄN RA"}
            </span>
          </div>

          <button
            className="popup-close-btn"
            style={{ position: "static" }}
            onClick={onClose}
            aria-label="Đóng chi tiết sự kiện"
            data-testid="detail-close-btn"
          >
            ✕
          </button>
        </div>

        {/* Loading / Error States */}
        {loading && (
          <div style={{ padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" }}>
            <div
              style={{
                width: 32,
                height: 32,
                border: "3px solid #e2e8f0",
                borderTopColor: "var(--brand-blue)",
                borderRadius: "50%",
                animation: "spin 1s linear infinite",
                margin: "0 auto 12px auto",
              }}
            />
            <p>Đang tải dữ liệu chi tiết sự kiện...</p>
          </div>
        )}

        {error && (
          <div style={{ padding: "24px 20px", color: "var(--brand-red)" }}>
            <p>⚠️ {error}</p>
          </div>
        )}

        {/* Content Body */}
        {detail && !loading && (
          <div className="detail-drawer-scroll">
            {/* Section A: Header & General Info */}
            <div className="detail-section">
              <h2
                style={{
                  fontSize: "var(--text-xl)",
                  fontWeight: 800,
                  lineHeight: 1.35,
                  color: "var(--text-primary)",
                }}
              >
                {detail.title}
              </h2>

              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "6px",
                  fontSize: "var(--text-sm)",
                  color: "var(--text-secondary)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ color: "var(--brand-red)" }}>📍</span>
                  <span style={{ fontWeight: 600 }}>{detail.location_label || detail.province}</span>
                  {detail.is_approximate && <span className="approximate-tag">Vùng ước tính</span>}
                </div>

                <div style={{ display: "flex", gap: "16px", color: "var(--text-muted)", fontSize: "var(--text-xs)" }}>
                  <span>Xảy ra: <strong>{formatICT(detail.occurred_at)}</strong></span>
                  <span>Cập nhật: <strong>{formatICT(detail.last_updated_at || detail.occurred_at)}</strong></span>
                </div>
              </div>
            </div>

            {/* Section B: AI Summary with Conflict Warning */}
            <div className="detail-section">
              <div className="detail-section-title">
                <span>🤖</span>
                <span>Tóm tắt tổng hợp</span>
              </div>

              <div className="summary-box">
                <div className="summary-badge-ai">✦ Phân tích đa nguồn</div>
                <p>{detail.summary || "Đang tổng hợp thông tin từ các cơ quan báo chí..."}</p>

                {(detail.has_conflicting_reports || detail.conflict_details) && (
                  <div className="summary-warning-callout">
                    <span>⚠️</span>
                    <div>
                      <strong>Cảnh báo thông tin đa chiều:</strong>{" "}
                      {detail.conflict_details ||
                        "Các nguồn tin đang có mâu thuẫn về số liệu thiệt hại hoặc nguyên nhân ban đầu. Đang chờ kết luận chính thức."}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Section C: Verification & Confidence Breakdown */}
            <div className="detail-section">
              <div className="detail-section-title">
                <span>🛡️</span>
                <span>Độ tin cậy & Xác thực</span>
              </div>

              <div className="confidence-card">
                <div className="confidence-card-score">
                  <div>
                    <span style={{ fontSize: "var(--text-xs)", color: "var(--text-muted)", display: "block" }}>
                      Chỉ số xác minh tổng hợp
                    </span>
                    <span className="confidence-score-val">
                      {Math.round((detail.confidence_score || 0.85) * 100)} / 100
                    </span>
                  </div>

                  <span className={`confidence-pill ${detail.confidence_level || "HIGH"}`} style={{ fontSize: "0.8125rem", padding: "4px 10px" }}>
                    {detail.confidence_level === "HIGH" ? "Mức độ: Rất tin cậy" : "Mức độ: Đang xác minh"}
                  </span>
                </div>

                <div className="factors-list">
                  <div className="factor-item">
                    <span className="factor-positive-icon">✓</span>
                    <span>Xác thực độc lập từ <strong>{detail.source_count} tòa soạn báo chí</strong> chính thống.</span>
                  </div>
                  <div className="factor-item">
                    <span className="factor-positive-icon">✓</span>
                    <span>Tọa độ xác định qua geocoder chuyên biệt <strong>{detail.location_label}</strong>.</span>
                  </div>
                  {detail.is_approximate && (
                    <div className="factor-item">
                      <span className="factor-warning-icon">!</span>
                      <span>Tọa độ ước lượng theo trung tâm khu vực hành chính.</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Section D: Chronological Timeline */}
            <div className="detail-section">
              <div className="detail-section-title">
                <span>⏱️</span>
                <span>Diễn biến sự kiện</span>
              </div>

              <div className="timeline-container">
                {detail.timeline && detail.timeline.length > 0 ? (
                  detail.timeline.map((step) => (
                    <div key={step.id} className="timeline-step">
                      <div className="timeline-dot" />
                      <div className="timeline-time">{formatICT(step.timestamp)}</div>
                      <div className="timeline-desc">{step.description}</div>
                      {step.source_name && (
                        <div style={{ fontSize: "var(--text-xs)", color: "var(--brand-blue)" }}>
                          Nguồn: {step.source_name}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <p style={{ fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
                    Đang theo dõi diễn biến sự kiện...
                  </p>
                )}
              </div>
            </div>

            {/* Section E: Sources List with Direct External Links */}
            <div className="detail-section">
              <div className="detail-section-title">
                <span>📰</span>
                <span>Nguồn báo chí ({detail.sources?.length || 0})</span>
              </div>

              <div className="source-cards-list">
                {detail.sources && detail.sources.length > 0 ? (
                  detail.sources.map((src) => (
                    <a
                      key={src.id}
                      href={src.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="source-card-item"
                    >
                      <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                        <div className="source-publisher-title">{src.publisher || src.name}</div>
                        <div className="source-article-title">{src.title}</div>
                      </div>

                      <div className="source-external-btn">
                        Đọc bài gốc ↗
                      </div>
                    </a>
                  ))
                ) : (
                  <p style={{ fontSize: "var(--text-sm)", color: "var(--text-muted)" }}>
                    Chưa có bài báo liên kết.
                  </p>
                )}
              </div>
            </div>

            {/* Section F: Related Events */}
            {detail.related_events && detail.related_events.length > 0 && (
              <div className="detail-section" style={{ paddingBottom: "20px" }}>
                <div className="detail-section-title">
                  <span>🔗</span>
                  <span>Sự kiện liên quan cùng khu vực</span>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  {detail.related_events.map((rel) => (
                    <div
                      key={rel.id}
                      className="event-card"
                      style={{ padding: "10px 12px" }}
                      onClick={() => onSelectRelatedEvent && onSelectRelatedEvent(rel.id)}
                    >
                      <span className="event-card-title" style={{ fontSize: "var(--text-sm)" }}>
                        {rel.title}
                      </span>
                      <span style={{ fontSize: "var(--text-xs)", color: "var(--text-muted)" }}>
                        {rel.location_label} · {rel.article_count} bài
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </aside>
    </div>
  );
};
