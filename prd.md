# PRD — Vietnam News Map

**Product name:** Vietnam News Map
**Document:** Product Requirements Document (PRD)
**Version:** 1.0
**Status:** Draft for implementation
**Primary market:** Vietnam
**Primary language:** Vietnamese
**Initial scope:** News events occurring in Vietnam and reported by Vietnamese/public news sources

---

## 1. Product Overview

### 1.1. Problem

Người dùng Việt Nam hiện phải mở nhiều trang báo, đọc từng bài và tự đối chiếu để biết:

- Đang có những sự kiện đáng chú ý nào trên cả nước.
- Sự kiện đang xảy ra ở đâu.
- Có bao nhiêu nguồn khác nhau đang đưa tin.
- Các bài báo khác nhau có đang nói về cùng một sự kiện hay không.
- Thông tin nào là thông tin chung giữa nhiều nguồn và thông tin nào còn chưa thống nhất.
- Một khu vực nào đó đang xuất hiện nhiều sự kiện/tin tức bất thường hay không.

Vietnam News Map giải quyết vấn đề này bằng cách biến tin tức thành dữ liệu địa lý và hiển thị chúng trực tiếp trên bản đồ Việt Nam.

### 1.2. Product concept

Thay vì xem:

> Article → Article → Article

sản phẩm tổ chức thông tin thành:

> **Article → Event → Location → Map**

Mỗi marker trên bản đồ đại diện cho **một sự kiện**, không phải một bài báo.

Nếu 20 bài báo cùng đưa tin về một vụ việc, hệ thống cố gắng gom chúng thành **1 event marker** và hiển thị số lượng nguồn/bài viết bên trong.

### 1.3. Product vision

Xây dựng một bản đồ tin tức Việt Nam nơi người dùng có thể:

1. Mở bản đồ và nhìn thấy các sự kiện đang/đã được báo chí đưa tin.
2. Click vào một marker để xem sự kiện.
3. Xem tóm tắt và vị trí/thời gian của sự kiện.
4. Xem tất cả nguồn báo liên quan.
5. Xem timeline cập nhật của sự kiện.
6. Xem mức độ nhất quán giữa các nguồn.
7. Sau khi dữ liệu lịch sử đủ lớn, nhận diện những event đang tăng nhanh về mức độ chú ý.
8. Ở phase sau, nghe tóm tắt sự kiện bằng TTS.

---

# 2. Goals & Non-goals

## 2.1. Goals

### MVP / Phase 1

- Thu thập tin tức từ nhiều nguồn phù hợp tại Việt Nam.
- Chuẩn hóa và loại bỏ bài trùng.
- Trích xuất sự kiện, thời gian, địa điểm và các thực thể liên quan.
- Geocode địa điểm thành tọa độ.
- Gom nhiều bài báo cùng nói về một sự kiện thành một event.
- Hiển thị event trên bản đồ Việt Nam.
- Cho phép click marker và xem event detail.
- Hiển thị danh sách nguồn báo của event.
- Hiển thị timeline của event.
- Hiển thị thông tin về mức độ hỗ trợ của các nguồn đối với event.
- Cho phép mở bài gốc.
- Có bộ lọc theo thời gian, tỉnh/thành, loại sự kiện và trạng thái.
- Lưu dữ liệu lịch sử để có thể phát triển Trend Engine sau này.

### Phase 2

- Phân tích tốc độ xuất hiện của event.
- Phát hiện event đang tăng mạnh về lượng tin.
- Kết hợp thêm các tín hiệu tìm kiếm/xu hướng và social signal khi nguồn dữ liệu phù hợp.
- Xây dựng Trend Score và Confidence Score riêng biệt.

### Phase 3

- Tạo bản tóm tắt âm thanh bằng TTS.
- Quick Brief và Full Brief cho từng event.
- Có thể mở rộng thành audio brief theo khu vực.

## 2.2. Non-goals ở MVP

MVP không tập trung vào:

- Tự động khẳng định một tin là đúng/sai tuyệt đối.
- Thay thế cơ quan báo chí hoặc cơ quan xác minh chính thức.
- Tự viết lại toàn bộ nội dung bài báo để thay thế bài gốc.
- Tạo hệ thống dự đoán chính xác diễn biến tương lai của sự kiện.
- Tích hợp TTS ngay từ đầu.
- Tối ưu toàn quốc ở quy mô cực lớn ngay phiên bản đầu tiên.
- Thu thập dữ liệu riêng tư hoặc dữ liệu vị trí cá nhân của người dùng.

