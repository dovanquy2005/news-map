/**
 * Hook for fetching and caching full event detail data.
 * Complies with TASK-038.
 */

import { useState, useEffect } from "react";
import { EventDetailItem } from "../types";
import { apiService } from "../services/api";

const detailCache = new Map<string, EventDetailItem>();

export function useEventDetail(eventId: string | null) {
  const [detail, setDetail] = useState<EventDetailItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!eventId) {
      setDetail(null);
      setLoading(false);
      setError(null);
      return;
    }

    if (detailCache.has(eventId)) {
      setDetail(detailCache.get(eventId)!);
      setLoading(false);
      return;
    }

    let isMounted = true;
    setLoading(true);
    setError(null);

    apiService
      .getEventDetail(eventId)
      .then((data) => {
        if (!isMounted) return;
        detailCache.set(eventId, data);
        setDetail(data);
        setLoading(false);
      })
      .catch((err) => {
        if (!isMounted) return;
        setError(err instanceof Error ? err.message : "Không thể tải chi tiết sự kiện");
        setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [eventId]);

  return { detail, loading, error };
}
