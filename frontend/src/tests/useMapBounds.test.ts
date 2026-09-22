/**
 * Unit tests for useMapBounds and viewport bounding box extraction.
 * Strictly complies with TASK-035 testing requirements.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { extractBoundsFromMap, useMapBounds } from "../hooks/useMapBounds";

describe("useMapBounds & Viewport Debouncing", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  function createMockGoogleMap(options?: {
    swLng?: number;
    swLat?: number;
    neLng?: number;
    neLat?: number;
    cLat?: number;
    cLng?: number;
    zoom?: number;
  }) {
    const swLng = options?.swLng ?? 105.12345;
    const swLat = options?.swLat ?? 10.12345;
    const neLng = options?.neLng ?? 107.98765;
    const neLat = options?.neLat ?? 12.98765;
    const cLat = options?.cLat ?? 11.55555;
    const cLng = options?.cLng ?? 106.55555;
    const zoom = options?.zoom ?? 10;

    return {
      getBounds: () => ({
        getSouthWest: () => ({
          lng: () => swLng,
          lat: () => swLat,
        }),
        getNorthEast: () => ({
          lng: () => neLng,
          lat: () => neLat,
        }),
      }),
      getCenter: () => ({
        lat: () => cLat,
        lng: () => cLng,
      }),
      getZoom: () => zoom,
    } as unknown as google.maps.Map;
  }

  it("extracts bounding box correctly and formats bbox=minLng,minLat,maxLng,maxLat", () => {
    const mockMap = createMockGoogleMap();
    const result = extractBoundsFromMap(mockMap);

    expect(result).not.toBeNull();
    expect(result!.bounds).toEqual({
      minLng: 105.1235,
      minLat: 10.1235,
      maxLng: 107.9877,
      maxLat: 12.9877,
    });
    expect(result!.bboxString).toBe("105.1235,10.1235,107.9877,12.9877");
    expect(result!.center).toEqual({ lat: 11.5556, lng: 106.5556 });
    expect(result!.zoom).toBe(10);
  });

  it("debounces rapid map idle events and fires exactly once after 300ms pause", () => {
    const onBoundsChange = vi.fn();
    const onCameraChange = vi.fn();

    const { result } = renderHook(() =>
      useMapBounds({
        debounceMs: 300,
        onBoundsChange,
        onCameraChange,
      })
    );

    const map1 = createMockGoogleMap({ cLat: 11.0, cLng: 106.0 });
    const map2 = createMockGoogleMap({ cLat: 11.1, cLng: 106.1 });
    const map3 = createMockGoogleMap({ cLat: 11.2, cLng: 106.2 });

    // Rapid camera movements
    act(() => {
      result.current.handleMapIdle(map1);
    });
    act(() => {
      vi.advanceTimersByTime(100);
    });

    act(() => {
      result.current.handleMapIdle(map2);
    });
    act(() => {
      vi.advanceTimersByTime(100);
    });

    act(() => {
      result.current.handleMapIdle(map3);
    });
    act(() => {
      vi.advanceTimersByTime(200);
    });

    // After 200ms since map3, should NOT have fired yet (total 300ms needed)
    expect(onBoundsChange).toHaveBeenCalledTimes(0);

    // Advance remaining 100ms
    act(() => {
      vi.advanceTimersByTime(100);
    });

    // Now it should fire EXACTLY once with map3's parameters
    expect(onBoundsChange).toHaveBeenCalledTimes(1);
    expect(onCameraChange).toHaveBeenCalledTimes(1);
    expect(onCameraChange).toHaveBeenCalledWith({ lat: 11.2, lng: 106.2 }, 10);
  });
});
