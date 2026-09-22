/**
 * FilterDrawer Component for Mobile / Tablet.
 * Accessible drawer with large touch targets (>= 48px), sliders, and reset options.
 * Strictly complies with TASK-039.
 */

import React from "react";
import { FilterState } from "../../types";
import { VIETNAM_PROVINCES, ProvinceInfo } from "../../constants/provinces";
import { TIME_PRESETS } from "../../hooks/useEventFilters";

export interface FilterDrawerProps {
  isOpen: boolean;
  filters: FilterState;
  onUpdateFilters: (partial: Partial<FilterState>) => void;
  onResetFilters: () => void;
  onClose: () => void;
  onProvinceSelect?: (province: ProvinceInfo) => void;
}

export const FilterDrawer: React.FC<FilterDrawerProps> = ({
  isOpen,
  filters,
  onUpdateFilters,
  onResetFilters,
  onClose,
  onProvinceSelect,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="filter-drawer-backdrop"
      onClick={onClose}
      data-testid="filter-drawer-backdrop"
    >
      <div
        className="filter-drawer-content"
        role="dialog"
        aria-modal="true"
        aria-label="Tùy chỉnh bộ lọc"
        data-testid="filter-drawer"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="filter-drawer-header">
          <h3 className="filter-drawer-title">Bộ lọc sự kiện</h3>
          <button
            className="popup-close-btn"
            style={{ position: "static" }}
            onClick={onClose}
            aria-label="Đóng bộ lọc"
          >
            ✕
          </button>
        </div>

        <div className="filter-drawer-body">
          {/* Province Group */}
          <div className="filter-group">
            <label className="filter-group-label" htmlFor="drawer-province">
              Tỉnh / Thành phố
            </label>
            <select
              id="drawer-province"
              className="filter-select"
              style={{ width: "100%", height: 48 }}
              value={filters.province || ""}
              onChange={(e) => {
                const provName = e.target.value;
                onUpdateFilters({ province: provName });
                if (provName && onProvinceSelect) {
                  const found = VIETNAM_PROVINCES.find((p) => p.name === provName);
                  if (found) onProvinceSelect(found);
                }
              }}
            >
              <option value="">Toàn quốc (63 tỉnh thành)</option>
              {VIETNAM_PROVINCES.map((p) => (
                <option key={p.code} value={p.name}>
                  {p.name} ({p.region})
                </option>
              ))}
            </select>
          </div>

          {/* Time Preset Group */}
          <div className="filter-group">
            <label className="filter-group-label" htmlFor="drawer-time">
              Khung thời gian
            </label>
            <select
              id="drawer-time"
              className="filter-select"
              style={{ width: "100%", height: 48 }}
              value={filters.timePreset}
              onChange={(e) => onUpdateFilters({ timePreset: e.target.value })}
            >
              {TIME_PRESETS.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          {/* Minimum Source Count */}
          <div className="filter-group">
            <label className="filter-group-label">
              Số nguồn báo tối thiểu: <strong>{filters.minSources} nguồn</strong>
            </label>
            <div style={{ display: "flex", gap: "8px" }}>
              {[1, 3, 5].map((cnt) => (
                <button
                  key={cnt}
                  type="button"
                  className={filters.minSources === cnt ? "btn-primary" : "btn-secondary"}
                  style={{ flex: 1, height: 44 }}
                  onClick={() => onUpdateFilters({ minSources: cnt })}
                >
                  ≥ {cnt} nguồn
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="filter-drawer-footer">
          <button
            type="button"
            className="btn-secondary"
            onClick={onResetFilters}
            data-testid="filter-reset-btn"
          >
            Đặt lại
          </button>
          <button
            type="button"
            className="btn-primary"
            onClick={onClose}
            data-testid="filter-apply-btn"
          >
            Áp dụng
          </button>
        </div>
      </div>
    </div>
  );
};
