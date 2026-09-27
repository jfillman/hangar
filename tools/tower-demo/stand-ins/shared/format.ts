export const STALE_THRESHOLD_MS = 7 * 24 * 60 * 60 * 1000;
export function relativeTime(iso?: string): string {
  if (!iso) return '—';
  const diff = Date.now() - new Date(iso).getTime();
  const abs = Math.abs(diff);
  const m = Math.round(abs / 60000);
  let s: string;
  if (m < 1) s = 'just now';
  else if (m < 60) s = `${m}m`;
  else if (m < 60 * 24) s = `${Math.round(m / 60)}h`;
  else s = `${Math.round(m / 1440)}d`;
  if (s === 'just now') return s;
  return diff >= 0 ? `${s} ago` : `in ${s}`;
}
export function formatDateTime(iso?: string): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-CA', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false });
}
