import { useEffect, useState } from "react";

import { useAuth } from "../hooks/useAuth";
import { settingsApi } from "../services/api";
import { ApiError } from "../services/apiClient";

export function Settings() {
  const { user } = useAuth();
  const [settings, setSettings] = useState<{ environment: string; anthropic_model: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    settingsApi
      .get()
      .then(setSettings)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load settings"));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Settings</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      <div className="card" style={{ marginBottom: 16 }}>
        <h2 style={{ marginTop: 0, fontSize: "1rem" }}>Account</h2>
        <p style={{ margin: "4px 0" }}>
          <strong>Name:</strong> {user?.full_name}
        </p>
        <p style={{ margin: "4px 0" }}>
          <strong>Email:</strong> {user?.email}
        </p>
      </div>

      <div className="card">
        <h2 style={{ marginTop: 0, fontSize: "1rem" }}>Backend</h2>
        {settings ? (
          <>
            <p style={{ margin: "4px 0" }}>
              <strong>Environment:</strong> {settings.environment}
            </p>
            <p style={{ margin: "4px 0" }}>
              <strong>AI model:</strong> {settings.anthropic_model}
            </p>
          </>
        ) : (
          <p className="empty-state">Loading...</p>
        )}
      </div>
    </div>
  );
}
