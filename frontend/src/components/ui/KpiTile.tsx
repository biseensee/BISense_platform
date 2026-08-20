import Card from './Card';
import { diverging } from '../../theme/tokens';

interface KpiTileProps {
  label: string;
  value: string;
  deltaPct?: number; // e.g. 4.2 or -1.8
  deltaLabel?: string; // e.g. "к пред. месяцу"
}

/**
 * Hero-number stat tile. Delta uses the diverging pair (blue = positive,
 * red = negative) per docs/DESIGN_SYSTEM.md §4 — text-colored, not a chip,
 * since it sits directly beside the KPI value as a reading aid.
 */
export default function KpiTile({ label, value, deltaPct, deltaLabel }: KpiTileProps) {
  const isPositive = (deltaPct ?? 0) >= 0;
  const deltaColor = deltaPct === undefined ? undefined : isPositive ? diverging.positive : diverging.negative;

  return (
    <Card>
      <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-secondary)' }}>{label}</div>
      <div
        style={{
          fontSize: 40,
          lineHeight: '44px',
          fontWeight: 700,
          color: 'var(--text-primary)',
          marginTop: 8,
        }}
      >
        {value}
      </div>
      {deltaPct !== undefined && (
        <div style={{ marginTop: 8, fontSize: 13, fontWeight: 600, color: deltaColor }}>
          {isPositive ? '▲' : '▼'} {Math.abs(deltaPct).toFixed(1)}%
          {deltaLabel && (
            <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}> {deltaLabel}</span>
          )}
        </div>
      )}
    </Card>
  );
}
