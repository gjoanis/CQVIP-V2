import { useEffect, useState } from "react";

import { DataTable } from "../components/DataTable";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { reportsApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { Report } from "../types";

export function Reports() {
  const { currentProject } = useCurrentProject();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  function load(projectId: string) {
    setLoading(true);
    reportsApi
      .list(projectId)
      .then(setReports)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load reports"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    if (currentProject) load(currentProject.id);
  }, [currentProject]);

  async function handleGenerate() {
    if (!currentProject) return;
    setGenerating(true);
    setError(null);
    try {
      await reportsApi.generate(currentProject.id);
      load(currentProject.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to generate report");
    } finally {
      setGenerating(false);
    }
  }

  async function handleDownload(report: Report) {
    if (!currentProject) return;
    setDownloadingId(report.id);
    setError(null);
    try {
      await reportsApi.download(currentProject.id, report);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to download report");
    } finally {
      setDownloadingId(null);
    }
  }

  if (!currentProject) {
    return <p className="empty-state">Select or create a project first.</p>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Reports — {currentProject.name}</h1>
        <button className="btn" disabled={generating} onClick={handleGenerate}>
          {generating ? "Generating..." : "Generate Validation Summary Report"}
        </button>
      </div>
      {error && <div className="page-error">{error}</div>}

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={reports}
          rowKey={(r) => r.id}
          emptyMessage="No reports generated yet. Click Generate Validation Summary Report above."
          columns={[
            { header: "Title", render: (r) => r.title, sortValue: (r) => r.title },
            { header: "Type", render: (r) => r.report_type, sortValue: (r) => r.report_type },
            {
              header: "Generated",
              render: (r) => new Date(r.generated_at).toLocaleString(),
              sortValue: (r) => new Date(r.generated_at).getTime(),
            },
            {
              header: "",
              render: (r) => (
                <button
                  className="btn-link"
                  disabled={downloadingId === r.id}
                  onClick={() => handleDownload(r)}
                >
                  {downloadingId === r.id ? "Downloading..." : "Download"}
                </button>
              ),
            },
          ]}
        />
      )}
    </div>
  );
}
