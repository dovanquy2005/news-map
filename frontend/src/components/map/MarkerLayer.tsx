/**
 * MarkerLayer Component.
 * Bridges application events data to Google Maps markers with dynamic clustering,
 * category coloring, touch accessibility, and offline canvas fallback rendering.
 * Strictly complies with TASK-036.
 */

import React, { useEffect, useRef } from "react";
import { NewsEventItem } from "../../types";
import { createCategoryMarkerSvgUri, getCategoryConfig } from "./icons";
import { NewsMapClusterManager } from "./clustering";

export interface MarkerLayerProps {
  map?: google.maps.Map | null;
  events: NewsEventItem[];
  selectedEventId?: string | null;
  onEventSelect: (event: NewsEventItem) => void;
  isFallbackMode?: boolean;
}

export const MarkerLayer: React.FC<MarkerLayerProps> = ({
  map,
  events,
  selectedEventId,
  onEventSelect,
  isFallbackMode = false,
}) => {
  const clusterManagerRef = useRef<NewsMapClusterManager | null>(null);
  const activeMarkersRef = useRef<google.maps.Marker[]>([]);

  // 1. Google Maps SDK Marker & Cluster lifecycle
  useEffect(() => {
    if (!map || typeof google === "undefined" || !google.maps) {
      return;
    }

    if (!clusterManagerRef.current) {
      clusterManagerRef.current = new NewsMapClusterManager({ map });
    }

    // Clean up previous markers
    activeMarkersRef.current.forEach((m) => m.setMap(null));
    activeMarkersRef.current = [];

    // Create markers for current event list
    const markers: google.maps.Marker[] = events.map((event) => {
      const isSelected = event.id === selectedEventId;
      const iconUri = createCategoryMarkerSvgUri(
        event.category,
        event.is_approximate,
        isSelected
      );

      const marker = new google.maps.Marker({
        position: { lat: event.latitude, lng: event.longitude },
        title: event.title,
        icon: {
          url: iconUri,
          scaledSize: new google.maps.Size(isSelected ? 44 : 36, isSelected ? 52 : 44),
          anchor: new google.maps.Point(isSelected ? 22 : 18, isSelected ? 50 : 42),
        },
        zIndex: isSelected ? 999 : 10,
      });

      marker.addListener("click", () => {
        onEventSelect(event);
      });

      return marker;
    });

    activeMarkersRef.current = markers;
    clusterManagerRef.current.setMarkers(markers);

    return () => {
      if (clusterManagerRef.current) {
        clusterManagerRef.current.destroy();
        clusterManagerRef.current = null;
      }
      activeMarkersRef.current.forEach((m) => m.setMap(null));
      activeMarkersRef.current = [];
    };
  }, [map, events, selectedEventId, onEventSelect]);

  // 2. Interactive SVG Canvas Fallback (Used when Google Maps API key is offline or in test environments)
  if (isFallbackMode || !map) {
    // Spatial bounds of Vietnam: Lat 8.5 to 23.5, Lng 102.0 to 110.0
    const minLat = 8.5;
    const maxLat = 23.5;
    const minLng = 102.0;
    const maxLng = 110.0;

    return (
      <div
        className="offline-canvas-container"
        data-testid="marker-layer-fallback"
        role="region"
        aria-label="Bản đồ sự kiện Việt Nam ngoại tuyến"
      >
        <div className="offline-watermark">
          <div className="offline-watermark-dot" />
          <span>Chế độ mô phỏng số liệu ({events.length} sự kiện)</span>
        </div>

        <div className="offline-interactive-stage">
          {events.map((event) => {
            const config = getCategoryConfig(event.category);
            const isSelected = event.id === selectedEventId;

            // Project coordinate to percentage on stage
            const topPct = 100 - ((event.latitude - minLat) / (maxLat - minLat)) * 100;
            const leftPct = ((event.longitude - minLng) / (maxLng - minLng)) * 100;

            return (
              <div
                key={event.id}
                role="button"
                tabIndex={0}
                aria-label={`Sự kiện: ${event.title}`}
                data-testid={`marker-pin-${event.id}`}
                className={`news-map-marker-pin ${event.is_approximate ? "approximate" : ""} ${
                  isSelected ? "active" : ""
                }`}
                style={{
                  position: "absolute",
                  top: `${Math.min(Math.max(topPct, 8), 92)}%`,
                  left: `${Math.min(Math.max(leftPct, 8), 92)}%`,
                  backgroundColor: config.fillColor,
                  border: `2px solid ${isSelected ? "#2563eb" : config.borderColor}`,
                  transform: `translate(-50%, -50%) rotate(-45deg) ${isSelected ? "scale(1.2)" : ""}`,
                  zIndex: isSelected ? 40 : 15,
                }}
                onClick={() => onEventSelect(event)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    onEventSelect(event);
                  }
                }}
              >
                <div
                  className="news-map-marker-icon"
                  dangerouslySetInnerHTML={{ __html: config.iconSvg }}
                />
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return null;
};