---

# 3. Target Users

## 3.1. Người dùng phổ thông

Muốn nhanh chóng biết:

- Chuyện gì đang xảy ra.
- Xảy ra ở đâu.
- Khu vực nào đang có nhiều tin.
- Có bao nhiêu nguồn đang đưa tin.

## 3.2. Người muốn theo dõi một khu vực

Ví dụ:

- Theo dõi TP.HCM.
- Theo dõi Hà Nội.
- Theo dõi một tỉnh/thành.
- Theo dõi một khu vực trên bản đồ.

## 3.3. Người nghiên cứu / phân tích

Muốn xem:

- Các event theo thời gian.
- Mật độ tin tức theo khu vực.
- Event cluster.
- Xu hướng tăng/giảm của số lượng bài viết.
- Sự khác biệt giữa các nguồn.

---

# 4. Core Product Principle

## 4.1. Marker = Event, không phải Article

Đây là nguyên tắc cốt lõi của sản phẩm.

Ví dụ:

```text
Báo A → “Tai nạn tại đường X”
Báo B → “Giao thông ùn tắc tại đường X”
Báo C → “Công an xử lý vụ việc tại đường X”
Báo D → “Thông tin mới về vụ việc tại đường X”

                 ↓

              EVENT #1827
                 📍
          4 articles / 4 sources
```

Mục tiêu là tránh tình trạng bản đồ đầy hàng chục marker cho một vụ việc duy nhất.

## 4.2. Source transparency

Mọi event quan trọng phải cho phép người dùng truy ngược về nguồn gốc:

- Nguồn nào đăng.
- Đăng lúc nào.
- Link bài gốc.
- Có bao nhiêu nguồn độc lập đề cập.
- Các nguồn có thông tin nào giống/khác nhau ở mức hệ thống có thể phát hiện.

## 4.3. Confidence không đồng nghĩa với Truth

`Confidence Score` chỉ thể hiện độ mạnh của dữ liệu thu thập được và mức độ nhất quán/độc lập của nguồn, không phải chứng nhận sự thật tuyệt đối.

Ví dụ:

```text
Confidence: HIGH

12 articles
7 independent sources
1 consistent location
multiple sources agree on core event
```

Nên tránh wording kiểu:

> “Tin này chắc chắn đúng 100%.”

Nên dùng:

> “Thông tin được đề cập bởi 7 nguồn độc lập.”

---

# 5. Main User Journey

## 5.1. Journey A — Xem toàn cảnh Việt Nam

```text
User mở website
        ↓
Vietnam Map
        ↓
Markers xuất hiện
        ↓
User zoom / pan
        ↓
Map cluster / event markers thay đổi theo viewport
```

## 5.2. Journey B — Xem một event

```text
Click marker
      ↓
Quick Popup
      ↓
Click “Xem chi tiết”
      ↓
Event Detail Panel
      ↓
Xem Summary
      ↓
Xem Sources
      ↓
Xem Timeline
      ↓
Mở Article gốc
```

## 5.3. Journey C — Tìm event

```text
User nhập:
“cháy” / “Đà Nẵng” / “tai nạn” / “18/09”
             ↓
Search / Filter
             ↓
Relevant events
             ↓
Map focus
```

## 5.4. Journey D — Theo dõi một tỉnh/thành

```text
Chọn TP.HCM
      ↓
Map focus vào TP.HCM
      ↓
Danh sách event trong tỉnh/thành
      ↓
Sort theo:
- mới nhất
- nhiều nguồn nhất
- nhiều bài nhất
- mức độ tăng (Phase 2)
```

---

# 6. Functional Requirements — Phase 1

## 6.1. News Source Management

Hệ thống phải hỗ trợ cấu hình nhiều nguồn tin.

Mỗi source có:

```text
source_id
name
domain
source_type
rss_url (nếu có)
parser_type
active
priority
last_success_at
last_error_at
```

### Source types

- RSS
- Sitemap / feed
- Public article listing
- API chính thức nếu được cấp phép
- Crawler/adapter riêng cho từng website khi cần

### Requirements

- Có thể bật/tắt source.
- Theo dõi trạng thái crawl.
- Ghi log lỗi từng source.
- Không để một source lỗi làm hỏng toàn pipeline.

---

## 6.2. Article Ingestion

Pipeline nhận article từ các nguồn.

### Article raw fields

