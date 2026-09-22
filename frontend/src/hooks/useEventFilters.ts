/**
 * Hook for managing search & filter state with two-way URL query synchronization.
 * Strictly complies with TASK-039 and docs/08-ui-ux-responsive.md.
 */

import { useState, useEffect, useCallback, useTransition } from "react";
import { FilterState } from "../types";

export const TIME_PRESETS: { id: string; label: string; hours?: number; days?: number }[] = [
  { id: "1h", label: "1 giờ qua", hours: 1 },
  { id: "6h", label: "6 giờ qua", hours: 6 },
  { id: "24h", label: "24 giờ qua (Mặc định)", hours: 24 },
  { id: "3d", label: "3 ngày qua", days: 3 },
  { id: "7d", label: "7 ngày qua", days: 7 },
  { id: "30d", label: "30 ngày qua", days: 30 },
  { id: "all", label: "Tất cả thời gian" },
];

export const CATEGORIES_LIST = [
  { id: "ALL", label: "Tất cả sự kiện", color: "#2563eb" },
  { id: "FIRE", label: "Cháy nổ", color: "#ef4444" },
  { id: "ACCIDENT", label: "Tai nạn", color: "#f97316" },
  { id: "WEATHER", label: "Thời tiết / Thiên tai", color: "#0ea5e9" },
  { id: "TRAFFIC", label: "Giao thông", color: "#f59e0b" },
  { id: "SECURITY", label: "An ninh", color: "#8b5cf6" },
  { id: "HEALTH", label: "Y tế", color: "#10b981" },
  { id: "OTHER", label: "Khác", color: "#64748b" },
];

export function useEventFilters() {
  const [, startTransition] = useTransition();

  // Read initial filters from browser URL query params
  const getInitialFilters = (): FilterState => {
    if (typeof window === "undefined") {
      return {
        searchQuery: "",
        timePreset: "24h",
        category: "ALL",
        province: "",
        minSources: 1,
        minArticles: 1,
      };
    }

    const params = new URLSearchParams(window.location.search);
    return {
      searchQuery: params.get("q") || "",
      timePreset: params.get("preset") || "24h",
      fromDate: params.get("from") || undefined,
      toDate: params.get("to") || undefined,
      province: params.get("province") || "",
      category: params.get("category") || "ALL",
      status: params.get("status") || "",
      minSources: parseInt(params.get("minSources") || "1", 10),
      minArticles: parseInt(params.get("minArticles") || "1", 10),
    };
  };

  const [filters, setFilters] = useState<FilterState>(getInitialFilters);
  const [debouncedQuery, setDebouncedQuery] = useState(filters.searchQuery);

  // Sync debounced search query (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(filters.searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [filters.searchQuery]);

  // Sync state to browser URL without full page reload
  const syncToUrl = useCallback((newFilters: FilterState) => {
    if (typeof window === "undefined") return;

    startTransition(() => {
      const params = new URLSearchParams(window.location.search);

      if (newFilters.searchQuery) params.set("q", newFilters.searchQuery);
      else params.delete("q");

      if (newFilters.timePreset && newFilters.timePreset !== "24h") {
        params.set("preset", newFilters.timePreset);
      } else {
        params.delete("preset");
      }

      if (newFilters.province) params.set("province", newFilters.province);
      else params.delete("province");

      if (newFilters.category && newFilters.category !== "ALL") {
        params.set("category", newFilters.category);
      } else {
        params.delete("category");
      }

      if (newFilters.minSources > 1) {
        params.set("minSources", String(newFilters.minSources));
      } else {
        params.delete("minSources");
      }

      const queryString = params.toString();
      const newUrl = queryString ? `${window.location.pathname}?${queryString}` : window.location.pathname;
      window.history.replaceState({}, "", newUrl);
    });
  }, []);

  const updateFilters = useCallback(
    (partial: Partial<FilterState>) => {
      setFilters((prev) => {
        const next = { ...prev, ...partial };
        syncToUrl(next);
        return next;
      });
    },
    [syncToUrl]
  );

  const resetFilters = useCallback(() => {
    const defaults: FilterState = {
      searchQuery: "",
      timePreset: "24h",
      category: "ALL",
      province: "",
      minSources: 1,
      minArticles: 1,
    };
    setFilters(defaults);
    syncToUrl(defaults);
  }, [syncToUrl]);

  return {
    filters,
    debouncedQuery,
    updateFilters,
    resetFilters,
  };
}
