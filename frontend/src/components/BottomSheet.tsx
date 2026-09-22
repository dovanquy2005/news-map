import React from "react";

export const BottomSheet: React.FC = () => {
  return (
    <section className="bottom-sheet" aria-label="Bảng tin sự kiện di động">
      <div className="bottom-sheet-handle" />
      <div className="bottom-sheet-content">
        <h2 style={{ fontSize: "var(--text-sm)", fontWeight: 600, marginBottom: "4px" }}>
          Sự kiện nổi bật
        </h2>
        <p style={{ fontSize: "var(--text-xs)", color: "var(--text-secondary)" }}>
          Chạm vào điểm đánh dấu trên bản đồ để xem chi tiết
        </p>
      </div>
    </section>
  );
};
