/**
 * 63 Vietnamese Provinces and Centroids.
 * Used for ProvinceSelect dropdown, quick map fly-to, and spatial filtering.
 */

export interface ProvinceInfo {
  name: string;
  code: string;
  region: "Miền Bắc" | "Miền Trung" | "Miền Nam";
  lat: number;
  lng: number;
  zoom: number;
}

export const VIETNAM_PROVINCES: ProvinceInfo[] = [
  // Miền Bắc
  { name: "Hà Nội", code: "HN", region: "Miền Bắc", lat: 21.0285, lng: 105.8542, zoom: 12 },
  { name: "Hải Phòng", code: "HP", region: "Miền Bắc", lat: 20.8449, lng: 106.6881, zoom: 12 },
  { name: "Quảng Ninh", code: "QN", region: "Miền Bắc", lat: 21.0069, lng: 107.2925, zoom: 11 },
  { name: "Bắc Ninh", code: "BN", region: "Miền Bắc", lat: 21.1861, lng: 106.0763, zoom: 12 },
  { name: "Hà Nam", code: "HNM", region: "Miền Bắc", lat: 20.5835, lng: 105.9237, zoom: 12 },
  { name: "Hải Dương", code: "HD", region: "Miền Bắc", lat: 20.9373, lng: 106.3151, zoom: 12 },
  { name: "Hưng Yên", code: "HY", region: "Miền Bắc", lat: 20.6462, lng: 106.0511, zoom: 12 },
  { name: "Nam Định", code: "ND", region: "Miền Bắc", lat: 20.4345, lng: 106.1776, zoom: 12 },
  { name: "Ninh Bình", code: "NB", region: "Miền Bắc", lat: 20.2506, lng: 105.9745, zoom: 12 },
  { name: "Thái Bình", code: "TB", region: "Miền Bắc", lat: 20.4463, lng: 106.3366, zoom: 12 },
  { name: "Vĩnh Phúc", code: "VP", region: "Miền Bắc", lat: 21.3609, lng: 105.5474, zoom: 12 },
  { name: "Hà Giang", code: "HG", region: "Miền Bắc", lat: 22.8233, lng: 104.9839, zoom: 10 },
  { name: "Cao Bằng", code: "CB", region: "Miền Bắc", lat: 22.6666, lng: 106.2639, zoom: 10 },
  { name: "Bắc Kạn", code: "BK", region: "Miền Bắc", lat: 22.1471, lng: 105.8348, zoom: 11 },
  { name: "Lạng Sơn", code: "LS", region: "Miền Bắc", lat: 21.8537, lng: 106.7615, zoom: 11 },
  { name: "Tuyên Quang", code: "TQ", region: "Miền Bắc", lat: 21.8236, lng: 105.2180, zoom: 11 },
  { name: "Thái Nguyên", code: "TN", region: "Miền Bắc", lat: 21.5942, lng: 105.8482, zoom: 11 },
  { name: "Phú Thọ", code: "PT", region: "Miền Bắc", lat: 21.3228, lng: 105.2280, zoom: 11 },
  { name: "Bắc Giang", code: "BG", region: "Miền Bắc", lat: 21.2731, lng: 106.1946, zoom: 11 },
  { name: "Lào Cai", code: "LC", region: "Miền Bắc", lat: 22.4856, lng: 103.9707, zoom: 11 },
  { name: "Yên Bái", code: "YB", region: "Miền Bắc", lat: 21.7168, lng: 104.8973, zoom: 11 },
  { name: "Điện Biên", code: "DB", region: "Miền Bắc", lat: 21.3869, lng: 103.0232, zoom: 11 },
  { name: "Hòa Bình", code: "HB", region: "Miền Bắc", lat: 20.8172, lng: 105.3376, zoom: 11 },
  { name: "Lai Châu", code: "LCH", region: "Miền Bắc", lat: 22.3963, lng: 103.4684, zoom: 11 },
  { name: "Sơn La", code: "SL", region: "Miền Bắc", lat: 21.3256, lng: 103.9188, zoom: 10 },

  // Miền Trung
  { name: "Đà Nẵng", code: "DN", region: "Miền Trung", lat: 16.0544, lng: 108.2022, zoom: 12 },
  { name: "Thanh Hóa", code: "TH", region: "Miền Trung", lat: 19.8067, lng: 105.7852, zoom: 11 },
  { name: "Nghệ An", code: "NA", region: "Miền Trung", lat: 18.6734, lng: 105.6813, zoom: 10 },
  { name: "Hà Tĩnh", code: "HT", region: "Miền Trung", lat: 18.3560, lng: 105.9058, zoom: 11 },
  { name: "Quảng Bình", code: "QB", region: "Miền Trung", lat: 17.4739, lng: 106.6000, zoom: 11 },
  { name: "Quảng Trị", code: "QT", region: "Miền Trung", lat: 16.7504, lng: 107.1856, zoom: 11 },
  { name: "Thừa Thiên Huế", code: "TTH", region: "Miền Trung", lat: 16.4637, lng: 107.5909, zoom: 12 },
  { name: "Quảng Nam", code: "QNA", region: "Miền Trung", lat: 15.5994, lng: 108.4811, zoom: 11 },
  { name: "Quảng Ngãi", code: "QNG", region: "Miền Trung", lat: 15.1205, lng: 108.7923, zoom: 11 },
  { name: "Bình Định", code: "BDH", region: "Miền Trung", lat: 13.7830, lng: 109.2197, zoom: 11 },
  { name: "Phú Yên", code: "PY", region: "Miền Trung", lat: 13.0882, lng: 109.3142, zoom: 11 },
  { name: "Khánh Hòa", code: "KH", region: "Miền Trung", lat: 12.2388, lng: 109.1967, zoom: 11 },
  { name: "Ninh Thuận", code: "NT", region: "Miền Trung", lat: 11.5647, lng: 108.9882, zoom: 11 },
  { name: "Bình Thuận", code: "BT", region: "Miền Trung", lat: 10.9805, lng: 108.2022, zoom: 11 },
  { name: "Kon Tum", code: "KT", region: "Miền Trung", lat: 14.3497, lng: 108.0002, zoom: 11 },
  { name: "Gia Lai", code: "GL", region: "Miền Trung", lat: 13.9833, lng: 108.0000, zoom: 11 },
  { name: "Đắk Lắk", code: "DL", region: "Miền Trung", lat: 12.6667, lng: 108.0500, zoom: 11 },
  { name: "Đắk Nông", code: "DNO", region: "Miền Trung", lat: 12.0044, lng: 107.6875, zoom: 11 },
  { name: "Lâm Đồng", code: "LD", region: "Miền Trung", lat: 11.9404, lng: 108.4583, zoom: 11 },

  // Miền Nam
  { name: "TP. Hồ Chí Minh", code: "HCM", region: "Miền Nam", lat: 10.8231, lng: 106.6297, zoom: 12 },
  { name: "Cần Thơ", code: "CT", region: "Miền Nam", lat: 10.0452, lng: 105.7469, zoom: 12 },
  { name: "Bình Phước", code: "BP", region: "Miền Nam", lat: 11.7511, lng: 106.9013, zoom: 11 },
  { name: "Bình Dương", code: "BD", region: "Miền Nam", lat: 11.1644, lng: 106.6572, zoom: 12 },
  { name: "Đồng Nai", code: "DNA", region: "Miền Nam", lat: 11.0500, lng: 107.0333, zoom: 11 },
  { name: "Tây Ninh", code: "TNH", region: "Miền Nam", lat: 11.3100, lng: 106.0983, zoom: 11 },
  { name: "Bà Rịa - Vũng Tàu", code: "BRVT", region: "Miền Nam", lat: 10.5417, lng: 107.2430, zoom: 11 },
  { name: "Long An", code: "LA", region: "Miền Nam", lat: 10.5360, lng: 106.4114, zoom: 11 },
  { name: "Đồng Tháp", code: "DT", region: "Miền Nam", lat: 10.4594, lng: 105.6358, zoom: 11 },
  { name: "Tiền Giang", code: "TG", region: "Miền Nam", lat: 10.4286, lng: 106.3423, zoom: 11 },
  { name: "An Giang", code: "AG", region: "Miền Nam", lat: 10.5216, lng: 105.1259, zoom: 11 },
  { name: "Bến Tre", code: "BTR", region: "Miền Nam", lat: 10.2434, lng: 106.3753, zoom: 11 },
  { name: "Vĩnh Long", code: "VL", region: "Miền Nam", lat: 10.2537, lng: 105.9722, zoom: 11 },
  { name: "Hậu Giang", code: "HAG", region: "Miền Nam", lat: 9.7844, lng: 105.4701, zoom: 11 },
  { name: "Kiên Giang", code: "KG", region: "Miền Nam", lat: 10.0125, lng: 105.0809, zoom: 10 },
  { name: "Sóc Trăng", code: "ST", region: "Miền Nam", lat: 9.6033, lng: 105.9800, zoom: 11 },
  { name: "Trà Vinh", code: "TV", region: "Miền Nam", lat: 9.9347, lng: 106.3456, zoom: 11 },
  { name: "Bạc Liêu", code: "BL", region: "Miền Nam", lat: 9.2941, lng: 105.7278, zoom: 11 },
  { name: "Cà Mau", code: "CM", region: "Miền Nam", lat: 9.1769, lng: 105.1524, zoom: 11 },
];
