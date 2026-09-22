/**
 * Mobile Bottom Sheet Preview Component.
 * Swipe-friendly drawer docked at bottom of mobile viewports (< 768px).
 * Strictly complies with TASK-037 and ADR-003.
 */

import React, { useRef, useState } from "react";
import { NewsEventItem } from "../../types";
import { getCategoryConfig } from "../map/icons";

export interface EventBottomSheetProps {
  event: NewsEventItem | null;
  isOpen: boolean;
  onOpenDetail: (eventId: string) => void;
  onClose: () => void;
}

export const EventBottomSheet: React.FC<EventBottomSheetProps> = ({
  event,
  isOpen,
  onOpenDetail,
  onClose,
}) => {
  const [dragOffset, setDragOffset] = useState(0);
  const startYRef = useRef<number | null>(null);

  if (!isOpen || !event) {
    return null;
  }

  const catConfig = getCategoryConfig(event.category);

  const formattedTime = new Intl.DateTimeFormat("vi-VN", {
    timeZone: "Asia/Ho_Chi_Minh",
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "2-digit",
  }).format(new Date(event.occurred_at));

  // Touch Swipe Handlers for Dismiss Gesture
  const handleTouchStart = (e: React.TouchEvent) => {
    startYRef.current = e.touches[0].clientY;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (startYRef.current !== null) {
      const deltaY = e.touches[0].clientY - startYRef.current;
      if (deltaY > 0) {
        setDragOffset(deltaY);
      }
    }
  };

  const handleTouchEnd = () => {
    if (dragOffset > 80) {
      onClose();
    }
    setDragOffset(0);
    startYRef.current = null;
  };

  return (
    <section
      className="mobile-bottom-sheet"
      style={{
        transform: `translateY(${dragOffset}px)`,
        transition: dragOffset === 0 ? "transform 200ms ease-out" : "none",
      }}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      role="dialog"
      aria-label={`Bảng tin di động: ${event.title}`}
      data-testid="event-bottom-sheet"
    >
      <div className="bottom-sheet-handle-bar" />

      {/* Top Badges */}
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
      <h3 className="event-card-title">{event.title}</h3>

      {/* Location */}
      <div className="event-card-location">
        <span className="location-icon">📍</span>
        <span>{event.location_label || event.province || "Việt Nam"}</span>
        {event.is_approximate && <span className="approximate-tag">Vùng ước tính</span>}
      </div>

      {/* Actions */}
      <div style={{ display: "flex", gap: "10px", marginTop: "4px" }}>
        <button
          className="btn-secondary"
          style={{ height: 48, width: 48, padding: 0 }}
          onClick={onClose}
          aria-label="Đóng"
        >
          ✕
        </button>

        <button
          className="btn-primary"
          style={{ height: 48 }}
          onClick={() => onOpenDetail(event.id)}
          data-testid="bottom-sheet-detail-cta"
        >
          Xem chi tiết ({event.article_count} bài · {event.source_count} nguồn) →
        </button>
      </div>
    </section>
  );
};
