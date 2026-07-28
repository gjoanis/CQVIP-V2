import type { ValidationActivity, ValidationActivityType, ValidationStatus } from "../types";

const PHASE_ORDER: ValidationActivityType[] = [
  "engineering_study", "fat", "sat", "commissioning", "iq", "oq", "pq", "final_report",
];

const PHASE_LABELS: Record<ValidationActivityType, string> = {
  engineering_study: "Engineering Studies",
  fat: "Factory Acceptance Testing (FAT)",
  sat: "Site Acceptance Testing (SAT)",
  commissioning: "Commissioning",
  iq: "Installation Qualification (IQ)",
  oq: "Operational Qualification (OQ)",
  pq: "Performance Qualification (PQ)",
  final_report: "Final Validation Report",
  other: "Other",
};

const STATUS_LABELS: Record<ValidationStatus, string> = {
  not_started: "Not started",
  in_progress: "In progress",
  passed: "Passed",
  failed: "Failed",
  blocked: "Blocked",
  not_applicable: "Not applicable",
};

const DAY_MS = 24 * 60 * 60 * 1000;

function parseDate(value: string | null | undefined): Date | null {
  if (!value) return null;
  const d = new Date(`${value}T00:00:00`);
  return Number.isNaN(d.getTime()) ? null : d;
}

interface DateRange {
  start: Date;
  end: Date;
  isPoint: boolean;
}

function effectiveRange(a: ValidationActivity): DateRange | null {
  const start = parseDate(a.start_date) ?? parseDate(a.planned_date);
  const end = parseDate(a.end_date) ?? parseDate(a.start_date) ?? parseDate(a.planned_date);
  if (!start && !end) return null;
  const s = start ?? (end as Date);
  const e = end ?? (start as Date);
  return { start: s, end: e, isPoint: s.getTime() === e.getTime() };
}

function formatShort(d: Date): string {
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

interface ValidationTimelineProps {
  activities: ValidationActivity[];
  /** The project's overall timeframe -- rendered as a shaded band behind every
   * row, and used to flag any activity whose dates fall outside of it. */
  windowStart?: string | null;
  windowEnd?: string | null;
}

export function ValidationTimeline({ activities, windowStart, windowEnd }: ValidationTimelineProps) {
  const windowStartDate = parseDate(windowStart);
  const windowEndDate = parseDate(windowEnd);
  const hasWindow = windowStartDate !== null || windowEndDate !== null;

  const ranged = activities
    .map((a) => ({ activity: a, range: effectiveRange(a) }))
    .filter((r) => r.range !== null) as { activity: ValidationActivity; range: DateRange }[];

  if (ranged.length === 0 && !hasWindow) {
    return (
      <p className="empty-state">
        No dates set yet — add a planned, start, or end date to an activity to see it on the timeline.
      </p>
    );
  }

  const allDates = [
    ...ranged.flatMap((r) => [r.range.start, r.range.end]),
    ...(windowStartDate ? [windowStartDate] : []),
    ...(windowEndDate ? [windowEndDate] : []),
  ];
  const minDate = new Date(Math.min(...allDates.map((d) => d.getTime())));
  const maxDate = new Date(Math.max(...allDates.map((d) => d.getTime())));
  const spanMs = Math.max(maxDate.getTime() - minDate.getTime(), DAY_MS);
  const padMs = Math.max(spanMs * 0.06, 3 * DAY_MS);
  const rangeStart = new Date(minDate.getTime() - padMs);
  const rangeEnd = new Date(maxDate.getTime() + padMs);
  const totalMs = rangeEnd.getTime() - rangeStart.getTime();

  function pct(d: Date): number {
    return ((d.getTime() - rangeStart.getTime()) / totalMs) * 100;
  }

  function isOutOfWindow(range: DateRange): boolean {
    if (windowStartDate && range.start < windowStartDate) return true;
    if (windowEndDate && range.end > windowEndDate) return true;
    return false;
  }

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const todayPct = today >= rangeStart && today <= rangeEnd ? pct(today) : null;

  const windowBandLeft = windowStartDate ? pct(windowStartDate) : 0;
  const windowBandRight = windowEndDate ? 100 - pct(windowEndDate) : 0;

  const hasOther = activities.some((a) => a.activity_type === "other");
  const types = hasOther ? [...PHASE_ORDER, "other" as ValidationActivityType] : PHASE_ORDER;

  const byType = new Map<ValidationActivityType, ValidationActivity[]>();
  for (const a of activities) {
    const list = byType.get(a.activity_type);
    if (list) list.push(a);
    else byType.set(a.activity_type, [a]);
  }

  const windowLabel = hasWindow
    ? `Project timeframe: ${windowStartDate ? formatShort(windowStartDate) : "no start set"} — ${
        windowEndDate ? formatShort(windowEndDate) : "no target end set"
      }`
    : undefined;

  return (
    <div className="timeline">
      <div className="timeline-axis">
        <span>{formatShort(rangeStart)}</span>
        <span>{formatShort(new Date((rangeStart.getTime() + rangeEnd.getTime()) / 2))}</span>
        <span>{formatShort(rangeEnd)}</span>
      </div>
      <div className="timeline-body">
        {types.map((type) => {
          const rows = byType.get(type) ?? [];
          const rowHeight = Math.max(rows.length, 1) * 32;
          return (
            <div className="timeline-row" key={type}>
              <div className="timeline-row-label">{PHASE_LABELS[type]}</div>
              <div className="timeline-track" style={{ height: `${rowHeight}px` }}>
                {hasWindow && (
                  <div
                    className="timeline-window-band"
                    style={{ left: `${windowBandLeft}%`, right: `${windowBandRight}%` }}
                    title={windowLabel}
                  />
                )}
                {todayPct !== null && (
                  <div className="timeline-today-line" style={{ left: `${todayPct}%` }} title={`Today — ${formatShort(today)}`} />
                )}
                {rows.length === 0 && <div className="timeline-track-empty" />}
                {rows.map((activity, i) => {
                  const range = effectiveRange(activity);
                  if (!range) return null;
                  const left = pct(range.start);
                  const width = range.isPoint ? 0 : Math.max(pct(range.end) - left, 0.6);
                  const top = i * 32;
                  const outOfWindow = isOutOfWindow(range);
                  const label = `${activity.name} — ${STATUS_LABELS[activity.status]} — ${
                    range.isPoint ? formatShort(range.start) : `${formatShort(range.start)} to ${formatShort(range.end)}`
                  }${outOfWindow ? " — outside project timeframe!" : ""}`;
                  return range.isPoint ? (
                    <div
                      key={activity.id}
                      className={`timeline-marker status-${activity.status}${outOfWindow ? " out-of-window" : ""}`}
                      style={{ left: `${left}%`, top: `${top + 6}px` }}
                      title={label}
                    />
                  ) : (
                    <div
                      key={activity.id}
                      className={`timeline-bar status-${activity.status}${outOfWindow ? " out-of-window" : ""}`}
                      style={{ left: `${left}%`, width: `${width}%`, top: `${top}px` }}
                      title={label}
                    >
                      <span className="timeline-bar-label">
                        {outOfWindow ? "⚠ " : ""}
                        {activity.name}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
      {hasWindow && (
        <div className="timeline-legend">
          <span className="timeline-legend-swatch timeline-legend-window" /> Project timeframe
        </div>
      )}
    </div>
  );
}
