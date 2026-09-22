/**
 * Leaflet / OpenStreetMap Interactive View Component.
 * High-performance, zero-config map provider using CartoDB Positron / OSM light tiles.
 * Provides resilient fallback when Google Maps API key is missing or restricted.
 */

import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { GeoPoint, MapViewportState, DEFAULT_VIETNAM_CENTER, DEFAULT_VIETNAM_ZOOM } from "../../types/map";
import { NewsEventItem } from "../../types";
import { getCategoryConfig } from "./icons";

export interface LeafletMapViewProps {
  initialCenter?: GeoPoint;
  initialZoom?: number;
  events?: NewsEventItem[];
  selectedEventId?: string | null;
  onEventSelect?: (event: NewsEventItem) => void;
  onBoundsChange?: (state: MapViewportState) => void;
  onCameraChange?: (center: GeoPoint, zoom: number) => void;
  onMapReady?: (map: L.Map) => void;
}

export const LeafletMapView: React.FC<LeafletMapViewProps> = ({
  initialCenter = DEFAULT_VIETNAM_CENTER,
  initialZoom = DEFAULT_VIETNAM_ZOOM,
  events = [],
  selectedEventId,
  onEventSelect,
  onBoundsChange,
  onCameraChange,
  onMapReady,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // 1. Initialize Leaflet Map Instance
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [initialCenter.lat, initialCenter.lng],
      zoom: initialZoom,
      minZoom: 5,
      maxZoom: 18,
      zoomControl: false, // Custom position
    });

    // Elegant Light Theme CartoDB Positron tiles (matching Editorial Light Theme)
    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: "abcd",
      maxZoom: 19,
    }).addTo(map);

    // Zoom control at bottom-right
    L.control
      .zoom({
        position: "bottomright",
      })
      .addTo(map);

    markersLayerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    if (onMapReady) {
      onMapReady(map);
    }

    // Camera and Bounds change sync
    const handleMove = () => {
      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = setTimeout(() => {
        if (!map) return;
        const center = map.getCenter();
        const zoom = map.getZoom();
        const bounds = map.getBounds();

        if (onCameraChange) {
          onCameraChange({ lat: center.lat, lng: center.lng }, zoom);
        }

        if (onBoundsChange) {
          const sw = bounds.getSouthWest();
          const ne = bounds.getNorthEast();
          const bboxString = `${sw.lng.toFixed(6)},${sw.lat.toFixed(6)},${ne.lng.toFixed(6)},${ne.lat.toFixed(6)}`;
          onBoundsChange({
            bounds: {
              minLng: sw.lng,
              minLat: sw.lat,
              maxLng: ne.lng,
              maxLat: ne.lat,
            },
            center: { lat: center.lat, lng: center.lng },
            zoom,
            bboxString,
          });
        }
      }, 300);
    };

    map.on("moveend", handleMove);
    map.on("zoomend", handleMove);

    return () => {
      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
      map.remove();
      mapRef.current = null;
      markersLayerRef.current = null;
    };
  }, []);

  // 2. Render Events as Custom HTML Marker Pins
  useEffect(() => {
    if (!mapRef.current || !markersLayerRef.current) return;

    markersLayerRef.current.clearLayers();

    events.forEach((event) => {
      const config = getCategoryConfig(event.category);
      const isSelected = event.id === selectedEventId;
      const size = isSelected ? 44 : 36;

      const html = `
        <div class="news-map-marker-pin ${event.is_approximate ? "approximate" : ""} ${
        isSelected ? "active" : ""
      }" style="
          width: ${size}px;
          height: ${size}px;
          background-color: ${config.fillColor};
          border: 2px solid ${isSelected ? "#2563eb" : config.borderColor};
          box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        ">
          <div class="news-map-marker-icon" style="transform: rotate(45deg); font-size: 14px;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              ${config.iconSvg}
            </svg>
          </div>
        </div>
      `;

      const customIcon = L.divIcon({
        html,
        className: "custom-leaflet-marker",
        iconSize: [size, size],
        iconAnchor: [size / 2, size],
      });

      const marker = L.marker([event.latitude, event.longitude], {
        icon: customIcon,
        title: event.title,
        zIndexOffset: isSelected ? 1000 : 10,
      });

      marker.on("click", () => {
        if (onEventSelect) {
          onEventSelect(event);
        }
      });

      markersLayerRef.current?.addLayer(marker);
    });
  }, [events, selectedEventId, onEventSelect]);

  return (
    <div
      ref={containerRef}
      id="leaflet-map-canvas"
      style={{ width: "100%", height: "100%", position: "relative" }}
      data-testid="leaflet-map-canvas"
    />
  );
};
