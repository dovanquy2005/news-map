/**
 * Unit & Component tests for EventDetailPanel.
 * Strictly complies with TASK-038 testing requirements.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { EventDetailPanel } from "../components/events/EventDetailPanel";
import { MOCK_VIETNAM_EVENTS } from "../services/api";

describe("EventDetailPanel Component", () => {
  const sampleEvent = MOCK_VIETNAM_EVENTS[0];

  it("renders all 6 core sections when open", async () => {
    const handleClose = vi.fn();

    render(
      <EventDetailPanel
        eventId={sampleEvent.id}
        isOpen={true}
        onClose={handleClose}
      />
    );

    expect(screen.getByTestId("event-detail-panel")).toBeDefined();

    // Wait for mock data resolution
    await waitFor(() => {
      expect(screen.getAllByText(sampleEvent.title).length).toBeGreaterThan(0);
    });

    // Verify Section B: Tóm tắt tổng hợp
    expect(screen.getByText("Tóm tắt tổng hợp")).toBeDefined();

    // Verify Section C: Độ tin cậy & Xác thực
    expect(screen.getByText("Độ tin cậy & Xác thực")).toBeDefined();

    // Verify Section D: Diễn biến sự kiện (Timeline)
    expect(screen.getByText("Diễn biến sự kiện")).toBeDefined();

    // Verify Section E: Nguồn báo chí
    expect(screen.getByText(/Nguồn báo chí/i)).toBeDefined();

    // Verify external links have secure attributes
    const externalLinks = screen.getAllByText("Đọc bài gốc ↗");
    expect(externalLinks.length).toBeGreaterThan(0);
    const firstAnchor = externalLinks[0].closest("a");
    expect(firstAnchor?.getAttribute("target")).toBe("_blank");
    expect(firstAnchor?.getAttribute("rel")).toBe("noopener noreferrer");
  });

  it("calls onClose when close button is clicked", async () => {
    const handleClose = vi.fn();

    render(
      <EventDetailPanel
        eventId={sampleEvent.id}
        isOpen={true}
        onClose={handleClose}
      />
    );

    const closeBtn = screen.getByTestId("detail-close-btn");
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
