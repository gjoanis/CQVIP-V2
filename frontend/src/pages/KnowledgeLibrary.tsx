import { useState, type FormEvent } from "react";

import { knowledgeApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { SearchResult } from "../types";

const COLLECTIONS = [
  { value: "regulatory_library", label: "Global Regulatory Library (FDA/EMA/MHRA/ICH/...)" },
  { value: "industry_standards", label: "Industry Standards (GAMP 5, ISO, ISPE, ...)" },
  { value: "client_knowledge", label: "Client Knowledge" },
  { value: "internal_knowledge", label: "Internal Knowledge" },
];

export function KnowledgeLibrary() {
  const [query, setQuery] = useState("");
  const [collection, setCollection] = useState(COLLECTIONS[0].value);
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [searching, setSearching] = useState(false);

  async function handleSubmit(e: FormEvent) {
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

      <form className="form-inline" onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="kb-collection">Collection</label>
          <select id="kb-collection" value={collection} onChange={(e) => setCollection(e.target.value)}>
            {COLLECTIONS.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>
        <div className="form-row" style={{ minWidth: 320 }}>
          <label htmlFor="kb-query">Search</label>
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
