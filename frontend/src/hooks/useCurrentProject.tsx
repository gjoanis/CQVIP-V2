import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { projectsApi } from "../services/api";
import type { Project } from "../types";

const STORAGE_KEY = "cqvip_current_project_id";

interface CurrentProjectContextValue {
  projects: Project[];
  currentProject: Project | null;
  setCurrentProjectId: (id: string) => void;
  refreshProjects: () => Promise<void>;
  loading: boolean;
}

const CurrentProjectContext = createContext<CurrentProjectContextValue | undefined>(undefined);

export function CurrentProjectProvider({ children }: { children: ReactNode }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProjectId, setCurrentProjectIdState] = useState<string | null>(
    () => localStorage.getItem(STORAGE_KEY),
  );
  const [loading, setLoading] = useState(true);

  async function refreshProjects() {
    setLoading(true);
    try {
      const list = await projectsApi.list();
      setProjects(list);
      // Fall back to the first project if nothing is stored yet, or if the
      // stored id no longer matches any project (e.g. a reset database).
      if (list.length > 0 && !list.some((p) => p.id === currentProjectId)) {
        setCurrentProjectId(list[0].id);
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function setCurrentProjectId(id: string) {
    setCurrentProjectIdState(id);
    localStorage.setItem(STORAGE_KEY, id);
  }

  const currentProject = projects.find((p) => p.id === currentProjectId) ?? null;

  return (
    <CurrentProjectContext.Provider
      value={{ projects, currentProject, setCurrentProjectId, refreshProjects, loading }}
    >
      {children}
    </CurrentProjectContext.Provider>
  );
}

export function useCurrentProject(): CurrentProjectContextValue {
  const ctx = useContext(CurrentProjectContext);
  if (!ctx) throw new Error("useCurrentProject must be used within CurrentProjectProvider");
  return ctx;
}
