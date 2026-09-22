/**
 * Unit & Component tests for FilterBar, CategoryChips, and FilterDrawer.
 * Strictly complies with TASK-039 testing requirements.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { FilterBar } from "../components/filters/FilterBar";
import { CategoryChips } from "../components/filters/CategoryChips";
import { FilterDrawer } from "../components/filters/FilterDrawer";
import { FilterState } from "../types";

describe("Filter & Search UI Components", () => {
  const defaultFilters: FilterState = {
    searchQuery: "",
    timePreset: "24h",
    category: "ALL",
    province: "",
    minSources: 1,
    minArticles: 1,
  };

  it("handles search input change and clear", () => {
    const handleUpdate = vi.fn();

    render(
      <FilterBar
        filters={{ ...defaultFilters, searchQuery: "cháy nhà" }}
        onUpdateFilters={handleUpdate}
      />
    );

    const input = screen.getByTestId("search-input") as HTMLInputElement;
    expect(input.value).toBe("cháy nhà");

    const clearBtn = screen.getByTestId("search-clear-btn");
    fireEvent.click(clearBtn);
    expect(handleUpdate).toHaveBeenCalledWith({ searchQuery: "" });
  });

  it("handles province dropdown selection", () => {
    const handleUpdate = vi.fn();
    const handleProvinceSelect = vi.fn();

    render(
      <FilterBar
        filters={defaultFilters}
        onUpdateFilters={handleUpdate}
        onProvinceSelect={handleProvinceSelect}
      />
    );

    const select = screen.getByTestId("province-select");
    fireEvent.change(select, { target: { value: "Hà Nội" } });

    expect(handleUpdate).toHaveBeenCalledWith({ province: "Hà Nội" });
    expect(handleProvinceSelect).toHaveBeenCalledWith(
      expect.objectContaining({ name: "Hà Nội", lat: 21.0285 })
    );
  });

  it("renders category chips and allows switching categories", () => {
    const handleSelectCategory = vi.fn();

    render(
      <CategoryChips
        selectedCategory="ALL"
        onSelectCategory={handleSelectCategory}
      />
    );

    const fireChip = screen.getByTestId("category-chip-FIRE");
    fireEvent.click(fireChip);
    expect(handleSelectCategory).toHaveBeenCalledWith("FIRE");
  });

  it("renders FilterDrawer and applies filters", () => {
    const handleUpdate = vi.fn();
    const handleReset = vi.fn();
    const handleClose = vi.fn();

    render(
      <FilterDrawer
        isOpen={true}
        filters={defaultFilters}
        onUpdateFilters={handleUpdate}
        onResetFilters={handleReset}
        onClose={handleClose}
      />
    );

    expect(screen.getByTestId("filter-drawer")).toBeDefined();

    const resetBtn = screen.getByTestId("filter-reset-btn");
    fireEvent.click(resetBtn);
    expect(handleReset).toHaveBeenCalledTimes(1);

    const applyBtn = screen.getByTestId("filter-apply-btn");
    fireEvent.click(applyBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
