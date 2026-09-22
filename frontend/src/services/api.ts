/**
 * API client and fallback demo data provider.
 * Strictly adheres to docs/09-api-contracts.md.
 */

import {
  NewsEventItem,
  EventDetailItem,
  PaginatedResponse,
  FilterState,
} from "../types";

const API_BASE = "/api/v1";

/**
 * Realistic Vietnam News Events for demo & fallback mode when backend DB is empty.
 * Matches exact coordinates in major cities and provinces of Vietnam.
 */
export const MOCK_VIETNAM_EVENTS: NewsEventItem[] = [
  {
    id: "evt-001",
    title: "Cháy lớn tại kho xưởng hóa chất khu công nghiệp Sài Đồng, khống chế sau 3 giờ",
    category: "FIRE",
    summary:
      "Vụ hỏa hoạn bùng phát lúc 14h tại kho chứa hóa chất và bao bì KCN Sài Đồng, quận Long Biên. Hơn 15 xe chữa cháy cùng 80 chiến sĩ PCCC đã có mặt kịp thời. Không có thương vong về người.",
    latitude: 21.0378,
    longitude: 105.9189,
    location_label: "KCN Sài Đồng, Quận Long Biên, Hà Nội",
    province: "Hà Nội",
    is_approximate: false,
    confidence_score: 0.94,
    confidence_level: "HIGH",
    article_count: 14,
    source_count: 8,
    occurred_at: new Date(Date.now() - 35 * 60 * 1000).toISOString(),
    status: "RESOLVED",
  },
  {
    id: "evt-002",
    title: "Va chạm liên hoàn 4 ô tô trên cầu Sài Gòn hướng về Thủ Đức gây ùn ứ kéo dài",
    category: "TRAFFIC",
    summary:
      "Vào giờ cao điểm sáng, một vụ tông liên hoàn giữa 2 xe con và 2 xe tải nhẹ trên dốc cầu Sài Gòn khiến giao thông tê liệt hơn 2km từ ngã tư Hàng Xanh.",
    latitude: 10.7997,
    longitude: 106.7225,
    location_label: "Cầu Sài Gòn, Bình Thạnh - TP. Thủ Đức",
    province: "TP. Hồ Chí Minh",
    is_approximate: false,
    confidence_score: 0.89,
    confidence_level: "HIGH",
    article_count: 9,
    source_count: 6,
    occurred_at: new Date(Date.now() - 75 * 60 * 1000).toISOString(),
    status: "ACTIVE",
  },
  {
    id: "evt-003",
    title: "Mưa lớn cực đoan kèm lốc xoáy làm tốc mái hơn 40 ngôi nhà ven biển Sơn Trà",
    category: "WEATHER",
    summary:
      "Đợt dông lốc quét qua địa bàn quận Sơn Trà vào rạng sáng, làm gãy đổ nhiều cây xanh lớn trên đường Hoàng Sa và hư hại hơn 40 mái nhà dân. Lực lượng cứu nạn đang hỗ trợ bà con.",
    latitude: 16.1032,
    longitude: 108.2612,
    location_label: "Bán đảo Sơn Trà, Quận Sơn Trà, Đà Nẵng",
    province: "Đà Nẵng",
    is_approximate: false,
    confidence_score: 0.92,
    confidence_level: "HIGH",
    article_count: 11,
    source_count: 7,
    occurred_at: new Date(Date.now() - 140 * 60 * 1000).toISOString(),
    status: "ACTIVE",
  },
  {
    id: "evt-004",
    title: "Xe container lật chắn ngang đường dẫn cầu Bãi Cháy, lực lượng chức năng phân luồng khẩn",
    category: "ACCIDENT",
    summary:
      "Xe đầu kéo chở bồn nặng bất ngờ mất lái lật nghiêng tại khúc cua đường dẫn lên cầu Bãi Cháy hướng Hòn Gai. Tài xế được người dân giải cứu an toàn.",
    latitude: 20.9587,
    longitude: 107.0543,
    location_label: "Dẫn cầu Bãi Cháy, TP. Hạ Long, Quảng Ninh",
    province: "Quảng Ninh",
    is_approximate: false,
    confidence_score: 0.88,
    confidence_level: "HIGH",
    article_count: 8,
    source_count: 5,
    occurred_at: new Date(Date.now() - 210 * 60 * 1000).toISOString(),
    status: "ACTIVE",
  },
  {
    id: "evt-005",
    title: "Triệt phá đường dây buôn bán hàng giả quy mô lớn tại cảng Cát Lái",
    category: "SECURITY",
    summary:
      "Cục Cảnh sát kinh tế phối hợp Hải quan TP.HCM thu giữ 6 container chứa thiết bị điện tử và phụ tùng giả mạo nhãn hiệu quốc tế, trị giá ước tính trên 30 tỷ đồng.",
    latitude: 10.7634,
    longitude: 106.7865,
    location_label: "Cảng Cát Lái, TP. Thủ Đức, TP. Hồ Chí Minh",
    province: "TP. Hồ Chí Minh",
    is_approximate: false,
    confidence_score: 0.95,
    confidence_level: "HIGH",
    article_count: 16,
    source_count: 10,
    occurred_at: new Date(Date.now() - 320 * 60 * 1000).toISOString(),
    status: "VERIFIED",
  },
  {
    id: "evt-006",
    title: "Cứu sống kịp thời bệnh nhân sốc phản vệ độ 4 do ong đốt tại Cần Thơ",
    category: "HEALTH",
    summary:
      "Bệnh viện Đa khoa Trung ương Cần Thơ tiếp nhận bệnh nhân nam 48 tuổi trong tình trạng mạch 0, huyết áp không đo được. Sau 45 phút hồi sức tích cực và dùng adrenalin, bệnh nhân đã qua cơn nguy kịch.",
    latitude: 10.0305,
    longitude: 105.7725,
    location_label: "BVĐK Trung ương Cần Thơ, Quận Ninh Kiều, Cần Thơ",
    province: "Cần Thơ",
    is_approximate: false,
    confidence_score: 0.91,
    confidence_level: "HIGH",
    article_count: 6,
    source_count: 4,
    occurred_at: new Date(Date.now() - 400 * 60 * 1000).toISOString(),
    status: "RESOLVED",
  },
  {
    id: "evt-007",
    title: "Sạt lở đất đá nghiêm trọng chia cắt đèo Prenn, khẩn trương thông tuyến",
    category: "WEATHER",
    summary:
      "Khối lượng đất đá khoảng 300m³ từ taluy dương sạt xuống mặt đường đèo Prenn sau cơn mưa dông lớn. Đội duy tu giao thông Lâm Đồng đang huy động máy ủi xử lý.",
    latitude: 11.9056,
    longitude: 108.4419,
    location_label: "Đèo Prenn, TP. Đà Lạt, Lâm Đồng",
    province: "Lâm Đồng",
    is_approximate: true,
    confidence_score: 0.85,
    confidence_level: "MEDIUM",
    article_count: 7,
    source_count: 5,
    occurred_at: new Date(Date.now() - 500 * 60 * 1000).toISOString(),
    status: "ACTIVE",
  },
  {
    id: "evt-008",
    title: "Hỏa hoạn thiêu rụi quán karaoke trên đường Nguyễn Khang, 4 người thoát nạn",
    category: "FIRE",
    summary:
      "Lửa bùng lên từ biển quảng cáo tầng 2 rồi nhanh chóng lan ra toàn bộ mặt tiền quán. Lực lượng cứu nạn dùng xe thang tiếp cận đưa 4 nhân viên xuống đất an toàn.",
    latitude: 21.0118,
    longitude: 105.7994,
    location_label: "Đường Nguyễn Khang, Quận Cầu Giấy, Hà Nội",
    province: "Hà Nội",
    is_approximate: false,
    confidence_score: 0.93,
    confidence_level: "HIGH",
    article_count: 12,
    source_count: 8,
    occurred_at: new Date(Date.now() - 650 * 60 * 1000).toISOString(),
    status: "RESOLVED",
  },
  {
    id: "evt-009",
    title: "Thông xe kỹ thuật cầu vượt nút giao Nguyễn Văn Linh - Nguyễn Hữu Thọ",
    category: "OTHER",
    summary:
      "Sáng nay, hầm chui HC2 thuộc nút giao trọng điểm Nam Sài Gòn chính thức cho các phương tiện lưu thông, giảm áp lực kẹt xe hướng từ Nhà Bè về Quận 4.",
    latitude: 10.7303,
    longitude: 106.7028,
    location_label: "Nút giao Nguyễn Văn Linh, Quận 7, TP. Hồ Chí Minh",
    province: "TP. Hồ Chí Minh",
    is_approximate: false,
    confidence_score: 0.97,
    confidence_level: "HIGH",
    article_count: 18,
    source_count: 11,
    occurred_at: new Date(Date.now() - 800 * 60 * 1000).toISOString(),
    status: "VERIFIED",
  },
  {
    id: "evt-010",
    title: "Phát hiện tàu cá gặp nạn trôi dạt cách đảo Cồn Cỏ 15 hải lý, lai dắt vào bờ",
    category: "WEATHER",
    summary:
      "Tàu cá số hiệu QB-92837 bị hỏng máy chính giữa sóng to gió lớn. Bộ đội biên phòng Quảng Trị phối hợp tàu cứu nạn SAR 412 đã tiếp cận và hỗ trợ 6 thuyền viên an toàn.",
    latitude: 17.1582,
    longitude: 107.3421,
    location_label: "Khu vực đảo Cồn Cỏ, Quảng Trị",
    province: "Quảng Trị",
    is_approximate: true,
    confidence_score: 0.82,
    confidence_level: "MEDIUM",
    article_count: 5,
    source_count: 4,
    occurred_at: new Date(Date.now() - 950 * 60 * 1000).toISOString(),
    status: "RESOLVED",
  },
];

