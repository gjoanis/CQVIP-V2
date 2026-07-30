import { api, downloadFile } from "./apiClient";
import type {
  ActionQueueRow,
  Client,
  CoverageSummary,
  DashboardMetrics,
  DocumentItem,
  FmeaAnalysis,
  FmeaLineItem,
  GapAnalysisRow,
  GeneratedProtocol,
  KnowledgeDocument,
  KnowledgeTaxonomy,
  Notification,
  Project,
  ProjectDashboard,
  ProjectNode,
  Report,
  Requirement,
  RequirementAttachment,
  RequirementStatus,
  Risk,
  Role,
  SearchResult,
  SystemItem,
  TraceabilityLink,
  User,
  ValidationActivity,
} from "../types";

export const dashboardApi = {
  get: () => api.get<DashboardMetrics>("/dashboard"),
};

export const projectDashboardApi = {
  get: (projectId: string) => api.get<ProjectDashboard>(`/projects/${projectId}/dashboard`),
  gapAnalysis: (projectId: string) =>
    api.get<GapAnalysisRow[]>(`/projects/${projectId}/dashboard/gap-analysis`),
  actionQueue: (projectId: string) =>
    api.get<ActionQueueRow[]>(`/projects/${projectId}/dashboard/action-queue`),
};

export const clientsApi = {
  list: () => api.get<Client[]>("/clients"),
  create: (data: Partial<Client>) => api.post<Client>("/clients", data),
  update: (id: string, data: Partial<Client>) => api.put<Client>(`/clients/${id}`, data),
  remove: (id: string) => api.del(`/clients/${id}`),
};

export const projectsApi = {
  list: (clientId?: string) => api.get<Project[]>(clientId ? `/projects?client_id=${clientId}` : "/projects"),
  get: (id: string) => api.get<Project>(`/projects/${id}`),
  create: (data: Partial<Project>) => api.post<Project>("/projects", data),
  update: (id: string, data: Partial<Project>) => api.put<Project>(`/projects/${id}`, data),
};

export const projectWorkspaceApi = {
  listNodes: (projectId: string) => api.get<ProjectNode[]>(`/projects/${projectId}/workspace/nodes`),
  createNode: (projectId: string, data: Partial<ProjectNode>) =>
    api.post<ProjectNode>(`/projects/${projectId}/workspace/nodes`, data),
};

export const systemsApi = {
  list: (projectId: string) => api.get<SystemItem[]>(`/systems?project_id=${projectId}`),
  create: (data: Partial<SystemItem>) => api.post<SystemItem>("/systems", data),
  update: (id: string, data: Partial<SystemItem>) => api.put<SystemItem>(`/systems/${id}`, data),
};

export const documentsApi = {
  list: (projectId: string) => api.get<DocumentItem[]>(`/documents?project_id=${projectId}`),
  upload: (projectId: string, docType: string, file: File, systemId?: string) => {
    const form = new FormData();
    form.append("file", file);
    const systemParam = systemId ? `&system_id=${systemId}` : "";
    return api.upload<DocumentItem>(
      `/documents?project_id=${projectId}&doc_type=${encodeURIComponent(docType)}${systemParam}`,
      form,
    );
  },
};

export const requirementsApi = {
  list: (projectId: string) => api.get<Requirement[]>(`/requirements?project_id=${projectId}`),
  get: (id: string) => api.get<Requirement>(`/requirements/${id}`),
  create: (data: Partial<Requirement>) => api.post<Requirement>("/requirements", data),
  update: (id: string, data: Partial<Requirement>) => api.put<Requirement>(`/requirements/${id}`, data),
  setStatus: (id: string, status: RequirementStatus) =>
    api.patch<Requirement>(`/requirements/${id}/status`, { status }),
  setSystem: (id: string, systemId: string | null) =>
    api.patch<Requirement>(`/requirements/${id}/system`, { system_id: systemId }),
  assignOwner: (id: string, userId: string) =>
    api.post<Requirement>(`/requirements/${id}/assign-owner`, { user_id: userId }),
  markNa: (id: string) => api.post<Requirement>(`/requirements/${id}/mark-na`),
  markUnderReview: (id: string) => api.post<Requirement>(`/requirements/${id}/mark-under-review`),
  verify: (id: string) => api.post<Requirement>(`/requirements/${id}/verify`),
  close: (id: string) => api.post<Requirement>(`/requirements/${id}/close`),
  assess: (id: string) => api.post<Requirement>(`/requirements/${id}/assess`),
  generateProtocol: (id: string) => api.post<GeneratedProtocol>(`/requirements/${id}/generate-protocol`),
  listAttachments: (id: string) => api.get<RequirementAttachment[]>(`/requirements/${id}/attachments`),
  uploadAttachment: (id: string, documentType: string, file: File, uploadedById?: string) => {
    const form = new FormData();
    form.append("file", file);
    const uploaderParam = uploadedById ? `&uploaded_by_id=${uploadedById}` : "";
    return api.upload<RequirementAttachment>(
      `/requirements/${id}/attachments?document_type=${encodeURIComponent(documentType)}${uploaderParam}`,
      form,
    );
  },
};