```text
article_id
source_id
source_url
canonical_url
title
subtitle
content_snippet
published_at
updated_at
author (nếu có)
image_url (nếu có)
raw_metadata
fetched_at
```

### Requirements

- Lưu `canonical_url`.
- Chuẩn hóa timestamp về UTC trong database hoặc có timezone rõ ràng.
- Lưu thời gian thu thập.
- Retry khi source lỗi.
- Có cơ chế chống crawl trùng.

---

## 6.3. Deduplication

Mục tiêu: cùng một bài nhưng URL/metadata khác nhau không tạo nhiều bản ghi.

### Dedup levels

1. Exact URL match.
2. Canonical URL match.
3. Title similarity.
4. Title + publication time similarity.
5. Content fingerprint / semantic similarity nếu cần.

### Output

```text
raw_articles
     ↓
normalized_articles
     ↓
unique_articles
```

---

# 7. Event Extraction

Đây là core AI/NLP pipeline.

Mỗi article được phân tích để xác định:

- Event type.
- Event title / normalized title.
- Người/tổ chức/địa điểm liên quan.
- Địa điểm chính của event nếu xác định được.
- Thời gian xảy ra.
- Thời gian bài viết.
- Các facts chính.
- Mức độ chắc chắn của từng field.

## 7.1. Event categories ban đầu

Có thể bắt đầu bằng:

```text
ACCIDENT
FIRE
CRIME
PUBLIC_SAFETY
WEATHER
FLOOD
TRAFFIC
PUBLIC_EVENT
POLITICS
BUSINESS
HEALTH
EDUCATION
ENTERTAINMENT
SPORTS
OTHER
```

Category phải có cơ chế mở rộng.

## 7.2. Event extraction schema

```json
{
  "event_title": "...",
  "event_type": "ACCIDENT",
  "location_text": "...",
  "province": "...",
  "district": "...",
  "ward": "...",
  "latitude": null,
  "longitude": null,
  "occurred_at": null,
  "facts": [],
  "entities": [],
  "confidence": 0.0
}
```

---

# 8. Location Resolution & Geocoding

## 8.1. Mục tiêu

Biến địa điểm trong bài viết thành tọa độ bản đồ.

Ví dụ:

```text
“đường Nguyễn Văn Linh, quận 7, TP.HCM”
                     ↓
lat/lng
```

## 8.2. Location hierarchy

```text
Country
 Province / Municipality
  District / Urban District
   Ward / Commune
    Street
     Landmark / POI
```

## 8.3. Location confidence

Mỗi event phải có:

```text
location_text
resolved_address
latitude
longitude
location_confidence
resolution_method
```

### Không được tự ý đặt tọa độ chính xác khi dữ liệu chỉ biết tới cấp tỉnh/thành.

Ví dụ bài chỉ nói:

> “tại Đà Nẵng”

thì marker có thể đặt ở centroid thành phố với label:

> “Vị trí gần đúng — chỉ xác định được TP. Đà Nẵng.”

Không được hiển thị như vị trí chính xác của sự kiện.

---

# 9. Event Clustering

Đây là chức năng quan trọng nhất sau ingestion.

## 9.1. Mục tiêu

Xác định các bài báo khác nhau có đang nói về cùng một event hay không.

## 9.2. Các tín hiệu clustering

Có thể kết hợp:

- Semantic similarity của title/content.
- Event type.
- Location proximity.
- Event time proximity.
- Named entities.
- Organizations/persons involved.
- Shared facts.
- Publication/update time.

## 9.3. Quy trình

```text
Article
  ↓
Extract event representation
  ↓
Candidate retrieval
  ↓
Similarity scoring
  ↓
Same-event classifier
  ↓
Existing event ?
 ├── YES → attach article
 └── NO  → create new event
```

## 9.4. Không merge mù

Hai bài ở cùng địa điểm chưa chắc là cùng event.

Ví dụ:

```text
18:00 — Tai nạn ở đường X
20:00 — Cháy tại cửa hàng trên đường X
```

Phải giữ thành 2 event nếu evidence cho thấy đây là hai vụ khác nhau.

---

# 10. Event Model

Một event tối thiểu gồm:

```text
event_id
title
normalized_title
category
summary
latitude
longitude
location_label
location_confidence
occurred_at
first_reported_at
last_updated_at
status
confidence_score
article_count
source_count
created_at
updated_at
```

## 10.1. Event status

```text
NEW
DEVELOPING
UPDATED
QUIET
ARCHIVED
```

