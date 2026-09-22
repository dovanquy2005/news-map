/**
 * Vietnam News Map — Map Types and Geospatial Definitions
 * Strictly complies with docs/08-ui-ux-responsive.md and tasks/TASK-035.
 */

export interface GeoPoint {
  lat: number;
  lng: number;
}

export interface MapBounds {
  minLng: number;
  minLat: number;
  maxLng: number;
  maxLat: number;
}

export interface MapViewportState {
  center: GeoPoint;
  zoom: number;
  bounds: MapBounds | null;
  bboxString: string | null;
}

/**
 * Default camera center centered on Vietnam (Da Nang / Central Region).
 */
export const DEFAULT_VIETNAM_CENTER: GeoPoint = {
  lat: 16.0471,
  lng: 107.8350,
};

/**
 * Default national overview zoom level.
 */
export const DEFAULT_VIETNAM_ZOOM = 6;

/**
 * Bounds restriction bounding box for Vietnam and East Sea islands.
 */
export const VIETNAM_BOUNDS_RESTRICTION = {
  north: 24.5,
  south: 8.0,
  west: 101.5,
  east: 112.5,
};
