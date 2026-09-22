/**
 * Unit & Component tests for EventQuickPopup and EventBottomSheet.
 * Strictly complies with TASK-037 testing requirements.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EventQuickPopup } from "../components/events/EventQuickPopup";
import { EventBottomSheet } from "../components/events/EventBottomSheet";
import { MOCK_VIETNAM_EVENTS } from "../services/api";

describe("EventQuickPopup & EventBottomSheet", () => {
  const sampleEvent = MOCK_VIETNAM_EVENTS[0];

  it("renders desktop quick popup with title, counts, and confidence badge", () => {
    const handleOpenDetail = vi.fn();
    const handleClose = vi.fn();

    render(
      <EventQuickPopup
        event={sampleEvent}
        onOpenDetail={handleOpenDetail}
        onClose={handleClose}
      />
    );

    expect(screen.getByTestId("event-quick-popup")).toBeDefined();
    expect(screen.getByText(sampleEvent.title)).toBeDefined();
    expect(screen.getByText(/14 bài · 8 nguồn/i)).toBeDefined();
    expect(screen.getByText(/Độ tin cậy: Cao/i)).toBeDefined();

    // Click CTA
    const ctaBtn = screen.getByTestId("popup-detail-cta");
    fireEvent.click(ctaBtn);
    expect(handleOpenDetail).toHaveBeenCalledWith(sampleEvent.id);

    // Click close
    const closeBtn = screen.getByTestId("popup-close-btn");
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("renders mobile bottom sheet when open and triggers CTA", () => {
    const handleOpenDetail = vi.fn();
    const handleClose = vi.fn();

    render(
      <EventBottomSheet
        event={sampleEvent}
        isOpen={true}
        onOpenDetail={handleOpenDetail}
        onClose={handleClose}
      />
    );

    expect(screen.getByTestId("event-bottom-sheet")).toBeDefined();
    expect(screen.getByText(sampleEvent.title)).toBeDefined();

    const ctaBtn = screen.getByTestId("bottom-sheet-detail-cta");
    fireEvent.click(ctaBtn);
    expect(handleOpenDetail).toHaveBeenCalledWith(sampleEvent.id);
  });
});