`status` không phải kết luận về sự thật của sự kiện; chỉ mô tả trạng thái dữ liệu/tin tức.

---

# 11. Event Summary

Mỗi event cần một summary ngắn được tạo từ các nguồn đã thu thập.

### Summary goals

- Ngắn.
- Dễ đọc.
- Không thêm fact không có trong nguồn.
- Phân biệt thông tin đã được nhiều nguồn hỗ trợ với chi tiết chỉ xuất hiện ở một nguồn.
- Có thể cập nhật khi xuất hiện bài mới.

### Example

```text
Khoảng 14:30 ngày 18/09, một vụ tai nạn được nhiều báo
đưa tin tại khu vực X, TP.HCM. Đến 16:00, đã có 7 nguồn
độc lập đề cập. Một số chi tiết về nguyên nhân vẫn chưa
thống nhất giữa các nguồn.
```

---

# 12. Source & Verification View

Khi user mở event, phải có section nguồn.

### Source list

```text
Báo A
Published: 14:35
Updated: 15:20
[Đọc bài]

Báo B
Published: 14:42
[Đọc bài]

Báo C
Published: 15:01
[Đọc bài]
```

### Metrics

```text
12 bài viết
7 nguồn độc lập
3 nguồn địa phương
```

Không được dùng `source_count` như một bằng chứng tuyệt đối rằng event đúng.

## 12.1. Source diversity

Có thể phân biệt:

- Official / government source.
- Major news source.
- Local news source.
- Other public source.

Chỉ dùng để mô tả nguồn, không tự động gán “uy tín tuyệt đối”.

---

# 13. Timeline

Mỗi event có timeline.

### Timeline sources

- Thời gian xảy ra event.
- Bài đầu tiên được phát hiện.
- Các bài tiếp theo.
- Các bản cập nhật.
- Thông tin chính thức nếu có.

### Example

```text
14:32
Event time

14:35
Báo A đăng bài

14:42
Báo B đăng bài

15:01
Báo C cập nhật

16:10
Nguồn chính thức được phát hiện
```

Timeline phải phân biệt:

- Event occurred time.
- Article published time.
- Article updated time.

Không được trộn ba loại timestamp thành một.

---

# 14. Map UI

## 14.1. Main map

Bản đồ trung tâm là Google Maps hoặc nền map tương thích được cấp phép.

Map phải hỗ trợ:

- Pan.
- Zoom.
- Marker.
- Marker clustering.
- Viewport loading.
- Click marker.
- Fit bounds.
- Search location.

## 14.2. Marker

Mỗi marker đại diện cho event.

Marker có thể biểu thị:

- Category.
- Event status.
- Mức độ chú ý (Phase 2).
- Cluster count khi zoom out.

## 14.3. Cluster

Khi zoom out, các event gần nhau có thể gom thành cluster.

Ví dụ:

```text
       (18)
```

Click cluster → zoom vào khu vực đó.

---

# 15. Event Quick Popup

Click marker mở popup.

### Required fields

```text
Event title
Location
Occurred time
Short summary
Article count
Source count
Confidence label
CTA: Xem chi tiết
```

### Example

```text
┌───────────────────────────────┐
│ 🔴 Tai nạn giao thông         │
│ 📍 TP.HCM                     │
│ 🕐 18/09 · 14:32              │
│                               │
│ Một vụ tai nạn được nhiều     │
│ nguồn báo chí đưa tin...      │
│                               │
│ 📰 12 bài · 7 nguồn           │
│                               │
│ [Xem chi tiết →]              │
└───────────────────────────────┘
```

---

# 16. Event Detail Panel

Panel bên phải hoặc full-screen trên mobile.

## Sections

### A. Header

- Event title.
- Category.
- Location.
- Last update.
- Status.

### B. Summary

- AI-generated summary.
- Warning nếu thông tin còn thiếu hoặc có mâu thuẫn.

### C. Verification

- Article count.
- Independent source count.
- Location confidence.
- Event confidence.

### D. Timeline

- Event time.
- Publication/update timeline.

### E. Sources

- Source list.
- Published time.
- Updated time.
- Link article gốc.

### F. Related events

Các event gần về địa điểm/thời gian/chủ đề nhưng chưa được merge.

Mục này giúp người dùng kiểm tra context.

---

# 17. Filters & Search

## 17.1. Filters

MVP phải có:

- Time range.
- Province/city.
- Category.
- Event status.
- Minimum article count.
- Minimum source count.

## 17.2. Time presets

