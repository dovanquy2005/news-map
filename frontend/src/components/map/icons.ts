/**
 * SVG Marker Icon Generator for Vietnam News Map.
 * Provides distinct category-themed SVG pins and cluster graphics.
 * Strictly complies with TASK-036 and Light Theme palette.
 */


export interface CategoryVisualConfig {
  nameVi: string;
  fillColor: string;
  borderColor: string;
  iconSvg: string;
  badgeBg: string;
  badgeText: string;
  badgeBorder: string;
}

export const CATEGORY_CONFIG: Record<string, CategoryVisualConfig> = {
  FIRE: {
    nameVi: "Cháy nổ",
    fillColor: "#ef4444",
    borderColor: "#b91c1c",
    badgeBg: "#fef2f2",
    badgeText: "#b91c1c",
    badgeBorder: "#fecaca",
    iconSvg: `<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>`,
  },
  ACCIDENT: {
    nameVi: "Tai nạn",
    fillColor: "#f97316",
    borderColor: "#c2410c",
    badgeBg: "#fff7ed",
    badgeText: "#c2410c",
    badgeBorder: "#fed7aa",
    iconSvg: `<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>`,
  },
  WEATHER: {
    nameVi: "Thiên tai / Thời tiết",
    fillColor: "#0ea5e9",
    borderColor: "#0369a1",
    badgeBg: "#f0f9ff",
    badgeText: "#0369a1",
    badgeBorder: "#bae6fd",
    iconSvg: `<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/><path d="m11 15-3 5"/><path d="m15 15-3 5"/>`,
  },
  TRAFFIC: {
    nameVi: "Giao thông",
    fillColor: "#f59e0b",
    borderColor: "#b45309",
    badgeBg: "#fffbeb",
    badgeText: "#b45309",
    badgeBorder: "#fde68a",
    iconSvg: `<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="12" cy="8" r="2"/><circle cx="12" cy="16" r="2"/>`,
  },
  SECURITY: {
    nameVi: "An ninh trật tự",
    fillColor: "#8b5cf6",
    borderColor: "#6d28d9",
    badgeBg: "#faf5ff",
    badgeText: "#6d28d9",
    badgeBorder: "#ddd6fe",
    iconSvg: `<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>`,
  },
  HEALTH: {
    nameVi: "Y tế / Dịch bệnh",
    fillColor: "#10b981",
    borderColor: "#047857",
    badgeBg: "#ecfdf5",
    badgeText: "#047857",
    badgeBorder: "#a7f3d0",
    iconSvg: `<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>`,
  },
  OTHER: {
    nameVi: "Khác",
    fillColor: "#64748b",
    borderColor: "#475569",
    badgeBg: "#f8fafc",
    badgeText: "#475569",
    badgeBorder: "#e2e8f0",
    iconSvg: `<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>`,
  },
};

/**
 * Returns Category visual properties, with fallback to OTHER.
 */
export function getCategoryConfig(category: string): CategoryVisualConfig {
  const upper = (category || "").toUpperCase();
  return CATEGORY_CONFIG[upper] || CATEGORY_CONFIG.OTHER;
}

/**
 * Generates an SVG Data URI for Google Maps Marker icon.
 */
export function createCategoryMarkerSvgUri(
  category: string,
  isApproximate: boolean = false,
  isSelected: boolean = false
): string {
  const config = getCategoryConfig(category);
  const size = isSelected ? 44 : 36;
  const strokeDash = isApproximate ? `stroke-dasharray="3,2" stroke-width="2.5"` : `stroke-width="2"`;
  const ringStroke = isSelected ? "#2563eb" : config.borderColor;

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size + 8}" viewBox="0 0 36 44" fill="none">
      <defs>
        <filter id="shadow" x="0" y="0" width="36" height="44" filterUnits="userSpaceOnUse">
          <feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#0f172a" flood-opacity="0.25"/>
        </filter>
      </defs>
      <path d="M18 42C18 42 32 27.5 32 17C32 9.26801 25.732 3 18 3C10.268 3 4 9.26801 4 17C4 27.5 18 42 18 42Z" 
            fill="${config.fillColor}" 
            stroke="${ringStroke}" 
            ${strokeDash} 
            filter="url(#shadow)"/>
      <circle cx="18" cy="17" r="10" fill="#ffffff" opacity="0.95"/>
      <g transform="translate(11, 10) scale(0.6)" stroke="${config.borderColor}" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
        ${config.iconSvg}
      </g>
    </svg>
  `.trim();

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}
