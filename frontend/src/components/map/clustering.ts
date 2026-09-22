/**
 * Marker Clustering Manager using @googlemaps/markerclusterer.
 * Efficiently aggregates markers into responsive cluster bubbles when zoomed out.
 * Strictly complies with TASK-036.
 */

import { MarkerClusterer } from "@googlemaps/markerclusterer";

export interface ClusterManagerOptions {
  map: google.maps.Map;
  onClusterClick?: (clusterBounds: google.maps.LatLngBounds) => void;
}

export class NewsMapClusterManager {
  private clusterer: MarkerClusterer | null = null;
  private markersMap: Map<string, google.maps.Marker> = new Map();

  constructor(options: ClusterManagerOptions) {
    if (typeof google === "undefined" || !google.maps) {
      return;
    }

    this.clusterer = new MarkerClusterer({
      map: options.map,
      onClusterClick: (_event, cluster, map) => {
        const bounds = cluster.bounds;
        if (bounds) {
          map.fitBounds(bounds, { top: 60, bottom: 60, left: 60, right: 60 });
          if (options.onClusterClick) {
            options.onClusterClick(bounds);
          }
        }
      },
    });
  }

  /**
   * Replaces current markers with new set.
   */
  public setMarkers(markers: google.maps.Marker[]): void {
    if (!this.clusterer) return;
    this.clusterer.clearMarkers();
    this.markersMap.clear();

    markers.forEach((m, idx) => {
      this.markersMap.set(String(idx), m);
    });

    this.clusterer.addMarkers(markers);
  }

  /**
   * Cleans up all markers and detaches clusterer from map.
   */
  public destroy(): void {
    if (this.clusterer) {
      this.clusterer.clearMarkers();
      this.clusterer.setMap(null);
      this.clusterer = null;
    }
    this.markersMap.clear();
  }
}
