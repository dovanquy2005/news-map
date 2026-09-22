/**
 * CategoryChips Component.
 * Horizontal scrolling category pills for rapid thematic filtering.
 * Strictly complies with TASK-039.
 */

import React from "react";
import { CATEGORIES_LIST } from "../../hooks/useEventFilters";

export interface CategoryChipsProps {
  selectedCategory: string;
  onSelectCategory: (category: string) => void;
}

export const CategoryChips: React.FC<CategoryChipsProps> = ({
  selectedCategory,
  onSelectCategory,
}) => {
  return (
    <div
      className="category-chips-bar"
      role="tablist"
      aria-label="Danh mục sự kiện"
      data-testid="category-chips-bar"
    >
      {CATEGORIES_LIST.map((cat) => {
        const isActive = (selectedCategory || "ALL") === cat.id;

        return (
          <button
            key={cat.id}
            role="tab"
            aria-selected={isActive}
            className={`category-chip ${isActive ? "active" : ""}`}
            onClick={() => onSelectCategory(cat.id)}
            data-testid={`category-chip-${cat.id}`}
          >
            <span
              className="category-chip-dot"
              style={{ backgroundColor: isActive ? "#ffffff" : cat.color }}
            />
            <span>{cat.label}</span>
          </button>
        );
      })}
    </div>
  );
};
