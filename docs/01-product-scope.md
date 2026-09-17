# Product Scope

## Core concept

`Article -> Event -> Location -> Evidence -> Map`

Marker đại diện cho **event**, không phải article.

## Phase 1 — MVP

- multi-source ingestion;
- normalization + dedup;
- event extraction;
- location extraction + geocoding;
- event clustering;
- event summary;
- source/provenance;
- event timeline;
- confidence metadata;
- Google Maps web UI;
- marker clustering + viewport loading;
- search/filter;
- feed view;
- admin source/pipeline monitoring;
- historical snapshots.

## Phase 2

- Trend Score;
- article/source velocity;
- search trend signal;
- social/public signals khi hợp pháp và khả thi;
- anomaly detection;
- hotspot/heatmap.

## Phase 3

- TTS Quick Brief;
- TTS Full Brief;
- cached audio;
- audio by area.

## Non-goals MVP

- không khẳng định truth 100%;
- không sao chép nguyên bài báo làm nội dung thay thế nguồn;
- không TTS ngay MVP;
- không microservices hóa sớm;
- không thu thập dữ liệu vị trí riêng tư của người dùng.
