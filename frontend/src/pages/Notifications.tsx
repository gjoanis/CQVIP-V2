import { useEffect, useState } from "react";

import { useAuth } from "../hooks/useAuth";
import { notificationsApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { Notification } from "../types";

export function Notifications() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  function load(userId: string) {
    setLoading(true);
    notificationsApi
      .listUnread(userId)
      .then(setNotifications)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load notifications"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    if (user) load(user.id);
  }, [user]);

  async function markRead(id: string) {
    await notificationsApi.markRead(id);
    if (user) load(user.id);
  }

  return (
    <div>
      <div className="page-header">
        <h1>Notifications</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : notifications.length === 0 ? (
        <p className="empty-state">You're all caught up.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {notifications.map((n) => (
            <div className="card" key={n.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontWeight: 600 }}>{n.title}</div>
                {n.message && <div style={{ fontSize: "0.88rem", color: "var(--color-text-muted)" }}>{n.message}</div>}
              </div>
              <button className="btn-secondary btn" onClick={() => markRead(n.id)}>
                Mark read
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
