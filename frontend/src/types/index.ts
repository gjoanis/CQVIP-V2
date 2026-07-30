export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
}

export interface Client {
  id: string;
  name: string;
  industry: string;
  contact_name: string;
  contact_email: string;
  address: string;
  notes: string;
}

export type ProjectStatus = "planning" | "active" | "on_hold" | "completed" | "cancelled";

export interface Project {
  id: string;
  client_id: string;
  name: string;
  code: string;
  description: string;
  status: ProjectStatus;
  start_date: string | null;
  target_end_date: string | null;
}

export interface ProjectNode {
  id: string;
  project_id: string;
  parent_id: string | null;
  node_type: string;
  name: string;
  order: number;
}

export type SystemType =
  | "equipment"
  | "facility_system"
  | "utility_system"
  | "computerized_system"
  | "process"
  | "other";

export interface SystemItem {
  id: string;
  project_id: string;
  name: string;
  system_type: SystemType;
  identifier: string;
  description: string;
  location: string;
}

export interface DocumentItem {
  id: string;
  project_id: string;
  system_id: string | null;
  name: string;
  doc_type: string;
  version: string;
  status: string;
  file_path: string;
}

export type RequirementPriority = "low" | "medium" | "high" | "critical";
export type RequirementStatus =
  | "open"
  | "in_progress"
  | "under_review"
  | "verified"
  | "closed"
  | "not_applicable";
export type RequirementDisposition = "applicable" | "not_applicable";

export interface Requirement {
  id: string;
  project_id: string;
  document_id: string | null;
  system_id: string | null;
  req_code: string;
  title: string;
  description: string;
  category: string;
  priority: RequirementPriority;
  status: RequirementStatus;
  source: string;
  disposition: RequirementDisposition;
  assigned_to_id: string | null;
  assigned_date: string | null;
  review_date: string | null;
  closed_date: string | null;
  verified: boolean;
  risk: string;
  gmp_reference: string;
  acceptance_criteria: string;
  suggested_test: string;
  protocol_section: string;
  verification_type: string;
}

export interface RequirementAttachment {
  id: string;
  file_name: string;
  document_type: string;
  content_type: string;
  uploaded_by_id: string | null;
  created_at: string;
}

export interface GeneratedProtocol {
  id: string;
  title: string;
  protocol_number: string;
  version: string;
}

export type RiskSeverity = "low" | "medium" | "high" | "critical";
export type RiskStatus = "open" | "mitigated" | "accepted" | "closed";

export interface Risk {
  id: string;
  project_id: string;
  requirement_id: string | null;
  owner_id: string | null;
  title: string;
  description: string;
  severity: RiskSeverity;
  likelihood: RiskSeverity;
  mitigation: string;
  status: RiskStatus;
  risk_score: number;
}

export type ValidationActivityType =
  | "engineering_study"
  | "fat"
  | "sat"
  | "commissioning"
  | "iq"
  | "oq"
  | "pq"
  | "final_report"
  | "other";
export type ValidationStatus = "not_started" | "in_progress" | "passed" | "failed" | "blocked" | "not_applicable";

export interface ValidationActivity {
  id: string;
  project_id: string;
  owner_id: string | null;
  name: string;
  activity_type: ValidationActivityType;
  status: ValidationStatus;
  planned_date: string | null;
  start_date: string | null;
  end_date: string | null;
}

export interface TraceabilityLink {
  id: string;
  requirement_id: string;
  req_code: string;
  requirement_title: string;
  protocol_id: string | null;
  protocol_number: string | null;
  protocol_title: string | null;
  test_step_id: string | null;
  test_step_description: string | null;
  coverage_status: string;
}

export interface CoverageSummary {
  total: number;
  covered: number;
  uncovered: number;
}

export interface Report {
  id: string;
  project_id: string;
  generated_by_id: string | null;
  report_type: string;
  title: string;
  file_path: string;
  generated_at: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  is_read: boolean;
  link: string;
}

export interface PortfolioProject {
  id: string;
  code: string;
  name: string;
  client_name: string;
  status: ProjectStatus;
  completion_pct: number;
  project_health: ProjectHealth;
  current_stage: string;
  systems_count: number;
  documents_count: number;
  requirements_count: number;
  open_risks: number;
  validation_activities_count: number;
}

export interface DashboardMetrics {
  projects: PortfolioProject[];
  total_projects: number;
  open_risks: number;
}

export type ProjectHealth = "red" | "yellow" | "green";

export interface PhaseReadiness {
  phase: number;
  label: string;
  pct: number;
}

export interface ProjectDashboard {
  lifecycle_readiness_pct: number;
  inspection_readiness_index_pct: number;
  execution_readiness_pct: number;
  current_stage: string;
  project_health: ProjectHealth;
  phase_readiness: PhaseReadiness[];
  total_requirements: number;
  critical_or_high_open: number;
  awaiting_verification: number;
  open_risks: number;
  executive_summary: string;
}

export interface GapAnalysisRow {
  requirement_id: string;
  req_code: string;
  title: string;
  category: string;
  priority: RequirementPriority;
  status: RequirementStatus;
  gap: string;
  risk: string;
  recommendation: string;
}

export interface ActionQueueRow {
  priority: RequirementPriority;
  requirement_id: string;
  req_code: string;
  title: string;
  action_required: string;
  owner_name: string;
  status: RequirementStatus;
}

export interface SearchResult {
  text: string;
  source: string;
  metadata: Record<string, unknown>;
  distance: number | null;
}

export interface KnowledgeDocument {
  document_id: string;
  title: string;
  source_url: string;
  added_at: string;
  uploaded_by_id: string;
  chunk_count: number;
  body?: string;
  standard?: string;
  category?: string;
  client_id?: string;
}

export type KnowledgeTaxonomy = Record<string, string[]>;

export interface ExtractedRequirement {
  req_code: string;
  title: string;
  description: string;
  category: string;
}

export type FmeaStatus = "draft" | "in_review" | "approved";

export interface FmeaAnalysis {
  id: string;
  project_id: string;
  system_id: string;
  title: string;
  description: string;
  status: FmeaStatus;
}

export interface FmeaLineItem {
  id: string;
  fmea_id: string;
  order: number;
  process_step: string;
  potential_failure_mode: string;
  potential_effect: string;
  severity: number;
  potential_cause: string;
  occurrence: number;
  current_controls: string;
  detection: number;
  rpn: number;
  recommended_action: string;
  action_owner_id: string | null;
  target_date: string | null;
  action_taken: string;
  resulting_severity: number | null;
  resulting_occurrence: number | null;
  resulting_detection: number | null;
  resulting_rpn: number | null;
}

export interface Role {
  id: string;
  name: string;
  description: string;
}
