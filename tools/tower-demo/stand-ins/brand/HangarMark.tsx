import marks from './marks.json';
export function HangarMark({ glyph, size = 24 }: { glyph: string; size?: number }) {
  const inner = (marks as Record<string, string>)[glyph] ?? '';
  return (
    <svg viewBox="0 0 96 96" width={size} height={size} role="img" aria-label={`${glyph} mark`}
      dangerouslySetInnerHTML={{ __html: inner }} style={{ flexShrink: 0 }} />
  );
}
