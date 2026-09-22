/**
 * EventCard Component for the Feed List.
 * Clean, modern editorial styling with category pills, timestamps, metrics, and selection states.
 * Strictly complies with TASK-040.
 */

import React from "react";
import { NewsEventItem } from "../../types";
import { getCategoryConfig } from "../map/icons";

export interface EventCardProps {
  event: NewsEventItem;
  isSelected: boolean;
  onSelect: (event: NewsEventItem) => void;
  onHover?: (event: NewsEventItem | null) => void;
}

export const EventCard: React.FC<EventCardProps> = ({
  event,
  isSelected,
  onSelect,
  onHover,
}) => {
  const catConfig = getCategoryConfig(event.category);

  // Relative time format
  const formatTimeAgo = (dateStr: string) => {
    const diffMin = Math.round((Date.now() - new Date(dateStr).getTime()) / 60000);
    if (diffMin < 60) return `${Math.max(1, diffMin)} phút trước`;
    const diffHours = Math.round(diffMin / 60);
    if (diffHours < 24) return `${diffHours} giờ trước`;
    return new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit" }).format(
      new Date(dateStr)
    );
  };

  return (
    <article
      tabIndex={0}
      role="button"
      aria-pressed={isSelected}
      aria-label={`Sự kiện: ${event.title}`}
      className={`event-card ${isSelected ? "selected" : ""}`}
      onClick={() => onSelect(event)}
      onMouseEnter={() => onHover && onHover(event)}
      onMouseLeave={() => onHover && onHover(null)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(event);
        }
      }}
      data-testid={`event-card-${event.id}`}
    >
      <div className="event-card-top">
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
            {event.confidence_level === "HIGH"
              ? "Tin cậy"
              : event.confidence_level === "MEDIUM"
              ? "Đang xác minh"
              : "Cần thẩm định"}
          </span>
        </div>

        <time className="event-time-stamp" dateTime={event.occurred_at}>
          {formatTimeAgo(event.occurred_at)}
        </time>
      </div>

      <h3 className="event-card-title">{event.title}</h3>

      <div className="event-card-location">
        <span className="location-icon">📍</span>
        <span>{event.location_label || event.province || "Việt Nam"}</span>
        {event.is_approximate && <span className="approximate-tag">Vùng ước tính</span>}
      </div>

      <div className="event-card-footer">
        <span className="metrics-text">
          {event.article_count} bài · {event.source_count} nguồn
        </span>

        <span className="view-detail-hint">
          Chi tiết →
        </span>
      </div>
    </article>
  );
};
