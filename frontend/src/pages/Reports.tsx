import { useEffect, useState } from "react";

import { DataTable } from "../components/DataTable";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { reportsApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { Report } from "../types";

const REPORT_TYPE_LABELS: Record<string, string> = {
  project_summary: "Project Life Cycle",
  validation_summary: "Project Life Cycle", // legacy value from before the renames
};

function reportTypeLabel(reportType: string): string {
  return REPORT_TYPE_LABELS[reportType] ?? reportType;
}

export function Reports() {
  const { currentProject } = useCurrentProject();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const [viewingReport, setViewingReport] = useState<Report | null>(null);
  const [content, setContent] = useState("");
  const [savedContent, setSavedContent] = useState("");
  const [contentLoading, setContentLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const dirty = content !== savedContent;

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
      const report = await reportsApi.generate(currentProject.id);
      load(currentProject.id);
      handleView(report);
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

  async function handleView(report: Report) {
    if (!currentProject) return;
    setViewingReport(report);
    setContentLoading(true);
    setError(null);
    try {
      const { content: loaded } = await reportsApi.getContent(currentProject.id, report.id);
      setContent(loaded);
      setSavedContent(loaded);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load report content");
    } finally {
      setContentLoading(false);
    }
  }

  function closeViewer() {
    setViewingReport(null);
    setContent("");
    setSavedContent("");
  }

  async function handleSave() {
    if (!currentProject || !viewingReport) return;
    setSaving(true);
    setError(null);
    try {
      await reportsApi.updateContent(currentProject.id, viewingReport.id, content);
      setSavedContent(content);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to save report");
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveAndDownload() {
    if (!currentProject || !viewingReport) return;
    if (dirty) await handleSave();
    await handleDownload(viewingReport);
  }

  if (!currentProject) {
    return <p className="empty-state">Select or create a project first.</p>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Reports — {currentProject.name}</h1>
        <button className="btn" disabled={generating} onClick={handleGenerate}>
          {generating ? "Generating..." : "Generate Project Life Cycle Report"}
        </button>
      </div>
      {error && <div className="page-error">{error}</div>}

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={reports}
          rowKey={(r) => r.id}
          emptyMessage="No reports generated yet. Click Generate Project Life Cycle Report above."
          columns={[
            { header: "Title", render: (r) => r.title, sortValue: (r) => r.title },
            { header: "Type", render: (r) => reportTypeLabel(r.report_type), sortValue: (r) => r.report_type },
            {
              header: "Generated",
              render: (r) => new Date(r.generated_at).toLocaleString(),
              sortValue: (r) => new Date(r.generated_at).getTime(),
            },
            {
              header: "",
              render: (r) => (
                <button className="btn-link" onClick={() => handleView(r)}>
                  View / Edit
                </button>
              ),
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

      {viewingReport && (
        <div className="card report-editor">
          <div className="report-editor-header">
            <h2>{viewingReport.title}</h2>
            <div className="toolbar">
              <button className="btn" disabled={!dirty || saving} onClick={handleSave}>
                {saving ? "Saving..." : "Save"}
              </button>
              <button
                className="btn"
                disabled={saving || downloadingId === viewingReport.id}
                onClick={handleSaveAndDownload}
              >
                {downloadingId === viewingReport.id ? "Downloading..." : dirty ? "Save & Download" : "Download"}
              </button>
              <button className="btn-link" onClick={closeViewer}>
                Close
              </button>
            </div>
          </div>
          <p className="page-subtitle" style={{ marginTop: -4 }}>
            Edits are saved back to this report file -- review and adjust the generated narrative before
            downloading.
          </p>
          {contentLoading ? (
            <div className="page-loading">Loading report...</div>
          ) : (
            <textarea
              className="report-editor-textarea"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              spellCheck={false}
            />
          )}
        </div>
      )}
    </div>
  );
}