export const risksApi = {
  list: (projectId: string) => api.get<Risk[]>(`/risks?project_id=${projectId}`),
  create: (data: Partial<Risk>) => api.post<Risk>("/risks", data),
  update: (id: string, data: Partial<Risk>) => api.put<Risk>(`/risks/${id}`, data),
};

export const validationActivitiesApi = {
  list: (projectId: string) =>
    api.get<ValidationActivity[]>(`/validation-activities?project_id=${projectId}`),
  create: (data: Partial<ValidationActivity>) => api.post<ValidationActivity>("/validation-activities", data),
  update: (id: string, data: Partial<ValidationActivity>) =>
    api.put<ValidationActivity>(`/validation-activities/${id}`, data),
  seedStandardPhases: (projectId: string) =>
    api.post<ValidationActivity[]>(`/validation-activities/seed-standard-phases?project_id=${projectId}`),
};

export const traceabilityApi = {
  matrix: (projectId: string) => api.get<TraceabilityLink[]>(`/projects/${projectId}/traceability/matrix`),
  coverage: (projectId: string) =>
    api.get<CoverageSummary>(`/projects/${projectId}/traceability/coverage`),
};

export const reportsApi = {
  list: (projectId: string) => api.get<Report[]>(`/projects/${projectId}/reports`),
  generate: (projectId: string) => api.post<Report>(`/projects/${projectId}/reports/generate`),
  download: (projectId: string, report: Report) =>
    downloadFile(
      `/projects/${projectId}/reports/${report.id}/download`,
      report.file_path.split("/").pop(),
    ),
};

export const knowledgeApi = {
  search: (query: string, collection = "knowledge_base", topK = 10) =>
    api.get<SearchResult[]>(
      `/knowledge/search?q=${encodeURIComponent(query)}&collection=${collection}&top_k=${topK}`,
    ),
  taxonomy: () => api.get<KnowledgeTaxonomy>("/knowledge/taxonomy"),
  listDocuments: (collection: string) =>
    api.get<KnowledgeDocument[]>(`/knowledge/documents?collection=${encodeURIComponent(collection)}`),
  uploadDocument: (params: {
    collection: string;
    title: string;
    taxonomyValue: string;
    file: File;
    sourceUrl?: string;
    clientId?: string;
  }) => {
    const form = new FormData();
    form.append("file", params.file);
    const query = new URLSearchParams({
      collection: params.collection,
      title: params.title,
      taxonomy_value: params.taxonomyValue,
    });
    if (params.sourceUrl) query.set("source_url", params.sourceUrl);
    if (params.clientId) query.set("client_id", params.clientId);
    return api.upload<KnowledgeDocument>(`/knowledge/documents?${query.toString()}`, form);
  },
  deleteDocument: (documentId: string, collection: string) =>
    api.del(`/knowledge/documents/${documentId}?collection=${encodeURIComponent(collection)}`),
};

export const fmeaApi = {
  list: (projectId: string) => api.get<FmeaAnalysis[]>(`/fmea?project_id=${projectId}`),
  get: (id: string) => api.get<FmeaAnalysis>(`/fmea/${id}`),
  create: (data: Partial<FmeaAnalysis>) => api.post<FmeaAnalysis>("/fmea", data),
  update: (id: string, data: Partial<FmeaAnalysis>) => api.put<FmeaAnalysis>(`/fmea/${id}`, data),
  listItems: (fmeaId: string) => api.get<FmeaLineItem[]>(`/fmea/${fmeaId}/items`),
  createItem: (fmeaId: string, processStep: string, order: number) =>
    api.post<FmeaLineItem>(`/fmea/${fmeaId}/items`, { process_step: processStep, order }),
  updateItem: (fmeaId: string, itemId: string, data: Partial<FmeaLineItem>) =>
    api.put<FmeaLineItem>(`/fmea/${fmeaId}/items/${itemId}`, data),
  deleteItem: (fmeaId: string, itemId: string) => api.del(`/fmea/${fmeaId}/items/${itemId}`),
  aiSuggest: (fmeaId: string, itemId: string) =>
    api.post<FmeaLineItem>(`/fmea/${fmeaId}/items/${itemId}/ai-suggest`),
};

export const administrationApi = {
  listRoles: () => api.get<Role[]>("/admin/roles"),
};

export const usersApi = {
  list: () => api.get<User[]>("/users"),
  create: (data: { email: string; full_name: string; password: string; role_id?: string | null }) =>
    api.post<User>("/users", data),
};

export const notificationsApi = {
  listUnread: (userId: string) => api.get<Notification[]>(`/notifications?user_id=${userId}`),
  markRead: (id: string) => api.post<Notification>(`/notifications/${id}/read`),
};

export const settingsApi = {
  get: () => api.get<{ environment: string; anthropic_model: string }>("/settings"),
};