```text
1 giờ qua
6 giờ qua
24 giờ qua
3 ngày qua
7 ngày qua
30 ngày qua
Khoảng thời gian tùy chọn
```

## 17.3. Search

Search phải hỗ trợ:

- Tên địa điểm.
- Tỉnh/thành.
- Từ khóa event.
- Category.
- Source.

Ví dụ:

```text
“cháy”
“Đà Nẵng”
“Vĩnh Khánh”
“tai nạn TP.HCM”
```

---

# 18. Feed View

Ngoài map, nên có danh sách event dạng feed.

```text
[Newest]

🔴 Tai nạn tại X
12 nguồn · 7 bài
18/09 16:20

🟠 Cháy tại Y
6 nguồn · 9 bài
18/09 15:58
```

Click event trong feed phải focus marker tương ứng trên map.

Map và feed phải đồng bộ filter.

---

# 19. Data Architecture

## 19.1. Logical pipeline

```text
                NEWS SOURCES
                     │
                     ▼
              INGESTION LAYER
                     │
                     ▼
              RAW ARTICLES
                     │
                     ▼
              NORMALIZATION
                     │
                     ▼
             DEDUPLICATION
                     │
                     ▼
            NLP / LLM EXTRACTION
                     │
           ┌─────────┼─────────┐
           ▼         ▼         ▼
        EVENT     LOCATION   ENTITIES
           │         │         │
           └─────────┼─────────┘
                     ▼
              EVENT MATCHING
                     │
                     ▼
               EVENT CLUSTER
                     │
                     ▼
                 DATABASE
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      REST API    Search API    Analytics
        │
        ▼
   Web application
        │
        ▼
   Google Maps UI
```

---

# 20. Suggested Data Model

## 20.1. sources

```text
id
name
domain
source_type
rss_url
active
priority
created_at
updated_at
```

## 20.2. articles

```text
id
source_id
url
canonical_url
title
summary_raw
content_excerpt
published_at
updated_at
fetched_at
content_hash
language
raw_metadata
```

## 20.3. events

```text
id
title
normalized_title
category
summary
latitude
longitude
location_label
location_confidence
occurred_at
first_reported_at
last_updated_at
status
confidence_score
created_at
updated_at
```

## 20.4. event_articles

```text
event_id
article_id
match_score
match_reason
created_at
```

## 20.5. event_facts

```text
event_id
fact_key
fact_value
fact_confidence
supporting_article_count
created_at
updated_at
```

## 20.6. event_timeline

```text
event_id
timestamp
timeline_type
text
source_article_id
created_at
```

## 20.7. locations

Có thể tách thành bảng riêng khi cần:

```text
id
raw_text
normalized_text
province
district
ward
address
latitude
longitude
provider
confidence
```

---

# 21. API Requirements

## 21.1. Get events

```http
GET /api/events
```

Query parameters:

```text
from
 to
province
category
status
minSources
minArticles
bbox
page
limit
```

## 21.2. Get event detail

```http
GET /api/events/{eventId}
```

Response phải chứa:

- Event.
- Summary.
- Location.
- Timeline.
- Sources.
- Related events.
- Confidence metadata.

## 21.3. Search events

```http
GET /api/events/search?q=...
```

## 21.4. Source health

```http
GET /api/sources/health
```

Admin-only nếu cần.

---

# 22. Data Freshness

MVP hướng tới near-real-time, không yêu cầu real-time tuyệt đối.

### Target

- RSS/feed polling: configurable.
- Default ingestion interval: 5–15 minutes tùy source.
- Processing queue: asynchronous.
- Map API có thể cache event responses ngắn hạn.

### Freshness metadata

Mỗi event nên biết:

```text
first_seen_at
last_seen_at
last_source_update_at
```

---

# 23. Reliability & Data Trust

## 23.1. Mỗi event phải có provenance

Có thể truy ngược:

```text
Event
 ↓
article_ids
 ↓
source
 ↓
original URL
```

## 23.2. Không tạo false precision

Nếu chưa xác định chính xác địa điểm:

- Không đặt marker vào một con đường cụ thể chỉ vì đoán.
- Ghi rõ location level.
- Hiển thị `approximate location` khi cần.

## 23.3. Không gộp event quá mạnh

Nếu similarity không đủ cao:

- Tạo event riêng.
- Chấp nhận duplicate event tốt hơn merge sai event.

## 23.4. Conflicting information

Khi nguồn khác nhau:

