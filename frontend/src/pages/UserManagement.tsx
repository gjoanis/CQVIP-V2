import { useEffect, useState, type FormEvent } from "react";

import { DataTable } from "../components/DataTable";
import { usersApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { User } from "../types";

export function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load() {
    setLoading(true);
    usersApi
      .list()
      .then(setUsers)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load users"))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await usersApi.create({ email, full_name: fullName, password });
      setEmail("");
      setFullName("");
      setPassword("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create user");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>User Management</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      <form className="form-inline" onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="user-email">Email</label>
          <input id="user-email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="form-row">
          <label htmlFor="user-name">Full name</label>
          <input id="user-name" required value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </div>
        <div className="form-row">
          <label htmlFor="user-password">Password</label>
          <input
            id="user-password"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button className="btn" type="submit" disabled={submitting}>
          Add user
        </button>
      </form>

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={users}
          rowKey={(u) => u.id}
          emptyMessage="No users yet."
          columns={[
            { header: "Name", render: (u) => u.full_name, sortValue: (u) => u.full_name },
            { header: "Email", render: (u) => u.email, sortValue: (u) => u.email },
            {
              header: "Active",
              render: (u) => <span className={`badge ${u.is_active ? "badge-active" : ""}`}>{u.is_active ? "Yes" : "No"}</span>,
              sortValue: (u) => (u.is_active ? 1 : 0),
            },
          ]}
        />
      )}
    </div>
  );
}
