/**
 * Google Maps JavaScript View Component.
 * Responsive full-viewport interactive map with subdued cartography,
 * touch gestures, debounced bounds sync, and error fallback states.
 * Strictly complies with docs/08-ui-ux-responsive.md and TASK-035.
 */

import React, { useEffect, useRef, useState } from "react";
import { Loader } from "@googlemaps/js-api-loader";
import { GeoPoint, MapViewportState, DEFAULT_VIETNAM_CENTER, DEFAULT_VIETNAM_ZOOM } from "../../types/map";
import { SUBDUED_DARK_MAP_STYLES } from "./mapStyles";
import { useMapBounds } from "../../hooks/useMapBounds";

export interface GoogleMapViewProps {
  apiKey?: string;
  initialCenter?: GeoPoint;
  initialZoom?: number;
  debounceMs?: number;
  onBoundsChange?: (state: MapViewportState) => void;
  onCameraChange?: (center: GeoPoint, zoom: number) => void;
  onMapReady?: (map: google.maps.Map) => void;
  onAuthFailure?: () => void;
  children?: React.ReactNode;
}

export const GoogleMapView: React.FC<GoogleMapViewProps> = ({
  apiKey,
  initialCenter = DEFAULT_VIETNAM_CENTER,
  initialZoom = DEFAULT_VIETNAM_ZOOM,
  debounceMs = 300,
  onBoundsChange,
  onCameraChange,
  onMapReady,
  onAuthFailure,
  children,
}) => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapInstanceRef = useRef<google.maps.Map | null>(null);
  const idleListenerRef = useRef<google.maps.MapsEventListener | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Catch Google Maps Authentication Failures (RefererNotAllowed, ApiNotActivated, etc.)
  useEffect(() => {
    (window as unknown as { gm_authFailure?: () => void }).gm_authFailure = () => {
      console.warn("Google Maps authentication failed with current API key.");
      setError("Google Maps không xác thực được API Key này. Đang tự động chuyển sang Bản đồ số (OSM).");
      if (onAuthFailure) {
        onAuthFailure();
      }
    };
    return () => {
      delete (window as unknown as { gm_authFailure?: () => void }).gm_authFailure;
    };
  }, [onAuthFailure]);

  const effectiveApiKey =
    apiKey !== undefined
      ? apiKey
      : typeof import.meta !== "undefined" && import.meta.env
      ? import.meta.env.VITE_MAPS_BROWSER_KEY || ""
      : "";

  const { handleMapIdle } = useMapBounds({
    debounceMs,
    onBoundsChange,
    onCameraChange,
  });

  useEffect(() => {
    if (!effectiveApiKey) {
      setIsLoading(false);
      setError("Thiếu Google Maps API Key (VITE_MAPS_BROWSER_KEY)");
      return;
    }

    let isMounted = true;
    setIsLoading(true);
    setError(null);

    const loader = new Loader({
      apiKey: effectiveApiKey,
      version: "weekly",
      libraries: ["geometry"],
    });

    loader
      .load()
      .then(() => {
        if (!isMounted || !mapContainerRef.current) return;

        const map = new google.maps.Map(mapContainerRef.current, {
          center: { lat: initialCenter.lat, lng: initialCenter.lng },
          zoom: initialZoom,
          minZoom: 5,
          maxZoom: 18,
          styles: SUBDUED_DARK_MAP_STYLES,
          disableDefaultUI: true,
          zoomControl: true,
          zoomControlOptions: {
            position: google.maps.ControlPosition.RIGHT_BOTTOM,
          },
          gestureHandling: "greedy",
        });

        mapInstanceRef.current = map;

        // Attach debounced idle event listener
        idleListenerRef.current = map.addListener("idle", () => {
          handleMapIdle(map);
        });

        if (onMapReady) {
          onMapReady(map);
        }

        setIsLoading(false);
      })
      .catch((err: unknown) => {
        if (!isMounted) return;
        setIsLoading(false);
        const errMsg = err instanceof Error ? err.message : "Không thể tải Google Maps SDK";
        setError(`Lỗi khởi tạo bản đồ: ${errMsg}`);
      });

    return () => {
      isMounted = false;
      if (idleListenerRef.current) {
        google.maps.event.removeListener(idleListenerRef.current);
        idleListenerRef.current = null;
      }
      mapInstanceRef.current = null;
    };
  }, [effectiveApiKey]);

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        backgroundColor: "#f8fafc",
      }}
    >
      {/* Map Canvas */}
      <div
        ref={mapContainerRef}
        id="google-map-canvas"
        style={{ width: "100%", height: "100%" }}
        data-testid="google-map-canvas"
      />

      {/* Loading Skeleton */}
      {isLoading && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "rgba(248, 250, 252, 0.95)",
            zIndex: 10,
            gap: 12,
            color: "#475569",
          }}
          data-testid="map-loading-skeleton"
        >
          <div
            style={{
              width: 36,
              height: 36,
              border: "3px solid #e2e8f0",
              borderTopColor: "#2563eb",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
            }}
          />
          <span style={{ fontSize: "0.875rem", fontWeight: 600 }}>
            Đang khởi tạo bản đồ số Việt Nam...
          </span>
        </div>
      )}

      {/* Offline / Demo Notice Badge */}
      {error && (
        <div
          style={{
            position: "absolute",
            top: 12,
            right: 12,
            display: "flex",
            alignItems: "center",
            gap: 8,
            backgroundColor: "rgba(255, 255, 255, 0.92)",
            backdropFilter: "blur(8px)",
            border: "1px solid #e2e8f0",
            borderRadius: 8,
            padding: "8px 14px",
            zIndex: 20,
            boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)",
            fontSize: "0.75rem",
            color: "#475569",
          }}
          data-testid="map-fallback-view"
        >
          <span style={{ color: "#d97706", fontSize: "1rem" }}>⚠️</span>
          <div>
            <strong style={{ display: "block", color: "#0f172a" }}>Chế độ bản đồ ngoại tuyến</strong>
            <span>Thiếu Google Maps API Key; đang dùng dữ liệu mô phỏng trực quan.</span>
          </div>
        </div>
      )}

      {/* Markers / Overlays slot */}
      {children}
    </div>
  );
};
