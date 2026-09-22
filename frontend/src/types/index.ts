/**
 * Data contracts strictly matching docs/09-api-contracts.md and prd.md
 */

export interface LocationCoordinates {
  latitude: number;
  longitude: number;
}

export interface ViewportBounds {
  north: number;
  south: number;
  east: number;
  west: number;
}

export type EventCategory =
  | "ACCIDENT"
  | "FIRE"
  | "WEATHER"
  | "TRAFFIC"
  | "SECURITY"
  | "HEALTH"
  | "OTHER";

export type ConfidenceLevel = "HIGH" | "MEDIUM" | "LOW";

export interface NewsEventItem {
  id: string;
  title: string;
  category: EventCategory | string;
  summary: string | null;
  latitude: number;
  longitude: number;
  location_label: string | null;
  province?: string | null;
  is_approximate?: boolean;
  confidence_score: number;
  confidence_level?: ConfidenceLevel;
  article_count: number;
  source_count: number;
  occurred_at: string;
  first_reported_at?: string;
  last_updated_at?: string;
  status: "ACTIVE" | "VERIFIED" | "RESOLVED" | "DISPUTED" | string;
}

export interface EventTimelineItem {
  id: string;
  milestone_type: "OCCURRED" | "FIRST_REPORTED" | "SOURCE_UPDATE" | "OFFICIAL_STATEMENT";
  timestamp: string;
  description: string;
  source_name?: string;
  source_url?: string;
}

export interface EventSourceItem {
  id: string;
  name: string;
  publisher: string;
  url: string;
  title: string;
  published_at: string;
  reliability_score?: number;
  is_primary?: boolean;
}

export interface EventConfidenceBreakdown {
  score: number;
  level: ConfidenceLevel;
  factors_positive: string[];
  factors_warning: string[];
  source_diversity_ratio: number;
  geocoding_precision: string;
}

export interface EventDetailItem extends NewsEventItem {
  confidence_breakdown?: EventConfidenceBreakdown;
  timeline: EventTimelineItem[];
  sources: EventSourceItem[];
  related_events?: NewsEventItem[];
  has_conflicting_reports?: boolean;
  conflict_details?: string | null;
}

export interface PaginationMeta {
  limit: number;
  offset: number;
  total: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
}

export interface FilterState {
  searchQuery: string;
  timePreset: string;
  fromDate?: string;
  toDate?: string;
  province?: string;
  category?: string;
  status?: string;
  minSources: number;
  minArticles: number;
}

export type SortOption = "NEWEST" | "MOST_SOURCES" | "MOST_ARTICLES";
