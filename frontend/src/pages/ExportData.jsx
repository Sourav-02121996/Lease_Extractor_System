import React, { useEffect, useState } from "react";
import { Download, FileSpreadsheet, CheckCircle2, Inbox } from "lucide-react";
import { Card, Button } from "../components/ui";
import { getApprovedCount, exportUrl } from "../lib/api";

const COLUMNS = [
  "File Name",
  "Upload Date",
  "Status",
  "Extraction Method",
  "Landlord / Property Owner Name",
  "Tenant / Business Name",
  "Guarantor Name(s)",
  "Mailing Addresses for all parties",
  "Contact Information",
  "Effective Date / Lease Start Date",
  "Lease End Date",
  "Lease Length",
  "Renewal Option Details",
  "Holdover Terms",
];

export default function ExportData() {
  const [count, setCount] = useState(null);

  useEffect(() => {
    getApprovedCount()
      .then((d) => setCount(d.approved))
      .catch(() => setCount(0));
  }, []);

  const hasApproved = count > 0;

  return (
    <div className="app-fade-in space-y-8">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.15em] text-[#9CA3AF]">
          Export
        </p>
        <h2 className="mt-1 font-heading text-3xl font-bold tracking-tight text-ink">
          Export Data
        </h2>
        <p className="mt-2 text-sm text-[#4B5563]">
          Download approved lease abstraction records as a CSV file (one row per approved
          document).
        </p>
      </div>

      <Card className="p-8">
        <div className="flex flex-col items-start gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-md bg-canvas-muted">
              <FileSpreadsheet className="text-ink" size={24} />
            </div>
            <div>
              <p className="font-heading text-lg font-semibold text-ink">
                Approved Lease CSV
              </p>
              <p className="mt-1 text-sm text-[#4B5563]" data-testid="approved-count-label">
                {count === null
                  ? "Checking approved records…"
                  : hasApproved
                  ? `${count} approved record${count === 1 ? "" : "s"} ready for export.`
                  : "No approved lease records available for export."}
              </p>
            </div>
          </div>

          {hasApproved ? (
            <a href={exportUrl} download data-testid="download-csv-link">
              <Button data-testid="download-csv-btn">
                <Download size={16} /> Download Approved Lease CSV
              </Button>
            </a>
          ) : (
            <Button disabled data-testid="download-csv-btn">
              <Download size={16} /> Download Approved Lease CSV
            </Button>
          )}
        </div>

        {!hasApproved && count !== null && (
          <div
            data-testid="no-approved-message"
            className="mt-6 flex items-center gap-3 rounded-sm border border-line bg-canvas-subtle px-4 py-3 text-sm text-[#4B5563]"
          >
            <Inbox size={18} className="text-[#9CA3AF]" />
            No approved lease records available for export. Approve documents from the review
            page to include them here.
          </div>
        )}
      </Card>

      {/* Column reference */}
      <Card className="p-6">
        <p className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-[#9CA3AF]">
          <CheckCircle2 size={14} /> CSV Columns
        </p>
        <div className="flex flex-wrap gap-2">
          {COLUMNS.map((c) => (
            <span
              key={c}
              className="rounded-sm border border-line bg-canvas-subtle px-2.5 py-1 font-mono text-xs text-[#4B5563]"
            >
              {c}
            </span>
          ))}
        </div>
      </Card>
    </div>
  );
}
