/**
 * EventFeedView Component.
 * Virtualized chronological list with sorting, auto-scroll synchronization,
 * and responsive split/collapsible behavior.
 * Strictly complies with TASK-040 and ADR-003.
 */

import React, { useState, useRef, useEffect, useMemo } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { NewsEventItem, SortOption } from "../../types";
import { EventCard } from "./EventCard";

export interface EventFeedViewProps {
  events: NewsEventItem[];
  selectedEventId?: string | null;
  onSelectEvent: (event: NewsEventItem) => void;
  onHoverEvent?: (event: NewsEventItem | null) => void;
  isTabletCollapsed?: boolean;
  onToggleTabletFeed?: () => void;
}

export const EventFeedView: React.FC<EventFeedViewProps> = ({
  events,
  selectedEventId,
  onSelectEvent,
  onHoverEvent,
  isTabletCollapsed = false,
  onToggleTabletFeed,
}) => {
  const [sortOption, setSortOption] = useState<SortOption>("NEWEST");
  const parentRef = useRef<HTMLDivElement | null>(null);

  // Sort events based on selected criteria
  const sortedEvents = useMemo(() => {
    const list = [...events];
    if (sortOption === "NEWEST") {
      list.sort((a, b) => new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime());
    } else if (sortOption === "MOST_SOURCES") {
      list.sort((a, b) => b.source_count - a.source_count);
    } else if (sortOption === "MOST_ARTICLES") {
      list.sort((a, b) => b.article_count - a.article_count);
    }
    return list;
  }, [events, sortOption]);

  // Virtualizer for smooth 60 FPS scrolling
  const rowVirtualizer = useVirtualizer({
    count: sortedEvents.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 148,
    overscan: 4,
  });

  // Bidirectional Map-Feed Sync: Scroll to card when marker is clicked on map
  useEffect(() => {
    if (selectedEventId && sortedEvents.length > 0) {
      const targetIndex = sortedEvents.findIndex((e) => e.id === selectedEventId);
      if (targetIndex !== -1) {
        rowVirtualizer.scrollToIndex(targetIndex, { align: "auto" });
      }
    }
  }, [selectedEventId, sortedEvents, rowVirtualizer]);

  return (
    <aside
      className={`feed-panel ${isTabletCollapsed ? "tablet-collapsed" : ""}`}
      aria-label="Bảng tin dòng sự kiện"
      data-testid="event-feed-panel"
    >
      {/* Tablet Toggle Button */}
      {onToggleTabletFeed && (
        <button
          className="tablet-feed-toggle-btn"
          onClick={onToggleTabletFeed}
          aria-label={isTabletCollapsed ? "Mở danh sách sự kiện" : "Thu gọn danh sách sự kiện"}
          data-testid="tablet-feed-toggle"
        >
          {isTabletCollapsed ? "◀" : "▶"}
        </button>
      )}

      {/* Feed Header */}
      <div className="feed-header">
        <div className="feed-title-group">
          <h2 className="feed-title">
            <span>Dòng sự kiện</span>
            <span className="feed-count-badge" data-testid="feed-count-badge">
              {sortedEvents.length}
            </span>
          </h2>
          <span className="feed-subtitle">Nhóm tự động đa nguồn</span>
        </div>

        {/* Sort Select */}
        <select
          className="feed-sort-select"
          value={sortOption}
          onChange={(e) => setSortOption(e.target.value as SortOption)}
          aria-label="Sắp xếp danh sách"
          data-testid="feed-sort-select"
        >
          <option value="NEWEST">Mới nhất</option>
          <option value="MOST_SOURCES">Nhiều nguồn nhất</option>
          <option value="MOST_ARTICLES">Nhiều bài nhất</option>
        </select>
      </div>

      {/* Empty State */}
      {sortedEvents.length === 0 && (
        <div style={{ padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" }}>
          <p style={{ fontSize: "1.5rem", marginBottom: "8px" }}>🔍</p>
          <p style={{ fontWeight: 600, color: "var(--text-secondary)" }}>Không có sự kiện phù hợp</p>
          <p style={{ fontSize: "var(--text-xs)", marginTop: "4px" }}>
            Hãy thử nới lỏng bộ lọc thời gian hoặc chọn toàn quốc.
          </p>
        </div>
      )}

      {/* Virtualized List Container */}
      {sortedEvents.length > 0 && (
        <div
          ref={parentRef}
          className="feed-list-scroll"
          role="feed"
          aria-busy="false"
          data-testid="feed-scroll-container"
        >
          <div
            style={{
              height: `${rowVirtualizer.getTotalSize()}px`,
              width: "100%",
              position: "relative",
            }}
          >
            {rowVirtualizer.getVirtualItems().map((virtualRow) => {
              const event = sortedEvents[virtualRow.index];
              const isSelected = event.id === selectedEventId;

              return (
                <div
                  key={event.id}
                  data-index={virtualRow.index}
                  ref={rowVirtualizer.measureElement}
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    transform: `translateY(${virtualRow.start}px)`,
                    paddingBottom: "10px",
                  }}
                >
                  <EventCard
                    event={event}
                    isSelected={isSelected}
                    onSelect={onSelectEvent}
                    onHover={onHoverEvent}
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </aside>
  );
};
