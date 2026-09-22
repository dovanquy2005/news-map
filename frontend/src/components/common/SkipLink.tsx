/**
 * SkipLink Component.
 * Accessibility keyboard bypass link allowing keyboard users to jump directly to map/content.
 * Complies with TASK-041 and WCAG 2.1 AA.
 */

import React from "react";

export const SkipLink: React.FC = () => {
  return (
    <a href="#main-content" className="skip-link" data-testid="skip-link">
      Chuyển đến nội dung chính (Bản đồ & Danh sách)
    </a>
  );
};
