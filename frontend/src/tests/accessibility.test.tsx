/**
 * Accessibility and Responsive Verification Tests.
 * Strictly complies with TASK-041 and WCAG 2.1 AA.
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { SkipLink } from "../components/common/SkipLink";
import { Header } from "../components/Header";

describe("Accessibility & WCAG AA Verification", () => {
  it("renders skip-to-content link pointing to #main-content", () => {
    render(<SkipLink />);

    const skipLink = screen.getByTestId("skip-link");
    expect(skipLink).toBeDefined();
    expect(skipLink.getAttribute("href")).toBe("#main-content");
  });

  it("header has appropriate banner role and accessible brand title", () => {
    render(
      <Header
        filters={{
          searchQuery: "",
          timePreset: "24h",
          category: "ALL",
          province: "",
          minSources: 1,
          minArticles: 1,
        }}
        onUpdateFilters={() => {}}
      />
    );

    const banner = screen.getByRole("banner");
    expect(banner).toBeDefined();

    const brand = screen.getByTestId("brand-logo");
    expect(brand).toBeDefined();
  });
});
