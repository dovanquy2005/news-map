/**
 * Component tests for GoogleMapView.
 * Strictly complies with TASK-035 testing requirements.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { GoogleMapView } from "../components/map/GoogleMapView";

vi.mock("@googlemaps/js-api-loader", () => {
  return {
    Loader: class MockLoader {
      load() {
        return new Promise(() => {}); // Simulates pending load
      }
    },
  };
});

describe("GoogleMapView Component", () => {
  it("renders fallback state when no API key is provided", () => {
    render(<GoogleMapView apiKey="" />);

    expect(screen.getByTestId("map-fallback-view")).toBeDefined();
    expect(screen.getByText("Chế độ bản đồ ngoại tuyến")).toBeDefined();
    expect(
      screen.getByText(/Thiếu Google Maps API Key/i)
    ).toBeDefined();
  });

  it("renders map canvas and loading state when API key is provided", () => {
    render(<GoogleMapView apiKey="mock-test-key" />);

    expect(screen.getByTestId("google-map-canvas")).toBeDefined();
    expect(screen.getByTestId("map-loading-skeleton")).toBeDefined();
    expect(
      screen.getByText("Đang khởi tạo bản đồ số Việt Nam...")
    ).toBeDefined();
  });
});
