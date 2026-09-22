/**
 * Unit & Component tests for MarkerLayer.
 * Strictly complies with TASK-036 testing requirements.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MarkerLayer } from "../components/map/MarkerLayer";
import { MOCK_VIETNAM_EVENTS } from "../services/api";
import { createCategoryMarkerSvgUri, getCategoryConfig } from "../components/map/icons";

describe("MarkerLayer Component", () => {
  it("renders correct number of marker pins in interactive fallback mode", () => {
    const handleSelect = vi.fn();

    render(
      <MarkerLayer
        events={MOCK_VIETNAM_EVENTS}
        onEventSelect={handleSelect}
        isFallbackMode={true}
      />
    );

    const fallbackStage = screen.getByTestId("marker-layer-fallback");
    expect(fallbackStage).toBeDefined();

    // Verify all pins rendered
    const pins = screen.getAllByRole("button");
    expect(pins.length).toBe(MOCK_VIETNAM_EVENTS.length);
  });

  it("assigns distinct colors and visual indicators per category", () => {
    const fireConfig = getCategoryConfig("FIRE");
    const weatherConfig = getCategoryConfig("WEATHER");

    expect(fireConfig.fillColor).toBe("#ef4444");
    expect(weatherConfig.fillColor).toBe("#0ea5e9");

    const svgUri = createCategoryMarkerSvgUri("FIRE", true, true);
    expect(svgUri).toContain("data:image/svg+xml");
    expect(decodeURIComponent(svgUri)).toContain("stroke-dasharray");
  });

  it("invokes onEventSelect when marker pin is clicked", () => {
    const handleSelect = vi.fn();

    render(
      <MarkerLayer
        events={MOCK_VIETNAM_EVENTS}
        onEventSelect={handleSelect}
        isFallbackMode={true}
      />
    );

    const firstPin = screen.getByTestId(`marker-pin-${MOCK_VIETNAM_EVENTS[0].id}`);
    fireEvent.click(firstPin);

    expect(handleSelect).toHaveBeenCalledTimes(1);
    expect(handleSelect).toHaveBeenCalledWith(MOCK_VIETNAM_EVENTS[0]);
  });
});