```text
Fact A
- 5 sources

Fact B
- 1 source

Status: conflicting / insufficient confirmation
```

Không tự động chọn một fact làm “sự thật” nếu chưa có cơ sở.

---

# 24. Event Confidence Score

Confidence là một chỉ số nội bộ/hiển thị có giải thích.

Có thể bắt đầu với các tín hiệu:

```text
source_count
independent_source_count
location_consistency
occurred_time_consistency
entity consistency
fact overlap
source diversity
```

Không nên chỉ tính:

```text
confidence = number_of_articles
```

### Example output

```text
Confidence: 86/100

+ nhiều nguồn độc lập
+ địa điểm nhất quán
+ thời gian nhất quán
+ nhiều facts trùng nhau
```

Confidence phải có explanation để người dùng hiểu tại sao hệ thống đưa ra mức đó.

---

# 25. Trend Engine — Phase 2

Trend Engine không phải là MVP core.

## 25.1. Mục tiêu

Phát hiện event/khu vực có mức tăng chú ý bất thường.

Không sử dụng “phổ biến” đơn thuần. Mục tiêu là tìm **change / velocity / anomaly**.

## 25.2. Internal signals

Có thể dùng:

- Article velocity.
- New source velocity.
- Search trend signal.
- Social mention signal.
- Historical baseline.
- Review/other public activity khi phù hợp.

## 25.3. Trend Score

```text
Trend Score
    = weighted combination of
      recent growth
      source growth
      search growth
      social growth
      historical anomaly
```

Trọng số phải cấu hình được.

## 25.4. Trend vs Confidence

Hai chỉ số độc lập:

```text
Trend Score = “độ tăng chú ý”
Confidence   = “độ mạnh của evidence hiện có”
```

Một event có thể:

```text
Trend 95
Confidence 42
```

nghĩa là:

> Có dấu hiệu tăng chú ý mạnh nhưng evidence độc lập còn ít.

Đây là trạng thái hợp lệ.

---

# 26. Historical Data

Từ MVP phải lưu dữ liệu theo thời gian.

Mỗi event cần giữ:

```text
article_count over time
source_count over time
first/last seen
trend-related snapshots
```

Mục tiêu là sau vài tuần/tháng có thể đo được:

- event velocity.
- normal baseline.
- anomaly.
- trend confirmation.

---

# 27. TTS — Phase 3 Only

TTS chưa nằm trong MVP.

## 27.1. Input

```text
Event
   ↓
Verified/normalized summary
   ↓
TTS script
   ↓
Audio
```

## 27.2. Quick Brief

20–40 giây.

Đọc:

- chuyện gì.
- ở đâu.
- khi nào.
- số nguồn.
- cảnh báo nếu có mâu thuẫn.

## 27.3. Full Brief

Khoảng 1–2 phút.

Có thể bao gồm:

- Summary.
- Timeline.
- Source diversity.
- Uncertainty.

## 27.4. Audio caching

Không generate TTS lại cho mỗi lượt nghe.

```text
Event summary version
        ↓
TTS generation
        ↓
Cached audio
        ↓
Many users listen
```

Khi summary thay đổi đáng kể → tạo audio version mới.

---

# 28. UI/UX Structure

## Desktop

```text
┌─────────────────────────────────────────────────────┐
│ Header: Search | Filters | Date Range               │
├───────────────────────────────┬─────────────────────┤
│                               │                     │
│                               │  Event Feed         │
│         GOOGLE MAP            │                     │
│                               │  - Event A          │
│       📍    📍                │  - Event B          │
│             🔴                │  - Event C          │
│   📍                   📍      │                     │
│                               │                     │
│                               │                     │
├───────────────────────────────┴─────────────────────┤
│ Optional status / legend                             │
└─────────────────────────────────────────────────────┘
```

Click marker → right panel/detail.

## Mobile

- Map-first UI.
- Bottom sheet cho event detail.
- Filters dạng drawer.
- Feed dạng bottom sheet/list.

---

# 29. Admin / Operations

MVP nên có trang admin tối thiểu để theo dõi pipeline.

## 29.1. Source monitor

Hiển thị:

```text
Source
Last successful crawl
Articles fetched
Errors
Status
```

## 29.2. Processing monitor

```text
Articles pending
Extraction success
Geocode success
Clustering success
Failures
```

## 29.3. Event review

Cho phép xem các event có:

- Confidence thấp.
- Location confidence thấp.
- Clustering score thấp.
- Conflict cao.

