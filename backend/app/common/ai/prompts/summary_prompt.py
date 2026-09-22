"""Fact-grounded event summarization prompt template."""

from __future__ import annotations

EVENT_SUMMARY_SYSTEM_INSTRUCTION = """Bạn là trợ lý AI chuyên tóm tắt tin tức sự kiện khách quan cho Vietnam News Map.
NHIỆM VỤ:
Viết một đoạn tóm tắt sự kiện súc tích bằng tiếng Việt dựa DUY NHẤT trên các dữ kiện được cung cấp.

QUY TẮC BẮT BUỘC:
1. Độ dài: từ 60 đến 120 từ. Ngắn gọn, súc tích, dễ đọc.
2. Tuyệt đối không bịa đặt hoặc thêm thông tin không có trong danh sách facts.
3. Nếu có thông tin mâu thuẫn giữa các nguồn (ví dụ số thương vong hoặc nguyên nhân), PHẢI nêu rõ sự khác biệt (ví dụ: "Hiện thông tin về số lượng thương vong vẫn chưa thống nhất giữa các nguồn").
4. Văn phong báo chí trung lập, không thêm cảm xúc hay bình phẩm cá nhân.
5. Không sao chép nguyên văn toàn bộ bài viết (tôn trọng bản quyền báo chí).
"""

def build_summary_prompt(
    event_title: str,
    category: str,
    location_label: str,
    facts: list[str],
    timeline_items: list[str],
    source_names: list[str],
) -> str:
    """Construct fenced untrusted prompt payload for event summary generation."""
    facts_block = "\n".join(f"- {f}" for f in facts) if facts else "- Không có dữ kiện chi tiết."
    timeline_block = "\n".join(f"- {t}" for t in timeline_items) if timeline_items else "- Chưa có dòng thời gian."
    sources_str = ", ".join(source_names) if source_names else "Nhiều nguồn"

    return f"""DỮ LIỆU ĐẦU VÀO SỰ KIỆN:
Tiêu đề sự kiện: {event_title}
Danh mục: {category}
Địa điểm: {location_label}
Các nguồn báo chí đưa tin: {sources_str}

CÁC DỮ KIỆN ĐÃ XÁC MINH:
{facts_block}

DÒNG THỜI GIAN CẬP NHẬT:
{timeline_block}

Hãy viết bản tóm tắt tiếng Việt chuẩn mực (60-120 từ):"""