/**
 * Builds mock detail representation matching Section 16 of prd.md.
 */
export function getMockEventDetail(eventId: string): EventDetailItem {
  const base =
    MOCK_VIETNAM_EVENTS.find((e) => e.id === eventId) || MOCK_VIETNAM_EVENTS[0];

  return {
    ...base,
    confidence_breakdown: {
      score: base.confidence_score,
      level: base.confidence_score >= 0.85 ? "HIGH" : base.confidence_score >= 0.65 ? "MEDIUM" : "LOW",
      factors_positive: [
        `Xác thực chéo từ ${base.source_count} cơ quan báo chí chính thống`,
        "Tọa độ địa lý khớp số nhà / địa danh hành chính",
        "Trích xuất nhất quán giữa các nguồn tin",
      ],
      factors_warning: base.is_approximate
        ? ["Tọa độ mang tính tương đối dựa theo cấp xã/phường hoặc tên vùng"]
        : [],
      source_diversity_ratio: 0.92,
      geocoding_precision: base.is_approximate ? "Tương đối (Cấp xã/phường)" : "Chính xác (POI / Số nhà)",
    },
    timeline: [
      {
        id: "tl-1",
        milestone_type: "OCCURRED",
        timestamp: base.occurred_at,
        description: "Thời điểm ghi nhận sự việc xảy ra tại hiện trường theo lời kể nhân chứng.",
      },
      {
        id: "tl-2",
        milestone_type: "FIRST_REPORTED",
        timestamp: new Date(new Date(base.occurred_at).getTime() + 15 * 60000).toISOString(),
        description: "Báo chí xuất bản bản tin khẩn cấp đầu tiên.",
        source_name: "Báo VnExpress",
        source_url: "https://vnexpress.net",
      },
      {
        id: "tl-3",
        milestone_type: "SOURCE_UPDATE",
        timestamp: new Date(new Date(base.occurred_at).getTime() + 45 * 60000).toISOString(),
        description: "Lực lượng chức năng công bố thông tin xử lý hiện trường.",
        source_name: "Báo Tuổi Trẻ",
        source_url: "https://tuoitre.vn",
      },
      {
        id: "tl-4",
        milestone_type: "OFFICIAL_STATEMENT",
        timestamp: new Date(new Date(base.occurred_at).getTime() + 90 * 60000).toISOString(),
        description: "Cơ quan điều tra hoàn tất khám nghiệm và điều tiết hoàn toàn giao thông.",
        source_name: "Thông tấn xã Việt Nam",
        source_url: "https://vnanet.vn",
      },
    ],
    sources: [
      {
        id: "src-1",
        name: "VnExpress",
        publisher: "VnExpress",
        url: "https://vnexpress.net",
        title: base.title,
        published_at: base.occurred_at,
        reliability_score: 0.95,
        is_primary: true,
      },
      {
        id: "src-2",
        name: "Tuổi Trẻ",
        publisher: "Báo Tuổi Trẻ",
        url: "https://tuoitre.vn",
        title: `${base.title} - Cập nhật mới nhất`,
        published_at: new Date(new Date(base.occurred_at).getTime() + 10 * 60000).toISOString(),
        reliability_score: 0.92,
      },
      {
        id: "src-3",
        name: "Thanh Niên",
        publisher: "Báo Thanh Niên",
        url: "https://thanhnien.vn",
        title: `Hiện trường vụ việc tại ${base.location_label}`,
        published_at: new Date(new Date(base.occurred_at).getTime() + 25 * 60000).toISOString(),
        reliability_score: 0.91,
      },
      {
        id: "src-4",
        name: "Dân Trí",
        publisher: "Báo Dân Trí",
        url: "https://dantri.com.vn",
        title: `Thông tin chi tiết nguyên nhân và thiệt hại tại ${base.province || "khu vực"}`,
        published_at: new Date(new Date(base.occurred_at).getTime() + 40 * 60000).toISOString(),
        reliability_score: 0.88,
      },
    ],
    related_events: MOCK_VIETNAM_EVENTS.filter((e) => e.id !== base.id).slice(0, 3),
  };
}

