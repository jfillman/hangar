// Dates shown to readers are always month first: "October 2, 2026", or "Oct 2, 2026" where space is tight.
// Data keeps ISO dates (2026-10-02); format them here, never by hand.
const at = (iso: string) => new Date(`${iso.slice(0, 10)}T12:00:00Z`);

export const longDate = (iso: string) =>
  at(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });

export const shortDate = (iso: string) =>
  at(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' });
