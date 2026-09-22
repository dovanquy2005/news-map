/**
 * Map Container Component.
 * Integrates GoogleMapView, LeafletMapView (OpenStreetMap / CartoDB Light),
 * MarkerLayer, Viewport State, and seamless Provider Switching.
 * Strictly complies with docs/08-ui-ux-responsive.md, TASK-035, and TASK-036.
 */

import React, { useCallback, useState, useRef, useEffect } from "react";
import L from "leaflet";
import { GoogleMapView } from "./GoogleMapView";
import { LeafletMapView } from "./LeafletMapView";
import { MarkerLayer } from "./MarkerLayer";
import { useMapCamera } from "../../hooks/useMapCamera";
import { MapViewportState } from "../../types/map";
import { NewsEventItem } from "../../types";

export interface MapContainerProps {
  events?: NewsEventItem[];
  selectedEventId?: string | null;
  onEventSelect?: (event: NewsEventItem) => void;
  onViewportChange?: (viewport: MapViewportState) => void;
  onMapInstanceReady?: (controller: { panTo: (lat: number, lng: number, zoom?: number) => void }) => void;
}

export type MapProvider = "osm" | "google";

export const MapContainer: React.FC<MapContainerProps> = ({
  events = [],
  selectedEventId,
  onEventSelect = () => {},
  onViewportChange,
  onMapInstanceReady,
}) => {
  const { initialCamera, syncCameraToUrl } = useMapCamera();
  const [currentViewport, setCurrentViewport] = useState<MapViewportState | null>(null);

  // Default to OSM since it requires no API key and works 100% out of the box
  const [provider, setProvider] = useState<MapProvider>("osm");
  const [isGoogleAuthFailed, setIsGoogleAuthFailed] = useState(false);

  // Map references
  const googleMapRef = useRef<google.maps.Map | null>(null);
  const leafletMapRef = useRef<L.Map | null>(null);

  // Unified camera controller for both providers
  const cameraController = useCallback(
    (lat: number, lng: number, zoom?: number) => {
      if (provider === "google" && googleMapRef.current) {
        googleMapRef.current.panTo({ lat, lng });
        if (zoom !== undefined) googleMapRef.current.setZoom(zoom);
      } else if (leafletMapRef.current) {
        if (zoom !== undefined) {
          leafletMapRef.current.setView([lat, lng], zoom);
        } else {
          leafletMapRef.current.panTo([lat, lng]);
        }
      }
    },
    [provider]
  );

  useEffect(() => {
    if (onMapInstanceReady) {
      onMapInstanceReady({ panTo: cameraController });
    }
  }, [cameraController, onMapInstanceReady]);

  const handleBoundsChange = useCallback(
    (state: MapViewportState) => {
      setCurrentViewport(state);
      if (onViewportChange) {
        onViewportChange(state);
      }
    },
    [onViewportChange]
  );

  const handleCameraChange = useCallback(
    (center: { lat: number; lng: number }, zoom: number) => {
      syncCameraToUrl(center, zoom);
    },
    [syncCameraToUrl]
  );

  const handleGoogleMapReady = useCallback((map: google.maps.Map) => {
    googleMapRef.current = map;
  }, []);

  const handleLeafletMapReady = useCallback((map: L.Map) => {
    leafletMapRef.current = map;
  }, []);

  const handleGoogleAuthFailure = useCallback(() => {
    setIsGoogleAuthFailed(true);
    setProvider("osm");
  }, []);

  return (
    <main
      className="map-viewport"
      id="main-content"
      data-testid="map-viewport"
      role="region"
      aria-label="Bản đồ sự kiện thời gian thực"
    >
      {/* Map Provider Switcher Controls */}
      <div
        style={{
          position: "absolute",
          top: 12,
          left: 12,
          zIndex: 35,
          display: "flex",
          backgroundColor: "rgba(255, 255, 255, 0.94)",
          backdropFilter: "blur(12px)",
          borderRadius: 8,
          padding: 3,
          boxShadow: "0 2px 10px rgba(15, 23, 42, 0.08)",
          border: "1px solid #e2e8f0",
          gap: 4,
        }}
        data-testid="map-provider-switcher"
      >
        <button
          type="button"
          onClick={() => setProvider("osm")}
          style={{
            padding: "5px 10px",
            fontSize: "0.75rem",
            fontWeight: 700,
            borderRadius: 6,
            backgroundColor: provider === "osm" ? "#2563eb" : "transparent",
            color: provider === "osm" ? "#ffffff" : "#475569",
            transition: "all 150ms ease",
          }}
          data-testid="provider-btn-osm"
        >
          🌐 Bản đồ số (OSM - Sẵn sàng)
        </button>

        <button
          type="button"
          onClick={() => setProvider("google")}
          style={{
            padding: "5px 10px",
            fontSize: "0.75rem",
            fontWeight: 700,
            borderRadius: 6,
            backgroundColor: provider === "google" ? "#2563eb" : "transparent",
            color: provider === "google" ? "#ffffff" : "#475569",
            transition: "all 150ms ease",
          }}
          data-testid="provider-btn-google"
        >
          📍 Google Maps
        </button>
      </div>

      {/* Provider A: OpenStreetMap / Leaflet (Zero-config, CartoDB Light theme, works 100%) */}
      {provider === "osm" && (
        <LeafletMapView
          initialCenter={initialCamera.center}
          initialZoom={initialCamera.zoom}
          events={events}
          selectedEventId={selectedEventId}
          onEventSelect={onEventSelect}
          onBoundsChange={handleBoundsChange}
          onCameraChange={handleCameraChange}
          onMapReady={handleLeafletMapReady}
        />
      )}

      {/* Provider B: Google Maps (Requires valid, un-restricted API Key) */}
      {provider === "google" && (
        <GoogleMapView
          initialCenter={initialCamera.center}
          initialZoom={initialCamera.zoom}
          onBoundsChange={handleBoundsChange}
          onCameraChange={handleCameraChange}
          onMapReady={handleGoogleMapReady}
          onAuthFailure={handleGoogleAuthFailure}
        >
          <MarkerLayer
            map={googleMapRef.current}
            events={events}
            selectedEventId={selectedEventId}
            onEventSelect={onEventSelect}
            isFallbackMode={!googleMapRef.current || isGoogleAuthFailed}
          />
        </GoogleMapView>
      )}

      {/* Bounding Box Indicator */}
      {currentViewport?.bboxString && (
        <div
          className="viewport-bbox-tag"
          data-testid="viewport-bbox-indicator"
          aria-hidden="true"
        >
          bbox: {currentViewport.bboxString}
        </div>
      )}
    </main>
  );
};
