/**
 * Unit & Component tests for EventFeedView and EventCard.
 * Strictly complies with TASK-040 testing requirements.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EventFeedView } from "../components/feed/EventFeedView";
import { EventCard } from "../components/feed/EventCard";
import { MOCK_VIETNAM_EVENTS } from "../services/api";

describe("EventFeedView & EventCard Components", () => {
  const sampleEvent = MOCK_VIETNAM_EVENTS[0];

  it("renders event card with title, metrics and triggers select callback", () => {
    const handleSelect = vi.fn();
    const handleHover = vi.fn();

    render(
      <EventCard
        event={sampleEvent}
        isSelected={false}
        onSelect={handleSelect}
        onHover={handleHover}
      />
    );

    expect(screen.getByTestId(`event-card-${sampleEvent.id}`)).toBeDefined();
    expect(screen.getByText(sampleEvent.title)).toBeDefined();
    expect(screen.getByText(/14 bài · 8 nguồn/i)).toBeDefined();

    const card = screen.getByTestId(`event-card-${sampleEvent.id}`);
    fireEvent.click(card);
    expect(handleSelect).toHaveBeenCalledWith(sampleEvent);
  });

  it("renders feed panel with total count and sorting dropdown", () => {
    const handleSelect = vi.fn();

    render(
      <EventFeedView
        events={MOCK_VIETNAM_EVENTS}
        onSelectEvent={handleSelect}
      />
    );

    expect(screen.getByTestId("event-feed-panel")).toBeDefined();
    expect(screen.getByTestId("feed-count-badge").textContent).toBe(
      String(MOCK_VIETNAM_EVENTS.length)
    );

    const sortSelect = screen.getByTestId("feed-sort-select") as HTMLSelectElement;
    expect(sortSelect.value).toBe("NEWEST");

    fireEvent.change(sortSelect, { target: { value: "MOST_SOURCES" } });
    expect(sortSelect.value).toBe("MOST_SOURCES");
  });
});
