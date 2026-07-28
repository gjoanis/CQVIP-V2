import { useEffect, useState } from "react";

import { DataTable } from "../components/DataTable";
import { administrationApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { Role } from "../types";

export function Administration() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    administrationApi
      .listRoles()
      .then(setRoles)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load roles"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Administration</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={roles}
          rowKey={(r) => r.id}
          emptyMessage="No roles defined yet."
          columns={[
            { header: "Name", render: (r) => r.name, sortValue: (r) => r.name },
            { header: "Description", render: (r) => r.description || "—", sortValue: (r) => r.description },
          ]}
        />
      )}
    </div>
  );
}
