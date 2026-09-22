/**
 * Light Cartography Map Styles for Google Maps.
 * Clean, soft silver-blue waterways, unobtrusive terrain and road network
 * designed specifically so colored event markers and cluster bubbles stand out vividly.
 */

export const LIGHT_CARTOGRAPHY_MAP_STYLES: google.maps.MapTypeStyle[] = [
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ color: "#dbeafe" }], // Pale pastel cyan/blue
  },
  {
    featureType: "water",
    elementType: "labels.text.fill",
    stylers: [{ color: "#60a5fa" }],
  },
  {
    featureType: "landscape",
    elementType: "geometry",
    stylers: [{ color: "#f8fafc" }], // Crisp light slate background
  },
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [{ color: "#ffffff" }],
  },
  {
    featureType: "road.highway",
    elementType: "geometry",
    stylers: [{ color: "#f1f5f9" }],
  },
  {
    featureType: "road.highway",
    elementType: "geometry.stroke",
    stylers: [{ color: "#e2e8f0" }],
  },
  {
    featureType: "road.arterial",
    elementType: "geometry",
    stylers: [{ color: "#ffffff" }],
  },
  {
    featureType: "road.local",
    elementType: "geometry",
    stylers: [{ color: "#ffffff" }],
  },
  {
    featureType: "poi",
    elementType: "geometry",
    stylers: [{ color: "#f1f5f9" }],
  },
  {
    featureType: "poi.park",
    elementType: "geometry",
    stylers: [{ color: "#ecfdf5" }], // Soft light green for parks
  },
  {
    featureType: "poi.park",
    elementType: "labels.text.fill",
    stylers: [{ color: "#059669" }],
  },
  {
    featureType: "administrative",
    elementType: "geometry.stroke",
    stylers: [{ color: "#cbd5e1" }, { weight: 0.8 }],
  },
  {
    featureType: "administrative.country",
    elementType: "geometry.stroke",
    stylers: [{ color: "#94a3b8" }, { weight: 1.2 }],
  },
  {
    featureType: "administrative.province",
    elementType: "geometry.stroke",
    stylers: [{ color: "#cbd5e1" }, { weight: 1 }],
  },
  {
    featureType: "all",
    elementType: "labels.text.fill",
    stylers: [{ color: "#475569" }],
  },
  {
    featureType: "all",
    elementType: "labels.text.stroke",
    stylers: [{ color: "#ffffff" }, { weight: 3 }],
  },
  {
    featureType: "transit",
    elementType: "geometry",
    stylers: [{ color: "#f1f5f9" }],
  },
];

// Retain alias for backward compatibility
export const SUBDUED_DARK_MAP_STYLES = LIGHT_CARTOGRAPHY_MAP_STYLES;
