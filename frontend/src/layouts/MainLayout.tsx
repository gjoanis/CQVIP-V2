import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

import { ProjectSelector } from "../components/ProjectSelector";
import { useAuth } from "../hooks/useAuth";
import { CurrentProjectProvider } from "../hooks/useCurrentProject";

interface NavItem {
  to: string;
  label: string;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    label: "Portfolio",
    items: [
      { to: "/clients", label: "Clients" },
      { to: "/projects", label: "Projects" },
      { to: "/trends", label: "Trends & Best Practices" },
      { to: "/workspace", label: "Project Workspace" },
      { to: "/systems", label: "Systems & Processes" },
    ],
  },
  {
    label: "Validation",
    items: [
      { to: "/documents", label: "Documents" },
      { to: "/requirements", label: "Requirements" },
      { to: "/risks", label: "Risk Register" },
      { to: "/fmea", label: "Process FMEA" },
      { to: "/traceability", label: "Traceability Matrix" },
      { to: "/validation", label: "Validation Activities" },
      { to: "/reports", label: "Reports" },
    ],
  },
  {
    label: "Knowledge",
    items: [{ to: "/knowledge", label: "Knowledge Library" }],
  },
  {
    label: "System",
    items: [
      { to: "/admin", label: "Administration" },
      { to: "/users", label: "User Management" },
      { to: "/notifications", label: "Notifications" },
      { to: "/settings", label: "Settings" },
    ],
  },
];

const STORAGE_KEY = "cqvip_sidebar_expanded";

function loadExpandedState(): Record<string, boolean> {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return JSON.parse(stored);
  } catch {
    // fall through to default
  }
  return Object.fromEntries(NAV_GROUPS.map((g) => [g.label, true]));
}

function SidebarNavGroup({ group }: { group: NavGroup }) {
  const location = useLocation();
  const containsActive = group.items.some((item) => location.pathname === item.to);
  const [expandedState, setExpandedState] = useState(loadExpandedState);
  const expanded = expandedState[group.label] ?? true;

  function toggle() {
    const next = { ...expandedState, [group.label]: !expanded };
    setExpandedState(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }

  const showItems = expanded || containsActive;

  return (
    <div className="sidebar-group">
      <button type="button" className="sidebar-group-header" onClick={toggle}>
        {group.label}
        <span className={"sidebar-group-chevron" + (showItems ? " expanded" : "")}>▶</span>
      </button>
      {showItems && (
        <div className="sidebar-group-items">
          {group.items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => "sidebar-link nested" + (isActive ? " active" : "")}
            >
              {item.label}
            </NavLink>
          ))}
        </div>
      )}
    </div>
  );
}

function getInitials(name: string | undefined): string {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/);
  const initials = parts.length > 1 ? parts[0][0] + parts[parts.length - 1][0] : parts[0].slice(0, 2);
  return initials.toUpperCase();
}

export function MainLayout() {
  const { user, logout } = useAuth();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const location = useLocation();

  // Close the mobile drawer whenever the route changes (i.e. after tapping a nav link).
  useEffect(() => {
    setMobileNavOpen(false);
  }, [location.pathname]);

  return (
    <CurrentProjectProvider>
      <div className="app-shell">
        {mobileNavOpen && <div className="sidebar-overlay" onClick={() => setMobileNavOpen(false)} />}
        <aside className={"sidebar" + (mobileNavOpen ? " mobile-open" : "")}>
          <div className="sidebar-brand">CQVIP</div>
          <nav className="sidebar-nav">
            <NavLink to="/" end className={({ isActive }) => "sidebar-link" + (isActive ? " active" : "")}>
              Dashboard
            </NavLink>
            {NAV_GROUPS.map((group) => (
              <SidebarNavGroup key={group.label} group={group} />
            ))}
          </nav>
        </aside>
        <div className="app-main">
          <header className="app-header">
            <button
              type="button"
              className="sidebar-toggle"
              aria-label="Toggle navigation"
              onClick={() => setMobileNavOpen((v) => !v)}
            >
              ☰
            </button>
            <ProjectSelector />
            <div className="app-header-user" data-initials={getInitials(user?.full_name)}>
              <span>{user?.full_name}</span>
              <button className="btn-link" onClick={logout}>
                Sign out
              </button>
            </div>
          </header>
          <main className="app-content">
            <Outlet />
          </main>
        </div>
      </div>
    </CurrentProjectProvider>
  );
}
