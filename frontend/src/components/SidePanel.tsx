import React from "react";

export const SidePanel: React.FC = () => {
  return (
    <aside className="side-panel" aria-label="Bảng tin sự kiện">
      <div style={{ padding: "16px", borderBottom: "1px solid var(--border-subtle)" }}>
        <h2 style={{ fontSize: "var(--text-base)", fontWeight: 600 }}>Dòng sự kiện nổi bật</h2>
        <p style={{ fontSize: "var(--text-xs)", color: "var(--text-secondary)" }}>
          Được nhóm tự động từ các nguồn báo chí uy tín
        </p>
      </div>
      <div style={{ padding: "16px", color: "var(--text-muted)", fontSize: "var(--text-sm)" }}>
        Đang đồng bộ dữ liệu sự kiện từ hệ thống...
      </div>
    </aside>
  );
};