export const apiService = {
  /**
   * Fetch events with filters and bbox from public read API.
   */
  async getEvents(
    filters?: Partial<FilterState>,
    bbox?: string,
    limit: number = 50,
    page: number = 1
  ): Promise<PaginatedResponse<NewsEventItem>> {
    const params = new URLSearchParams();
    if (bbox) params.set("bbox", bbox);
    if (filters?.province) params.set("province", filters.province);
    if (filters?.category && filters.category !== "ALL") params.set("category", filters.category);
    if (filters?.fromDate) params.set("from", filters.fromDate);
    if (filters?.toDate) params.set("to", filters.toDate);
    if (filters?.status) params.set("status", filters.status);
    if (filters?.minSources && filters.minSources > 1) {
      params.set("minSources", String(filters.minSources));
    }
    params.set("limit", String(limit));
    params.set("page", String(page));

    try {
      const response = await fetch(`${API_BASE}/events?${params.toString()}`);
      if (response.ok) {
        const json = await response.json();
        if (json.data && json.data.length > 0) {
          return json;
        }
      }
    } catch {
      // Backend not running or unreachable: use rich mock data fallback
    }

    // Fallback: Filter mock data client-side
    let filtered = [...MOCK_VIETNAM_EVENTS];
    if (filters?.province) {
      filtered = filtered.filter((e) => e.province === filters.province);
    }
    if (filters?.category && filters.category !== "ALL") {
      filtered = filtered.filter((e) => e.category === filters.category);
    }
    if (filters?.minSources && filters.minSources > 1) {
      filtered = filtered.filter((e) => e.source_count >= filters.minSources!);
    }

    return {
      data: filtered,
      pagination: {
        limit,
        offset: (page - 1) * limit,
        total: filtered.length,
      },
    };
  },

  /**
   * Search events full-text.
   */
  async searchEvents(
    q: string,
    filters?: Partial<FilterState>,
    limit: number = 20
  ): Promise<PaginatedResponse<NewsEventItem>> {
    const params = new URLSearchParams({ q });
    if (filters?.province) params.set("province", filters.province);
    if (filters?.category && filters.category !== "ALL") params.set("category", filters.category);
    params.set("limit", String(limit));

    try {
      const response = await fetch(`${API_BASE}/events/search?${params.toString()}`);
      if (response.ok) {
        const json = await response.json();
        return json;
      }
    } catch {
      // Fallback search in mock data
    }

    const queryLower = q.toLowerCase();
    const matched = MOCK_VIETNAM_EVENTS.filter(
      (e) =>
        e.title.toLowerCase().includes(queryLower) ||
        (e.summary && e.summary.toLowerCase().includes(queryLower)) ||
        (e.location_label && e.location_label.toLowerCase().includes(queryLower))
    );

    return {
      data: matched,
      pagination: {
        limit,
        offset: 0,
        total: matched.length,
      },
    };
  },

  /**
   * Fetch single event detail with timeline, confidence and sources.
   */
  async getEventDetail(eventId: string): Promise<EventDetailItem> {
    try {
      const response = await fetch(`${API_BASE}/events/${eventId}`);
      if (response.ok) {
        const json = await response.json();
        return json;
      }
    } catch {
      // Fallback
    }

    return getMockEventDetail(eventId);
  },
};
