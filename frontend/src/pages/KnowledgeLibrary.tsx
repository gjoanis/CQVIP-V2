import { useEffect, useRef, useState, type FormEvent } from "react";

import { DataTable } from "../components/DataTable";
import { clientsApi, knowledgeApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { Client, KnowledgeDocument, KnowledgeTaxonomy, SearchResult } from "../types";

const COLLECTIONS = [
  { value: "regulatory_library", label: "Global Regulatory Library (FDA/EMA/MHRA/ICH/...)", field: "body" },
  { value: "industry_standards", label: "Industry Standards (GAMP 5, ISO, ISPE, ...)", field: "standard" },
  { value: "client_knowledge", label: "Client Knowledge", field: "category" },
  { value: "internal_knowledge", label: "Internal Knowledge", field: "category" },
];

function formatDate(value: string): string {
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleDateString();
}

export function KnowledgeLibrary() {
  const [collection, setCollection] = useState(COLLECTIONS[0].value);
  const [taxonomy, setTaxonomy] = useState<KnowledgeTaxonomy>({});
  const [clients, setClients] = useState<Client[]>([]);
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [docsLoading, setDocsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadTaxonomyValue, setUploadTaxonomyValue] = useState("");
  const [uploadSourceUrl, setUploadSourceUrl] = useState("");
  const [uploadClientId, setUploadClientId] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{ sent: number; total: number } | null>(null);

  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [searching, setSearching] = useState(false);

  const activeCollection = COLLECTIONS.find((c) => c.value === collection)!;
  const taxonomyValues = taxonomy[collection] ?? [];

  useEffect(() => {
    knowledgeApi.taxonomy().then(setTaxonomy).catch(() => setTaxonomy({}));
    clientsApi.list().then(setClients).catch(() => setClients([]));
  }, []);

  function loadDocuments(coll: string) {
    setDocsLoading(true);
    knowledgeApi
      .listDocuments(coll)
      .then(setDocuments)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load documents"))
      .finally(() => setDocsLoading(false));
  }

  useEffect(() => {
    loadDocuments(collection);
    setUploadTaxonomyValue("");
  }, [collection]);

  async function handleUpload(e: FormEvent) {
    e.preventDefault();
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setError("Choose a file to upload");
      return;
    }
    setUploading(true);
    setUploadProgress(file.size > 800_000 ? { sent: 0, total: file.size } : null);
    setError(null);
    try {
      await knowledgeApi.uploadDocument({
        collection,
        title: uploadTitle,
        taxonomyValue: uploadTaxonomyValue,
        file,
        sourceUrl: uploadSourceUrl || undefined,
        clientId: collection === "client_knowledge" ? uploadClientId : undefined,
        onProgress: (sent, total) => setUploadProgress({ sent, total }),
      });
      setUploadTitle("");
      setUploadSourceUrl("");
      if (fileInputRef.current) fileInputRef.current.value = "";
      loadDocuments(collection);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      setUploadProgress(null);
    }
  }

  async function handleDelete(documentId: string) {
    setError(null);
    try {
      await knowledgeApi.deleteDocument(documentId, collection);
      setDocuments((prev) => prev.filter((d) => d.document_id !== documentId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to delete document");
    }
  }

  function clientName(id: string | undefined): string {
    return clients.find((c) => c.id === id)?.name ?? id ?? "—";
  }

  async function handleSearch(e: FormEvent) {
    e.preventDefault();
    setSearching(true);
    setError(null);
    try {
      setResults(await knowledgeApi.search(query, collection));
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `${err.message} (if this is a 500, the backend's chromadb dependency may not be installed — see backend/README.md)`
          : "Search failed",
      );
      setResults(null);
    } finally {
      setSearching(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Knowledge Library</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      <div className="form-row" style={{ maxWidth: 420, marginBottom: 20 }}>
        <label htmlFor="kb-active-collection">Collection</label>
        <select id="kb-active-collection" value={collection} onChange={(e) => setCollection(e.target.value)}>
          {COLLECTIONS.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Add / Update Knowledge</h2>
        <p className="page-subtitle" style={{ marginTop: -4, marginBottom: 16 }}>
          Upload a new document or a newer version of an existing one — it's parsed, chunked, and made
          searchable immediately.
        </p>
        <form className="form-inline" onSubmit={handleUpload} style={{ marginBottom: 0 }}>
          <div className="form-row">
            <label htmlFor="kb-title">Title</label>
            <input id="kb-title" required value={uploadTitle} onChange={(e) => setUploadTitle(e.target.value)} />
          </div>
          <div className="form-row">
            <label htmlFor="kb-taxonomy">{activeCollection.field === "body" ? "Regulatory Body" : activeCollection.field === "standard" ? "Standard" : "Category"}</label>
            <select
              id="kb-taxonomy"
              required
              value={uploadTaxonomyValue}
              onChange={(e) => setUploadTaxonomyValue(e.target.value)}
            >
              <option value="" disabled>
                — Select —
              </option>
              {taxonomyValues.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </div>
          {collection === "client_knowledge" && (
            <div className="form-row">
              <label htmlFor="kb-client">Client</label>
              <select id="kb-client" required value={uploadClientId} onChange={(e) => setUploadClientId(e.target.value)}>
                <option value="" disabled>
                  — Select —
                </option>
                {clients.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div className="form-row">
            <label htmlFor="kb-source">Source reference (optional)</label>
            <input
              id="kb-source"
              placeholder="e.g. document number or URL"
              value={uploadSourceUrl}
              onChange={(e) => setUploadSourceUrl(e.target.value)}
            />
          </div>
          <div className="form-row">
            <label htmlFor="kb-file">File</label>
            <input id="kb-file" type="file" ref={fileInputRef} required />
          </div>
          <button className="btn" type="submit" disabled={uploading}>
            {uploading
              ? uploadProgress
                ? `Uploading... ${Math.round((uploadProgress.sent / uploadProgress.total) * 100)}%`
                : "Uploading..."
              : "Add to Knowledge Library"}
          </button>
        </form>
      </div>

      <h2 className="section-heading" style={{ marginTop: 0 }}>
        Documents in {activeCollection.label}
      </h2>
      {docsLoading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={documents}
          rowKey={(d) => d.document_id}
          emptyMessage="Nothing uploaded to this collection yet."
          columns={[
            { header: "Title", render: (d) => d.title, sortValue: (d) => d.title },
            {
              header: activeCollection.field === "body" ? "Body" : activeCollection.field === "standard" ? "Standard" : "Category",
              render: (d) => d.body ?? d.standard ?? d.category ?? "—",
            },
            ...(collection === "client_knowledge"
              ? [{ header: "Client", render: (d: KnowledgeDocument) => clientName(d.client_id) }]
              : []),
            { header: "Source", render: (d) => d.source_url || "—" },
            { header: "Added", render: (d) => formatDate(d.added_at), sortValue: (d) => d.added_at },
            { header: "Chunks", render: (d) => d.chunk_count },
            {
              header: "",
              render: (d) => (
                <button className="btn-link" onClick={() => handleDelete(d.document_id)}>
                  Delete
                </button>
              ),
            },
          ]}
        />
      )}

      <h2 className="section-heading">Search</h2>
      <form className="form-inline" onSubmit={handleSearch}>
        <div className="form-row" style={{ minWidth: 320 }}>
          <label htmlFor="kb-query">Search {activeCollection.label}</label>
          <input id="kb-query" required value={query} onChange={(e) => setQuery(e.target.value)} />
        </div>
        <button className="btn" type="submit" disabled={searching}>
          {searching ? "Searching..." : "Search"}
        </button>
      </form>

      {results && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {results.length === 0 && <p className="empty-state">No results.</p>}
          {results.map((r, i) => (
            <div className="card" key={i}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>{r.source}</div>
              <div style={{ fontSize: "0.88rem", color: "var(--color-text-muted)" }}>{r.text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
