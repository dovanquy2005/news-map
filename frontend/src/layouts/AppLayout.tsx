/**
 * Master Application Layout Component.
 * Orchestrates Map View, Virtualized Feed Panel, Search & Filter Bar,
 * Category Chips, Event Quick Popup / Mobile Bottom Sheet, and Event Detail Drawer.
 * Strictly complies with docs/08-ui-ux-responsive.md, TASK-036 through TASK-041.
 */

import React, { useState, useEffect, useCallback } from "react";
import { Header } from "../components/Header";
import { MapContainer } from "../components/MapContainer";
import { EventFeedView } from "../components/feed/EventFeedView";
import { CategoryChips } from "../components/filters/CategoryChips";
import { FilterDrawer } from "../components/filters/FilterDrawer";
import { EventQuickPopup } from "../components/events/EventQuickPopup";
import { EventBottomSheet } from "../components/events/EventBottomSheet";
import { EventDetailPanel } from "../components/events/EventDetailPanel";
import { SkipLink } from "../components/common/SkipLink";
import { useEventFilters } from "../hooks/useEventFilters";
import { apiService } from "../services/api";
import { NewsEventItem } from "../types";
import { MapViewportState } from "../types/map";
import { ProvinceInfo } from "../constants/provinces";

export const AppLayout: React.FC = () => {
  const { filters, debouncedQuery, updateFilters, resetFilters } = useEventFilters();

  const [events, setEvents] = useState<NewsEventItem[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<NewsEventItem | null>(null);
  const [detailEventId, setDetailEventId] = useState<string | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);
  const [isTabletFeedCollapsed, setIsTabletFeedCollapsed] = useState(false);
  const [currentBbox, setCurrentBbox] = useState<string | null | undefined>(undefined);
  const [mapController, setMapController] = useState<{ panTo: (lat: number, lng: number, zoom?: number) => void } | null>(null);

  // 1. Fetch Events when filters, search query, or viewport changes
  useEffect(() => {
    let isMounted = true;

    if (debouncedQuery && debouncedQuery.trim().length >= 2) {
      apiService.searchEvents(debouncedQuery.trim(), filters).then((res) => {
        if (isMounted) setEvents(res.data);
      });
    } else {
      apiService.getEvents(filters, currentBbox || undefined).then((res) => {
        if (isMounted) setEvents(res.data);
      });
    }

    return () => {
      isMounted = false;
    };
  }, [filters, debouncedQuery, currentBbox]);

  // 2. Synchronize selected event with URL (?event=) on mount
  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const eventParam = params.get("event");
    if (eventParam && events.length > 0) {
      const match = events.find((e) => e.id === eventParam);
      if (match) {
        setSelectedEvent(match);
      }
    }
  }, [events]);

  // 3. Selection Handlers
  const handleSelectEvent = useCallback((event: NewsEventItem) => {
    setSelectedEvent(event);

    // Sync to URL ?event=
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      params.set("event", event.id);
      window.history.replaceState({}, "", `${window.location.pathname}?${params.toString()}`);
    }

    // Pan map camera to event coordinates
    if (mapController) {
      mapController.panTo(event.latitude, event.longitude);
    }
  }, [mapController]);

  const handleOpenDetail = useCallback((eventId: string) => {
    setDetailEventId(eventId);
    setIsDetailOpen(true);
  }, []);

  const handleCloseDetail = useCallback(() => {
    setIsDetailOpen(false);
  }, []);

  const handleClosePreview = useCallback(() => {
    setSelectedEvent(null);
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      params.delete("event");
      const qs = params.toString();
      window.history.replaceState({}, "", qs ? `${window.location.pathname}?${qs}` : window.location.pathname);
    }
  }, []);

  // 4. Province selection pan/zoom
  const handleProvinceSelect = useCallback((province: ProvinceInfo) => {
    if (mapController) {
      mapController.panTo(province.lat, province.lng, province.zoom);
    }
  }, [mapController]);

  const handleViewportChange = useCallback((viewport: MapViewportState) => {
    setCurrentBbox(viewport.bboxString);
  }, []);

  return (
    <>
      <SkipLink />

      <Header
        filters={filters}
        onUpdateFilters={updateFilters}
        onProvinceSelect={handleProvinceSelect}
        onOpenMobileFilter={() => setIsMobileFilterOpen(true)}
      />

      <CategoryChips
        selectedCategory={filters.category || "ALL"}
        onSelectCategory={(catId) => updateFilters({ category: catId })}
      />

      <div className="app-layout">
        {/* Map Viewport Area */}
        <MapContainer
          events={events}
          selectedEventId={selectedEvent?.id}
          onEventSelect={handleSelectEvent}
          onViewportChange={handleViewportChange}
          onMapInstanceReady={setMapController}
        />

        {/* Desktop Quick Popup Preview */}
        {selectedEvent && !isDetailOpen && (
          <EventQuickPopup
            event={selectedEvent}
            onOpenDetail={handleOpenDetail}
            onClose={handleClosePreview}
          />
        )}

        {/* Mobile Swipeable Bottom Sheet */}
        <EventBottomSheet
          event={selectedEvent}
          isOpen={Boolean(selectedEvent) && !isDetailOpen}
          onOpenDetail={handleOpenDetail}
          onClose={handleClosePreview}
        />

        {/* Event Feed List (Desktop Split / Tablet Collapsible) */}
        <EventFeedView
          events={events}
          selectedEventId={selectedEvent?.id}
          onSelectEvent={handleSelectEvent}
          isTabletCollapsed={isTabletFeedCollapsed}
          onToggleTabletFeed={() => setIsTabletFeedCollapsed((prev) => !prev)}
        />

        {/* Event Detail Slide-Over Drawer */}
        <EventDetailPanel
          eventId={detailEventId}
          isOpen={isDetailOpen}
          onClose={handleCloseDetail}
          onSelectRelatedEvent={(relId) => {
            const rel = events.find((e) => e.id === relId);
            if (rel) handleSelectEvent(rel);
            setDetailEventId(relId);
          }}
        />

        {/* Mobile / Tablet Filter Drawer Modal */}
        <FilterDrawer
          isOpen={isMobileFilterOpen}
          filters={filters}
          onUpdateFilters={updateFilters}
          onResetFilters={resetFilters}
          onClose={() => setIsMobileFilterOpen(false)}
          onProvinceSelect={handleProvinceSelect}
        />
      </div>
    </>
  );
};
