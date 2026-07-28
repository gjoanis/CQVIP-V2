// Shared ordering for low/medium/high/critical style fields, so sorting by
// severity or priority reflects actual severity order, not alphabetical order.
export const SEVERITY_RANK: Record<string, number> = {
  low: 0,
  medium: 1,
  high: 2,
  critical: 3,
};