Đây là công cụ rất quan trọng khi cần cải thiện model.

---

# 30. Observability

Phải có log/metrics cho:

### Ingestion

- Articles fetched/source.
- Fetch latency.
- Fetch failure rate.

### NLP

- Extraction success rate.
- Extraction latency.
- Invalid outputs.

### Geocoding

- Resolution success.
- Approximate rate.
- Failure rate.

### Clustering

- New event rate.
- Merge rate.
- Potential duplicate rate.

### API

- Request count.
- Error rate.
- Latency.

---

# 31. Security

- API keys không được commit vào repository.
- Secret nằm trong environment variables/secret manager.
- Rate limit public API.
- Admin endpoints phải authentication.
- Validate all external URLs before opening/processing where relevant.
- Chống prompt injection từ nội dung bài báo khi dùng LLM.
- Không để article content điều khiển system prompt.

---

# 32. Legal / Content Handling

Đây là hệ thống tổng hợp/định vị dữ liệu tin tức.

Nguyên tắc:

- Ưu tiên lưu metadata, title, excerpt/summary cần thiết thay vì sao chép toàn bộ bài báo.
- Luôn giữ link nguồn gốc.
- Hiển thị rõ source attribution.
- Tôn trọng robots.txt, điều khoản sử dụng, API terms và quyền khai thác của từng nguồn.
- Không dùng crawler vượt cơ chế chống truy cập của website.
- Khi một nguồn yêu cầu không được sử dụng dữ liệu, source đó phải có khả năng disable.
- TTS giai đoạn sau không được trở thành công cụ đọc lại trái phép toàn bộ bài báo có bản quyền.

---

# 33. Performance Requirements

## MVP target

- Initial map render: mục tiêu < 3s trong điều kiện mạng bình thường.
- Event API response: mục tiêu P95 < 800ms với query đã cache/indexed.
- Search: mục tiêu P95 < 1s.
- Marker rendering phải sử dụng clustering/viewport loading để tránh render toàn bộ event cùng lúc.
- Event detail có thể lazy-load sources/timeline.

Các con số này là target engineering, cần đo lại sau benchmark thực tế.

---

# 34. MVP Scope Definition

## Must Have

```text
[✓] Multi-source news ingestion
[✓] Article normalization
[✓] Deduplication
[✓] Event extraction
[✓] Location extraction
[✓] Geocoding
[✓] Event clustering
[✓] Event database
[✓] Google Map integration
[✓] Event markers
[✓] Marker clustering
[✓] Event popup
[✓] Event detail panel
[✓] Summary
[✓] Sources
[✓] Timeline
[✓] Confidence metadata
[✓] Search
[✓] Filters
[✓] Feed view
[✓] Source attribution
[✓] Admin source monitoring
[✓] Historical snapshots
```

## Should Have

```text
[ ] Related events
[ ] Conflict/fact comparison
[ ] Advanced spatial search
[ ] Better entity resolution
[ ] Manual admin correction tools
```

## Later

```text
[ ] Trend Score
[ ] Google Trends integration
[ ] Social signals
[ ] Hotspot/heatmap
[ ] TTS
[ ] Audio news by area
[ ] Personalized watchlists
[ ] Notifications
```

---

# 35. MVP Acceptance Criteria

MVP được xem là đạt khi toàn bộ flow sau chạy được:

```text
1. Hệ thống nhận một bài báo mới
        ↓
2. Lưu article metadata
        ↓
3. Deduplicate
        ↓
4. Extract event + location + time
        ↓
5. Geocode location
        ↓
6. Tìm các event tương tự
        ↓
7. Merge vào existing event hoặc create event mới
        ↓
8. Cập nhật source count/article count
        ↓
9. Cập nhật summary/timeline
        ↓
10. API trả event
        ↓
11. Map hiển thị marker
        ↓
12. User click marker
        ↓
13. Popup hiện thông tin
        ↓
14. User mở Event Detail
        ↓
15. User xem source + timeline
        ↓
16. User mở article gốc
```

### Data quality acceptance

- Event phải có provenance.
- Event phải có source URL.
- Location phải có confidence.
- Hệ thống không được đặt tọa độ “chính xác” khi chỉ biết tỉnh/thành.
- Các event có evidence rõ ràng là khác nhau không được merge chỉ vì cùng khu vực.
- Các bài rõ ràng thuộc cùng một event phải có khả năng merge thành một event.

---

# 36. Recommended Implementation Order

## Sprint 1 — Foundation

