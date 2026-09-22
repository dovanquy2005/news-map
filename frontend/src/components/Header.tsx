/**
 * Header Component.
 * Incorporates editorial branding, real-time status pill, and responsive FilterBar.
 * Strictly complies with TASK-039, TASK-041, and Light Theme.
 */

import React from "react";
import { FilterBar } from "./filters/FilterBar";
import { FilterState } from "../types";
import { ProvinceInfo } from "../constants/provinces";

export interface HeaderProps {
  filters: FilterState;
  onUpdateFilters: (partial: Partial<FilterState>) => void;
  onProvinceSelect?: (province: ProvinceInfo) => void;
  onOpenMobileFilter?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  filters,
  onUpdateFilters,
  onProvinceSelect,
  onOpenMobileFilter,
}) => {
  return (
    <header className="header-bar" role="banner" data-testid="app-header">
      {/* Brand Identity */}
      <div className="brand-wrapper" data-testid="brand-logo">
        <div className="brand-flag-badge" aria-hidden="true">
          🇻🇳
        </div>
        <div className="brand-text-group">
          <div className="brand-title">
            <span>Vietnam News Map</span>
            <span className="brand-pill">Bản đồ tin tức</span>
          </div>
          <span className="brand-tagline">Tổng hợp sự kiện báo chí đa nguồn thời gian thực</span>
        </div>
      </div>

      {/* Filter Bar */}
      <FilterBar
        filters={filters}
        onUpdateFilters={onUpdateFilters}
        onProvinceSelect={onProvinceSelect}
        onOpenMobileFilter={onOpenMobileFilter}
      />
    </header>
  );
};
