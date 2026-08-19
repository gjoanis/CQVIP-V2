import { useEffect, useState, type FormEvent } from "react";

import { DataTable } from "../components/DataTable";
import { clientsApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { Client } from "../types";

export function Clients() {
  const [clients, setClients] = useState<Client[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [deletePendingId, setDeletePendingId] = useState<string | null>(null);

  function load() {
    setLoading(true);
    clientsApi
      .list()
      .then(setClients)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load clients"))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await clientsApi.create({ name, industry });
      setName("");
      setIndustry("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create client");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(clientId: string) {
    setError(null);
    try {
      await clientsApi.remove(clientId);
      setDeletePendingId(null);
      setClients((prev) => prev.filter((c) => c.id !== clientId));
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message || "Failed to delete client -- it may still have projects attached"
          : "Failed to delete client",
      );
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Clients</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      <form className="form-inline" onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="client-name">Name</label>
          <input id="client-name" required value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className="form-row">
          <label htmlFor="client-industry">Industry</label>
          <input id="client-industry" value={industry} onChange={(e) => setIndustry(e.target.value)} />
        </div>
        <button className="btn" type="submit" disabled={submitting}>
          Add client
        </button>
      </form>

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={clients}
          rowKey={(c) => c.id}
          emptyMessage="No clients yet — add one above."
          columns={[
            { header: "Name", render: (c) => c.name, sortValue: (c) => c.name },
            { header: "Industry", render: (c) => c.industry || "—", sortValue: (c) => c.industry },
            { header: "Contact", render: (c) => c.contact_email || "—", sortValue: (c) => c.contact_email },
            {
              header: "",
              render: (c) =>
                deletePendingId === c.id ? (
                  <span className="inline-confirm">
                    <button className="btn-danger" onClick={() => handleDelete(c.id)}>
                      Confirm
                    </button>
                    <button className="btn-link" onClick={() => setDeletePendingId(null)}>
                      Cancel
                    </button>
                  </span>
                ) : (
                  <button className="btn-link" onClick={() => setDeletePendingId(c.id)}>
                    Delete
                  </button>
                ),
            },
          ]}
        />
      )}
    </div>
  );
}
