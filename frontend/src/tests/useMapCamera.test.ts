/**
 * Unit tests for useMapCamera and URL camera state synchronization.
 * Strictly complies with TASK-035 testing requirements.
 */

import { describe, it, expect } from "vitest";
import {
  parseCameraFromUrl,
  formatUrlWithCamera,
} from "../hooks/useMapCamera";
import { DEFAULT_VIETNAM_CENTER, DEFAULT_VIETNAM_ZOOM } from "../types/map";

describe("useMapCamera URL Synchronizer", () => {
  it("parses valid coordinates and zoom from URL query string", () => {
    const search = "?lat=10.7769&lng=106.7009&zoom=12";
    const state = parseCameraFromUrl(search);

    expect(state.center.lat).toBe(10.7769);
    expect(state.center.lng).toBe(106.7009);
    expect(state.zoom).toBe(12);
  });

  it("falls back to default Vietnam center and zoom when query params are absent", () => {
    const state = parseCameraFromUrl("");

    expect(state.center.lat).toBe(DEFAULT_VIETNAM_CENTER.lat);
    expect(state.center.lng).toBe(DEFAULT_VIETNAM_CENTER.lng);
    expect(state.zoom).toBe(DEFAULT_VIETNAM_ZOOM);
  });

  it("falls back to defaults when coordinates are out of valid range or malformed", () => {
    const search = "?lat=999.0&lng=notanumber&zoom=-5";
    const state = parseCameraFromUrl(search);

    expect(state.center.lat).toBe(DEFAULT_VIETNAM_CENTER.lat);
    expect(state.center.lng).toBe(DEFAULT_VIETNAM_CENTER.lng);
    expect(state.zoom).toBe(DEFAULT_VIETNAM_ZOOM);
  });

  it("formats new URL query string with 4-decimal precision coordinates", () => {
    const formatted = formatUrlWithCamera(
      "?filter=news",
      { lat: 21.028511, lng: 105.854167 },
      14.3
    );

    expect(formatted).toBe("?filter=news&lat=21.0285&lng=105.8542&zoom=14");
  });
});
