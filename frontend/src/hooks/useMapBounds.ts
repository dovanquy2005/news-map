/**
 * Hook for viewport bounds calculation and debounced change notifications.
 * Strictly complies with docs/08-ui-ux-responsive.md and TASK-035.
 */

import { useCallback, useRef, useState } from "react";
import { GeoPoint, MapBounds, MapViewportState } from "../types/map";

export interface UseMapBoundsOptions {
  debounceMs?: number;
  onBoundsChange?: (state: MapViewportState) => void;
  onCameraChange?: (center: GeoPoint, zoom: number) => void;
}

export function extractBoundsFromMap(map: google.maps.Map): {
  bounds: MapBounds;
  bboxString: string;
  center: GeoPoint;
  zoom: number;
} | null {
  const gBounds = map.getBounds();
  const gCenter = map.getCenter();
  const zoom = map.getZoom() ?? 6;

  if (!gBounds || !gCenter) {
    return null;
  }

  const sw = gBounds.getSouthWest();
  const ne = gBounds.getNorthEast();

  const minLng = Math.round(sw.lng() * 10000) / 10000;
  const minLat = Math.round(sw.lat() * 10000) / 10000;
  const maxLng = Math.round(ne.lng() * 10000) / 10000;
  const maxLat = Math.round(ne.lat() * 10000) / 10000;

  const bounds: MapBounds = { minLng, minLat, maxLng, maxLat };
  const bboxString = `${minLng},${minLat},${maxLng},${maxLat}`;

  const center: GeoPoint = {
    lat: Math.round(gCenter.lat() * 10000) / 10000,
    lng: Math.round(gCenter.lng() * 10000) / 10000,
  };

  return { bounds, bboxString, center, zoom };
}

export function useMapBounds(options: UseMapBoundsOptions = {}) {
  const { debounceMs = 300, onBoundsChange, onCameraChange } = options;

  const [viewportState, setViewportState] = useState<MapViewportState>({
    center: { lat: 16.0471, lng: 107.8350 },
    zoom: 6,
    bounds: null,
    bboxString: null,
  });

  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleMapIdle = useCallback(
    (map: google.maps.Map) => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      debounceTimerRef.current = setTimeout(() => {
        const extracted = extractBoundsFromMap(map);
        if (!extracted) return;

        const newState: MapViewportState = {
          center: extracted.center,
          zoom: extracted.zoom,
          bounds: extracted.bounds,
          bboxString: extracted.bboxString,
        };

        setViewportState(newState);

        if (onBoundsChange) {
          onBoundsChange(newState);
        }

        if (onCameraChange) {
          onCameraChange(extracted.center, extracted.zoom);
        }
      }, debounceMs);
    },
    [debounceMs, onBoundsChange, onCameraChange]
  );

  return {
    viewportState,
    handleMapIdle,
  };
}
