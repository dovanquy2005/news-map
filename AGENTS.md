# AGENTS.md — Mandatory Engineering Rules

## 1. Role
Bạn là coding agent của dự án Vietnam News Map. Mục tiêu là triển khai đúng spec hiện có, không tự ý thiết kế lại sản phẩm.

## 2. Source of truth hierarchy
Khi có xung đột, ưu tiên theo thứ tự:

1. Quyết định được người dùng chốt trực tiếp trong conversation.
2. `adr/*.md` đã được đánh dấu Accepted.
3. `docs/*.md`.
4. `prd.md`.
5. Assumption của agent.

Không được dùng assumption để override một spec đã tồn tại.

## 3. Không tự ý đổi kiến trúc
Agent KHÔNG được tự ý:

- chuyển modular monolith thành microservices;
- đổi database;
- thêm Kafka/Kubernetes/Elasticsearch/Redis Cluster chỉ vì “xịn hơn”;
- đổi provider bản đồ/geocoding;
- đổi authentication strategy;
- thêm framework lớn;
- tạo service mới.

Nếu thay đổi architecture là cần thiết, tạo ADR trước hoặc đề xuất thay đổi trong output của task.

## 4. Task boundary
Trước khi code phải xác định:

- mục tiêu task;
- files/modules bị ảnh hưởng;
- API/data contract liên quan;
- acceptance criteria;
- tests cần cập nhật.

Không sửa code ngoài boundary nếu không có lý do kỹ thuật rõ ràng.

## 5. API contract first
Backend API phải tuân thủ `docs/09-api-contracts.md`.

Không:

- trả thêm dữ liệu nhạy cảm ngoài contract;
- đổi field đang public mà không version/ADR;
- bỏ validation vì frontend đã validate;
- nhận query/filter không có giới hạn.

## 6. Security by default
Mọi input từ user, browser, feed, crawler, RSS, article, LLM và third-party API đều là **untrusted input**.

Đặc biệt phải kiểm soát:

- SQL injection;
- XSS;
- SSRF;
- prompt injection;
- broken authorization;
- excessive resource consumption;
- unsafe third-party API consumption;
- secrets leakage.

Chi tiết ở `docs/10-security.md`.

## 7. AI output is untrusted
LLM không được ghi thẳng dữ liệu vào database mà bỏ qua schema validation.

Pipeline bắt buộc:

`raw input -> model -> schema validation -> business validation -> persistence`

Article content không được thay đổi system/developer instruction.

## 8. Responsive is mandatory
Web phải hoạt động tốt ở:

- mobile: 360–767px;
- tablet: 768–1023px;
- laptop/desktop: >=1024px.

Không thiết kế desktop trước rồi “co lại” bằng CSS.

Chi tiết ở `docs/08-ui-ux-responsive.md`.

## 9. Performance rules
Không được:

- fetch toàn bộ event của Việt Nam về browser;
- render hàng nghìn marker DOM cùng lúc;
- query DB không có index cho endpoint public;
- dùng N+1 query trong event detail;
- gọi LLM/geocoding đồng bộ trong request của user nếu có thể đưa vào worker.

## 10. Tests
Mọi change phải có test tương ứng:

- business logic -> unit test;
- API -> integration/API test;
- database query quan trọng -> integration test;
- UI interaction quan trọng -> component/e2e test;
- security-sensitive change -> security regression test.

Không dùng “test passed” nếu chưa thực sự chạy.

## 11. Logging
Không log:

- API keys;
- secrets;
- access tokens;
- full sensitive payloads.

Log phải có correlation/request ID khi có thể.

## 12. Definition of done
Task chỉ được coi là xong khi:

- implementation đúng spec;
- validation/error handling đầy đủ;
- tests liên quan pass;
- không phá API contract;
- không tạo secret trong repo;
- responsive UI không bị vỡ nếu task có UI;
- cập nhật docs nếu contract/architecture thay đổi.

## 13. Vibe coding output format
Sau mỗi task, agent phải báo:

1. Đã thay đổi gì.
2. File nào thay đổi.
3. Contract nào ảnh hưởng.
4. Test nào đã chạy.
5. Có assumption nào không.
6. Có ADR/doc nào cần cập nhật không.
