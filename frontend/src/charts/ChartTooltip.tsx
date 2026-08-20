import { type TooltipProps } from 'recharts';

/**
 * Shared hover tooltip — dataviz-skill rule: every line/bar/donut ships a
 * hover layer by default. Card-styled to match the rest of the UI kit.
 */
export default function ChartTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div
      style={{
        background: 'var(--surface-card)',
        border: '1px solid var(--border-hairline)',
        borderRadius: 12,
        boxShadow: 'var(--shadow-popover, 0 12px 32px rgba(11,11,11,0.14))',
        padding: '10px 14px',
        fontSize: 13,
        minWidth: 140,
      }}
    >
      {label !== undefined && (
        <div style={{ fontWeight: 600, marginBottom: 6, color: 'var(--text-primary)' }}>{label}</div>
      )}
      {payload.map((entry) => (
        <div
          key={entry.dataKey as string}
          style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)' }}
        >
          <span
            aria-hidden
            style={{ width: 8, height: 8, borderRadius: '50%', background: entry.color }}
          />
          <span style={{ flex: 1 }}>{entry.name}</span>
          <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
            {typeof entry.value === 'number' ? entry.value.toLocaleString('ru-RU') : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
}