- Project structure.
- Database.
- Source management.
- Article model.
- Basic ingestion.

## Sprint 2 — News pipeline

- Normalization.
- Deduplication.
- NLP extraction.
- Location extraction.
- Geocoding.

## Sprint 3 — Event engine

- Event model.
- Similarity search.
- Event clustering.
- Summary generation.
- Timeline.

## Sprint 4 — Map product

- Google Maps.
- Event markers.
- Marker clustering.
- Popup.
- Event detail panel.
- Feed.
- Filters/search.

## Sprint 5 — Trust & operations

- Confidence scoring.
- Source monitor.
- Processing monitor.
- Error handling.
- Historical snapshots.
- Data quality review.

## Sprint 6 — Stabilization

- Performance.
- Caching.
- Security.
- Monitoring.
- UI polish.
- End-to-end tests.

**Sau khi Phase 1 ổn định mới bắt đầu Phase 2 Trend. TTS để Phase 3.**

---

# 37. Suggested Tech Stack (implementation guidance, not a hard requirement)

## Frontend

- React + TypeScript.
- Map UI: Google Maps JavaScript API.
- UI framework: Tailwind CSS hoặc component system tương đương.
- State/query: TanStack Query hoặc tương đương.

## Backend

- Python FastAPI hoặc Node.js/NestJS.
- Async job queue: Celery/RQ/BullMQ hoặc tương đương.

## Database

- PostgreSQL.
- PostGIS cho geospatial query.
- pgvector nếu dùng semantic similarity trong database.

## Search

MVP có thể bắt đầu bằng PostgreSQL full-text search.

Khi scale lớn hơn có thể cân nhắc Elasticsearch/OpenSearch.

## AI/NLP

- LLM/API có structured output để extraction/summarization.
- Embedding model cho article/event similarity.
- Có schema validation sau model output.

## Caching

- Redis hoặc tương đương.

## Storage

- Object storage chỉ khi thực sự cần lưu media/audio.

## Deployment

Có thể bắt đầu bằng một backend + worker + PostgreSQL/Redis, sau đó scale từng pipeline độc lập khi cần.

---

# 38. Key Product Metrics

## Product metrics

- Daily active users.
- Map sessions.
- Event opens.
- Source article clicks.
- Search usage.
- Filter usage.
- Average events viewed/session.

## Data metrics

- Articles ingested/day.
- Event creation rate.
- Event merge rate.
- Duplicate rate.
- Geocoding success rate.
- Location confidence distribution.
- Source availability.

## Quality metrics

- Event duplicate rate.
- Incorrect merge rate.
- Incorrect location rate.
- Summary factual error rate.
- Source attribution accuracy.

Trend engine và TTS không nên được đánh giá trước khi Phase 1 đạt chất lượng nền đủ tốt.

---

# 39. Future Extensions

Sau khi core event map ổn định:

### A. Trend Map

```text
🔥 Event đang tăng mạnh
```

### B. Area Heatmap

Hiển thị mật độ event theo tỉnh/khu vực.

### C. Watchlist

Người dùng theo dõi:

- tỉnh/thành.
- khu vực.
- category.
- từ khóa.

### D. Notification

Thông báo khi có event mới trong vùng theo dõi.

### E. TTS

```text
Event → Quick Brief → Audio
```

### F. Local audio briefing

```text
“Tin đáng chú ý quanh Quận 7 trong 24 giờ qua...”
```

### G. Analytics dashboard

Theo dõi biến động event theo ngày/tuần/tháng.

---

# 40. Final Product Definition

Vietnam News Map là một hệ thống **geospatial news intelligence cho Việt Nam**.

Giá trị cốt lõi không phải chỉ là “đưa tin lên Google Maps”, mà là biến dữ liệu báo chí thành cấu trúc:

```text
ARTICLE
   ↓
EVENT
   ↓
LOCATION
   ↓
MULTI-SOURCE EVIDENCE
   ↓
TIMELINE
   ↓
MAP
```

Phase 1 phải chứng minh được pipeline này.

Sau đó:

```text
EVENT HISTORY
      ↓
TREND DETECTION
      ↓
HOT EVENT / HOT AREA
```

Và cuối cùng:

```text
EVENT SUMMARY
      ↓
TTS
      ↓
AUDIO NEWS
```

**Nguyên tắc phát triển:** xây chắc Event + Location + Source + Verification trước; Trend và TTS chỉ là các lớp mở rộng phía trên dữ liệu nền này.
