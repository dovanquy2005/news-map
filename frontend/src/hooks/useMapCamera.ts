/**
 * Hook for two-way synchronization between Map Camera and Browser URL.
 * Strictly complies with docs/08-ui-ux-responsive.md and TASK-035.
 */

import { useCallback, useMemo } from "react";
import { DEFAULT_VIETNAM_CENTER, DEFAULT_VIETNAM_ZOOM, GeoPoint } from "../types/map";

export interface UrlCameraState {
  center: GeoPoint;
  zoom: number;
}

export function parseCameraFromUrl(search: string): UrlCameraState {
  const params = new URLSearchParams(search);

  const rawLat = parseFloat(params.get("lat") || "");
  const rawLng = parseFloat(params.get("lng") || "");
  const rawZoom = parseInt(params.get("zoom") || "", 10);

  const isValidLat = !isNaN(rawLat) && rawLat >= -90 && rawLat <= 90;
  const isValidLng = !isNaN(rawLng) && rawLng >= -180 && rawLng <= 180;
  const isValidZoom = !isNaN(rawZoom) && rawZoom >= 1 && rawZoom <= 20;

  return {
    center: {
      lat: isValidLat ? Math.round(rawLat * 10000) / 10000 : DEFAULT_VIETNAM_CENTER.lat,
      lng: isValidLng ? Math.round(rawLng * 10000) / 10000 : DEFAULT_VIETNAM_CENTER.lng,
    },
    zoom: isValidZoom ? rawZoom : DEFAULT_VIETNAM_ZOOM,
  };
}

export function formatUrlWithCamera(
  currentSearch: string,
  center: GeoPoint,
  zoom: number
): string {
  const params = new URLSearchParams(currentSearch);
  params.set("lat", center.lat.toFixed(4));
  params.set("lng", center.lng.toFixed(4));
  params.set("zoom", Math.round(zoom).toString());
  return `?${params.toString()}`;
}

export function useMapCamera() {
  // Read initial camera on mount
  const initialCamera = useMemo(() => {
    if (typeof window === "undefined") {
      return { center: DEFAULT_VIETNAM_CENTER, zoom: DEFAULT_VIETNAM_ZOOM };
    }
    return parseCameraFromUrl(window.location.search);
  }, []);

  // Update browser URL query without reloading the page
  const syncCameraToUrl = useCallback((center: GeoPoint, zoom: number) => {
    if (typeof window === "undefined") return;

    const newQuery = formatUrlWithCamera(window.location.search, center, zoom);
    const newUrl = `${window.location.pathname}${newQuery}${window.location.hash}`;

    // Avoid unnecessary replaceState calls if URL has not changed
    if (window.location.search !== newQuery) {
      window.history.replaceState(null, "", newUrl);
    }
  }, []);

  return {
    initialCamera,
    syncCameraToUrl,
  };
}
