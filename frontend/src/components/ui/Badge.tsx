import { status } from '../../theme/tokens';

type StatusKey = keyof typeof status;

const LABELS: Record<StatusKey, string> = {
  good: 'В норме',
  warning: 'Внимание',
  serious: 'Проблема',
  critical: 'Критично',
};

/**
 * Status chip. Per dataviz-skill rule, status color never carries meaning
 * alone — always paired with an icon (dot) + text label.
 */
export default function Badge({ status: statusKey }: { status: StatusKey }) {
  const color = status[statusKey];
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        padding: '4px 10px',
        borderRadius: 'var(--radius-chip)',
        background: `${color}1A`, // ~10% alpha wash
        color,
        fontSize: 13,
        fontWeight: 600,
      }}
    >
      <span aria-hidden style={{ width: 8, height: 8, borderRadius: '50%', background: color }} />
      {LABELS[statusKey]}
    </span>
  );
}
