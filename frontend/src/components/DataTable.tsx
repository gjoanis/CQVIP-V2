import { useMemo, useState, type ReactNode } from "react";

interface Column<T> {
  header: string;
  render: (row: T) => ReactNode;
  /** Value to sort by when this column's header is clicked. Omit for non-sortable columns. */
  sortValue?: (row: T) => string | number;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  emptyMessage?: string;
}

type SortDirection = "asc" | "desc";

export function DataTable<T>({ columns, rows, rowKey, emptyMessage = "No records yet." }: DataTableProps<T>) {
  const [sortHeader, setSortHeader] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");

  const sortedRows = useMemo(() => {
    const column = columns.find((c) => c.header === sortHeader);
    if (!column?.sortValue) return rows;
    const sorted = [...rows].sort((a, b) => {
      const va = column.sortValue!(a);
      const vb = column.sortValue!(b);
      if (va < vb) return -1;
      if (va > vb) return 1;
      return 0;
    });
    return sortDirection === "asc" ? sorted : sorted.reverse();
  }, [rows, columns, sortHeader, sortDirection]);

  if (rows.length === 0) {
    return <p className="empty-state">{emptyMessage}</p>;
  }

  function handleHeaderClick(column: Column<T>) {
    if (!column.sortValue) return;
    if (sortHeader === column.header) {
      setSortDirection((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortHeader(column.header);
      setSortDirection("asc");
    }
  }

  return (
    <div className="data-table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col.header}
                className={col.sortValue ? "sortable" : undefined}
                onClick={() => handleHeaderClick(col)}
              >
                {col.header}
                {col.sortValue && (
                  <span className="sort-indicator">
                    {sortHeader === col.header ? (sortDirection === "asc" ? " ▲" : " ▼") : " ⇅"}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedRows.map((row) => (
            <tr key={rowKey(row)}>
              {columns.map((col) => (
                <td key={col.header}>{col.render(row)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
