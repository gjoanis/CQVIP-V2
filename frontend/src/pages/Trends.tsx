import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { DataTable } from "../components/DataTable";
import { dashboardApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { LeaderboardRow, PortfolioTrends } from "../types";

const WEEK_OPTIONS = [4, 8, 12, 26];

const SERIES_COLORS = ["#4f46e5", "#0d9488", "#d97706", "#db2777", "#0284c7", "#65a30d", "#9333ea"];

function formatWeekLabel(dateStr: string): string {
  return new Date(`${dateStr}T00:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

interface LineChartProps {
  labels: string[];
  series: { name: string; color: string; values: number[] }[];
  maxValue?: number;
  valueSuffix?: string;
}

function LineChart({ labels, series, maxValue, valueSuffix = "" }: LineChartProps) {
  const width = 720;
  const height = 220;
  const padding = { top: 12, right: 16, bottom: 28, left: 36 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const allValues = series.flatMap((s) => s.values);
  const yMax = maxValue ?? Math.max(1, ...allValues);
  const stepX = labels.length > 1 ? plotWidth / (labels.length - 1) : 0;

  function pointFor(index: number, value: number): [number, number] {
    const x = padding.left + index * stepX;
    const y = padding.top + plotHeight - (value / yMax) * plotHeight;
    return [x, y];
  }

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="trend-chart" role="img">
      {[0, 0.25, 0.5, 0.75, 1].map((frac) => {
        const y = padding.top + plotHeight * (1 - frac);
        return (
          <g key={frac}>
            <line x1={padding.left} y1={y} x2={width - padding.right} y2={y} className="trend-chart-gridline" />
            <text x={padding.left - 6} y={y + 3} textAnchor="end" className="trend-chart-axis-label">
              {Math.round(yMax * frac)}
              {valueSuffix}
            </text>
          </g>
        );
      })}
      {labels.map((label, i) => {
        if (labels.length > 6 && i % Math.ceil(labels.length / 6) !== 0 && i !== labels.length - 1) return null;
        const [x] = pointFor(i, 0);
        return (
          <text key={label} x={x} y={height - 6} textAnchor="middle" className="trend-chart-axis-label">
            {formatWeekLabel(label)}
          </text>
        );
      })}
      {series.map((s) => {
        const d = s.values.map((v, i) => pointFor(i, v)).map(([x, y], i) => `${i === 0 ? "M" : "L"}${x},${y}`).join(" ");
        return (
          <g key={s.name}>
            <path d={d} fill="none" stroke={s.color} strokeWidth={2} />
            {s.values.map((v, i) => {
              const [x, y] = pointFor(i, v);
              return <circle key={i} cx={x} cy={y} r={2.5} fill={s.color} />;
            })}
          </g>
        );
      })}
    </svg>
  );
}

export function Trends() {
  const [weeks, setWeeks] = useState(12);
  const [trends, setTrends] = useState<PortfolioTrends | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([dashboardApi.trends(weeks), dashboardApi.leaderboard()])
      .then(([trendData, leaderboardData]) => {
        setTrends(trendData);
        setLeaderboard(leaderboardData.projects);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load trend data"))
      .finally(() => setLoading(false));
  }, [weeks]);

  const rankedByVerification = useMemo(
    () => [...leaderboard].sort((a, b) => b.requirement_verification_rate_pct - a.requirement_verification_rate_pct),
    [leaderboard],
  );

  const labels = trends?.projects[0]?.points.map((p) => p.date) ?? [];

  const readinessSeries = useMemo(
    () =>
      (trends?.projects ?? []).map((p, i) => ({
        name: p.name,
        color: SERIES_COLORS[i % SERIES_COLORS.length],
        values: p.points.map((pt) => pt.lifecycle_readiness_pct),
      })),
    [trends],
  );

  const riskSeries = useMemo(
    () =>
      (trends?.projects ?? []).map((p, i) => ({
        name: p.name,
        color: SERIES_COLORS[i % SERIES_COLORS.length],
        values: p.points.map((pt) => pt.open_risks),
      })),
    [trends],
  );

  return (
    <div>
      <div className="page-header">
        <h1>Trends &amp; Best Practices</h1>
        <select value={weeks} onChange={(e) => setWeeks(Number(e.target.value))}>
          {WEEK_OPTIONS.map((w) => (
            <option key={w} value={w}>
              Last {w} weeks
            </option>
          ))}
        </select>
      </div>
      <p className="page-subtitle">
        Trends are derived from existing requirement and risk timestamps, not a separate history log — they're
        directional (good for spotting patterns) rather than an exact audit-trail replay of past values. The
        leaderboard ranks projects by verification speed and risk closure speed to surface the best-performing
        projects worth learning from.
      </p>
      {error && <div className="page-error">{error}</div>}

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <>
          <h2 className="section-heading">Lifecycle Readiness % over time</h2>
          <LineChart labels={labels} series={readinessSeries} maxValue={100} valueSuffix="%" />

          <h2 className="section-heading">Open Risks over time</h2>
          <LineChart labels={labels} series={riskSeries} />

          <div className="trend-legend">
            {(trends?.projects ?? []).map((p, i) => (
              <span key={p.id} className="trend-legend-item">
                <span className="trend-legend-swatch" style={{ background: SERIES_COLORS[i % SERIES_COLORS.length] }} />
                {p.name}
              </span>
            ))}
          </div>

          <h2 className="section-heading">Leaderboard — Best Practices</h2>
          <DataTable
            rows={rankedByVerification}
            rowKey={(r) => r.id}
            emptyMessage="No projects yet."
            columns={[
              {
                header: "Project",
                render: (r) => (
                  <Link to={`/projects/${r.id}/dashboard`} className="requirement-link">
                    {r.name}
                  </Link>
                ),
                sortValue: (r) => r.name,
              },
              {
                header: "Requirements Verified",
                render: (r) => `${r.requirement_verified_count} / ${r.requirement_count}`,
              },
              {
                header: "Verification Rate",
                render: (r) => `${r.requirement_verification_rate_pct}%`,
                sortValue: (r) => r.requirement_verification_rate_pct,
              },
              {
                header: "Avg Days to Verify",
                render: (r) => (r.avg_requirement_verification_days ?? "—") + (r.avg_requirement_verification_days !== null ? " days" : ""),
                sortValue: (r) => r.avg_requirement_verification_days ?? Infinity,
              },
              {
                header: "Risks Closed",
                render: (r) => `${r.closed_risk_count} / ${r.risk_count}`,
              },
              {
                header: "Avg Days to Close Risk",
                render: (r) => (r.avg_risk_closure_days ?? "—") + (r.avg_risk_closure_days !== null ? " days" : ""),
                sortValue: (r) => r.avg_risk_closure_days ?? Infinity,
              },
            ]}
          />
        </>
      )}
    </div>
  );
}
