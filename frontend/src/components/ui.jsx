import React from "react";

// ---- Status badge ----------------------------------------------------------
const STATUS_STYLES = {
  extracted: { bg: "#ECFDF5", text: "#065F46", border: "#A7F3D0", label: "Extracted" },
  approved: { bg: "#F0FDF4", text: "#166534", border: "#BBF7D0", label: "Approved" },
  processed: { bg: "#EFF6FF", text: "#1E40AF", border: "#BFDBFE", label: "Processed" },
  needs_review: { bg: "#FEF3C7", text: "#92400E", border: "#FDE68A", label: "Needs Review" },
  missing: { bg: "#FEF2F2", text: "#991B1B", border: "#FECACA", label: "Missing" },
  failed: { bg: "#FEE2E2", text: "#991B1B", border: "#FECACA", label: "Failed" },
};

export function StatusBadge({ status, testId }) {
  const s = STATUS_STYLES[status] || STATUS_STYLES.processed;
  return (
    <span
      data-testid={testId}
      className="inline-flex items-center rounded-sm border px-2 py-0.5 text-xs font-semibold whitespace-nowrap"
      style={{ backgroundColor: s.bg, color: s.text, borderColor: s.border }}
    >
      {s.label}
    </span>
  );
}

// ---- Quality badge ---------------------------------------------------------
const QUALITY_STYLES = {
  high: { text: "#065F46", label: "High" },
  medium: { text: "#92400E", label: "Medium" },
  low: { text: "#991B1B", label: "Low" },
};

export function QualityBadge({ score, testId }) {
  const q = QUALITY_STYLES[score] || { text: "#4B5563", label: score || "—" };
  return (
    <span
      data-testid={testId}
      className="inline-flex items-center gap-1.5 text-xs font-medium"
      style={{ color: q.text }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: q.text }} />
      {q.label}
    </span>
  );
}

// ---- Extraction method tag -------------------------------------------------
const METHOD_LABELS = { text_pdf: "Text PDF", ocr: "OCR", failed: "Failed" };
export function MethodTag({ method }) {
  return (
    <span className="inline-flex items-center rounded-sm border border-line bg-canvas-muted px-2 py-0.5 font-mono text-xs text-[#4B5563]">
      {METHOD_LABELS[method] || method || "—"}
    </span>
  );
}

// ---- Confidence indicator --------------------------------------------------
export function Confidence({ value, testId }) {
  const pct = Math.round((value || 0) * 100);
  let color = "#991B1B";
  if (pct >= 90) color = "#16A34A";
  else if (pct >= 75) color = "#65A30D";
  else if (pct >= 70) color = "#CA8A04";
  return (
    <div className="flex items-center gap-2" data-testid={testId}>
      <div className="h-1.5 w-16 rounded-full bg-canvas-muted overflow-hidden">
        <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="font-tabular text-xs font-semibold tabular-nums" style={{ color }}>
        {pct}%
      </span>
    </div>
  );
}

// ---- Button ----------------------------------------------------------------
export function Button({ variant = "primary", className = "", children, ...props }) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-sm px-4 py-2 text-sm font-semibold transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-ink text-white hover:bg-ink-hover",
    outline: "border border-line-strong bg-white text-ink hover:bg-canvas-muted",
    ghost: "text-[#4B5563] hover:bg-canvas-muted",
    danger: "bg-[#991B1B] text-white hover:bg-[#7F1D1D]",
  };
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}

// ---- Card ------------------------------------------------------------------
export function Card({ className = "", children, ...props }) {
  return (
    <div
      className={`rounded-md border border-line bg-white shadow-sm ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
