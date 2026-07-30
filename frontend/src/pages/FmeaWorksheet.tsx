import { useEffect, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";

import { fmeaApi, systemsApi, usersApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { FmeaAnalysis, FmeaLineItem, FmeaStatus, SystemItem, User } from "../types";

const RATINGS = Array.from({ length: 10 }, (_, i) => i + 1);
const STATUSES: FmeaStatus[] = ["draft", "in_review", "approved"];

function rpnClass(rpn: number): string {
  if (rpn >= 100) return "critical";
  if (rpn >= 50) return "high";
  if (rpn >= 20) return "medium";
  return "low";
}

const AI_FIELD_KEYS = [
  "potential_failure_mode", "potential_effect", "severity",
  "potential_cause", "occurrence", "current_controls", "detection", "recommended_action",
] as const satisfies readonly (keyof FmeaLineItem)[];

type AiFieldKey = (typeof AI_FIELD_KEYS)[number];

function pickAiFields(source: FmeaLineItem): Pick<FmeaLineItem, AiFieldKey> {
  const picked = {} as Pick<FmeaLineItem, AiFieldKey>;
  for (const key of AI_FIELD_KEYS) picked[key] = source[key] as never;
  return picked;
}

interface ItemCardProps {
  item: FmeaLineItem;
  fmeaId: string;
  users: User[];
  onSave: (itemId: string, fields: Partial<FmeaLineItem>) => Promise<void>;
  onDelete: (itemId: string) => void;
}

function FmeaItemCard({ item, fmeaId, users, onSave, onDelete }: ItemCardProps) {
  const [draft, setDraft] = useState(item);
  const [suggesting, setSuggesting] = useState(false);
  const [pendingSuggestion, setPendingSuggestion] = useState(false);
  const [accepting, setAccepting] = useState(false);

  useEffect(() => {
    if (!pendingSuggestion) setDraft(item);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [item, pendingSuggestion]);

  function field<K extends keyof FmeaLineItem>(key: K, value: FmeaLineItem[K]) {
    setDraft((d) => ({ ...d, [key]: value }));
  }

  function isAiField(key: keyof FmeaLineItem): key is AiFieldKey {
    return (AI_FIELD_KEYS as readonly string[]).includes(key as string);
  }

  function saveField<K extends keyof FmeaLineItem>(key: K) {
    if (pendingSuggestion && isAiField(key)) return; // reviewing a suggestion -- don't persist yet
    if (draft[key] === item[key]) return;
    onSave(item.id, { [key]: draft[key] } as Partial<FmeaLineItem>);
  }

  async function saveNow<K extends keyof FmeaLineItem>(key: K, value: FmeaLineItem[K]) {
    setDraft((d) => ({ ...d, [key]: value }));
    if (pendingSuggestion && isAiField(key)) return; // reviewing a suggestion -- don't persist yet
    await onSave(item.id, { [key]: value } as Partial<FmeaLineItem>);
  }

  async function handleAiSuggest() {
    setSuggesting(true);
    try {
      const preview = await fmeaApi.aiSuggest(fmeaId, item.id);
      setDraft((d) => ({ ...d, ...pickAiFields(preview) }));
      setPendingSuggestion(true);
    } finally {
      setSuggesting(false);
    }
  }

  async function handleAcceptSuggestion() {
    setAccepting(true);
    try {
      await onSave(item.id, pickAiFields(draft));
      setPendingSuggestion(false);
    } finally {
      setAccepting(false);
    }
  }

  function handleDiscardSuggestion() {
    setDraft((d) => ({ ...d, ...pickAiFields(item) }));
    setPendingSuggestion(false);
  }

  const hasResulting = item.resulting_rpn !== null;
  const displayRpn = pendingSuggestion ? draft.severity * draft.occurrence * draft.detection : item.rpn;

  return (
    <div className="card assessment-entry">
      <div className="assessment-entry-header">
        <input
          className="fmea-step-input"
          value={draft.process_step}
          onChange={(e) => field("process_step", e.target.value)}
          onBlur={() => saveField("process_step")}
          aria-label="Process step"
        />
        <div className="requirement-group-meta">
          <span className={`badge badge-${rpnClass(displayRpn)}`}>RPN {displayRpn}</span>
          <button type="button" className="btn" disabled={suggesting || pendingSuggestion} onClick={handleAiSuggest}>
            {suggesting ? "Thinking..." : "AI Suggest"}
          </button>
          <button type="button" className="btn-link" onClick={() => onDelete(item.id)}>
            Delete
          </button>
        </div>
      </div>

      {pendingSuggestion && (
        <div className="ai-suggestion-banner">
          <span>AI suggestion below is a draft — edit anything, then:</span>
          <div className="ai-suggestion-actions">
            <button type="button" className="btn" disabled={accepting} onClick={handleAcceptSuggestion}>
              {accepting ? "Saving..." : "Accept Suggestion"}
            </button>
            <button type="button" className="btn-link" onClick={handleDiscardSuggestion}>
              Discard
            </button>
          </div>
        </div>
      )}

      <div className="field-list">
        <div className="field-row">
          <span className="field-label">Potential Failure Mode</span>
          <textarea
            className="field-value-left fmea-textarea"
            value={draft.potential_failure_mode}
            onChange={(e) => field("potential_failure_mode", e.target.value)}
            onBlur={() => saveField("potential_failure_mode")}
          />
        </div>
        <div className="field-row">
          <span className="field-label">Potential Effect</span>
          <textarea
            className="field-value-left fmea-textarea"
            value={draft.potential_effect}
            onChange={(e) => field("potential_effect", e.target.value)}
            onBlur={() => saveField("potential_effect")}
          />
        </div>
        <div className="field-row">
          <span className="field-label">Potential Cause</span>
          <textarea
            className="field-value-left fmea-textarea"
            value={draft.potential_cause}
            onChange={(e) => field("potential_cause", e.target.value)}
            onBlur={() => saveField("potential_cause")}
          />
        </div>
        <div className="field-row">
          <span className="field-label">Current Controls</span>
          <textarea
            className="field-value-left fmea-textarea"
            value={draft.current_controls}
            onChange={(e) => field("current_controls", e.target.value)}
            onBlur={() => saveField("current_controls")}
          />
        </div>

        <div className="fmea-sod-row">
          <label>
            Severity
            <select value={draft.severity} onChange={(e) => saveNow("severity", Number(e.target.value))}>
              {RATINGS.map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>
          <label>
            Occurrence
            <select value={draft.occurrence} onChange={(e) => saveNow("occurrence", Number(e.target.value))}>
              {RATINGS.map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>
          <label>
            Detection
            <select value={draft.detection} onChange={(e) => saveNow("detection", Number(e.target.value))}>
              {RATINGS.map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="field-row">
          <span className="field-label">Recommended Action</span>
          <textarea
            className="field-value-left fmea-textarea"
            value={draft.recommended_action}
            onChange={(e) => field("recommended_action", e.target.value)}
            onBlur={() => saveField("recommended_action")}
          />
        </div>
        <div className="field-row">
          <span className="field-label">Owner</span>
          <select
            className="field-value"
            value={draft.action_owner_id ?? ""}
            onChange={(e) => saveNow("action_owner_id", e.target.value || null)}
          >
            <option value="">— Unassigned —</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.full_name}
              </option>
            ))}
          </select>
        </div>
        <div className="field-row">
          <span className="field-label">Target Date</span>
          <input
            type="date"
            className="field-value"
            value={draft.target_date ?? ""}
            onChange={(e) => saveNow("target_date", e.target.value || null)}
          />
        </div>
        <div className="field-row">
          <span className="field-label">Action Taken</span>
          <textarea
            className="field-value-left fmea-textarea"
            value={draft.action_taken}
            onChange={(e) => field("action_taken", e.target.value)}
            onBlur={() => saveField("action_taken")}
          />
        </div>

        <div className="fmea-sod-row">
          <label>
            Resulting Severity
            <select
              value={draft.resulting_severity ?? ""}
              onChange={(e) => saveNow("resulting_severity", e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">—</option>
              {RATINGS.map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>
          <label>
            Resulting Occurrence
            <select
              value={draft.resulting_occurrence ?? ""}
              onChange={(e) => saveNow("resulting_occurrence", e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">—</option>
              {RATINGS.map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>
          <label>
            Resulting Detection
            <select
              value={draft.resulting_detection ?? ""}
              onChange={(e) => saveNow("resulting_detection", e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">—</option>
              {RATINGS.map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>
          {hasResulting && (
            <span className={`badge badge-${rpnClass(item.resulting_rpn!)}`}>
              Resulting RPN {item.resulting_rpn}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export function FmeaWorksheet() {
  const { id } = useParams<{ id: string }>();
  const [fmea, setFmea] = useState<FmeaAnalysis | null>(null);
  const [system, setSystem] = useState<SystemItem | null>(null);
  const [items, setItems] = useState<FmeaLineItem[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newStep, setNewStep] = useState("");
  const [adding, setAdding] = useState(false);

  function load() {
    if (!id) return;
    setLoading(true);
    setError(null);
    fmeaApi
      .get(id)
      .then((analysis) => {
        setFmea(analysis);
        return Promise.all([fmeaApi.listItems(id), systemsApi.list(analysis.project_id), usersApi.list()]).then(
          ([itemList, systemList, userList]) => {
            setItems(itemList);
            setSystem(systemList.find((s) => s.id === analysis.system_id) ?? null);
            setUsers(userList);
          },
        );
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load Process FMEA"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function handleAddStep(e: FormEvent) {
    e.preventDefault();
    if (!id || !newStep.trim()) return;
    setAdding(true);
    setError(null);
    try {
      const item = await fmeaApi.createItem(id, newStep, items.length);
      setItems((prev) => [...prev, item]);
      setNewStep("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to add process step");
    } finally {
      setAdding(false);
    }
  }

  async function handleSaveItem(itemId: string, fields: Partial<FmeaLineItem>) {
    if (!id) return;
    try {
      const updated = await fmeaApi.updateItem(id, itemId, fields);
      setItems((prev) => prev.map((it) => (it.id === itemId ? updated : it)));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to save changes");
    }
  }

  async function handleDeleteItem(itemId: string) {
    if (!id) return;
    setError(null);
    try {
      await fmeaApi.deleteItem(id, itemId);
      setItems((prev) => prev.filter((it) => it.id !== itemId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to delete process step");
    }
  }

  async function handleStatusChange(status: FmeaStatus) {
    if (!id || !fmea) return;
    try {
      const updated = await fmeaApi.update(id, { title: fmea.title, description: fmea.description, status });
      setFmea(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to update status");
    }
  }

  if (loading) return <div className="page-loading">Loading...</div>;
  if (error && !fmea) return <div className="page-error">{error}</div>;
  if (!fmea) return <div className="page-error">Process FMEA not found.</div>;

  const highestRpn = items.reduce((max, it) => Math.max(max, it.rpn), 0);

  return (
    <div>
      <Link to="/fmea" className="back-link">
        ← Back to Process FMEA
      </Link>
      <div className="page-header">
        <h1>{fmea.title}</h1>
      </div>
      <p className="page-subtitle">
        {system ? system.name : "—"}
        {fmea.description ? ` · ${fmea.description}` : ""}
      </p>
      {error && <div className="page-error">{error}</div>}

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{items.length}</div>
          <div className="stat-label">Process Steps</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{highestRpn}</div>
          <div className="stat-label">Highest RPN</div>
        </div>
        <div className="stat-card">
          <div className="form-row" style={{ marginBottom: 0 }}>
            <label htmlFor="fmea-status">Status</label>
            <select
              id="fmea-status"
              value={fmea.status}
              onChange={(e) => handleStatusChange(e.target.value as FmeaStatus)}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <form className="form-inline" onSubmit={handleAddStep}>
        <div className="form-row" style={{ minWidth: 320 }}>
          <label htmlFor="fmea-new-step">Process step</label>
          <input
            id="fmea-new-step"
            required
            placeholder="e.g. Vial loading onto filling line"
            value={newStep}
            onChange={(e) => setNewStep(e.target.value)}
          />
        </div>
        <button className="btn" type="submit" disabled={adding}>
          {adding ? "Adding..." : "Add Process Step"}
        </button>
      </form>

      {items.length === 0 ? (
        <p className="empty-state">No process steps added yet.</p>
      ) : (
        <div className="assessment-doc">
          {[...items]
            .sort((a, b) => b.rpn - a.rpn)
            .map((item) => (
              <FmeaItemCard
                key={item.id}
                item={item}
                fmeaId={id!}
                users={users}
                onSave={handleSaveItem}
                onDelete={handleDeleteItem}
              />
            ))}
        </div>
      )}
    </div>
  );
}
