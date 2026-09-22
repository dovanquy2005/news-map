/**
 * FilterBar Component.
 * Integrates Search input with debouncing, Province dropdown, Time preset selector,
 * and Mobile filter drawer trigger.
 * Strictly complies with TASK-039.
 */

import React from "react";
import { FilterState } from "../../types";
import { VIETNAM_PROVINCES, ProvinceInfo } from "../../constants/provinces";
import { TIME_PRESETS } from "../../hooks/useEventFilters";

export interface FilterBarProps {
  filters: FilterState;
  onUpdateFilters: (partial: Partial<FilterState>) => void;
  onProvinceSelect?: (province: ProvinceInfo) => void;
  onOpenMobileFilter?: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  onUpdateFilters,
  onProvinceSelect,
  onOpenMobileFilter,
}) => {
  const handleProvinceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const provName = e.target.value;
    onUpdateFilters({ province: provName });

    if (provName && onProvinceSelect) {
      const found = VIETNAM_PROVINCES.find((p) => p.name === provName);
      if (found) {
        onProvinceSelect(found);
      }
    }
  };

  return (
    <div className="filter-bar-desktop" role="search" aria-label="Bộ lọc sự kiện">
      {/* Search Input Field */}
      <div className="search-input-wrapper">
        <span className="search-input-icon">🔍</span>
        <input
          type="text"
          className="search-input-field"
          placeholder="Tìm kiếm vụ cháy, tai nạn, địa danh..."
          value={filters.searchQuery}
          maxLength={100}
          onChange={(e) => onUpdateFilters({ searchQuery: e.target.value })}
          aria-label="Tìm kiếm sự kiện"
          data-testid="search-input"
        />
        {filters.searchQuery && (
          <button
            className="search-clear-btn"
            onClick={() => onUpdateFilters({ searchQuery: "" })}
            aria-label="Xóa từ khóa tìm kiếm"
            data-testid="search-clear-btn"
          >
            ✕
          </button>
        )}
      </div>

      {/* Province / City Select */}
      <select
        className="filter-select"
        value={filters.province || ""}
        onChange={handleProvinceChange}
        aria-label="Chọn tỉnh thành phố"
        data-testid="province-select"
      >
        <option value="">Toàn quốc (63 tỉnh thành)</option>
        {VIETNAM_PROVINCES.map((p) => (
          <option key={p.code} value={p.name}>
            {p.name}
          </option>
        ))}
      </select>

      {/* Time Preset Select */}
      <select
        className="filter-select"
        value={filters.timePreset}
        onChange={(e) => onUpdateFilters({ timePreset: e.target.value })}
        aria-label="Mốc thời gian"
        data-testid="time-preset-select"
      >
        {TIME_PRESETS.map((t) => (
          <option key={t.id} value={t.id}>
            {t.label}
          </option>
        ))}
      </select>

      {/* Mobile Filter Button */}
      {onOpenMobileFilter && (
        <button
          className="btn-secondary"
          onClick={onOpenMobileFilter}
          style={{ height: 38, display: "flex", alignItems: "center", gap: "6px" }}
          aria-label="Mở bộ lọc nâng cao"
          data-testid="mobile-filter-open-btn"
        >
          <span>⚙️</span>
          <span>Bộ lọc</span>
        </button>
      )}
    </div>
  );
};
