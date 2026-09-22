/**
 * Event Quick Popup Component for Desktop / Tablet Viewports.
 * Displays lightweight event summary card with CTA to open full detail.
 * Strictly complies with TASK-037 and prd.md Section 15.
 */

import React, { useEffect } from "react";
import { NewsEventItem } from "../../types";
import { getCategoryConfig } from "../map/icons";

export interface EventQuickPopupProps {
  event: NewsEventItem;
  onOpenDetail: (eventId: string) => void;
  onClose: () => void;
  position?: { top?: number; left?: number; bottom?: number; right?: number };
}

export const EventQuickPopup: React.FC<EventQuickPopupProps> = ({
  event,
  onOpenDetail,
  onClose,
  position = { top: 20, left: 20 },
}) => {
  const catConfig = getCategoryConfig(event.category);

  // Format occurred timestamp to ICT (Vietnam Time, UTC+7)
  const formattedTime = new Intl.DateTimeFormat("vi-VN", {
    timeZone: "Asia/Ho_Chi_Minh",
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "2-digit",
  }).format(new Date(event.occurred_at));

  // Dismiss on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return (
    <div
      className="event-quick-popup"
      style={position}
      data-testid="event-quick-popup"
      role="dialog"
      aria-label={`Xem nhanh: ${event.title}`}
    >
      <button
        className="popup-close-btn"
        onClick={onClose}
        aria-label="Đóng bảng xem nhanh"
        data-testid="popup-close-btn"
      >
        ✕
      </button>

      {/* Badges Row */}
      <div className="badge-group">
        <span
          className={`category-badge ${event.category}`}
          style={{
            backgroundColor: catConfig.badgeBg,
            color: catConfig.badgeText,
            borderColor: catConfig.badgeBorder,
          }}
        >
          {catConfig.nameVi}
        </span>

        <span className={`confidence-pill ${event.confidence_level || "HIGH"}`}>
          Độ tin cậy: {event.confidence_level === "HIGH" ? "Cao" : event.confidence_level === "MEDIUM" ? "Trung bình" : "Thấp"}
        </span>

        <span className="event-time-stamp">{formattedTime}</span>
      </div>

      {/* Title */}
      <h3 className="event-card-title" title={event.title}>
        {event.title}
      </h3>

      {/* Location */}
      <div className="event-card-location">
        <span className="location-icon">📍</span>
        <span>{event.location_label || event.province || "Việt Nam"}</span>
        {event.is_approximate && <span className="approximate-tag">Vùng ước tính</span>}
      </div>

      {/* Multi-source metrics & CTA */}
      <div className="event-card-footer">
        <span className="metrics-text">
          {event.article_count} bài · {event.source_count} nguồn
        </span>

        <button
          className="btn-primary"
          style={{ height: 36, padding: "0 12px", fontSize: "0.8125rem", flex: "none" }}
          onClick={() => onOpenDetail(event.id)}
          data-testid="popup-detail-cta"
        >
          Xem chi tiết →
        </button>
      </div>
    </div>
  );
};
