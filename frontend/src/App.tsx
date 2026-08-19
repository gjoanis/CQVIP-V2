import { Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import { AuthLayout } from "./layouts/AuthLayout";
import { MainLayout } from "./layouts/MainLayout";
import { Administration } from "./pages/Administration";
import { Clients } from "./pages/Clients";
import { Dashboard } from "./pages/Dashboard";
import { DocumentView } from "./pages/DocumentView";
import { Documents } from "./pages/Documents";
import { FmeaWorksheet } from "./pages/FmeaWorksheet";
import { KnowledgeLibrary } from "./pages/KnowledgeLibrary";
import { Login } from "./pages/Login";
import { Notifications } from "./pages/Notifications";
import { ProcessFmea } from "./pages/ProcessFmea";
import { ProjectDashboard } from "./pages/ProjectDashboard";
import { ProjectWorkspace } from "./pages/ProjectWorkspace";
import { Projects } from "./pages/Projects";
import { Reports } from "./pages/Reports";
import { RequirementWorkspace } from "./pages/RequirementWorkspace";
import { Requirements } from "./pages/Requirements";
import { RiskRegister } from "./pages/RiskRegister";
import { Settings } from "./pages/Settings";
import { Systems } from "./pages/Systems";
import { TraceabilityMatrix } from "./pages/TraceabilityMatrix";
import { Trends } from "./pages/Trends";
import { UserManagement } from "./pages/UserManagement";
import { ValidationActivities } from "./pages/ValidationActivities";

function LoginRoute() {
  const { user } = useAuth();
  if (user) return <Navigate to="/" replace />;
  return (
    <AuthLayout>
      <Login />
    </AuthLayout>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="trends" element={<Trends />} />
          <Route path="clients" element={<Clients />} />
          <Route path="projects" element={<Projects />} />
          <Route path="projects/:projectId/dashboard" element={<ProjectDashboard />} />
          <Route path="workspace" element={<ProjectWorkspace />} />
          <Route path="systems" element={<Systems />} />
          <Route path="documents" element={<Documents />} />
          <Route path="documents/:id" element={<DocumentView />} />
          <Route path="requirements" element={<Requirements />} />
          <Route path="requirements/:id" element={<RequirementWorkspace />} />
          <Route path="risks" element={<RiskRegister />} />
          <Route path="fmea" element={<ProcessFmea />} />
          <Route path="fmea/:id" element={<FmeaWorksheet />} />
          <Route path="traceability" element={<TraceabilityMatrix />} />
          <Route path="validation" element={<ValidationActivities />} />
          <Route path="reports" element={<Reports />} />
          <Route path="knowledge" element={<KnowledgeLibrary />} />
          <Route path="admin" element={<Administration />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
