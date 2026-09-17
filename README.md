# Vietnam News Map — Engineering Spec Pack

Bộ tài liệu kỹ thuật được tách từ `prd.md` để dùng làm **source of truth cho AI coding agents**.

## Thứ tự đọc bắt buộc cho agent

1. `/AGENTS.md`
2. `/docs/01-product-scope.md`
3. `/docs/02-system-architecture.md`
4. File spec đúng với task đang làm.
5. `/docs/16-vibe-coding-workflow.md`
6. ADR liên quan trong `/adr/` nếu task chạm architecture.

## Cách dùng

- `prd.md` mô tả **WHAT**: sản phẩm phải làm gì.
- `docs/*.md` mô tả **HOW/CONSTRAINTS**: xây như thế nào và bị giới hạn bởi gì.
- `adr/*.md` ghi các quyết định kiến trúc đã được chốt.
- `AGENTS.md` là luật bắt buộc đối với coding agent.

## Nguyên tắc

> Không code khi chưa biết task thuộc module nào, contract nào, test nào và spec nào đang kiểm soát thay đổi.

Kiến trúc MVP: **modular monolith + async workers**, chưa tách microservices khi chưa có bottleneck thực tế.
